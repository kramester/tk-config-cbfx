import os
import sgtk

HookBaseClass = sgtk.get_hook_baseclass()

class CopyLibraryPlugin(HookBaseClass):
    """
    Plugin for copying source elements to the element library
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
        return "Copy to element library"

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
            }
        }

    @property
    def item_filters(self):
        """
        List of item types this plugin is interested in.
        """

        return ["file.image","file.image.sequence" "file.video"]

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

    def publish(self, setttings, item):
        """
        Executes the publish logic for the given item and settings.
        """

        publisher = self.parent
        srcPath = item.properties["path"]

        self.logger.info("Generating folders in library")

    def finalize(self, settings, item):
        """
        Execute the finialization pass. This pass executes once all the publish
        tasks have completed, and can for example be used to version up files.
        """
