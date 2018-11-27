import os
import sys
import RLPy
import math

import PySide2
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import QWidget, QAbstractItemView 
from PySide2.QtWidgets import QMenu, QAction
from PySide2.QtWidgets import QTreeWidgetItem, QTreeWidget, QTreeView
from PySide2.shiboken2 import wrapInstance

app = PySide2.QtWidgets.QApplication.instance()
if not app:
    app = PySide2.QtWidgets.QApplication([])

layer_manger_dlg = None
rl_event = None

# Callback
mocap_event_callback = None
#bool
IsRegister = False
X_Bool = False
Y_Bool = False
Z_Bool = False
#ObjVector3
transform_Vector3 = None
camera_Vector3 = None


def global_get_avatars(active):
    avatar_list = []
    if active:
        avatar_type = RLPy.EAvatarType_Standard | RLPy.EAvatarType_NonStandard | RLPy.EAvatarType_StandardSeries
        avatar_list = RLPy.RGlobal.GetAvatars(avatar_type)
    return avatar_list

def global_get_props(active):
    prop_list = []
    if active:
        prop_list = RLPy.RGlobal.GetProps()
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

#Todo Reload
class MocapEventCallback(RLPy.REventCallback):
    def __init__(self):
        RLPy.REventCallback.__init__(self)

    def OnObjectSelectionChanged(self):
        open_Viwer()   
    
