from PySide2 import QtGui, QtCore, QtWidgets, QtUiTools, QtOpenGL
from shiboken2 import wrapInstance
from functools import partial
# deque is a list-like container with fast O(1) appends and pops on either end
from collections import deque
# import maya.OpenMaya as om
import maya.OpenMayaUI as omui
import maya.cmds as cmds
import pymel.core as pm
# import os
import logging
import json
# import yaml
# The Qt Resource System for .png files
# Add tabs for facial and body pickers
# Scene level template,
# Work with namespaces
# paint your own customizable button?
# if instanced rig is the same, 50 orcs
# render viewport and use as background
# QMimeType?
# ctrl+A to select all
# key = QShortcut(QKeySequence('Ctrl+A'), self)
# key.activated.connect()


logger = logging.getLogger(__name__)
logging.basicConfig()
logger.setLevel(logging.DEBUG)


def file_dialog(parent=None, caption=None, directory='', for_open=True,
                fmt={'desc': ['ext']}, is_folder=False, native_dialog=False):
    options = QtWidgets.QFileDialog.Options()
    # pipe notation | is a bitwise operator for OR
    if native_dialog:
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        options |= QtWidgets.QFileDialog.DontUseCustomDirectoryIcons
    dialog = QtWidgets.QFileDialog(parent=parent,
                                   caption=caption)
    dialog.setOptions(options)

    dialog.setFilter(dialog.filter() | QtCore.QDir.Hidden)

    # files or folder
    if is_folder:
        dialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)
    else:
        dialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
    # open or save
    if for_open:
        dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen)
    else:
        dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)

    # set format, if specified
    if not is_folder:
        # dialog.setDefaultSuffix(fmt[0])
        filters = []
        for desc, ext in fmt.iteritems():
            ext = '(*.' + ' *.'.join(ext) + ')'
            filter = '{desc} {ext}'.format(desc=desc, ext=ext)
            filters.append(filter)
        dialog.setNameFilters(filters)

    # set the starting directory
    if directory != '':
        dialog.setDirectory(str(directory))
    # else:
    #     dialog.setDirectory(str(ROOT_DIR))

    if dialog.exec_() == QtWidgets.QDialog.Accepted:
        path = dialog.selectedFiles()[0]
        # returns a list
        return path
    else:
        return ''


# list to temporarily store button data
button_list = list()


class SceneData(object):
    def __init__(self, char_list=list()):
        # list of CharacterData
        self.char_list = char_list


class CharacterData(object):
    def __init__(self, name, namespace = None,tab_list=list()):
        self.name = str(name)
        self.namespace = namespace
        # list of TabData
        self.tab_list = tab_list


class TabData(object):
    def __init__(self, name, button_list=list()):
        self.name = str(name)
        # list of ButtonData
        self.button_list = button_list


class ButtonData(object):
    def __init__(self, name, pxm_enabled, pxm_hover, pxm_pressed,
                 x, y, scale, command):
        self.name = str(name)
        self.pxm_enabled = pxm_enabled
        self.pxm_hover = pxm_hover
        self.pxm_pressed = pxm_pressed
        self.x = x
        self.y = y
        self.scale = scale
        self.command = command
        self.store_data()

    def store_data(self):
        '''
        store the button data object into button_list
        '''
        button_list.append(self)


button_01 = ButtonData('button_01',
                       'B:/Documents/GitHub/RAA_autoRig/icons/button_star_orange_enabled.png',
                       'B:/Documents/GitHub/RAA_autoRig/icons/button_star_orange_hover.png',
                       'B:/Documents/GitHub/RAA_autoRig/icons/button_star_orange_pressed.png',
                       100, 0, 1, partial(cmds.select, 'pSphere1'))
button_02 = ButtonData('button_02',
                       'B:/Documents/GitHub/RAA_autoRig/icons/button_star_purple_enabled.png',
                       'B:/Documents/GitHub/RAA_autoRig/icons/button_star_purple_hover.png',
                       'B:/Documents/GitHub/RAA_autoRig/icons/button_star_purple_pressed.png',
                       0, 180, 0.6, partial(cmds.select, 'pCube1'))
