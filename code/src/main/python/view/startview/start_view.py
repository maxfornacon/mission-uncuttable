import os

from PyQt5.QtCore import QFileSystemWatcher, Qt
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QWidget, \
    QStackedLayout, QLabel, QListWidgetItem
from PyQt5 import uic, QtGui, QtSvg
from PyQt5.QtGui import QPixmap
from config import Settings, Resources, Language
from projectconfig import Projectsettings


class StartView(QMainWindow):
    """
    A class used as the View for the start window.

    The start window shows up first, when the program is launched.
    Its a small window, where the user can either open a already existing
    project or create a new one. When the user decides to create a new project,
    the view changes and the user is able to chose between the auto-cut-mode
    and the manual-cut-mode.
    """
    def __init__(self):
        """
        Loads the UI-file and sets up the GUI.

        Initially hides 'new_project_frame' and binds switch_frame() to
        'new_project_button' and 'back_button'.
        """
        super(StartView, self).__init__()
        uic.loadUi(Resources.files.startview, self)

        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)

        self.init_stylesheet()

        "QSS HOT RELOAD"
        self.__qss_watcher = QFileSystemWatcher()
        self.__qss_watcher.addPath(Resources.files.qss_dark)
        self.__qss_watcher.fileChanged.connect(self.update_qss)

        self.select_project_widget = SelectProjectWidget()
        self.decision_widget = DecisionWidget()

        self.stacked_layout = QStackedLayout()
        self.stacked_layout.addWidget(self.select_project_widget)
        self.stacked_layout.addWidget(self.decision_widget)

        self.centralWidget().setLayout(self.stacked_layout)

        new_project_button = self.findChild(QWidget, "new_project_button")
        new_project_button.setText(str(Language.current.startview.newproject))

        back_button = self.findChild(QWidget, "back_button")
        back_button.setText(str(Language.current.startview.back))

        # centering the window
        rectangle = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        rectangle.moveCenter(center_point)
        self.move(rectangle.topLeft())

    def init_stylesheet(self):
        current_stylesheet = Settings.get_instance().get_settings().design.color_theme.current
        if current_stylesheet == 0:
            self.setStyleSheet(open(Resources.files.qss_dark, "r").read())     
        elif current_stylesheet == 1:
            self.setStyleSheet(open(Resources.files.qss_light, "r").read())    
    
    def show(self):
        """Starts the start-window normal (not maximized)."""
        self.showNormal()

    def switch_frame(self):
        """
        Switches the visible Widget of StartView.

        When 'select_project_widget' is visible, hide it and show
        'decision_widget', but when 'decision_widget' is visible, hide it and
        show 'select_project_widget'.
        """
        self.select_project_widget.setHidden(not self.select_project_widget.isHidden())
        self.decision_widget.setHidden(not self.decision_widget.isHidden())

    def update_qss(self):
        """ Updates the View when stylesheet changed, can be removed in production"""
        self.init_stylesheet()
        self.__qss_watcher = QFileSystemWatcher()
        self.__qss_watcher.addPath(Resources.files.qss_dark)
        self.__qss_watcher.fileChanged.connect(self.update_qss)

"Fehler"
class SelectProjectWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        uic.loadUi(Resources.files.select_project_widget, self)

        text = str(Language.current.startview.last_projects)
        self.findChild(QLabel, "lbl_text").setText(text)

        self.projects_list_view = self.findChild(QWidget, "projects_list_view")

        for p in Projectsettings.get_projects():
            name = os.path.split(p)
            name = name[-1]
            name = name[:-3]
            item = QListWidgetItem(name)
            item.setStatusTip(p)
            self.projects_list_view.addItem(item)


class DecisionWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        uic.loadUi(Resources.files.decision_widget, self)

        height = self.frameGeometry().height()
        logo_with_name = QtGui.QPixmap(Resources.images.logo_with_name)
        picture = self.findChild(QLabel, "label_pic")
        logo_with_name = logo_with_name.scaled(height/2 - 50, height/2 - 50,
                                               Qt.KeepAspectRatio,
                                               transformMode=Qt.SmoothTransformation)
        picture.setPixmap(logo_with_name)

        name_label = self.findChild(QLabel, "name_label")
        name_label.setText(str(Language.current.startview.namelabel))

        folder_label = self.findChild(QLabel, "folder_label")
        folder_label.setText(str(Language.current.startview.folderlabel))