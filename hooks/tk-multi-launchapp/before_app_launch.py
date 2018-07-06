# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Before App Launch Hook

This hook is executed prior to application launch and is useful if you need
to set environment variables or run scripts as part of the app initialization.
"""

import os
import tank

class BeforeAppLaunch(tank.Hook):
    """
    Hook to set up the system prior to app launch.
    """

    def execute(self, app_path, app_args, version, engine_name, **kwargs):
        """
        The execute functon of the hook will be called prior to starting the required application

        :param app_path: (str) The path of the application executable
        :param app_args: (str) Any arguments the application may require
        :param version: (str) version of the application being run if set in the
            "versions" settings of the Launcher instance, otherwise None
        :param engine_name (str) The name of the engine associated with the
            software about to be launched.

        """

        # accessing the current context (current shot, etc)
        # can be done via the parent object
        #
        # > multi_launchapp = self.parent
        # > current_entity = multi_launchapp.context.entity

        # you can set environment variables like this:
        # os.environ["MY_SETTING"] = "foo bar"


        # this is the way SG says to do this

        self.logger.debug("[CBFX] engine name: %s" % engine_name)

        if engine_name == "tk-nuke":
            env_vars={
                # "NUKE_PATH": "R:/code/work/anthony.kramer/nuke/cbfx-nuke-tools",
                "NUKE_PATH": "S:/tools/nuke/cbfx/current",
            }
            for k,v in env_vars.iteritems():
                tank.util.append_path_to_env_var(k, v)
                self.logger.debug("[CBFX] added environ %s=%s" % (k,v))

        if engine_name == "tk-hiero":
            env_vars={
                "HIERO_PLUGIN_PATH": "R:/code/work/anthony.kramer/nuke/cbfx-hiero-tools",
                # "HIERO_PLUGIN_PATH": "S:/tools/hiero/cbfx/current",
            }
            for k,v in env_vars.iteritems():
                tank.util.append_path_to_env_var(k, v)
                self.logger.debug("[CBFX] added environ %s=%s" % (k,v))
