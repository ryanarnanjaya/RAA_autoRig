from PySide2 import QtGui, QtCore, QtWidgets
from shiboken2 import wrapInstance
# from functools import partial
# deque is a list-like container with fast O(1) appends and pops on either end
# from collections import deque
# import maya.OpenMaya as om
import maya.OpenMayaUI as omui
import maya.cmds as cmds
import pymel.core as pm
# import os
import logging
import json
import re
# import yaml
# The Qt Resource System for .png files
# paint your own customizable button?
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
    # or update sets
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


class JsonConvert(object):
    '''
    class to convert class objects from and to json
    '''
    mappings = {}

    @classmethod
    def register(cls, class_instance):
        '''
        decorator method to register a class for JsonConvert
        '''
        class_attr = tuple(class_instance().__dict__.keys())
        # frozenset returns immutable set object
        cls.mappings[frozenset(class_attr)] = class_instance
        return class_instance

    @classmethod
    def complex_handler(cls, obj):
        '''
        handler to json
        '''
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        else:
            message = 'Type {} with value {} is not JSON serializable'
            raise TypeError(message.format(type(obj), repr(obj)))

    @classmethod
    def class_mapper(cls, dictionary):
        '''
        mapper from json to class
        '''
        for keys, cls in cls.mappings.items():
            # are all required arguments present?
            # True if keys has every elements of dictionary.keys()
            if keys.issuperset(dictionary.keys()):
                # ** unpacks dictionary
                return cls(**dictionary)
        else:
            # Raise exception instead of silently returning None
            # {!s} applies str() to format
            message = 'Unable to find a matching class for object: {!s}'
            raise ValueError(message.format(dictionary))

    @classmethod
    def to_json(cls, obj):
        return json.dumps(obj.__dict__,
                          default=cls.complex_handler,
                          indent=4)

    @classmethod
    def from_json(cls, json_str):
        return json.loads(json_str,
                          object_hook=cls.class_mapper)

    @classmethod
    def to_file(cls, obj, path):
        with open(path, 'w') as json_file:
            json_file.writelines([cls.to_json(obj)])
        return path

    @classmethod
    def from_file(cls, filepath):
        result = None
        with open(filepath, 'r') as json_file:
            result = cls.from_json(json_file.read())
        return result


@JsonConvert.register
class SceneData(object):
    def __init__(self, character_data_list=None):
        # list of CharacterData
        self.character_data_list = character_data_list


@JsonConvert.register
class CharacterData(object):
    def __init__(self, name=None, tab_data_list=None, scene_data=None,
                 namespace=None):
        self.name = str(name)
        self.namespace = namespace
        # list of TabData
        self.tab_data_list = tab_data_list


@JsonConvert.register
class TabData(object):
    def __init__(self, name=None, button_data_list=None,
                 pxm_background=None):
        self.name = str(name)
        # list of ButtonData
        self.button_data_list = button_data_list
        self.pxm_background = pxm_background


@JsonConvert.register
class ButtonData(object):
    def __init__(self, name=None,
                 pxm_enabled=None, pxm_hover=None, pxm_pressed=None,
                 x=None, y=None, scale=None,
                 command_select=None, command_deselect=None,
                 node_list=None):
        self.name = str(name)
        self.pxm_enabled = pxm_enabled
        self.pxm_hover = pxm_hover
        self.pxm_pressed = pxm_pressed
        self.x = x
        self.y = y
        self.scale = scale
        self.command_select = command_select
        self.command_deselect = command_deselect
        # list of nodes as inputs for commands
        self.node_list = node_list


