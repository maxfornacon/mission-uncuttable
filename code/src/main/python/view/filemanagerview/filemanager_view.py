import os

from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QListWidgetItem, QListView
from PyQt5.QtCore import QObject, QSize, pyqtSignal
from config import Resources, Language

from view.mainview import FileListView


class FilemanagerView(QWidget):

    changed = pyqtSignal()

    def __init__(self, parent=None):
        super(FilemanagerView, self).__init__(parent)
        """Loads the UI file"""
        uic.loadUi(Resources.files.filemanager, self)

        self.delete_button = self.findChild(QWidget, 'delete_button')
        self.delete_button.setText(str(Language.current.filemanager.deleteButtonName))

        self.pick_button = self.findChild(QWidget, 'pick_files_button')
        self.pick_button.setText(str(Language.current.filemanager.pushButtonName))

        self.new_folder_button = self.findChild(QWidget, 'new_folder_button')
        self.new_folder_button.setText(str(Language.current.filemanager.newFolderButton))

        self.listWidget = FileListView()
        self.listWidget.setObjectName("list_widget")
        old_list_widget = self.findChild(QObject, 'listWidget')
        self.layout().replaceWidget(old_list_widget, self.listWidget)
        old_list_widget.deleteLater()

        """Set properties of the Widget"""
        self.listWidget.setViewMode(QListView.IconMode)
        self.listWidget.setIconSize(QSize(115, 115))

    def set_delete_action(self, action):
        self.delete_button.clicked.connect(action)

    def set_pick_action(self, action):
        self.pick_button.clicked.connect(action)

    def set_selected_action(self, action):
        self.listWidget.itemSelectionChanged.connect(action)

    def get_current_item(self):
        return self.listWidget.currentItem().statusTip()

    def remove_selected_item(self):
        self.listWidget.takeItem(self.listWidget.currentRow())

    def add_item(self, pixmap, file):
        icon = QIcon(pixmap.scaled(QSize(275, 200)))
        item = QListWidgetItem(os.path.basename(file)[:15], self.listWidget)
        item.setIcon(icon)
        item.setToolTip(file)
        item.setStatusTip(file)
