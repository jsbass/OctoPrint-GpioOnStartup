# coding=utf-8
from __future__ import absolute_import

### (Don't forget to remove me)
# This is a basic skeleton for your plugin's __init__.py. You probably want to adjust the class name of your plugin
# as well as the plugin mixins it's subclassing from. This is really just a basic skeleton to get you started,
# defining your plugin as a template plugin, settings and asset plugin. Feel free to add or remove mixins
# as necessary.
#
# Take a look at the documentation on what other plugin mixins are available.

import octoprint.plugin
from gpiozero import Device, LED
from gpiozero.pins.mock import MockFactory

# Used for testing on PC
Device.pin_factory = MockFactory()

class GpioOnStartupPlugin(octoprint.plugin.StartupPlugin,
    octoprint.plugin.ShutdownPlugin,
    octoprint.plugin.SettingsPlugin,
    octoprint.plugin.TemplatePlugin
):
    def on(self):
        try:
            self.led.on()
        except AttributeError:
            pass

    def off(self):
        try:
            self.led.off()
        except AttributeError:
            pass
    
    def make_new_led_from_settings(self):
        self.off()

        pin = self._settings.get(["pin"])
        if(pin != None and type(pin) == int):
            self.led = LED(pin)
            self._logger.info("Registered new LED on GPIO pin %s" % pin)
        else:
            self._logger.info("no pin registered")

    ##~~ ShutdownPlugin mixin
    def on_shutdown(self):
        self._logger.info("shutdown")
        self.off()

    ##~~ StartupPlugin mixin
    def on_after_startup(self):
        self._logger.info("startup")
        self.make_new_led_from_settings()
        self.on()
    
    ##~~ SettingsPlugin mixin
    def get_settings_defaults(self):
        return dict(pin=None)

    def on_settings_save(self, data):
        self._logger.info("settings save")
        try:
            data['pin'] = int(data['pin'])
        except ValueError:
            data['pin'] = None
        
        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
        self.make_new_led_from_settings()
        self.on()
    
    ##~~ TemplatePlugin mixins
    def get_template_vars(self):
        return dict(pin=self._settings.get(["pin"]))

    def get_template_configs(self):
        return [
            dict(type="settings", custom_bindings=False)
        ]

    ##~~ AssetPlugin mixin

    def get_assets(self):
        # Define your plugin's asset files to automatically include in the
        # core UI here.
        return {
            "js": ["js/GpioOnStartup.js"],
            "css": ["css/GpioOnStartup.css"],
            "less": ["less/GpioOnStartup.less"]
        }

    ##~~ Softwareupdate hook

    def get_update_information(self):
        # Define the configuration for your plugin to use with the Software Update
        # Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
        # for details.
        return {
            "GpioOnStartup": {
                "displayName": "GPIO On Startup",
                "displayVersion": self._plugin_version,

                # version check: github repository
                "type": "github_release",
                "user": "seabass992",
                "repo": "OctoPrint-GpioOnStartup",
                "current": self._plugin_version,

                # update method: pip
                "pip": "https://github.com/seabass992/OctoPrint-GpioOnStartup/archive/{target_version}.zip",
            }
        }

# Starting with OctoPrint 1.4.0 OctoPrint will also support to run under Python 3 in addition to the deprecated
# Python 2. New plugins should make sure to run under both versions for now. Uncomment one of the following
# compatibility flags according to what Python versions your plugin supports!
#__plugin_pythoncompat__ = ">=2.7,<3" # only python 2
#__plugin_pythoncompat__ = ">=3,<4" # only python 3
__plugin_pythoncompat__ = ">=2.7,<4" # python 2 and 3

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = GpioOnStartupPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
