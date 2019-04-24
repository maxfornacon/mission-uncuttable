from PyQt5.QtWidgets import QVBoxLayout
from .size_linkable_frame import SizeLinkableFrame
from .time_needle import TimeNeedle

class TrackFrame(SizeLinkableFrame):
    """
    Extends SizeLinkableFrame to a frame which is mainly intended to
    show TrackViews.

    The TrackFrame has the size-linkable property. For information on
    how to use this see the SizeLinkableFrame class.
    """

    def __init__(self, parent=None):
        """
        Create an empty TrackFrame without any size linkage.

        :param parent: the parent component
        """
        super(TrackFrame, self).__init__(parent)

        self.setLayout(QVBoxLayout())
        self.setStyleSheet("background-color: orange")

        height = self.height()

        self.needle = TimeNeedle(height)
        self.needle.setParent(self)


    def add_track(self, track):
        """
        Adds a TrackView to the TrackFrame

        :param track: the Track to add
        """
        self.layout().addWidget(track)
        track.stackUnder(self.needle)
        self.adjustSize()