def get_maya_window():
    '''
    get maya main window from a C++ pointer in memory using shiboken2
    advantage: works without pymel
    disadvantage: requires more lines of code, unsupported < Maya 2017
    '''
    try:
        pointer = omui.MQtUtil.mainWindow()
        maya_main_window = wrapInstance(int(pointer), QtWidgets.QMainWindow)
    except Exception as e:
        maya_main_window = None
        logger.error(e)
    return maya_main_window


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        if parent is None:
            self.parent = get_maya_window()
            # self.parent = pm.ui.Window('MayaWindow').asQtObject()

        super(MainWindow, self).__init__(parent)
        self.setWindowFlags(self.windowFlags()
                            | QtCore.Qt.WindowStaysOnTopHint)
        # self.setWindowFlags(QtCore.Qt.Window)
        self.setProperty('saveWindowPref', True)
        self.title = 'RAA_picker'
        self.size = (824, 880)
        self.scene_data = None
        self.character_data = None
        self.create_ui()
        self.new_scene()

    def create_ui(self):
        self.setWindowTitle(self.title)
        self.resize(QtCore.QSize(*self.size))

        self.create_menu_bar()

        self.tool_bar = self.addToolBar('Namespace')
        self.tool_bar.setMovable(False)
        # self.statusBar().showMessage('...')

        self.combo_box = ComboBox(self.tool_bar)
        self.tool_bar.addWidget(self.combo_box)
        self.combo_box.setFixedSize(144, 18)
        self.combo_box.activated.connect(self.combo_box_activated)
        # self.new_character(name='Character_1')

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
        self.name_label.editingFinished.connect(self.propagate_namespace)
        # name_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed,
        #                          QtWidgets.QSizePolicy.Expanding)
        # name_label.setFixedSize(150, 18)
        self.name_label.setText('rig:')
        # self.character_data.namespace = 'rig:'

    def add_tool_bar_spacer(self, width, height):
        '''
        add a blank widget as a toolbar spacer
        '''
        spacer = QtWidgets.QWidget(self.tool_bar)
        spacer.setFixedSize(width, height)
        self.tool_bar.addWidget(spacer)

    def create_menu_bar(self):
        menu_bar = self.menuBar()

        menu_file = menu_bar.addMenu('Scene')
        act_scene_new = menu_file.addAction('New Scene')
        act_scene_new.setStatusTip('Create a new picker scene')
        act_scene_new.triggered.connect(self.new_scene)
        act_scene_open = menu_file.addAction('Open Scene...')
        act_scene_open.setStatusTip('Open a picker scene')
        act_scene_open.triggered.connect(self.open_scene)
        act_scene_save = menu_file.addAction('Save Scene')
        act_scene_save.setStatusTip('Save picker scene')
        act_scene_save.triggered.connect(self.save_scene)

        menu_file = menu_bar.addMenu('Character')
        act_character_new = menu_file.addAction('New Character')
        act_character_new.setStatusTip('Add a new character')
        act_character_new.triggered.connect(self.new_character)
        act_character_open = menu_file.addAction('Open Character...')
        act_character_open.setStatusTip('Open a character')
        act_character_open.triggered.connect(self.open_character)
        act_character_save = menu_file.addAction('Save Character')
        act_character_save.setStatusTip('Save current character')
        act_character_save.triggered.connect(self.save_character)
        act_character_rename = menu_file.addAction('Rename Character')
        act_character_rename.setStatusTip('Rename current character')
        act_character_rename.triggered.connect(self.rename_character)
        self.act_character_delete = menu_file.addAction('Delete Character')
        self.act_character_delete.setStatusTip('Delete current character')
        self.act_character_delete.triggered.connect(self.delete_character)
        self.act_character_delete.setDisabled(True)

        menu_file = menu_bar.addMenu('Tab')
        # act_tab_new = menu_file.addAction('New Tab')
        # act_tab_new.setStatusTip('Add a new blank tab')
        act_tab_open = menu_file.addAction('Open Tab...')
        act_tab_open.setStatusTip('Open a tab')
        act_tab_open.triggered.connect(self.open_tab)
        act_tab_save = menu_file.addAction('Save Tab')
        act_tab_save.setStatusTip('Save current tab')
        act_tab_save.triggered.connect(self.save_tab)
        # act_tab_delete = menu_file.addAction('Delete Tab')
        # act_tab_delete.setStatusTip('Delete current tab')

    def new_scene(self):
        '''
        clear all characters in combo_box
        create a new SceneData with blank character_data_list
        add a new Character_1
        update namespace on CharacterData based on name_label
        '''
        self.combo_box.clear()
        self.scene_data = SceneData(character_data_list=list())
        self.new_character(name='Character_1')
        self.propagate_namespace()

    def open_scene(self):
        '''
        open json file to SceneData
        apply SceneData
        create characters from character_data_list
        '''
        title = 'Open Scene'
        path = file_dialog(parent=self, caption=title, for_open=True,
                           fmt={'Json File': ['json']})
        if path == '':
            return
        scene_data = JsonConvert.from_file(path)
        if not isinstance(scene_data, SceneData):
            logger.error('{} is not a scene file'.format(path))
            return
        self.combo_box.clear()
        self.scene_data = scene_data
        for character_data in self.scene_data.character_data_list:
            self.create_character(character_data)

    def save_scene(self):
        '''
        save SceneData to json file
        '''
        title = 'Save Scene'
        path = file_dialog(parent=self, caption=title, for_open=False,
                           fmt={'Json File': ['json']})
        if path != '':
            JsonConvert.to_file(self.scene_data, path)

    def new_character(self, name=None):
        '''
        create a new character
        '''
        if name is None:
            name, ok = QtWidgets.QInputDialog.getText(self,
                                                      'New Character',
                                                      'Character name:')
        else:
            # if window init with given name
            ok = True
        if ok:
            character_data = CharacterData(name=name,
                                           tab_data_list=list())
            self.scene_data.character_data_list.append(character_data)
            self.create_character(character_data)

    def create_character(self, character_data):
        '''
        create a character based on character_data
        '''
        self.character_data = character_data
        self.combo_box.addItem(character_data.name,
                               character_data,
                               )
        index = self.combo_box.findData(character_data)
        if index != -1:
            self.combo_box.setCurrentIndex(index)
        self.new_tab_widget(character_data)

        if self.combo_box.count() > 1:
            # enable Delete Character menu action
            self.act_character_delete.setEnabled(True)

    def combo_box_activated(self, index):
        '''
        when user selects a character from combo_box
        set namespace from CharacterData
        '''
        self.character_data = self.combo_box.itemData(index)
        self.new_tab_widget(self.character_data)
        self.name_label.setText(self.character_data.namespace)
        self.propagate_namespace()
        if self.combo_box.count() == 1:
            self.act_character_delete.setDisabled(True)

    def new_tab_widget(self, character_data):
        '''
        create a new main widget for a new character
        '''
        tab_widget = TabWidget(character_data=character_data,
                               parent=self)
        self.setCentralWidget(tab_widget)

    def open_character(self):
        '''
        open json file to CharacterData
        apply CharacterData
        create character
        '''
        title = 'Open Character'
        path = file_dialog(parent=self, caption=title, for_open=True,
                           fmt={'Json File': ['json']})
        if path == '':
            return
        character_data = JsonConvert.from_file(path)
        if not isinstance(character_data, CharacterData):
            logger.error('{} is not a character file'.format(path))
            return
        self.character_data = character_data
        self.create_character(self.character_data)

    def save_character(self):
        '''
        save CharacterData to json file
        '''
        title = 'Save Character'
        path = file_dialog(parent=self, caption=title, for_open=False,
                           fmt={'Json File': ['json']})
        if path != '':
            JsonConvert.to_file(self.character_data, path)

    def rename_character(self):
        '''
        rename active character
        update CharacterData and combo_box
        '''
        instruction = 'Rename "{}" to:'.format(self.character_data.name)
        text, ok = QtWidgets.QInputDialog.getText(self,
                                                  'Rename Character',
                                                  instruction)
        if ok:
            self.character_data.name = text
            current_index = self.combo_box.currentIndex()
            self.combo_box.setItemText(current_index, text)

    def delete_character(self):
        '''
        delete active character
        remove current data from character_data_list in SceneData
        '''
        if self.combo_box.count() == 1:
            return
        current_index = self.combo_box.currentIndex()
        current_data = self.combo_box.itemData(current_index)
        self.scene_data.character_data_list.remove(current_data)
        self.combo_box.removeItem(current_index)
        current_index = self.combo_box.currentIndex()
        self.combo_box_activated(current_index)

    def open_tab(self):
        '''
        open json file to TabData
        append TabData to tab_data_list
        create tab
        '''
        title = 'Open Tab'
        path = file_dialog(parent=self, caption=title, for_open=True,
                           fmt={'Json File': ['json']})
        if path == '':
            return
        tab_data = JsonConvert.from_file(path)
        if not isinstance(tab_data, TabData):
            logger.error('{} is not a tab file'.format(path))
            return
        self.character_data.tab_data_list.append(tab_data)
        tab_widget = self.centralWidget()
        tab_widget.create_tab(tab_data)

    def save_tab(self):
        '''
        save TabData to json file
        get TabData from QGraphicsView
        '''
        title = 'Save Tab'
        path = file_dialog(parent=self, caption=title, for_open=False,
                           fmt={'Json File': ['json']})
        if path == '':
            return
        # tab_widget = self.findChildren(QtWidgets.QTabWidget)
        tab_widget = self.centralWidget()
        current_widget = tab_widget.currentWidget()
        graphics_view = current_widget.findChildren(QtWidgets.QGraphicsView)
        tab_data = graphics_view[0].tab_data
        JsonConvert.to_file(tab_data, path)

    def update_namespace(self):
        '''
        update namespace QLineEdit based on selection
        propegate new namespace
        '''
        try:
            namespace = pm.ls(os=True)[0].namespace()
        except IndexError as e:
            logger.info(e)
        else:
            # if try success
            self.name_label.setText(namespace)
            self.propagate_namespace()

    def propagate_namespace(self):
        '''
        update CharacterData
        propagate namespace in each child buttons
        '''
        self.character_data.namespace = self.name_label.text()
        child_graphics_view = self.findChildren(QtWidgets.QGraphicsView)
        for graphics_view in child_graphics_view:
            for button in graphics_view.items():
                if QtWidgets.QGraphicsItem.ItemIsSelectable == button.flags():
                    # only buttons have ItemIsSelectable flag
                    button.set_namespace()


