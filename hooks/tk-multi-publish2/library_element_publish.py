import os
import sgtk
from shutil import copy

HookBaseClass = sgtk.get_hook_baseclass()

try:
    from sgtk.platform.qt import QtCore, QtGui
except ImportError:
    CustomWidgetController = None
else:
    class Completer(QtGui.QCompleter):

        def __init__(self, parent=None):
            super(Completer, self).__init__(parent)

            self.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
            self.setCompletionMode(QtGui.QCompleter.PopupCompletion)
            self.setWrapAround(False)

        # Add texts instead of replace
        def pathFromIndex(self, index):
            path = QtGui.QCompleter.pathFromIndex(self, index)

            lst = str(self.widget().text()).split(',')

            if len(lst) > 1:
                path = '%s, %s' % (','.join(lst[:-1]), path)

            return path

        # Add operator to separate between texts
        def splitPath(self, path):
            path = str(path.split(',')[-1]).lstrip(' ')
            return [path]

    class LibraryElementUI(QtGui.QWidget):
        def __init__(self, parent, app, qtframework):
            super(LibraryElementUI, self).__init__(parent)
            self._app = app
            self._initialized = False

            #shotgun_fields = qtframework.import_module("shotgun_fields")

            #self._fields_manager = shotgun_fields.ShotgunFieldManager(self)
            #self._fields_manager.initialized.connect(self.on_initialized)
            #self._fields_manager.initialize()

            #self._fields_manager.register_entity_field_class('Tag','name',shotgun_fields.multi_entity_widget.MultiEntityWidget,self._fields_manager.EDITABLE)

            layout = QtGui.QFormLayout(self)
            self.setLayout(layout)

            NameLayout = QtGui.QHBoxLayout(self)
            label = QtGui.QLabel("Element Name: ", self)
            self._name_field = QtGui.QLineEdit(self)
            NameLayout.addWidget(label)
            NameLayout.addWidget(self._name_field)
            layout.addRow(NameLayout)

            SourceLayout = QtGui.QHBoxLayout(self)
            sourceLabel = QtGui.QLabel("Element Source: ", self)
            self.sourceModel = QtGui.QStringListModel()
            self._source_field = QtGui.QLineEdit(self)
            sourceCompleter = Completer()
            self._source_field.setCompleter(sourceCompleter)
            sourceCompleter.setModel(self.sourceModel)
            SourceLayout.addWidget(sourceLabel)
            SourceLayout.addWidget(self._source_field)
            layout.addRow(SourceLayout)

            categories = self._app.sgtk.shotgun.schema_field_read("CustomNonProjectEntity01")['sg_category']['properties']['valid_values']['value']
            CatLayout = QtGui.QHBoxLayout(self)
            catLabel = QtGui.QLabel("Category: ", self)
            self._category = QtGui.QComboBox()
            for cat in categories:
                self._category.addItem(cat)
            CatLayout.addWidget(catLabel)
            CatLayout.addWidget(self._category)
            layout.addRow(CatLayout)

            TagLayout = QtGui.QHBoxLayout(self)
            TagLabel = QtGui.QLabel("Tags: ", self)
            self.tagModel = QtGui.QStringListModel()
            self._tags = QtGui.QLineEdit(self)
            completer = Completer()
            self._tags.setCompleter(completer)
            completer.setModel(self.tagModel)
            #self._tags = self._fields_manager.create_widget('Tag','name')
            TagLayout.addWidget(TagLabel)
            TagLayout.addWidget(self._tags)
            layout.addRow(TagLayout)

            self.updateFieldValues()
            self._initialized = True

        def updateFieldValues(self):
            fields = self._app.sgtk.shotgun.find("CustomNonProjectEntity01",[],["sg_source","tags"])
            src = list(dict.fromkeys([s["sg_source"] for s in fields]))
            tags = [s['name'] for s in self._app.sgtk.shotgun.find('Tag',[],['name'])]

            self.tagModel.setStringList(tags)
            self.sourceModel.setStringList(src)

        @property
        def initialized(self):
            return self._initialized

        @property
        def destName(self):
            return self._name_field.text()

        @destName.setter
        def destName(self, text):
            self._name_field.setText(text)

        @property
        def source(self):
            return self._source_field.text()

        @source.setter
        def source(self, text):
            self._source_field.setText(text)

        @property
        def category(self):
            return self._category.currentText()

        @category.setter
        def category(self, cat):
            i = self._category.findText(cat)
            if i == -1:
                i = 0
            self._category.setCurrentIndex(i)

        @property
        def tags(self):
            #return self._tags.get_value()
            if self._tags.text() == "":
                return []
            return self._tags.text().split(',')

        @tags.setter
        def tags(self, tagDict):
            tagNames = [tag['name'] for tag in tagDict]
            self._tags.setText(",".join(tagNames))
            #self._tags.set_value(tagDict)

