# Copyright 2018 The Reallusion Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

import RLPy
from PySide2 import QtWidgets
from PySide2.QtCore import Qt
from PySide2.shiboken2 import wrapInstance

#create main dialog
layer_manger_dlg = None

class LayerManagerTreeWidget(QtWidgets.QTreeWidget):
    def __init__(self):
        super().__init__()
        
        #-----QTreeWidget Property settings-----
        self.setHeaderHidden(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.viewport().setAcceptDrops(True)
        
        #-----Bind context menu event to self.context_menu_requested-----
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.context_menu_requested)
        
        #-----Get all avatar / prop / camera / light-----
        self.scene_objects = RLPy.RScene.FindObjects( RLPy.EObjectType_Avatar | RLPy.EObjectType_Prop | RLPy.EObjectType_Light | RLPy.EObjectType_Camera )
        self.items_dict = {} 

        #-----QTreeWidgetItem Property settings-----
        self.default_item = QtWidgets.QTreeWidgetItem()
        self.default_item.setText(0, "Group_0")
        self.items_dict["Group_0"] = {}
        self.items_dict["Group_0"]["Group_0"] = self.default_item
        self.default_item.setCheckState(0,Qt.Checked)
        self.addTopLevelItem(self.default_item)
        self.default_item.setFlags(self.default_item.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
        
        #-----Create item for all scene objects-----
        for item in self.scene_objects:
            _name = item.GetName()
            temp_item = QtWidgets.QTreeWidgetItem()
            temp_item.setText(0, _name)
            temp_item.setCheckState(0,Qt.Checked)
            temp_item.setFlags(temp_item.flags() & ~Qt.ItemIsDropEnabled)

            self.items_dict["Group_0"][_name] = temp_item
            self.default_item.addChild(temp_item)
            #self.default_item.removeChild(temp_item)
            temp_item.setFlags(temp_item.flags() | Qt.ItemIsUserCheckable)

        self.itemChanged.connect(self.on_item_changed)
        
    def dropEvent(self, evt):
        item = self.itemAt(evt.pos())
        super().dropEvent(evt)
        #print (item)
        print (self.default_item.childCount())
        #self.default_item.addChild(self.items_dict["Group_0"]["Ball_000"])
        #self.clear()
        #self.insertTopLevelItems(1,self.default_item)

    
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
                
    def context_menu_requested(self, pos):
        _menu = QtWidgets.QMenu()
        _item = self.itemAt(pos)
        if _item:
            action = QtWidgets.QAction('Delete Group', self)
            action.triggered.connect(lambda: self.remove_item(_item))
            _menu.addAction(action)
        else:
            action = QtWidgets.QAction('Create Group', self)
            action.triggered.connect(self.create_new_layer)
            _menu.addAction(action)
        _menu.exec_(self.mapToGlobal(pos))

    def create_new_layer(self):
        item = QtWidgets.QTreeWidgetItem()
        layer_name = 'Group_'+str(len(self.items_dict))
        
        for k,v in self.items_dict.items():
            if (k == layer_name):
                layer_name = 'Group_'+str(len(self.items_dict)+1)
        
        item.setText(0, layer_name)
        item.setCheckState(0,Qt.Checked)

        item.setFlags(item.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable | Qt.ItemIsEditable )

        self.addTopLevelItem(item)
        self.items_dict[layer_name] = {}
        self.items_dict[layer_name][layer_name] = item

    def remove_item(self, item):
    
        if (item.text(0) == "Group_0"):
            return
    
        parent = item.parent()
        
        if (item.childCount() == 0 ):
            parent.takeChild(parent.indexOfChild(item))
        else:
            child_list = []
            for i in range(item.childCount()):
                #print(item.child(i))
                temp_item = item.child(i)
                child_list.append(temp_item)
                
            for child in child_list:
                item.removeChild(child)
                self.default_item.addChild(child)
            self.takeTopLevelItem(self.indexOfTopLevelItem(item))
            
            try:
                parent.takeChild(parent.indexOfChild(item))
            except:
                pass

        
def run_script(): 
    global layer_manager_dlg
    layer_manager_tree_widget = LayerManagerTreeWidget()
    
    layer_manager_dlg = RLPy.RUi.CreateRDockWidget()
    layer_manager_dlg.SetWindowTitle("Group Manager")
    
    main_pyside_dlg = wrapInstance(int(layer_manager_dlg.GetWindow()), QtWidgets.QDockWidget)
    
    main_widget = QtWidgets.QWidget()
    
    main_pyside_dlg.setWidget(main_widget)
    
    main_widget_layout = QtWidgets.QVBoxLayout()
    
    main_widget.setLayout(main_widget_layout)
    
    
    label = QtWidgets.QLabel()
    label.setText("Right click on an empty area to create a new Group.\nYou can drag the nodes to assign Groups.\nDouble-click on the Group label to rename the Group.")
    
    main_widget_layout.addWidget(label)
    main_widget_layout.addWidget(layer_manager_tree_widget)
    
    layer_manager_dlg.Show()
    
