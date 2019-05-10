files = {
    "startview": "ui/start_view.ui",
    "filemanager": "ui/filemanager.ui",
    "preview_view": "ui/form.ui",
    "mainview": "ui/main_window.ui",
    "settingsview": "ui/settings_window.ui",
    "projectsettings_view": "ui/projectsettings_window.ui",
    "export_view": "ui/export.ui",
    "timeline_scrollarea_view": "ui/timeline_scroll_area.ui",
    "timeline_view": "ui/timeline_view.ui",
    "qss_dark": "stylesheets/dark.qss",
    "qss_light": "stylesheets/light.qss"
}
images = {
    "play_button": "images/buttons/play.png",
    "pause_button": "images/buttons/pause.png",
    "first_frame_button": "images/buttons/fast_backwards.png",
    "last_frame_button": "images/buttons/fast_forward.png",
    "back_button": "images/buttons/step_back.png",
    "forward_button": "images/buttons/step_forward.png",
    "maximize_button": "images/buttons/maximize.png",
    "media_symbols": "images/filemanagerIcons",
}
strings = {
    "de": "strings/de/strings.xml",
    "en": "strings/en/strings.xml"
}


class Resources:
    """
    This class loads the paths of included files.
    This is necessary because the project has different paths after freezing and installing.
    """
    __instance = None

    def __init__(self, app):
        self.app = app
        if Resources.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            Resources.__instance = self
            self.load_file_paths()

    @staticmethod
    def get_instance():
        if Resources.__instance is None:
            raise Exception("Resources not initialized!")
        else:
            return Resources.__instance

    def load_file_paths(self):
        self.files = Category()
        for attribute, value in files.items():
            setattr(self.files, attribute, self.app.get_resource(value))
        self.images = Category()
        for attribute, value in images.items():
            setattr(self.images, attribute, self.app.get_resource(value))
class Category:
    pass