class LibraryElementPublishPlugin(HookBaseClass):
    """
    Plugin for publishing elements to the element library
    """


    @property
    def icon(self):
        """
        Path to icon on disk
        """

        return os.path.join(
            self.disk_location,
            "icons",
            "alembic_cache_publish.py"
        )

    @property
    def name(self):
        """
        One line display name describing the Plugin
        """
        return "Library Element Publish"

    @property
    def description(self):
        """
        Verbose multi-line description of what the plugin does
        """
        publisher = self.parent
        library_path = publisher.sgtk.roots["element_library"]

        return """
        Copy the input source file to the element library located at %s
        """% (library_path)

    @property
    def settings(self):
        """
        Dictionary defining the settings that this plugin expexts to recieve
        through the settings parameter in the accept, validate, publish and
        finalize methods.
        """

        return{
            "File Extensions": {
                "type": "str",
                "default": "jpeg, jpg, png, mov, mp4, exr, dpx, tga",
                "description": "File extensions of files to include"
            },
            "Element Name": {
                "type": "str",
                "default": "",
                "decription": "New name of element for both library element and directory"
            },
            "Element Source": {
                "type": "str",
                "default": "",
                "decription": "Source of the element, could be a collected element library or a client, or internal..."
            },
            "Element Category": {
                "type": "str",
                "default": "",
                "description": "Category to submit the library element with"
            },
            "Element Tags": {
                "type": "list",
                "default": [],
                "desciption": "Tags that will submit to the library element to allow easier searching"
            }
        }

    @property
    def item_filters(self):
        """
        List of item types this plugin is interested in.
        """

        return ["file.image","file.image.sequence","file.video"]

    def accept(self, settings, item):
        """
        Method called by publisher to determine if an item is of any
        interest to this plugin. Only items matching the filters defined
        via the item_filters property will be presented to this method.
        """

        publisher = self.parent
        file_path = item.properties["path"]

        file_info = publisher.util.get_file_path_components(file_path)
        extension = file_info["extension"].lower()

        valid_extensions = [ext.strip().lstrip(".") for ext in settings["File Extensions"].value.split(",")]

        if extension in valid_extensions:
            self.logger.info(
                "Copy Library Plugin accepted: %s"% (file_path),
                extra={
                    "action_show_folder": {
                        "path": file_path
                    }
                }
            )
            return {"accepted": True}
        else:
            self.logger.debug(
                "%s is not in the valid extension list for Copy Library"% (extension)
            )
            return {"accepted": False}

    def validate(self, settings, item):
        """
        Validates the given item to check that it is okay to publish.
        Returns boolean to indicate validity.
        """

        return True

    def publish(self, settings, item):
        """
        Executes the publish logic for the given item and settings.
        """
        project_id = 227
        publisher = self.parent

        srcPath = item.properties["path"]
        srcName = item.name
        library_path = publisher.sgtk.roots["element_library"]
        name = settings["Element Name"].value
        source = settings["Element Source"].value
        category = settings["Element Category"].value
        tags = settings["Element Tags"].value

        sourceTemplate = publisher.sgtk.templates["library_element_source_area"]
        exrTemplate = publisher.sgtk.templates["library_element_version_filename"]
        fields = {"library_element" : name,
                "version": 1,
                "SEQ": "%04d"}

        srcDest = sourceTemplate.apply_fields(fields)
        exrOut = exrTemplate.apply_fields(fields)
        proxyOut = '\\'.join((srcDest,name + ".proxy.mov"))

        nuke_entity = publisher.sgtk.shotgun.find_one("Software",[['projects', 'in', {'type': 'Project', 'id': project_id}],['engine', 'is', 'tk-nuke']],['code','version_names','windows_path','mac_path','linux_path'])
        nuke_path = nuke_entity['windows_path'].replace('{version}',nuke_entity['version_names'])
        nuke_script = '\\'.join((os.path.dirname(os.path.abspath( __file__ )),'NukeRenderProxy.py'))

        self.logger.info("Copying source file to library")

        if not os.path.exists(srcDest):
            os.makedirs(srcDest)
        copy(srcPath, srcDest)

        self.logger.info("Source copied to %s"%(srcDest))

        data = {
            "code": name,
            "sg_category": category,
            "sg_source": source,
            "tags": tags
        }

        element = publisher.sgtk.shotgun.create("CustomNonProjectEntity01", data)
        context = publisher.sgtk.context_from_entity_dictionary(element)
        ctxDict = context.to_dict()
        ctxDict['project'] = {'type': 'Project', 'id': 227, 'name': 'Library'}
        context = context.from_dict(publisher.sgtk, ctxDict)

        self.logger.info("Created library entity: %s"%(element))

        versiondata = {
            'project': context.project,
            'code': name + "_v001",
            'description': 'Initial EXR Sequence',
            'sg_path_to_frames': exrOut,
            'sg_status_list': 'na',
            'entity': element
        }

        version = publisher.sgtk.shotgun.create("Version", versiondata)

        self.logger.info("Created version v001 enity: %s"%(version))

        publish = sgtk.util.register_publish(
            tk = publisher.sgtk,
            context = context,
            path = exrOut,
            name = name+".v001",
            version_number = 1,
            version_entity = {'type': 'Version','id': version['id']},
            comment = "Initial upload",
            published_file_type = "Rendered Image"
        )

        self.logger.info("Created initial publish for v001: %s"%publish)

        self.logger.info("Rendering v001 from Nuke")

        nukeCmd = '%s -t %s "%s,%s,%s"'%(nuke_path, nuke_script,'\\'.join((srcDest,srcName)),exrOut,proxyOut)
        os.popen(nukeCmd).read()

        self.logger.info("Uploading proxy movie to v001")

        publisher.sgtk.shotgun.upload("Version", version["id"], proxyOut, field_name = "sg_uploaded_movie", display_name = "proxy")


    def parseTags(self, tags):
        if not tags or tags == '':
            return []
        app = self.parent
        existingTags = app.sgtk.shotgun.find('Tag',[],['name'])
        tagList = []
        for tag in tags:
            match = [t for t in existingTags if t["name"] == tag]
            if match:
                tagList.append(match[0])
            else:
                try:
                    newTag = app.sgtk.shotgun.create("Tag", {"name" : tag})
                    tagList.append(newTag)
                except:
                    self.logger.warning('Could not create new tag "%s". User does not have permission'%tag)

        return tagList

    def finalize(self, settings, item):
        """
        Execute the finialization pass. This pass executes once all the publish
        tasks have completed, and can for example be used to version up files.
        """

    def create_settings_widget(self, parent):
        widget = LibraryElementUI(parent, self.parent, self.load_framework('tk-framework-qtwidgets_v2.x.x'))
        return widget

    def set_ui_settings(self, widget, settings):
        settings = settings[0]
        widget.destName = settings["Element Name"]
        widget.source = settings["Element Source"]
        widget.category = settings["Element Category"]
        widget.tags = settings["Element Tags"]
        widget.updateFieldValues()
        return True

    def get_ui_settings(self, widget):
        return {"Element Name" : widget.destName, "Element Source" : widget.source, "Element Category" : widget.category, "Element Tags" : self.parseTags(widget.tags)}
