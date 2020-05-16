from PySide2 import QtGui, QtCore, QtWidgets, QtUiTools
from shiboken2 import wrapInstance
import maya.OpenMaya as om
import maya.OpenMayaUI as omui
import maya.cmds as cmds
import pymel.core as pm
import functools
import os
import logging
from PySide2.QtCore import Qt
import json
# import yaml
# The Qt Resource System for .png files

logger = logging.getLogger(__name__)
logging.basicConfig()
logger.setLevel(logging.INFO)


class ButtonData(object):
    def __init__(self, name, pxm_enabled, pxm_hover, pxm_pressed,
                 x, y, scale, command):
        self.name = name
        self.pxm_enabled = pxm_enabled
        self.pxm_hover = pxm_hover
        self.pxm_pressed = pxm_pressed
        self.x = x
        self.y = y
        self.scale = scale
        self.command = command


button_obj = list()


def getMayaWindow():
    '''
    get maya main window from a C++ pointer in memory using shiboken2
    '''
    try:
        pointer = omui.MQtUtil.mainWindow()
        maya_main_window = wrapInstance(long(pointer), QtWidgets.QMainWindow)
    except Exception as e:
        maya_main_window = None
        logger.error(e)
    return maya_main_window


class TestUi(QtWidgets.QDialog):
    def __init__(self, parent=None):
        if parent is None:
            parent = getMayaWindow()
        super(TestUi, self).__init__(parent)
        self.window = 'test_star'
        self.title = 'Star'
        self.size = (512, 512)
        self.create_ui()

    def create_ui(self):
        # if pm.window(self.window, exists=True):
        #     pm.deleteUI(self.window, window=True)

        self.setWindowTitle(self.title)
        self.resize(QtCore.QSize(*self.size))
        self.test_view = GraphicsView(self)

        # action = QtGui.QAction("&Quit", self)
        # action.setShortcut("Ctrl+Q")
        # action.setStatusTip('Leave The App')
        # action.triggered.connect(self.close_application)

        # menu_bar = self.menuBar()

        # menu_help = menu_bar.addMenu('&Help')
        # menu_help.addAction(extractAction)

        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.addWidget(self.test_view)
        self.setLayout(self.mainLayout)


class GraphicsView(QtWidgets.QGraphicsView):

    def __init__(self, scene, parent=None):
        # create scene first
        self._scene = QtWidgets.QGraphicsScene()
        self._scene.setSceneRect(0, 0, 1, 1)
        # pass scene to the QGraphicsView's constructor method
        super(GraphicsView, self).__init__(self._scene, parent)
        self.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)
        self.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform)

        pxm_enabled = QtGui.QPixmap('B:/Pictures/school/ANM 355 Advanced Scripting/button_star_orange_enabled.png')
        pxm_hover = QtGui.QPixmap('B:/Pictures/school/ANM 355 Advanced Scripting/button_star_orange_hover.png')
        pxm_pressed = QtGui.QPixmap('B:/Pictures/school/ANM 355 Advanced Scripting/button_star_orange_pressed.png')

        pxm_enabled_p = QtGui.QPixmap('B:/Pictures/school/ANM 355 Advanced Scripting/button_star_purple_enabled.png')
        pxm_hover_p = QtGui.QPixmap('B:/Pictures/school/ANM 355 Advanced Scripting/button_star_purple_hover.png')
        pxm_pressed_p = QtGui.QPixmap('B:/Pictures/school/ANM 355 Advanced Scripting/button_star_purple_pressed.png')
        # pixmap_scaled = pixmap.scaled(60, 60,
        #                               QtCore.Qt.KeepAspectRatio,
        #                               QtCore.Qt.FastTransformation)

        pxm_item_01 = PixmapItem(pxm_enabled=pxm_enabled,
                                 pxm_hover=pxm_hover,
                                 pxm_pressed=pxm_pressed)
        pxm_item_01.setPos(0, 60)

        pxm_item_02 = PixmapItem(pxm_enabled=pxm_enabled_p,
                                 pxm_hover=pxm_hover_p,
                                 pxm_pressed=pxm_pressed_p)
        pxm_item_02.setPos(-120, 180)

        # .png alpha as bounding box
        # pixmap_item.ShapeMode(QtWidgets.QGraphicsPixmapItem.MaskShape)

        self._scene.addItem(pxm_item_01)
        self._scene.addItem(pxm_item_02)

        '''
        rect_item = QtWidgets.QGraphicsRectItem(QtCore.QRectF(0, 0,
                                                              100, 100))
        rect_item.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, False)
        self._scene.addItem(rect_item)
        '''
        '''
        self.viewport().installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj is self.viewport():
            if event.type() == QtCore.QEvent.MouseButtonPress:
                print('mouse press event = ', event.pos())
            elif event.type() == QtCore.QEvent.MouseButtonRelease:
                print('mouse release event = ', event.pos())

        return QtWidgets.QWidget.eventFilter(self, obj, event)
    '''

    def contextMenuEvent(self, event):
        super(GraphicsView, self).contextMenuEvent(event)
        # # check if item exists on event position
        item = self.itemAt(event.pos())
        if item:
            # try run items context if it has one
            try:
                item.contextMenuEvent(event)
                return
            except Exception as e:
                logger.debug(e)
                return

        menu_popup = QtWidgets.QMenu(self)
        action_new = menu_popup.addAction('New Button')
        action_save = menu_popup.addAction('Save Configuration')
        selected_action = menu_popup.exec_(event.globalPos())