class LayerManagerTreeWidget(QTreeWidget):
    def __init__(self):
        super().__init__()

        self.setHeaderHidden(True)        
        self.setContextMenuPolicy(Qt.CustomContextMenu)        
        self.viewport().setAcceptDrops(True)
        self.items_dict = {}         
        self.default_item = QTreeWidgetItem()
        self.default_item2 = QTreeWidgetItem()
        self.default_item.setText(0, "Avatar")
        self.default_item2.setText(0, "Prop")
        self.items_dict["0(default)"] = {}
        self.items_dict["0(default)"]["0(default)"] = self.default_item
        self.items_dict["0(default)"]["1(default)"] = self.default_item2
        self.addTopLevelItem(self.default_item)
        self.addTopLevelItem(self.default_item2)        
        self.default_item.setFlags(self.default_item.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
        self.default_item2.setFlags(self.default_item2.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)        
        self.scene_objects = global_get_avatars(True)
        self.scene_objects2 = global_get_props(True)

        #Avatars
        for item in self.scene_objects:        
            _name = item.GetName()
            if _name != "Shadow Catcher ": #ignore Shadow Catcher Obj
                temp_item = QTreeWidgetItem()
                temp_item.setText(0, _name)
                temp_item.setFlags(temp_item.flags() & ~Qt.ItemIsDropEnabled)
                self.items_dict["0(default)"][_name] = temp_item           
                self.default_item.addChild(temp_item)                
                temp_item.setFlags(temp_item.flags() | Qt.ItemIsUserCheckable)
        #Props
        for item in self.scene_objects2:        
            _name = item.GetName()            
            temp_item = QTreeWidgetItem()
            temp_item.setText(0, _name)
            temp_item.setFlags(temp_item.flags() & ~Qt.ItemIsDropEnabled)
            self.items_dict["0(default)"][_name] = temp_item          
            self.default_item2.addChild(temp_item)                
            temp_item.setFlags(temp_item.flags() | Qt.ItemIsUserCheckable)

        self.itemChanged.connect(self.on_item_changed)
        self.itemDoubleClicked.connect(self.on_item_selection)
    
    def on_item_changed (self, current, previous):
        for key, value in self.items_dict.items():
            for key2, value2 in self.items_dict[key].items():
                if (value2.checkState(0)==Qt.Checked):
                    print (key2 + " set visible" )
                else:
                    print (key2 + " set invisible" )
    
    def on_object_selection_changed(self):
        _selected_items = RLPy.RGlobal.GetSelectedObjects()

        for key, value in self.items_dict.items():
            for key2, value2 in self.items_dict[key].items():
                self.setItemSelected(value2, False)
            
            for i in range (len(_selected_items)):
                _name = _selected_items[i].GetName()
                if ( _name in self.items_dict[key] ):                    
                    selected_item = self.items_dict[key][_name]
                    self.setItemSelected(selected_item, True)                

    def on_item_selection(self, _items):
        global transform_Vector3
        global X_Bool
        global Y_Bool
        global Z_Bool

        avatar_Clicked = RLPy.RScene.FindObject( RLPy.EObjectType_Avatar | RLPy.EObjectType_Prop, _items.text( 0 ) )

        if(avatar_Clicked != None):
            #Get Transform
            transform_control = None;
            transform_control = avatar_Clicked.GetControl("Transform")     
            transform_Vector3 = RLPy.RTransform.IDENTITY
            transform_control.GetValue(RLPy.RGlobal.GetTime(),transform_Vector3)

            #Camera
            camera = RLPy.RScene.FindObject( RLPy.EObjectType_Camera, "Camera" )
            time = RLPy.RGlobal.GetTime()

            #Move_Current
            transform_Vector3.T().z += (transform_Vector3.S().z*100)/2
            transform_Vector3.T().y -= ((transform_Vector3.S().z*100)+(transform_Vector3.S().y*100)/2)*5
            camera.GetControl("Transform").GetDataBlock().GetControl('Rotation/RotationX').SetValue(time, (95/180)*3.14) #180 = 3.14
            camera.GetControl("Transform").GetDataBlock().GetControl('Rotation/RotationY').SetValue(time, 0) 
            camera.GetControl("Transform").GetDataBlock().GetControl('Rotation/RotationZ').SetValue(time, 0)

            #Do_Move_Animation
            X_Bool = False
            Y_Bool = False
            Z_Bool = False
            timer_callback.register_time_out(self.MoveAnimation)
            rl_py_timer.Start()

    #DoTimer
    def MoveAnimation(self):
        global timer
        global camera_Vector3
        global transform_Vector3

        #Current Vector3
        camera = RLPy.RScene.FindObject( RLPy.EObjectType_Camera, "Camera" ).GetControl("Transform")
        camera_Vector3 = RLPy.RTransform(RLPy.RTransform.IDENTITY)
        camera.GetValue(RLPy.RGlobal.GetTime(),camera_Vector3)

        #Move
        self.MoveVecor3(transform_Vector3.T().y,camera_Vector3.T().y,"Y")
        self.MoveVecor3(transform_Vector3.T().z,camera_Vector3.T().z,"Z")
        self.MoveVecor3(transform_Vector3.T().x,camera_Vector3.T().x,"X")
        camera.SetValue(RLPy.RGlobal.GetTime(), camera_Vector3)  

    def MoveVecor3(self,pos_obj,pos_camera,xyz):       
        global camera_Vector3
        global X_Bool
        global Y_Bool
        global Z_Bool

        if(xyz=="X"):
            if(pos_obj > pos_camera and RLPy.RMath.Abs(pos_obj-pos_camera)>=2):
                camera_Vector3.T().x += RLPy.RMath.Abs(pos_obj-pos_camera)/30
            elif (pos_obj < pos_camera and RLPy.RMath.Abs(pos_obj-pos_camera)>=2):
                camera_Vector3.T().x -= RLPy.RMath.Abs(pos_obj-pos_camera)/30
            else:
                X_Bool = True 

        elif (xyz=="Y"):
            if(pos_obj > pos_camera and RLPy.RMath.Abs(pos_obj-pos_camera)>=2):
                camera_Vector3.T().y += RLPy.RMath.Abs(pos_obj-pos_camera)/30
            elif (pos_obj < pos_camera and RLPy.RMath.Abs(pos_obj-pos_camera)>=2):
                camera_Vector3.T().y -= RLPy.RMath.Abs(pos_obj-pos_camera)/30
            else:
               Y_Bool = True

        else :
            #"Z"
            if(pos_obj > pos_camera and RLPy.RMath.Abs(pos_obj-pos_camera)>=2):
                camera_Vector3.T().z += RLPy.RMath.Abs(pos_obj-pos_camera)/30
            elif (pos_obj < pos_camera and RLPy.RMath.Abs(pos_obj-pos_camera)>=2):
                camera_Vector3.T().z -= RLPy.RMath.Abs(pos_obj-pos_camera)/30
            else:
               Z_Bool = True

        if(X_Bool and Y_Bool and Z_Bool):
            rl_py_timer.Stop()

#TImerRegister
class RLPyTimerCallback(RLPy.RPyTimerCallback):
    def __init__(self):
        RLPy.RPyTimerCallback.__init__(self)
        self.time_timeout_func = None
    
    def Timeout(self):
        self.time_timeout_func()
        
    def register_time_out(self, func):
        self.time_timeout_func = func


rl_py_timer=RLPy.RPyTimer()
rl_py_timer.SetInterval(2)
timer_callback = RLPyTimerCallback()
rl_py_timer.RegisterPyTimerCallback(timer_callback)

def open_Viwer(): 
    global layer_manager_dlg

    layer_manager_dlg = RLPy.RUi.CreateRDialog()
    layer_manager_dlg.SetWindowTitle("EZLook")

    main_pyside_dlg = wrapInstance(int(layer_manager_dlg.GetWindow()), PySide2.QtWidgets.QDialog)
    main_pyside_layout = main_pyside_dlg.layout()
    
    layer_manager_tree_widget = LayerManagerTreeWidget()

    main_pyside_layout.addWidget(layer_manager_tree_widget)
    main_pyside_dlg.adjustSize()

    layer_manager_dlg.Show()


    global IsRegister
    if(not IsRegister):
        #register_event
        global mocap_event_callback
        mocap_event_callback = MocapEventCallback()
        RLPy.REventHandler.RegisterCallback(mocap_event_callback)
        IsRegister = True