button_02 = ButtonData('button_03',
                       'B:/Documents/GitHub/RAA_autoRig/icons/button_star_purple_enabled.png',
                       'B:/Documents/GitHub/RAA_autoRig/icons/button_star_purple_hover.png',
                       'B:/Documents/GitHub/RAA_autoRig/icons/button_star_purple_pressed.png',
                       200, 180, 1, partial(cmds.select, 'pCylinder1'))
button_02 = ButtonData('button_03',
                       'B:/Documents/GitHub/RAA_autoRig/icons/button_star_orange_enabled.png',
                       'B:/Documents/GitHub/RAA_autoRig/icons/button_star_orange_hover.png',
                       'B:/Documents/GitHub/RAA_autoRig/icons/button_star_orange_pressed.png',
                       100, 360, 0.6, partial(cmds.select, 'pCone1'))


class ButtonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ButtonData):
            return (obj.name,
                    obj.pxm_enabled,
                    obj.pxm_hover, obj.pxm_pressed,
                    obj.x, obj.y,
                    obj.scale, obj.command)
        else:
            return super(ButtonEncoder, self).default(obj)


class ButtonDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super(ButtonDecoder, self).__init__(self, object_hook=self.object_hook,
                                            *args, **kwargs)

    def object_hook(self, dct):
        if 'name' in dct:
            return ButtonData(dct['name'],
                              dct['pxm_enabled'],
                              dct['pxm_hover'], dct['pxm_pressed'],
                              dct['x'], dct['y'],
                              dct['scale'], dct['command'])
        return dct


def get_maya_window():
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


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        if parent is None:
            self.parent = get_maya_window()

        super(MainWindow, self).__init__(parent)
        self.setWindowFlags(self.windowFlags()
                            | QtCore.Qt.WindowStaysOnTopHint)
        self.window = 'test_star'
        self.title = 'Star'
        self.size = (720, 720)
        self.create_ui()

    def create_ui(self):
        self.setWindowTitle(self.title)
        self.resize(QtCore.QSize(*self.size))

        self.create_menu_bar()

        main_widget = MainWidget(self)
        self.setCentralWidget(main_widget)

        self.tool_bar = self.addToolBar('Namespace')
        self.tool_bar.setMovable(False)
        # self.statusBar().showMessage('...')

        combo_box = QtWidgets.QComboBox(self.tool_bar)
        self.tool_bar.addWidget(combo_box)
        combo_box.addItem("Frodo")
        combo_box.addItem("Bilbo")
        combo_box.addItem("Gandalf")

        self.add_tool_bar_spacer()
        # self.tool_bar.addSeparator()
        # self.add_tool_bar_spacer()

        self.name_button = QtWidgets.QPushButton(self.tool_bar)
        self.tool_bar.addWidget(self.name_button)
        self.name_button.setFixedSize(110, 18)
        font = QtGui.QFont()
        self.name_button.setFont(font)
        self.name_button.setText('Update Namespace:')
        self.name_button.clicked.connect(self.update_namespace)

        self.name_label = QtWidgets.QLineEdit(self.tool_bar)
        self.tool_bar.addWidget(self.name_label)
        # name_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed,
        #                          QtWidgets.QSizePolicy.Expanding)
        # name_label.setFixedSize(150, 18)
        self.name_label.setText('rig:')

    def add_tool_bar_spacer(self):
        '''
        add a blank widget as a toolbar spacer
        '''
        spacer = QtWidgets.QWidget(self.tool_bar)
        spacer.setFixedSize(4, 18)
        self.tool_bar.addWidget(spacer)

    def update_namespace(self):
        try:
            namespace = pm.ls(os=True)[0].namespace()
            self.name_label.setText(namespace)
            # todo: store it in a data object
        except IndexError as e:
            logger.info(e)


    def create_menu_bar(self):
        menu_bar = self.menuBar()

        menu_file = menu_bar.addMenu('Scene')
        act_scene_new = menu_file.addAction('New Scene')
        act_scene_new.setStatusTip('Create a new picker scene')
        act_scene_open = menu_file.addAction('Open Scene...')
        act_scene_open.setStatusTip('Open a picker scene')
        act_scene_save = menu_file.addAction('Save Scene')
        act_scene_save.setStatusTip('Save picker scene')

        menu_file = menu_bar.addMenu('Character')
        act_char_new = menu_file.addAction('New Character')
        act_char_new.setStatusTip('Add a new character')
        act_char_open = menu_file.addAction('Open Character...')
        act_char_open.setStatusTip('Open a character')
        act_char_save = menu_file.addAction('Save Character')
        act_char_save.setStatusTip('Save current character')
        act_char_del = menu_file.addAction('Delete Character')
        act_char_del.setStatusTip('Delete current character')

        menu_file = menu_bar.addMenu('Tab')
        act_tab_new = menu_file.addAction('New Tab')
        act_tab_new.setStatusTip('Add a new blank tab')
        act_tab_open = menu_file.addAction('Open Tab...')
        act_tab_open.setStatusTip('Open a tab')
        act_tab_save = menu_file.addAction('Save Tab')
        act_tab_save.setStatusTip('Save current tab')
        act_tab_del = menu_file.addAction('Delete Tab')
        act_tab_del.setStatusTip('Delete current tab')


