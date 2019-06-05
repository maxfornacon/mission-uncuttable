import json

from PyQt5.QtWidgets import QFileDialog

from shortcuts import ShortcutLoader
from .settings_controller import SettingsController
from .projectsettings_controller import ProjectSettingsController
from .timeline_controller import TimelineController
from model.project import Project
from view.settingsview import SettingsView, ProjectSettingsView
from view.exportview import ExportView
from projectconfig import Projectsettings
from config import Settings


class VideoEditorController:
    """
    A class used as the Controller for the video-editor window.

    Manages starting and stopping of the video-editor window.
    """
    def __init__(self, view):
        self.__video_editor_view = view
        self.__video_editor_view.action_settings.triggered.connect(
            self.__start_settings_controller)
        self.__settings_controller = SettingsController(None)
        self.__video_editor_view.action_projectsettings.triggered.connect(
            self.__start_projectsettings_controller)
        self.__video_editor_view.actionExport.triggered.connect(
            self.__start_export_controller)
        self.__video_editor_view.actionUndo.triggered.connect(
            self.__start_undo)
        self.__video_editor_view.actionRedo.triggered.connect(
            self.__start_redo)
        self.__video_editor_view.actionSpeichern.triggered.connect(
            self.__start_save)
        self.__video_editor_view.actionSpeichern_als.triggered.connect(
            self.__start_save_as)
        self.__video_editor_view.actionOeffnen.triggered.connect(
            self.__start_open)

        self.__history = Project.get_instance().get_history()
        ShortcutLoader(self.__video_editor_view)

    def __show_view(self):
        """Calls show() of 'VideoEditorView'."""
        self.__video_editor_view.show()

    def start(self):
        """Calls '__show_view()' of VideoEditorController"""
        self.__show_view()

    def stop(self):
        """Closes the video-editor Window."""
        self.__video_editor_view.close()

    def __start_settings_controller(self):
        """Opens the settings window"""
        if self.__settings_controller.checkIfClosed():
            self.settings_view = SettingsView()
            self.__settings_controller = SettingsController(self.settings_view)
            self.__settings_controller.start()
        else:
            self.__settings_controller.focus()

    def __start_projectsettings_controller(self):
        """Opens the projectsettings window"""
        projectsettings_view = ProjectSettingsView()
        self.__projectsettings_controller = ProjectSettingsController(projectsettings_view)
        self.__projectsettings_controller.start()

    def __start_export_controller(self):
        """shows the export view"""
        export_view = ExportView()
        export_view.start()

    def __start_undo(self):
        """ Undo last action """
        try:
            self.__history.undo_last_operation()
        except:
            pass

    def __start_redo(self):
        """ Redo last action """
        try:
            self.__history.redo_last_operation()
        except:
            pass

    def __start_save(self):
        """ Save the Project """
        project = Project.get_instance()
        if project.path is None:
            self.__start_save_as()
            return

        self.__write_project_data(project.path)

    def __start_save_as(self):
        """ Lets the user select a file and saves the project in that file """
        # select file
        file_dialog = QFileDialog(self.__video_editor_view)
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setNameFilter('uc files (*.uc)')
        file_dialog.setDefaultSuffix('uc')
        if file_dialog.exec_() == QFileDialog.Accepted:
            filename = file_dialog.selectedFiles()[0]
        else:
            return

        self.__write_project_data(filename)

        project = Project.get_instance()
        project.path = filename

        Projectsettings.add_project(filename)

    def __write_project_data(self, filename):
        """ Saves project data into a file """
        # get timeline data
        timeline_controller = TimelineController.get_instance()
        timeline_data = timeline_controller.get_project_timeline()

        # get filemanager data
        filemanager = self.__video_editor_view.filemanager
        filemanager_data = filemanager.get_project_filemanager()

        project_data = {
            "timeline": timeline_data,
            "filemanager": filemanager_data
        }

        # write data
        with open(filename, 'w') as f:
            json.dump(project_data, f, ensure_ascii=False)

    def __start_open(self):
        """ Open a project """
        filetypes = Settings.get_instance().get_dict_settings()[
            "Invisible"]["project_formats"]
        path, _ = QFileDialog.getOpenFileName(self.__video_editor_view,
                                              'Open Project', '', filetypes)

        with open(path, 'r') as f:
            project_data = json.load(f)

        # set up timeline
        timeline_controller = TimelineController.get_instance()
        timeline_controller.clear_timeline()

        if "timeline" in project_data:
            timeline_controller.create_project_timeline(project_data["timeline"])
        else:
            timeline_controller.create_default_tracks()

        # set up filemanager
        if "filemanager" in project_data:
            filemanager = self.__video_editor_view.filemanager
            filemanager.create_project_filemanager(project_data["filemanager"])

        # set project path
        project = Project.get_instance()
        project.path = path
