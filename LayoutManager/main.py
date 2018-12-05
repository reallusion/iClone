import os
import sys
import RLPy
import PySide2
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import QWidget, QAbstractItemView 
from PySide2.QtWidgets import QMenu, QAction
from PySide2.QtWidgets import QTreeWidgetItem, QTreeWidget, QTreeView
from PySide2.shiboken2 import wrapInstance

layer_manger_dlg = None

rl_event = None

def global_get_avatars(active):
    avatar_list = []
    if active:
        avatar_type = RLPy.EAvatarType_Standard | RLPy.EAvatarType_NonStandard | RLPy.EAvatarType_StandardSeries
        avatar_list = RLPy.RScene.GetAvatars(avatar_type)
    return avatar_list

def global_get_props(active):
    prop_list = []
    if active:
        prop_list = RLPy.RScene.GetProps()
    return prop_list
        
class REventListenerCallback(RLPy.REventCallback):
    def __init__(self):
        RLPy.REventCallback.__init__(self)
        self.on_object_selection_changed = None
            
    def on_object_selection_changed(self):
        if self.on_object_selection_changed != None:
            self.on_object_selection_changed()

    def register_on_object_selection_changed(self, _evt):
        self.on_object_selection_changed = _evt

    
class LayerManagerTreeWidget(QTreeWidget):
    def __init__(self):
        super().__init__()

        self.setHeaderHidden(True)
        
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.context_menu_requested)

        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        
        self.viewport().setAcceptDrops(True)
        
        global rl_event
        rl_event = REventListenerCallback()
        rl_event.register_on_object_selection_changed(self.on_object_selection_changed)
        id = RLPy.REventHandler.RegisterCallback(rl_event)
        
        self.items_dict = {} 
        
        self.default_item = QTreeWidgetItem()
        self.default_item.setText(0, "0(default)")
        self.items_dict["0(default)"] = {}
        self.items_dict["0(default)"]["0(default)"] = self.default_item
        self.default_item.setCheckState(0,Qt.Checked)
        self.addTopLevelItem(self.default_item)
        
        self.default_item.setFlags(self.default_item.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
        
        self.scene_objects = global_get_avatars(True) + global_get_props(True)

        for item in self.scene_objects:
        
            _name = item.GetName()
            
            temp_item = QTreeWidgetItem()
            temp_item.setText(0, _name)
            temp_item.setCheckState(0,Qt.Checked)
            temp_item.setFlags(temp_item.flags() & ~Qt.ItemIsDropEnabled)

            self.items_dict["0(default)"][_name] = temp_item
            
            self.default_item.addChild(temp_item)
            
            temp_item.setFlags(temp_item.flags() | Qt.ItemIsUserCheckable)

        self.itemChanged.connect(self.on_item_changed)
    
    def on_item_changed (self, current, previous):
        for key, value in self.items_dict.items():

            for key2, value2 in self.items_dict[key].items():
                if (value2.checkState(0)==Qt.Checked):
                    for item in self.scene_objects:
                        _name = item.GetName()
                        if (_name == key2):
                            RLPy.RScene.Show(item)
                else:
                    for item in self.scene_objects:
                        _name = item.GetName()
                        if (_name == key2):
                            RLPy.RScene.Hide(item)
    
    def on_object_selection_changed(self):
        _selected_items = RLPy.RScene.GetSelectedObjects()

        for key, value in self.items_dict.items():
            for key2, value2 in self.items_dict[key].items():
                self.setItemSelected(value2, False)
            
            for i in range (len(_selected_items)):
                _name = _selected_items[i].GetName()
                if ( _name in self.items_dict[key] ):
                    selected_item = self.items_dict[key][_name]
                    self.setItemSelected(selected_item, True)
                
    def context_menu_requested(self, pos):
        _menu = QMenu()
        _item = self.itemAt(pos)
        if _item:
            action = QAction('Delete Item', self)
            action.triggered.connect(lambda: self.remove_item(_item))
            _menu.addAction(action)
        else:
            action = QAction('Create Layer', self)
            action.triggered.connect(self.create_new_layer)
            _menu.addAction(action)
        _menu.exec_(self.mapToGlobal(pos))

    def create_new_layer(self):
        item = QTreeWidgetItem()
        item.setText(0, 'Layer001')
        item.setCheckState(0,Qt.Unchecked)

        item.setFlags(item.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable | Qt.ItemIsEditable )

        self.addTopLevelItem(item)
        self.items_dict["Layer001"] = {}
        self.items_dict["Layer001"]["Layer001"] = item
        
    def remove_item(self, item):
        parent = item.parent()
        if parent:
            parent.takeChild(parent.indexOfChild(item))
        else:
            self.takeTopLevelItem(self.indexOfTopLevelItem(item))
            

def run_script(): 
    global layer_manager_dlg

    layer_manager_dlg = RLPy.RUi.CreateRDialog()
    layer_manager_dlg.SetWindowTitle("Layer Manager")

    main_pyside_dlg = wrapInstance(int(layer_manager_dlg.GetWindow()), PySide2.QtWidgets.QDialog)
    main_pyside_layout = main_pyside_dlg.layout()
    
    layer_manager_tree_widget = LayerManagerTreeWidget()

    main_pyside_layout.addWidget(layer_manager_tree_widget)
    main_pyside_dlg.adjustSize()

    layer_manager_dlg.Show()
    
