from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic
from PyQt5 import QtWidgets
from view import VideoEditorView

import os


class StartView(QMainWindow):
    """
    @TODO Doc
    """
    def __init__(self):
        super(StartView, self).__init__()
        path = os.path.abspath('src/main/python/view/startview')
        uic.loadUi(path + '/start_view.ui', self)

    def show(self):
        self.showNormal()

    def showVideoEditor(self):
        videoeditor = VideoEditorView()
        videoeditor.exec_()
