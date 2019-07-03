import os

from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QAction, QMenu
from PyQt5.QtCore import QDataStream, Qt, QIODevice, QRectF, QPoint

from .add_track_view import AddTrackView
from model.data import TimeableModel
from model.project import Project
from controller import TimelineController, AddTrackController
from util.timeline_utils import generate_id
from config import Language, Resources


class TrackView(QGraphicsView):
    """
    A View for a single Track, which can be added to the TrackFrame in the Timeline along
    with other TrackViews. The TrackView can hold Timeables.
    """

    def __init__(self, width, height, num, name, button, is_video,
                 is_overlay=False, parent=None):
        """
        Creates TrackView with fixed width and height. The width and height should be
        the same for all TrackViews.

        @param width: track width
        @param height: track height
        @param num: the layer of the track, clips in tracks with
                    higher numbers get rendered above others
        """
        super(TrackView, self).__init__(parent)

        self.width = width
        self.height = height
        self.num = num
        self.name = name
        self.button = button
        self.is_overlay = is_overlay
        self.is_video = is_video

        # set button context menu policy so you can get a rightclick menu on the button
        self.button.setContextMenuPolicy(Qt.CustomContextMenu)
        self.button.customContextMenuRequested.connect(self.on_context_menu)

        # for drag and drop handling
        self.item_dropped = False
        self.current_timeable = None
        self.drag_from_track = False
        self.dragged_timeable_id = None

        self.__controller = TimelineController.get_instance()

        self.setAcceptDrops(True)

        self.setup_ui()

    def setup_ui(self):
        """ sets up the trackview """
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        self.setCacheMode(QGraphicsView.CacheBackground)
        self.setViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate)
        self.setScene(QGraphicsScene())

        self.resize()

    def get_info_dict(self):
        return {
            "width": self.width,
            "height": self.height,
            "num": self.num,
            "name": self.name,
            "is_overlay": self.is_overlay,
            "type": self.is_video,
        }

    def on_context_menu(self, point):
        """ shows a menu on rightclick """
        button_menu = QMenu()
        button_menu.setStyleSheet(open(Resources.files.qss_dark, "r").read())

        delete = QAction(str(Language.current.track.delete))
        button_menu.addAction(delete)
        delete.triggered.connect(self.delete)

        add = QAction(str(Language.current.track.add))
        button_menu.addAction(add)
        add.triggered.connect(self.add)

        button_menu.exec_(self.button.mapToGlobal(point) + QPoint(10, 0))

    def add(self):
        """
        Calls the TimelineController to add a track
        This method is only for the context menu on the track button
        """
        view = AddTrackView()
        AddTrackController(self.__controller, view).start()

    def delete(self):
        """
        Calls the TimelineController to removes this track.
        This method is only for the context menu on the track button
        """
        self.__controller.delete_track(self.num)

    def wheelEvent(self, event):
        """ Overrides wheelEvent from QGraphicsView to prevent scrolling in a track """
        pass

    def keyPressEvent(self, event):
        """
        Overrides wheelEvent from QGraphicsView to prevent scrolling in a
        track. If a keyPressEvent should occur it needs to be explicitly
        handled here.

        :param event: Event
        """
        pass

    def resize(self):
        """ sets the size of the trackview to self.width and self.height """
        self.scene().setSceneRect(0, 0, self.width, self.height)
        self.setFixedSize(self.width, self.height)

    def set_width(self, new_width):
        """
        Changes the width of the trackview.

        @param new_width: the new width of the track
        """
        self.width = new_width
        self.resize()
        self.update_player()

    def add_timeable(self, timeable):
        """ Adds a TimeableView to the GraphicsScene """
        if self.is_video:
            timeable.model.set_layer(self.num)
        else:
            timeable.model.set_layer(0)

        self.scene().addItem(timeable)
        self.update_player()

    def add_from_filemanager(self, drag_event):
        """ Adds a timeable when item from filemanager is dragged into the track """
        # get the path from the dropped item
        item_data = drag_event.mimeData().data('ubicut/file')
        stream = QDataStream(item_data, QIODevice.ReadOnly)
        path = QDataStream.readString(stream).decode()
        width = QDataStream.readInt(stream)

        x_pos = drag_event.pos().x()

        # check if theres already another timeable at the drop position
        rect = QRectF(x_pos, 0, width, self.height)
        colliding = self.scene().items(rect)
        # add the timeable when there are no colliding items
        if not colliding:
            model = TimeableModel(path, generate_id())
            model.move(x_pos)
            model.set_end(width)

            name = os.path.basename(path)
            self.__controller.create_timeable(self.num, name, width, x_pos,
                                              model, generate_id(), is_drag=True)
            self.item_dropped = True

    def add_from_track(self, drag_event):
        """ Adds a timeable when a drag was started from a timeable on a track """
        # get the data thats needed to check for collisions
        item_data = drag_event.mimeData().data('ubicut/timeable')
        stream = QDataStream(item_data, QIODevice.ReadOnly)

        view_id = QDataStream.readString(stream).decode()
        timeable = self.__controller.get_timeable_by_id(view_id)

        self.dragged_timeable_id = view_id

        name = timeable.name
        width = timeable.width
        pos = timeable.mouse_press_pos

        # get a list of items at the position where the timeable would be added
        start_pos = drag_event.pos().x()
        if start_pos < pos:
            return

        rect = QRectF(start_pos - pos, 0, width, self.height)
        colliding = [item for item in self.scene().items(rect)
                     if item.isVisible]

        # only add the timeable if colliding is empty
        if not colliding:
            res_left = timeable.resizable_left
            res_right = timeable.resizable_right
            file_name = timeable.model.file_name

            # create new timeable
            model = TimeableModel(file_name, generate_id())

            old_clip = timeable.model.clip

            # adjust the new model
            model.set_start(old_clip.Start(), is_sec=True)
            model.set_end(old_clip.End(), is_sec=True)
            model.move(start_pos - pos)

            # add the timeable to the track
            self.__controller.create_timeable(
                self.num, name, width, start_pos, model, generate_id(), res_left=res_left,
                res_right=res_right, mouse_pos=pos, hist=False, is_drag=True)
            self.drag_from_track = True

            # set item_dropped to True because the timeable was succesfully created
            self.item_dropped = True
        self.update_player()

    def move_dropped_timeable(self, event):
        pos = event.pos().x() - self.current_timeable.mouse_press_pos
        self.current_timeable.move_on_track(pos)

    def dragEnterEvent(self, event):
        """ Gets called when something is dragged into the track """
        if event.mimeData().hasFormat('ubicut/timeable'):
            # try to add a timeable
            self.add_from_track(event)

            event.accept()
        elif event.mimeData().hasFormat('ubicut/file'):
            # try to add a timeable
            self.add_from_filemanager(event)

            event.accept()
        else:
            event.ignore()
        self.update_player()

    def dragLeaveEvent(self, event):
        """ Gets called when something is dragged out of the track """
        if self.current_timeable is not None:
            # delete dragged timeable if mouse leaves track
            self.current_timeable.delete(hist=False)
            if not self.drag_from_track:
                Project.get_instance().get_history().remove_last_operation()

            # clear data
            self.item_dropped = False
            self.current_timeable = None

            event.ignore()

        self.update()
        event.accept()
        self.update_player()

    def dragMoveEvent(self, event):
        """ Gets called when there is an active drag and the mouse gets moved """
        if event.mimeData().hasFormat('ubicut/timeable'):
            # move the timeable if it was created
            if self.item_dropped:
                self.move_dropped_timeable(event)
                event.accept()
                return

            # try to add the timeable if it wasn't added before
            self.add_from_track(event)
            event.accept()
        elif event.mimeData().hasFormat('ubicut/file'):
            # move the timeable if it was created
            if self.item_dropped:
                self.move_dropped_timeable(event)
                event.accept()
                return

            # try to add the timeable if it wasn't added before
            self.add_from_filemanager(event)
            event.accept()
        else:
            event.ignore()
        self.update_player()

    def dropEvent(self, event):
        """ Gets called when there is an active drag and the mouse gets released """
        if event.mimeData().hasFormat('ubicut/timeable'):
            # accept MoveAction if timeable was succesfully created
            if self.current_timeable is not None:
                if self.drag_from_track:
                    controller = TimelineController.get_instance()
                    t = controller.get_timeable_by_id(self.dragged_timeable_id)
                    self.current_timeable.model.move(self.current_timeable.x_pos)
                    controller.drag_timeable(t.get_info_dict(),
                                             self.current_timeable.get_info_dict(),
                                             t.model, self.current_timeable.model)

                event.acceptProposedAction()

                self.current_timeable = None
                self.dragged_timeable_id = None

            # set item_dropped to false for next drag
            self.item_dropped = False
            self.update()
            self.update_player()

        elif event.mimeData().hasFormat('ubicut/file'):
            # clear data for next drag
            self.item_dropped = False
            if self.current_timeable is not None:
                self.current_timeable.model.move(self.current_timeable.x_pos)
                self.current_timeable = None
            self.update()

        else:
            event.ignore()

        self.update_player()

    def update_player(self):
        # self.parent().parent().parent().parent().parent().parent().parent().parent().connect_update()
        pass
