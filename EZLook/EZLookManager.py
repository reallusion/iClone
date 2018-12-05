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

EZLook_event_callback = None
IsRegister = False
is_x_arrive = False
is_y_arrive = False
is_z_arrive = False
object_transform = None
camera_transform = None
camera = None;


#register timer event
class RLPyTimerCallback(RLPy.RPyTimerCallback):
    def __init__(self):
        RLPy.RPyTimerCallback.__init__(self)
        self.time_timeout_func = None
    
    def Timeout(self):
        if self.time_timeout_func:
            self.time_timeout_func()
        
    def register_time_out(self, func):
        self.time_timeout_func = func

rl_py_timer=RLPy.RPyTimer()
rl_py_timer.SetInterval(2)
timer_callback = RLPyTimerCallback()
rl_py_timer.RegisterPyTimerCallback(timer_callback)

#register EZLook event
class EZLookEventCallback(RLPy.REventCallback):
    def __init__(self):
        RLPy.REventCallback.__init__(self)

    def OnObjectSelectionChanged(self):
        open_Viwer()


def open_Viwer(): 
    #set dialog
    global layer_manager_dlg
    layer_manager_dlg = RLPy.RUi.CreateRDialog()
    layer_manager_dlg.SetWindowTitle("EZLook")
    main_pyside_dlg = wrapInstance(int(layer_manager_dlg.GetWindow()), PySide2.QtWidgets.QDialog)
    main_pyside_layout = main_pyside_dlg.layout()    
    layer_manager_tree_widget = LayerManagerTreeWidget()
    main_pyside_layout.addWidget(layer_manager_tree_widget)
    main_pyside_dlg.adjustSize()
    layer_manager_dlg.Show()
    #register EZLook event
    global IsRegister
    if(not IsRegister):
        global EZLook_event_callback
        EZLook_event_callback = EZLookEventCallback()
        RLPy.REventHandler.RegisterCallback(EZLook_event_callback)
        IsRegister = True

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
        self.all_avatars = global_get_avatars(True)
        self.all_props = global_get_props(True)

        #set avatars menu item
        for item in self.all_avatars:        
            _name = item.GetName()            
            temp_item = QTreeWidgetItem()
            temp_item.setText(0, _name)            
            self.items_dict["0(default)"][_name] = temp_item           
            self.default_item.addChild(temp_item)                

        #set props menu item
        for item in self.all_props:      
            _name = item.GetName()
            if _name != "Shadow Catcher ": #ignore Shadow Catcher Obj
                temp_item = QTreeWidgetItem()
                temp_item.setText(0, _name)                
                self.items_dict["0(default)"][_name] = temp_item          
                self.default_item2.addChild(temp_item)              

        #double click menu item
        self.itemDoubleClicked.connect(self.on_item_selection)
    
    def on_item_selection(self, _items):        
        global camera
        global is_x_arrive
        global is_y_arrive
        global is_z_arrive
        global object_transform;
        #set object
        object_Clicked = RLPy.RScene.FindObject(RLPy.EObjectType_Avatar | RLPy.EObjectType_Prop, _items.text(0))
        #set camera    
        camera_list = RLPy.RScene.FindObjects(RLPy.EObjectType_Camera)
        camera = camera_list[0] if(len(camera_list)>0) else None
        #set time
        time = RLPy.RGlobal.GetTime()

        if(object_Clicked != None and camera!= None):
            #get object transform and find final position
            object_transform = object_Clicked.WorldTransform();
            object_transform.T().z += (object_transform.S().z*100)/2
            object_transform.T().y -= ((object_transform.S().z*100)+(object_transform.S().y*100)/2)*5
            #set camera rotation
            camera.GetControl("Transform").GetDataBlock().GetControl('Rotation/RotationX').SetValue(time, self.AngularTransform(95))
            camera.GetControl("Transform").GetDataBlock().GetControl('Rotation/RotationY').SetValue(time, 0) 
            camera.GetControl("Transform").GetDataBlock().GetControl('Rotation/RotationZ').SetValue(time, 0)
            #reset boolean
            is_x_arrive = False
            is_y_arrive = False
            is_z_arrive = False
            #start timer function
            timer_callback.register_time_out(self.MoveAnimation)
            rl_py_timer.Start()   

    def AngularTransform(self, degrees):
        AngularValue = (degrees/180)* RLPy.RMath.CONST_PI
        return AngularValue

    def MoveAnimation(self):
        global timer
        global camera
        global camera_transform
        global object_transform
        #get camera transform
        camera_control = camera.GetControl("Transform")
        camera_transform = RLPy.RTransform(RLPy.RTransform.IDENTITY)
        camera_control.GetValue(RLPy.RGlobal.GetTime(), camera_transform)
        #do MoveAnimation
        self.DoMoveAnimation(object_transform.T().y, camera_transform.T().y, "Y")
        self.DoMoveAnimation(object_transform.T().z, camera_transform.T().z, "Z")
        self.DoMoveAnimation(object_transform.T().x, camera_transform.T().x, "X")
        #set camera position
        camera_control.SetValue(RLPy.RGlobal.GetTime(), camera_transform) 

    def DoMoveAnimation(self, pos_obj, pos_camera, xyz):       
        global camera_transform
        global is_x_arrive
        global is_y_arrive
        global is_z_arrive

        distance = RLPy.RMath.Abs(pos_obj-pos_camera)
        is_far_away = True if(distance>=2) else False
        speed = 30

        if(xyz=="X"):
            if(pos_obj > pos_camera and is_far_away):
                camera_transform.T().x += distance/speed
            elif (pos_obj < pos_camera and is_far_away):
                camera_transform.T().x -= distance/speed
            else:
                is_x_arrive = True 

        elif (xyz=="Y"):
            if(pos_obj > pos_camera and is_far_away):
                camera_transform.T().y += distance/speed
            elif (pos_obj < pos_camera and is_far_away):
                camera_transform.T().y -= distance/speed
            else:
               is_y_arrive = True

        else :
            #"Z"
            if(pos_obj > pos_camera and is_far_away):
                camera_transform.T().z += distance/speed
            elif (pos_obj < pos_camera and is_far_away):
                camera_transform.T().z -= distance/speed
            else:
               is_z_arrive = True

        #if XYZ arrived to stop timer
        if(is_x_arrive and is_y_arrive and is_z_arrive):
            rl_py_timer.Stop()
    