class MainWidget(QtWidgets.QWidget):
    '''
    container widget for tabs and QGraphicsView
    '''

    def __init__(self, parent=None):
        # if parent is None:
        #     self.parent = get_maya_window()
        super(MainWidget, self).__init__(parent)
        self.window = 'test_star'
        self.title = 'Star'
        self.size = (512, 512)
        self.create_ui()

    def create_ui(self):
        # self.setWindowTitle(self.title)
        # self.resize(QtCore.QSize(*self.size))
        self.tab_widget = TabWidget(self)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.addWidget(self.tab_widget)
        # # plus button on right edge of window
        # self.tab_plus_button = QtWidgets.QToolButton(self)
        # self.tab_plus_button.setText('+')
        # font = self.tab_plus_button.font()
        # font.setBold(True)
        # self.tab_plus_button.setFont(font)
        # self.tab_widget.setCornerWidget(self.tab_plus_button)
        # self.tab_plus_button.clicked.connect(self.create_tab)

        # menu_bar = QtWidgets.QMenuBar(self)
        # fileMenu = menu_bar.addMenu('&File')

    # def delete_instance(self):
    #     if ui_instance is not None:
    #         print('not None')
    #         try:
    #             ui_instance.setParent(None)
    #             ui_instance.deleteLater()
    #         except Exception as e:
    #             pass
    # def delete_ui(self):
    #     for child in self.parent.children():
    #         print(child.__class__.__module__)
    #         if child.__class__.__module__ == 'RAA_picker':
    #             child.setParent(None)
    #             child.deleteLater()
    #             logger.debug(child)


class TabWidget(QtWidgets.QTabWidget):
    # bug with setMovable plus

    def __init__(self, parent=None):
        super(TabWidget, self).__init__(parent)
        self.setTabsClosable(True)
        # self.setMovable(True)
        self.tabCloseRequested.connect(self.close_tab)
        select_left = QtWidgets.QTabBar.SelectLeftTab
        self.tabBar().setSelectionBehaviorOnRemove(select_left)
        self.pad = 1
        self.create_tabs()

    def create_tabs(self):
        '''
        create a '+' tab and a blank untitled tab
        '''
        # create the 'new tab' tab with a button
        self.insertTab(0, QtWidgets.QWidget(),'')
        nb = self.new_btn = QtWidgets.QPushButton()
        nb.setFixedSize(20, 20)
        nb.setFlat(True)
        font = QtGui.QFont()
        # font.setBold(True)
        font.setPointSize(12)
        nb.setFont(font)
        nb.setText('+')
        nb.clicked.connect(self.new_tab)
        self.tabBar().setTabButton(0, QtWidgets.QTabBar.RightSide, nb)
        self.tabBar().setTabEnabled(0, False)
        self.new_tab()

    def new_tab(self, name='untitled'):
        '''
        create a new blank untitled tab
        '''
        tab_layout = QtWidgets.QVBoxLayout()
        widget = QtWidgets.QWidget()
        graphics_view = GraphicsView(self)

        index = self.count() - 1
        self.insertTab(index, widget, '{n}_{p}'.format(n=name, p=self.pad))
        self.pad += 1
        widget.setLayout(tab_layout)
        tab_layout.addWidget(graphics_view)
        self.setCurrentIndex(index)
        return widget

    def close_tab(self, index):
        '''
        slot to close tab
        '''
        # if self.count() > 2:
        self.removeTab(index)


