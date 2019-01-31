from PyQt5.QtWidgets import QMainWindow, QDesktopWidget
from PyQt5 import uic
from config import Settings
import os


class StartView(QMainWindow):
    """
    A class used as the View for the start window.

    The start window shows up first, when the program is launched.
    Its a small window, where the user can either open a already existing
    project or create a new one. When the user decides to create a new project,
    the view changes and he is able to chose between the auto-cut-mode
    and the manual-cut-mode.
    """
    def __init__(self):
        """
        Loads the UI-file and sets up the GUI.

        Initially hides 'new_project_frame' and binds switch_frame() to
        'new_project_button' and 'back_button'.
        """
        super(StartView, self).__init__()
        path = os.path.abspath('src/main/python/view/startview')
        uic.loadUi(path + '/start_view.ui', self)

        # centering the window
        rectangle = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        rectangle.moveCenter(center_point)
        self.move(rectangle.topLeft())

        self.new_project_frame.hide()
        self.new_project_button.clicked.connect(self.switch_frame)
        self.back_button.clicked.connect(self.switch_frame)

        settings = Settings.get_instance()

        self.settings = settings.get_settings()
        print(self.settings.language)
        print(self.settings.kinder[0].name)

        new_settings = {
            "language": "spa",
            "beruf": None,
            "kinder": [
                {
                    "name": "Jason",
                    "alter": 19,
                    "schulabschluss": "Realschule"
                }
            ]
        }

        settings.save_settings(new_settings)

    def show(self):
        """Starts the start-window normal (not maximized)."""
        self.showNormal()

    def switch_frame(self):
        """
        Switches the frames of StartView.

        When 'start_frame' is visible, hide it and show 'new_project_frame',
        but when 'new_project_frame' is visible, hide it and show 'start_frame'.
        """
        self.start_frame.setHidden(not self.start_frame.isHidden())
        self.new_project_frame.setHidden(not self.new_project_frame.isHidden())