class PixmapItem(QtWidgets.QGraphicsPixmapItem):

    def __init__(self, pxm_enabled, pxm_hover, pxm_pressed,
                 command=None, parent=None):
        self.pxm_enabled = pxm_enabled
        self.pxm_hover = pxm_hover
        self.pxm_pressed = pxm_pressed
        self.command = command
        super(PixmapItem, self).__init__(self.pxm_enabled, parent)
        self.setAcceptHoverEvents(True)
        self.setAcceptTouchEvents(True)
        self.drag = False

    def contextMenuEvent(self, event):
        super(PixmapItem, self).contextMenuEvent(event)
        menu_popup = QtWidgets.QMenu()
        # self.menu_popup = QtWidgets.QMenu()
        # self.menu_popup.setObjectName("popupMenu")
        # self.vertical_layout_widget = QtGui.QVBoxLayout(self)

        action_add = menu_popup.addAction('Change Icon')
        action_add.setStatusTip('Change Icon')
        # action_add.setShortcut('Ctrl+Shift+C')
        # action_add.triggered.connect()

        action_remove = menu_popup.addAction('Remove Button')
        action_remove.setStatusTip('Remove Button')
        selected_action = menu_popup.exec_(event.screenPos())
        # event.accept()

    def hoverEnterEvent(self, event):
        self.setPixmap(self.pxm_hover)
        super(PixmapItem, self).hoverEnterEvent(event)

    def mousePressEvent(self, event):
        print('CLICK')
        self.setPixmap(self.pxm_pressed)
        # self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        # self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        super(PixmapItem, self).mousePressEvent(event)

        if event.button() == QtCore.Qt.LeftButton:
            print('RUN COMMAND')

        elif event.button() == QtCore.Qt.RightButton:
            print('RIGHT')

        elif event.button() == QtCore.Qt.MidButton:
            # change cursor to quad arrow
            cursor = QtGui.QCursor(QtCore.Qt.SizeAllCursor)
            QtWidgets.QApplication.instance().setOverrideCursor(cursor)
            self.drag = True
            print('DRAG')
        '''
        stops event propagation using event.accept()
        UI events get propagated up to ascending widgets
        until one of them accepts it
        '''
        event.accept()

    def mouseMoveEvent(self, event):
        super(PixmapItem, self).mouseMoveEvent(event)
        if self.drag:
            new_pos = event.scenePos()
            # Keep the old Y position, so only the X-pos changes.
            # old_pos = self.scenePos()
            # new_pos.setY( old_pos.y() )
            self.setPos(new_pos)

    def mouseReleaseEvent(self, event):
        print('RELEASE')
        self.setPixmap(self.pxm_hover)
        super(PixmapItem, self).mouseReleaseEvent(event)
        self.drag = False
        QtWidgets.QApplication.instance().restoreOverrideCursor()
        # self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, False)
        # self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, False)

    # def hoverMoveEvent(self, event):
    #     self.setPixmap(self.pxm_hover)
    #     super(PixmapItem, self).hoverMoveEvent(event)

    def hoverLeaveEvent(self, event):
        self.setPixmap(self.pxm_enabled)
        super(PixmapItem, self).hoverLeaveEvent(event)

    # @QtCore.pyqtSlot()
    # def simulate_left_click(self):
    #     mouse_event = QtGui.QMouseEvent(
    #         QtCore.QEvent.GraphicsSceneMousePress,
    #         self.cursor().pos(),
    #         QtCore.Qt.LeftButton,
    #         QtCore.Qt.LeftButton,
    #         QtCore.Qt.NoModifier,
    #         )

    #     QtCore.QCoreApplication.postEvent(self, mouse_event)


v = TestUi()
v.setAttribute(QtCore.Qt.WA_DeleteOnClose)
v.show()
