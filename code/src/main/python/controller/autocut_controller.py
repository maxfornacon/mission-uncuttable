import os
import shutil

from PyQt5.QtWidgets import QApplication, QFileDialog
from PyQt5.QtCore import Qt
from autocut import VideoSplitter
from autocut import Presentation
from controller import VideoEditorController, TimelineController
from model.folder import Folder
from view import VideoEditorView
from config import Settings
from config import Language

RESOLUTION = 250


class AutocutController:
    """A class used as the Controller for the autocut window."""

    def __init__(self, view, main_controller, project_path, project_name, filename):
        self.__autocut_view = view
        self.video_button = self.__autocut_view.video_button
        self.video_button.clicked.connect(self.pick_video)
        self.pdf_button = self.__autocut_view.pdf_button
        self.pdf_button.clicked.connect(self.pick_pdf)
        self.ok_button = self.__autocut_view.ok_button
        self.ok_button.clicked.connect(self.ready)
        self.cancel_button = self.__autocut_view.cancel_button
        self.cancel_button.setText(str(Language.current.autocut.cancel))
        self.cancel_button.clicked.connect(self.stop)
        self.__main_controller = main_controller
        self.textlabel = self.__autocut_view.text_label
        self.textlabel.setText(str(Language.current.autocut.starttext))
        self.textlabel.setAlignment(Qt.AlignCenter)
        self.textlabel.setWordWrap(True)
        self.progressbar = self.__autocut_view.progress_bar
        self.progressbar.setMinimum(0)
        self.progressbar.setMaximum(100)
        self.ok_button.setEnabled(False)

        self.filename_video = None
        self.filename_pdf = None
        self.pictures = []

        self.project_path = project_path
        self.project_name = project_name
        self.filename = filename

    def start(self):
        """Calls '__show_view()' of AutocutController"""
        self.__autocut_view.show()

    def stop(self):
        """Closes the window."""
        self.__autocut_view.close()
        self.__main_controller.start()

        try:
            shutil.rmtree(os.path.join(self.project_path, self.project_name))
        except OSError:
            pass

    def pick_video(self):
        """Opens a file picker to select a video file."""
        supported_filetypes = Settings.get_instance().get_dict_settings()[
            "Invisible"]["autocutvideo_import_formats"]
        self.filename_video, _ = QFileDialog.getOpenFileName(
            self.__autocut_view,
            'QFileDialog.getOpenFileNames()',
            '',
            (
                supported_filetypes
            )
        )
        if self.filename_video:
            self.textlabel.setText(str(Language.current.autocut.ready))
            self.__autocut_view.change_icon(self.__autocut_view.video_image_label)
            self.ok_button.setEnabled(True)

    def pick_pdf(self):
        """Opens a file picker to select a pdf."""
        supported_filetypes = Settings.get_instance().get_dict_settings()[
            "Invisible"]["autocutpdf_import_formats"]
        self.filename_pdf, _ = QFileDialog.getOpenFileName(
            self.__autocut_view,
            'QFileDialog.getOpenFileNames()',
            '',
            (
                supported_filetypes
            )
        )
        if self.filename_pdf:
            self.textlabel.setText(str(Language.current.autocut.addvideotext))
            self.__autocut_view.change_icon(self.__autocut_view.pdf_image_label)
        else:
            pass

    def ready(self):
        """autocut the input files and start the video editor view"""
        self.progressbar.setValue(0)
        QApplication.processEvents()
        self.textlabel.setText(str(Language.current.autocut.inprogress))
        self.video_button.setEnabled(False)
        self.pdf_button.setEnabled(False)
        self.cancel_button.setEnabled(False)
        self.ok_button.setEnabled(False)
        QApplication.processEvents()

        video_editor_view = VideoEditorView()
        video_editor_controller = VideoEditorController(video_editor_view)
        filemanager = video_editor_controller.get_filemanager_controller()

        try:
            if self.filename_pdf is not None:
                filename = os.path.split(self.filename_pdf)
                filename = filename[-1]
                filename = filename[:-4]
                folder = Folder(filename)

                presentation = Presentation(self.filename_pdf)
                if not os.path.isdir(os.path.join(self.project_path, self.project_name, 'files', filename)):
                    try:
                        os.mkdir(os.path.join(self.project_path, self.project_name, 'files', filename))
                    except OSError:
                        pass

                self.textlabel.setText(str(Language.current.autocut.slidesprogressing))
                self.pictures = presentation.convert_pdf(self.project_path,
                                                         os.path.join(self.project_name, "files", filename),
                                                         RESOLUTION)
                for pic in self.pictures:
                    folder.add_to_content(pic)

                filemanager.file_list.append(folder)
        except:
            print("pdf error")
            pass

        try:
            if self.filename_video is not None:
                video_splitter = VideoSplitter(self.project_path,
                                               os.path.join(self.project_name, "files"),
                                               self.filename_video)

                QApplication.processEvents()
                self.textlabel.setText(str(Language.current.autocut.audioprogress))
                audio = video_splitter.cut_audio_from_video()

                QApplication.processEvents()
                self.textlabel.setText(str(Language.current.autocut.splittingprogress))
                update_progress = lambda progress: self.progressbar.setValue(int(progress*0.4))
                video_splitter.cut_video(update_progress)
                update_progress2 = lambda progress: self.progressbar.setValue(int(40+progress*0.2))
                video_splitter.cut_zoom_video(update_progress2)
                QApplication.processEvents()
                speaker_video = video_splitter.get_speaker_video()
                slide_video = video_splitter.get_slide_video()

                self.textlabel.setText(str(Language.current.autocut.videoanalysis))
                QApplication.processEvents()
                update_progress3 = lambda progress: self.progressbar.setValue(int(60+progress*0.2))
                board_video = video_splitter.get_board_video()
                board_video.check_board_area(update_progress3)

                QApplication.processEvents()
                update_progress4 = lambda progress: self.progressbar.setValue(int(80+progress*0.2))
                visualizer_video = video_splitter.get_visualizer_video()
                visualizer_video.check_visualiser_area(update_progress4)
                self.textlabel.setText(str(Language.current.autocut.cutting))
                QApplication.processEvents()

        except Exception as e:
            print(e)

            return

        self.progressbar.setValue(100)
        timeline_controller = TimelineController.get_instance()

        self.__main_controller.__video_editor_controller = video_editor_controller
        timeline_controller.create_autocut_tracks()

        timeline_controller.create_autocut_timeables(speaker_video.get(), 3,
                                                     board_video.speaker_subvideos)
        timeline_controller.create_autocut_timeables(board_video.get(), 2,
                                                     board_video.board_subvideos)
        timeline_controller.create_autocut_timeables(visualizer_video.get(), 1,
                                                     visualizer_video.visualizer_subvideos)
        timeline_controller.add_clip(slide_video.get(), 0)
        timeline_controller.add_clip(audio.get(), -1)

        filemanager.addFileNames(self.filename_video)
        filemanager.addFileNames(board_video.get())
        filemanager.addFileNames(visualizer_video.get())
        filemanager.addFileNames(slide_video.get())
        filemanager.addFileNames(speaker_video.get())
        filemanager.addFileNames(audio.get())

        self.__autocut_view.close()
        video_editor_controller.new_project(os.path.join(self.project_path, self.project_name, self.filename))
        video_editor_controller.start()