class ComboBox(QtWidgets.QComboBox):
    '''
    reimplement findData to work with python objects
    '''
    def findData(self, data):
        for index in range(self.count()):
            if self.itemData(index) == data:
                return index
        return -1


class TabWidget(QtWidgets.QTabWidget):
    '''
    tab widget with tabs and plus button
    bug with setMovable and plus button
    '''
    def __init__(self, character_data, parent=None):
        super(TabWidget, self).__init__(parent)
        self.character_data = character_data
        self.setTabBar(TabBar(self))
        self.setTabsClosable(True)
        # self.setMovable(True)
        self.currentChanged.connect(self.resize_close_button)
        self.tabCloseRequested.connect(self.close_tab)
        select_left = QtWidgets.QTabBar.SelectLeftTab
        self.tabBar().setSelectionBehaviorOnRemove(select_left)
        self.init_tabs()

    def init_tabs(self):
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
        if self.character_data.tab_data_list == list():
            self.new_tab()
        else:
            for tab_data in self.character_data.tab_data_list:
                self.create_tab(tab_data)

    def get_max_padding(self):
        '''
        get maximum # padding in Untitled_# tab names
        '''
        padding_list = list()
        for tab_data in self.character_data.tab_data_list:
            if 'Untitled_' not in tab_data.name:
                continue
            match = re.search('^Untitled_0*([1-9]+[0-9]{0,})$',
                              tab_data.name)
            if match:
                padding_list.append(int(match.group(1)))
            else:
                padding_list.append(0)
        if padding_list:
            return max(padding_list)
        else:
            return 0

    def new_tab(self, name='Untitled'):
        '''
        create a new blank untitled tab
        '''
        padding = self.get_max_padding() + 1
        tab_name = '{n}_{p}'.format(n=name, p=padding)
        tab_data = TabData(name=tab_name,
                           button_data_list=list())
        self.character_data.tab_data_list.append(tab_data)
        # self.pad += 1

        return self.create_tab(tab_data)

    def create_tab(self, tab_data):
        '''
        basic method to create a tab
        '''
        tab_layout = QtWidgets.QVBoxLayout()
        widget = QtWidgets.QWidget()
        widget.setLayout(tab_layout)

        index = self.count() - 1
        self.insertTab(index, widget, tab_data.name)
        self.setCurrentIndex(index)

        graphics_view = GraphicsView(tab_data=tab_data,
                                     parent=widget)
        tab_layout.addWidget(graphics_view)
        graphics_view.init_button_list()
        return widget

    @QtCore.Slot()
    def close_tab(self, index):
        '''
        slot to close tab
        '''
        # if self.count() > 2:
        self.removeTab(index)
        self.character_data.tab_data_list.pop(index)
        self.resize_close_button()

    def resize_close_button(self):
        right_side = QtWidgets.QTabBar.RightSide
        if self.count() > 2:
            self.tabBar().tabButton(0, right_side).show()
        if self.count() == 2:
            self.tabBar().tabButton(0, right_side).hide()


