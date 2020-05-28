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
    def __init__(self, character_list=list()):
        # list of CharacterData
        self.character_list = character_list


class CharacterData(object):
    def __init__(self, name, scene_data, namespace=None,
                 tab_list=list()):
        self.name = str(name)
        self.scene_data = scene_data
        self.namespace = namespace
        # list of TabData
        self.tab_list = tab_list


class TabData(object):
    def __init__(self, name, character_data, button_list=list()):
        self.name = str(name)
        # list of ButtonData
        self.character_data = character_data
        self.button_list = button_list


class ButtonData(object):
    def __init__(self, name, pxm_enabled, pxm_hover, pxm_pressed,
                 x, y, scale, command_select, command_deselect,
                 tab_data):
        self.name = str(name)
        self.pxm_enabled = pxm_enabled
        self.pxm_hover = pxm_hover
        self.pxm_pressed = pxm_pressed
        self.x = x
        self.y = y
        self.scale = scale
        self.command_select = command_select
        self.command_deselect = command_deselect
        self.tab_data = tab_data
        self.store_data()

    def store_data(self):
        '''
        store the button data object into button_list
        '''
        button_list.append(self)


# button_01 = ButtonData('button_01',
#                        'B:/Documents/GitHub/RAA_autoRig/icons/button_star_orange_enabled.png',
#                        'B:/Documents/GitHub/RAA_autoRig/icons/button_star_orange_hover.png',
#                        'B:/Documents/GitHub/RAA_autoRig/icons/button_star_orange_pressed.png',
#                        100, 0, 1,
#                        'pm.select("pSphere1", add=True)',
#                        'pm.select("pSphere1", deselect=True)')
# button_02 = ButtonData('button_02',
#                        'B:/Documents/GitHub/RAA_autoRig/icons/button_star_purple_enabled.png',
#                        'B:/Documents/GitHub/RAA_autoRig/icons/button_star_purple_hover.png',
#                        'B:/Documents/GitHub/RAA_autoRig/icons/button_star_purple_pressed.png',
#                        0, 180, 0.6,
#                        'pm.select("pCube1", add=True)',
#                        'pm.select("pCube1", deselect=True)')
# button_02 = ButtonData('button_03',
#                        'B:/Documents/GitHub/RAA_autoRig/icons/button_star_purple_enabled.png',
#                        'B:/Documents/GitHub/RAA_autoRig/icons/button_star_purple_hover.png',
#                        'B:/Documents/GitHub/RAA_autoRig/icons/button_star_purple_pressed.png',
#                        200, 180, 1,
#                        'pm.select("pCylinder1", add=True)',
#                        'pm.select("pCylinder1", deselect=True)')
# button_02 = ButtonData('button_04',
#                        'B:/Documents/GitHub/RAA_autoRig/icons/button_star_orange_enabled.png',
#                        'B:/Documents/GitHub/RAA_autoRig/icons/button_star_orange_hover.png',
#                        'B:/Documents/GitHub/RAA_autoRig/icons/button_star_orange_pressed.png',
#                        100, 360, 0.6,
#                        'pm.select("pCone1", add=True)',
#                        'pm.select("pCone1", deselect=True)')


class ButtonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ButtonData):
            return (obj.name,
                    obj.pxm_enabled,
                    obj.pxm_hover, obj.pxm_pressed,
                    obj.x, obj.y,
                    obj.scale, obj.command_select, obj.command_deselect)
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
                              dct['scale'],
                              dct['command_select'], dct['command_deselect'])
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
        self.setProperty('saveWindowPref', True)
        self.window = 'test_star'
        self.title = 'Star'
        self.size = (720, 720)
        self.scene_data = None
        self.create_ui()

    def create_ui(self):
        self.setWindowTitle(self.title)
        self.resize(QtCore.QSize(*self.size))

        self.create_menu_bar()

        tab_widget = TabWidget(self)
        self.setCentralWidget(tab_widget)

        self.tool_bar = self.addToolBar('Namespace')
        self.tool_bar.setMovable(False)
        # self.statusBar().showMessage('...')

        self.combo_box = QtWidgets.QComboBox(self.tool_bar)
        self.tool_bar.addWidget(combo_box)
        self.combo_box.addItem('Frodo')
        self.combo_box.addItem('Bilbo')
        self.combo_box.addItem('Gandalf')

        self.add_tool_bar_spacer(4, 8)

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

        self.new_scene()

    def add_tool_bar_spacer(self, width, height):
        '''
        add a blank widget as a toolbar spacer
        '''
        spacer = QtWidgets.QWidget(self.tool_bar)
        spacer.setFixedSize(width, height)
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
        act_scene_new.triggered.connect(self.new_scene)
        act_scene_open = menu_file.addAction('Open Scene...')
        act_scene_open.setStatusTip('Open a picker scene')
        act_scene_save = menu_file.addAction('Save Scene')
        act_scene_save.setStatusTip('Save picker scene')

        menu_file = menu_bar.addMenu('Character')
        act_character_new = menu_file.addAction('New Character')
        act_character_new.setStatusTip('Add a new character')
        act_character_new.triggered.connect(self.new_character)
        act_character_open = menu_file.addAction('Open Character...')
        act_character_open.setStatusTip('Open a character')
        act_character_save = menu_file.addAction('Save Character')
        act_character_save.setStatusTip('Save current character')
        act_character_del = menu_file.addAction('Delete Character')
        act_character_del.setStatusTip('Delete current character')

        menu_file = menu_bar.addMenu('Tab')
        act_tab_new = menu_file.addAction('New Tab')
        act_tab_new.setStatusTip('Add a new blank tab')
        act_tab_open = menu_file.addAction('Open Tab...')
        act_tab_open.setStatusTip('Open a tab')
        act_tab_save = menu_file.addAction('Save Tab')
        act_tab_save.setStatusTip('Save current tab')
        act_tab_del = menu_file.addAction('Delete Tab')
        act_tab_del.setStatusTip('Delete current tab')

    def new_character(self):
        '''
        create a new character
        '''
        name, ok = QtWidgets.QInputDialog.getText(self,
                                                  'New Character',
                                                  'Enter character name:')
        if ok:
            character_data = CharacterData(name=name,
                                           scene_data=self.scene_data)
            self.combo_box.addItem(text=name, userData=character_data)
            self.new_tab_widget(character_data)

    def new_tab_widget(self, character_data):
        '''
        create a new main widget for new character
        '''
        tab_widget = TabWidget(character_data, self)
        self.setCentralWidget(tab_widget)

    def new_scene(self):
        '''
        create a new scene
        '''
        self.scene_data = SceneData()


# class MainWidget(QtWidgets.QWidget):
#     '''
#     container widget for tabs widget and QGraphicsView
#     '''
#     def __init__(self, parent=None):
#         super(MainWidget, self).__init__(parent)
#         self.size = (512, 512)
#         self.create_ui()

#     def create_ui(self):
#         self.tab_widget = TabWidget(self)
#         self.main_layout = QtWidgets.QVBoxLayout()
#         self.setLayout(self.main_layout)
#         self.main_layout.addWidget(self.tab_widget)