class GraphicsView(QtWidgets.QGraphicsView):
    '''
    class for QGraphicsView to contain buttons
    '''

    def __init__(self, scene, parent=None):
        # create scene first
        self._scene = QtWidgets.QGraphicsScene()
        self._scene.setSceneRect(0, 0, 1, 1)
        # pass scene to the QGraphicsView's constructor method
        super(GraphicsView, self).__init__(self._scene, parent)
        self.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.setRenderHints(QtGui.QPainter.Antialiasing
                            | QtGui.QPainter.SmoothPixmapTransform)

        format = QtOpenGL.QGLFormat(QtOpenGL.QGL.SampleBuffers)
        self.setViewport(QtOpenGL.QGLWidget(format))

        # self.rubberBand = QtWidgets.QRubberBand(QtWidgets.QRubberBand.Rectangle, self)
        # self.setMouseTracking(True)
        # self.origin = QtCore.QPoint()
        # self.changeRubberBand = False
        self.setDragMode(self.RubberBandDrag)

        self.background = QtWidgets.QGraphicsPixmapItem(None)
        self._scene.addItem(self.background)

        for button_data in button_list:
            self.create_button(button_data)

        # self.viewport().installEventFilter(self)

    # def eventFilter(self, obj, event):
    #     if obj is self.viewport():
    #         if event.type() == QtCore.QEvent.MouseButtonPress:
    #             print('mouse press event = ', event.pos())
    #         elif event.type() == QtCore.QEvent.MouseButtonRelease:
    #             print('mouse release event = ', event.pos())

    #     return QtWidgets.QWidget.eventFilter(self, obj, event)

    def contextMenuEvent(self, event):
        '''
        right click context menu for QGraphicsView
        '''
        super(GraphicsView, self).contextMenuEvent(event)
        # QGraphicsItem will setAccepted() if overlaps GraphicsView
        if not event.isAccepted():
            menu_popup = QtWidgets.QMenu(self)
            action_new = menu_popup.addAction('New Button')
            action_new.triggered.connect(self.add_button)

            action_bg = menu_popup.addAction('Change Background')
            action_bg.triggered.connect(self.change_background)

            # action_open = menu_popup.addAction('New Configuration')
            # action_open = menu_popup.addAction('Open Configuration')
            # action_save = menu_popup.addAction('Save Configuration')
            selected_action = menu_popup.exec_(event.globalPos())

    def create_button(self, button_data):
        '''
        create a button in scene
        '''
        pxm_list = [button_data.pxm_enabled,
                    button_data.pxm_hover,
                    button_data.pxm_pressed]
        pxm_s_list = list()
        for path in pxm_list:
            pxm = QtGui.QPixmap(path)
            pxm_s = pxm.scaled(pxm.size() * button_data.scale,
                               QtCore.Qt.KeepAspectRatio)
            pxm_s_list.append(pxm_s)
        command = button_data.command
        pxm_item = PixmapItem(pxm_enabled=pxm_s_list[0],
                              pxm_hover=pxm_s_list[1],
                              pxm_pressed=pxm_s_list[2],
                              command=command,
                              button_data=button_data)
        pxm_item.setPos(button_data.x, button_data.y)
        # .png alpha as bounding box, already default
        # pxm_item.ShapeMode(QtWidgets.QGraphicsPixmapItem.MaskShape)

        self._scene.addItem(pxm_item)

    def get_mouse_pos(self):
        '''
        get current mouse position relative to the scene
        return type:
        QPointF
        '''
        origin = self.mapFromGlobal(QtGui.QCursor.pos())
        relative_origin = self.mapToScene(origin)
        return relative_origin

    def add_button(self):
        '''
        called from contextMenuEvent
        add a new button on mouse position
        command selects current selection
        maya.cmds because list of PyNode must be strings
        '''
        sel = cmds.ls(os=True)
        x = self.get_mouse_pos().x()
        y = self.get_mouse_pos().y()
        pxm_list = ['pxm_enabled',
                    'pxm_hover',
                    'pxm_pressed']
        path_list = list()
        for string in pxm_list:
            title = 'Open {}'.format(string)
            path = file_dialog(caption=title, for_open=True,
                               fmt={'Image Files': ['png', 'jpeg',
                                                    'jpg', 'jpe']})
            path_list.append(path)
        button_data = ButtonData(None,
                                 path_list[0],
                                 path_list[1],
                                 path_list[2],
                                 x, y, 1, partial(cmds.select, sel))
        self.create_button(button_data)

    def change_background(self):
        '''
        called from contextMenuEvent
        change the background of the picker
        '''
        title = 'Open Background'
        path = file_dialog(caption=title, for_open=True,
                           fmt={'Image Files': ['png', 'jpeg',
                                                'jpg', 'jpe']})
        if path != '':
            pxm = QtGui.QPixmap(path)
            self.background.setPixmap(pxm)

    def mousePressEvent(self, event):
        logger.debug('view CLICK')
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        # let Shift act as if Control
        if modifiers & QtCore.Qt.ShiftModifier:
            event.setModifiers(QtCore.Qt.ControlModifier)
        super(GraphicsView, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        logger.debug('view RELEASE')
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        # let Shift act as if Control
        if modifiers & QtCore.Qt.ShiftModifier:
            event.setModifiers(QtCore.Qt.ControlModifier)
        super(GraphicsView, self).mouseReleaseEvent(event)


# variable to store selected buttons for shift combo
_selected_item = deque()


class PixmapItem(QtWidgets.QGraphicsPixmapItem):

    def __init__(self, pxm_enabled, pxm_hover, pxm_pressed,
                 command=None, button_data=None, parent=None):
        self.pxm_enabled = pxm_enabled
        self.pxm_hover = pxm_hover
        self.pxm_pressed = pxm_pressed
        self.command = command
        self.button_data = button_data
        super(PixmapItem, self).__init__(self.pxm_enabled, parent)
        self.setAcceptHoverEvents(True)
        self.setAcceptTouchEvents(True)
        self._drag = False
        # self._combo = False
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        # self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, False)

    def hoverEnterEvent(self, event):
        '''
        Change pxm when hover
        '''
        self.setPixmap(self.pxm_hover)
        super(PixmapItem, self).hoverEnterEvent(event)

    def mousePressEvent(self, event):
        logger.debug('CLICK')
        self.setPixmap(self.pxm_pressed)
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        # let Shift act as if Control
        if modifiers & QtCore.Qt.ShiftModifier:
            event.setModifiers(QtCore.Qt.ControlModifier)
        super(PixmapItem, self).mousePressEvent(event)

        if(event.button() == QtCore.Qt.LeftButton
           and modifiers == QtCore.Qt.ControlModifier):
            logger.debug('CONTROL COMBO')

        elif (event.button() == QtCore.Qt.LeftButton and
              modifiers == QtCore.Qt.ShiftModifier):
            logger.debug('SHIFT COMBO')

        elif event.button() == QtCore.Qt.LeftButton:
            logger.debug('LEFT')

        elif event.button() == QtCore.Qt.RightButton:
            logger.debug('RIGHT')

        elif event.button() == QtCore.Qt.MidButton:
            logger.debug('DRAG')
            # change cursor to quad arrow
            cursor = QtGui.QCursor(QtCore.Qt.SizeAllCursor)
            QtWidgets.QApplication.instance().setOverrideCursor(cursor)
            self._drag = True
        '''
        stops event propagation using event.accept()
        UI events get propagated up to ascending widgets
        until one of them accepts it
        '''
        event.accept()

    def mouseMoveEvent(self, event):
        super(PixmapItem, self).mouseMoveEvent(event)
        if self._drag:
            new_pos = event.scenePos()
            # Keep the old Y position, so only the X-pos changes.
            # old_pos = self.scenePos()
            # new_pos.setY( old_pos.y() )
            self.setPos(new_pos)

    def mouseReleaseEvent(self, event):
        logger.debug('RELEASE')
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        # let Shift act as if Control
        if modifiers & QtCore.Qt.ShiftModifier:
            event.setModifiers(QtCore.Qt.ControlModifier)
        self.setPixmap(self.pxm_hover)
        super(PixmapItem, self).mouseReleaseEvent(event)
        if self._drag:
            self._drag = False
            self.button_data.x = self.x()
            self.button_data.y = self.y()
        QtWidgets.QApplication.instance().restoreOverrideCursor()

    def hoverLeaveEvent(self, event):
        self.setPixmap(self.pxm_enabled)
        super(PixmapItem, self).hoverLeaveEvent(event)

    def itemChange(self, change, value):
        '''
        detect when item is selected
        '''

        if change == self.ItemSelectedChange:
            if value:
                try:
                    self.command(add=True)
                except (TypeError, ValueError) as e:
                    logger.info(e)
            elif not value:
                try:
                    self.command(deselect=True)
                except (TypeError, ValueError) as e:
                    logger.info(e)
        return QtWidgets.QGraphicsItem.itemChange(self,
                                                  change, value)

    def contextMenuEvent(self, event):
        super(PixmapItem, self).contextMenuEvent(event)
        menu_popup = QtWidgets.QMenu()

        action_add = menu_popup.addAction('Change Icon')
        action_add.setStatusTip('Change icon')
        # action_add.setShortcut('Ctrl+Shift+C')
        action_add.triggered.connect(self.change_icon)

        action_remove = menu_popup.addAction('Remove Button')
        action_remove.setStatusTip('Remove button')
        action_remove.triggered.connect(self.remove_button)

        action_select = menu_popup.addAction('Change Selection')
        action_select.setStatusTip('Change command to current selection')
        action_select.triggered.connect(self.change_selection)
        selected_action = menu_popup.exec_(event.screenPos())
        event.setAccepted(True)

    def change_icon(self):
        '''
        called from contextMenuEvent
        change the enabled, hover, pressed icons
        update the path in ButtonData
        '''
        pxm_list = ['pxm_enabled',
                    'pxm_hover',
                    'pxm_pressed']
        for string in pxm_list:
            title = 'Change {}'.format(string)
            path = file_dialog(caption=title, for_open=True,
                               fmt={'Image Files': ['png', 'jpeg',
                                                    'jpg', 'jpe']})
            if path != '':
                pxm = QtGui.QPixmap(path)
                setattr(self, string, pxm)
                setattr(self.button_data, string, pxm)
        self.setPixmap(self.pxm_enabled)

    def remove_button(self):
        '''
        called from contextMenuEvent
        remove a button and its ButtonData in button_list
        '''
        self.scene().removeItem(self)
        try:
            button_list.remove(self.button_data)
        except ValueError as e:
            logger.error(e)
        logger.debug(button_list)

    def change_selection(self):
        '''
        update selection command based on currently selected
        '''
        sel = cmds.ls(os=True)
        self.command = partial(cmds.select, sel)
        self.button_data.command = self.command


test_ui = MainWindow()
test_ui.setAttribute(QtCore.Qt.WA_DeleteOnClose)
test_ui.show()