class TabBar(QtWidgets.QTabBar):
    '''
    QTabBar with double click signal and tab rename behavior.
    '''

    def __init__(self, parent=None):
        super(TabBar, self).__init__(parent)

    def mouseDoubleClickEvent(self, event):
        tab_index = self.tabAt(event.pos())
        try:
            # interupted rename by double-click other tab
            self.finish_rename()
        except AttributeError as e:
            logger.debug(e)
        self.start_rename(tab_index)

    def start_rename(self, tab_index):
        if tab_index is (self.count() - 1):
            # if plus button
            return
        self.edited_tab = tab_index
        rect = self.tabRect(tab_index)
        top_margin = 3
        left_margin = 6
        self.line_edit = QtWidgets.QLineEdit(self)
        self.line_edit.show()
        self.line_edit.move(rect.left() + left_margin,
                            rect.top() + top_margin)
        self.line_edit.resize(rect.width() - 2 * left_margin,
                              rect.height() - 2 * top_margin)
        self.line_edit.setText(self.tabText(tab_index))
        self.line_edit.selectAll()
        self.line_edit.setFocus()
        try:
            self.line_edit.editingFinished.connect(self.finish_rename)
        except AttributeError as e:
            logger.debug(e)

    @QtCore.Slot()
    def finish_rename(self):
        logger.debug('finish_rename')
        new_name = self.line_edit.text()
        self.setTabText(self.edited_tab,
                        new_name)
        self.line_edit.deleteLater()
        self.line_edit = None
        # update tab_data.name
        character_data = self.parentWidget().character_data
        tab_data = character_data.tab_data_list[self.edited_tab]
        tab_data.name = new_name