class TabWidget(QtWidgets.QTabWidget):
    '''
    tab widget with tabs and plus button
    bug with setMovable and plus button
    '''

    def __init__(self, character_data, parent=None):
        self.main_widget = QtWidgets.QWidget()
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_widget.setLayout(self.main_layout)
        super(TabWidget, self).__init__(self.main_widget)
        self.main_layout.addWidget(self)

        self.setTabsClosable(True)
        # self.setMovable(True)
        self.tabCloseRequested.connect(self.close_tab)
        select_left = QtWidgets.QTabBar.SelectLeftTab
        self.tabBar().setSelectionBehaviorOnRemove(select_left)
        self.pad = 1
        self.create_tabs()
        self.character_data = character_data

    def create_tabs(self):
        '''
        create a '+' tab and a blank untitled tab
        '''
        # style sheet for flat rounded buttons
        style_sheet = '''QPushButton {
                            border-radius: 10px;
                            font: bold 16px;
                            color: rgb(200, 200, 200);
                            padding: 0px 0px 5px 0px;
                            }
                         QPushButton:hover {
                            background-color: rgb(80, 80, 80);
                            }
                         QPushButton:pressed {
                            background-color: rgb(90, 90, 90);
                            }'''
        # create the 'new tab' tab with a button
        self.insertTab(0, QtWidgets.QWidget(), '')
        nb = self.new_btn = QtWidgets.QPushButton()
        nb.setFixedSize(20, 20)
        nb.setFlat(True)
        # font = QtGui.QFont()
        # font.setPointSize(12)
        # font.setBold(True)
        # nb.setFont(font)
        nb.setText('+')
        nb.setStyleSheet(style_sheet)
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
        tab_data = TabData(name=name, character_data=self.character_data)
        self.character_data.tab_list.append(tab_data)
        graphics_view = GraphicsView(tab_data, self)

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

    def __init__(self, tab_data=None, parent=None):
        # create scene first
        self._scene = QtWidgets.QGraphicsScene()
        self._scene.setSceneRect(0, 0, 1, 1)
        # pass scene to the QGraphicsView's constructor method
        super(GraphicsView, self).__init__(self._scene, parent)
        self.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.setRenderHints(QtGui.QPainter.Antialiasing
                            | QtGui.QPainter.SmoothPixmapTransform)

        # format = QtOpenGL.QGLFormat(QtOpenGL.QGL.SampleBuffers)
        # self.setViewport(QtOpenGL.QGLWidget(format))

        self.setDragMode(self.RubberBandDrag)

        self.background = QtWidgets.QGraphicsPixmapItem(None)
        self._scene.addItem(self.background)

        self.tab_data = tab_data

        # for button_data in button_list:
        #     self.create_button(button_data)

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
            action_new.triggered.connect(self.new_button)

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
                               QtCore.Qt.KeepAspectRatio,
                               QtCore.Qt.SmoothTransformation)
            pxm_s_list.append(pxm_s)
        command_select = button_data.command_select
        command_deselect = button_data.command_deselect
        pxm_item = PixmapItem(pxm_enabled=pxm_s_list[0],
                              pxm_hover=pxm_s_list[1],
                              pxm_pressed=pxm_s_list[2],
                              command_select=command_select,
                              command_deselect=command_deselect,
                              button_data=button_data)
        pxm_item.setPos(button_data.x, button_data.y)
        # .png alpha as bounding box, already default
        # pxm_item.ShapeMode(QtWidgets.QGraphicsPixmapItem.MaskShape)

        self.tab_data.button_list.append(button_data)
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

    def new_button(self):
        '''
        called from contextMenuEvent
        add a new button on mouse position
        command selects current selection
        maya.cmds because list of PyNode must be strings
        '''
        x = self.get_mouse_pos().x()
        y = self.get_mouse_pos().y()

        sel = cmds.ls(os=True)
        if not isinstance(sel, list):
            sel = '"{}"'.format(sel)
        command_select = 'pm.select({}, add=True)'.format(sel)
        command_deselect = 'pm.select({}, deselect=True)'.format(sel)

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
                                 x, y, 1,
                                 command_select, command_deselect)
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


class PixmapItem(QtWidgets.QGraphicsPixmapItem):

    def __init__(self, pxm_enabled, pxm_hover, pxm_pressed,
                 command_select=None, command_deselect=None,
                 button_data=None, parent=None):
        self.pxm_enabled = pxm_enabled
        self.pxm_hover = pxm_hover
        self.pxm_pressed = pxm_pressed
        self.command_select = command_select
        self.command_deselect = command_deselect
        self.button_data = button_data
        super(PixmapItem, self).__init__(self.pxm_enabled, parent)
        self.setAcceptHoverEvents(True)
        self.setAcceptTouchEvents(True)
        self._drag = False
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)

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
                    exec(self.command_select)
                except (TypeError, ValueError) as e:
                    logger.info(e)
            elif not value:
                try:
                    exec(self.command_deselect)
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
        menu_popup.exec_(event.screenPos())
        event.setAccepted(True)

    @QtCore.Slot()
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

    @QtCore.Slot()
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

    @QtCore.Slot()
    def change_selection(self):
        '''
        called from contextMenuEvent
        update selection command based on currently selected
        '''
        sel = cmds.ls(os=True)
        if not isinstance(sel, list):
            sel = '"{}"'.format(sel)
        self.command_select = 'pm.select({}, add=True)'.format(sel)
        self.command_deselect = 'pm.select({}, deselect=True)'.format(sel)
        self.button_data.command_select = self.command_select
        self.button_data.command_deselect = self.command_deselect


test_ui = MainWindow()
test_ui.setAttribute(QtCore.Qt.WA_DeleteOnClose)
test_ui.show()