class GraphicsView(QtWidgets.QGraphicsView):
    '''
    class for QGraphicsView to contain buttons
    '''

    def __init__(self, tab_data=None, parent=None):
        # create scene first
        # self.parent = parent
        self.graphics_scene = QtWidgets.QGraphicsScene()
        self.graphics_scene.setSceneRect(0, 0, 1, 1)
        # pass scene to the QGraphicsView's constructor method
        super(GraphicsView, self).__init__(self.graphics_scene, parent)
        self.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.setRenderHints(QtGui.QPainter.Antialiasing
                            | QtGui.QPainter.SmoothPixmapTransform)

        # format = QtOpenGL.QGLFormat(QtOpenGL.QGL.SampleBuffers)
        # self.setViewport(QtOpenGL.QGLWidget(format))
        self.setDragMode(self.RubberBandDrag)
        self.background = QtWidgets.QGraphicsPixmapItem(None)
        self.graphics_scene.addItem(self.background)
        self.tab_data = tab_data
        if self.tab_data.pxm_background is not None:
            self.change_background(self.tab_data.pxm_background)

    def init_button_list(self):
        '''
        init buttons based on button_data_list
        '''
        for button_data in self.tab_data.button_data_list:
            self.create_button(button_data)

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
            menu_popup.exec_(event.globalPos())

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

        pxm_item = PixmapItem(pxm_enabled=pxm_s_list[0],
                              pxm_hover=pxm_s_list[1],
                              pxm_pressed=pxm_s_list[2],
                              button_data=button_data,
                              )
        pxm_item.setPos(button_data.x, button_data.y)
        # .png alpha as bounding box, already default
        # pxm_item.ShapeMode(QtWidgets.QGraphicsPixmapItem.MaskShape)
        self.graphics_scene.addItem(pxm_item)
        pxm_item.set_namespace()

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

        # get selection name without namespace
        selection = pm.ls(os=True)
        node_list = list()
        for sel in selection:
            # remove all namespace and append to selection_list
            node_list.append(sel.stripNamespace().__str__())
        # {{}} will output excaped {}
        command_select = 'pm.select({}, add=True)'
        command_deselect = 'pm.select({}, deselect=True)'

        # file_dialog to choose button states images
        pxm_list = ['pxm_enabled',
                    'pxm_hover',
                    'pxm_pressed']
        path_list = list()
        for string in pxm_list:
            title = 'Open {}'.format(string)
            path = file_dialog(parent=self, caption=title, for_open=True,
                               fmt={'Image Files': ['png', 'jpeg',
                                                    'jpg', 'jpe']})
            path_list.append(path)
        button_data = ButtonData(None,
                                 path_list[0],
                                 path_list[1],
                                 path_list[2],
                                 x, y, 1,
                                 command_select, command_deselect,
                                 node_list,
                                 )
        self.create_button(button_data)
        self.tab_data.button_data_list.append(button_data)

    def change_background(self, path=None):
        '''
        called from contextMenuEvent
        change the background of the picker
        '''
        if path is None:
            title = 'Open Background'
            path = file_dialog(parent=self, caption=title, for_open=True,
                               fmt={'Image Files': ['png', 'jpeg',
                                                    'jpg', 'jpe']})
        if path != '':
            pxm = QtGui.QPixmap(path)
            self.background.setPixmap(pxm)
            self.tab_data.pxm_background = path

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
                 button_data=None, parent=None):
        self.pxm_enabled = pxm_enabled
        self.pxm_hover = pxm_hover
        self.pxm_pressed = pxm_pressed
        self.button_data = button_data
        self.command_select = button_data.command_select
        self.command_deselect = button_data.command_deselect
        self.node_list = button_data.node_list
        self.name_list = list()
        super(PixmapItem, self).__init__(self.pxm_enabled, parent)
        self.setAcceptHoverEvents(True)
        self.setAcceptTouchEvents(True)
        self._drag = False
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)

    def set_namespace(self):
        '''
        set namespace to name_list for every node in node_list
        declare self.graphics_view
        '''
        self.graphics_view = self.scene().views()[0]
        # QGraphicsView > QWidget > QVBoxLayout > QTabWidget
        tab_widget = self.graphics_view.parentWidget().parentWidget().parentWidget()
        namespace = tab_widget.character_data.namespace
        if namespace is None:
            return
        self.name_list = list()
        for node in self.node_list:
            self.name_list.append(namespace + node)

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
        todo: work with current namespace
        '''
        if change == self.ItemSelectedChange:
            if value:
                try:
                    exec(self.command_select.format(self.name_list))
                except (TypeError, ValueError) as e:
                    logger.info(e)
            elif not value:
                try:
                    exec(self.command_deselect.format(self.name_list))
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

        action_command = menu_popup.addAction('Edit Command')
        action_command.setStatusTip('Edit select and deselect commands')
        action_command.triggered.connect(self.edit_command)
        menu_popup.exec_(event.screenPos())
        # prevent QGraphicsView's contextMenuEvent to run
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
            path = file_dialog(parent=self.graphics_view,
                               caption=title, for_open=True,
                               fmt={'Image Files': ['png', 'jpeg',
                                                    'jpg', 'jpe']})
            if path != '':
                pxm = QtGui.QPixmap(path)
                setattr(self, string, pxm)
                setattr(self.button_data, string, path)
        self.setPixmap(self.pxm_enabled)

    @QtCore.Slot()
    def remove_button(self):
        '''
        called from contextMenuEvent
        remove a button and its ButtonData in TabData.button_data_list
        todo: remove from TabData
        '''
        self.scene().removeItem(self)
        try:
            button_data_list = self.graphics_view.tab_data.button_data_list
            button_data_list.remove(self.button_data)
        except ValueError as e:
            logger.error(e)

    @QtCore.Slot()
    def change_selection(self):
        '''
        called from contextMenuEvent
        update selection command based on currently selected
        '''
        # get selection name without namespace
        selection = pm.ls(os=True)
        self.node_list = list()
        for sel in selection:
            # remove all namespace and append to selection_list
            self.node_list.append(sel.stripNamespace().__str__())
        # update ButtonData
        self.button_data.node_list = self.node_list
        self.set_namespace()

    def edit_command(self):
        '''
        edit select and deselect command
        create a new QDialog with two QTextEdit inputs
        '''
        self.dialog_command = QtWidgets.QDialog(parent=self.graphics_view)
        title = 'Edit Command'
        size = (412, 440)

        self.dialog_command.setWindowTitle(title)
        self.dialog_command.resize(QtCore.QSize(*size))
        self.dialog_command.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        vertical_layout = QtWidgets.QVBoxLayout()
        self.dialog_command.setLayout(vertical_layout)

        label_select = QtWidgets.QLabel(parent=self.dialog_command, text='Select command:')
        self.text_edit_select = LNTextEdit(parent=self.dialog_command)
        self.text_edit_select.setText(self.command_select)

        label_deselect = QtWidgets.QLabel(parent=self.dialog_command, text='Deselect command:')
        self.text_edit_deselect = LNTextEdit(parent=self.dialog_command)
        self.text_edit_deselect.setText(self.command_deselect)

        dialog_button = QtWidgets.QDialogButtonBox(parent=self.dialog_command)
        dialog_button.setStandardButtons(dialog_button.Save
                                         | dialog_button.Cancel)
        dialog_button.accepted.connect(self.save_edit_command)
        dialog_button.rejected.connect(self.dialog_command.close)

        vertical_layout.addWidget(label_select)
        vertical_layout.addWidget(self.text_edit_select)
        vertical_layout.addWidget(label_deselect)
        vertical_layout.addWidget(self.text_edit_deselect)
        vertical_layout.addWidget(dialog_button)

        self.dialog_command.show()

    def save_edit_command(self):
        '''
        save and apply command strings from edit command dialog
        apply to PixmapItem button
        apply to ButtonData
        close edit command dialog
        '''
        self.command_select = self.text_edit_select.getText()
        self.command_deselect = self.text_edit_deselect.getText()

        self.button_data.command_select = self.command_select
        self.button_data.command_deselect = self.command_deselect

        self.dialog_command.close()


class LNTextEdit(QtWidgets.QFrame):
    '''
    PySide2 implementation of:
    https://nachtimwald.com/2009/08/19/better-qplaintextedit-with-line-numbers/
    '''

    class NumberBar(QtWidgets.QWidget):

        def __init__(self, edit):
            QtWidgets.QWidget.__init__(self, edit)

            self.edit = edit
            self.adjustWidth(1)

        def paintEvent(self, event):
            self.edit.numberbarPaint(self, event)
            QtWidgets.QWidget.paintEvent(self, event)

        def adjustWidth(self, count):
            width = self.fontMetrics().width(str(count))
            if self.width() != width:
                self.setFixedWidth(width)

        def updateContents(self, rect, scroll):
            if scroll:
                self.scroll(0, scroll)
            else:
                # It would be nice to do
                # self.update(0, rect.y(), self.width(), rect.height())
                # But we can't because it will not remove the bold on the
                # current line if word wrap is enabled and a new block is
                # selected.
                self.update()


    class PlainTextEdit(QtWidgets.QPlainTextEdit):

        def __init__(self, *args):
            QtWidgets.QPlainTextEdit.__init__(self, *args)

            # self.setFrameStyle(QFrame.NoFrame)

            self.setFrameStyle(QtWidgets.QFrame.NoFrame)
            self.highlight()
            # self.setLineWrapMode(QPlainTextEdit.NoWrap)

            self.cursorPositionChanged.connect(self.highlight)

        def highlight(self):
            hi_selection = QtWidgets.QTextEdit.ExtraSelection()

            hi_selection.format.setBackground(self.palette().alternateBase())
            hi_selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
            hi_selection.cursor = self.textCursor()
            hi_selection.cursor.clearSelection()

            self.setExtraSelections([hi_selection])

        def numberbarPaint(self, number_bar, event):
            font_metrics = self.fontMetrics()
            current_line = self.document().findBlock(self.textCursor().position()).blockNumber() + 1

            block = self.firstVisibleBlock()
            line_count = block.blockNumber()
            painter = QtGui.QPainter(number_bar)
            painter.fillRect(event.rect(), self.palette().base())

            # Iterate over all visible text blocks in the document.
            while block.isValid():
                line_count += 1
                block_top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()

                # Check if the position of the block is out side of the visible
                # area.
                if not block.isVisible() or block_top >= event.rect().bottom():
                    break

                # We want the line number for the selected line to be bold.
                if line_count == current_line:
                    font = painter.font()
                    font.setBold(True)
                    painter.setFont(font)
                else:
                    font = painter.font()
                    font.setBold(False)
                    painter.setFont(font)

                # Draw the line number right justified at the position of the line.
                paint_rect = QtCore.QRect(0, block_top, number_bar.width(), font_metrics.height())
                painter.drawText(paint_rect, QtCore.Qt.AlignRight, str(line_count))

                block = block.next()
            painter.end()

    def __init__(self, parent, *args):
        QtWidgets.QFrame.__init__(self, parent=parent, *args)

        self.setFrameStyle(QtWidgets.QFrame.StyledPanel | QtWidgets.QFrame.Sunken)

        self.edit = self.PlainTextEdit()
        self.number_bar = self.NumberBar(self.edit)

        hbox = QtWidgets.QHBoxLayout(self)
        hbox.setSpacing(0)
        hbox.setMargin(0)
        hbox.addWidget(self.number_bar)
        hbox.addWidget(self.edit)

        self.edit.blockCountChanged.connect(self.number_bar.adjustWidth)
        self.edit.updateRequest.connect(self.number_bar.updateContents)

    def getText(self):
        return str(self.edit.toPlainText())

    def setText(self, text):
        self.edit.setPlainText(text)

    def isModified(self):
        return self.edit.document().isModified()

    def setModified(self, modified):
        self.edit.document().setModified(modified)

    def setLineWrapMode(self, mode):
        self.edit.setLineWrapMode(mode)


test_ui = MainWindow()
test_ui.setAttribute(QtCore.Qt.WA_DeleteOnClose)
test_ui.show()
