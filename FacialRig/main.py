import os
import sys
import RLPy
import math

import PySide2
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2 import QtWidgets
from PySide2.QtWidgets import QWidget, QAbstractItemView 
from PySide2.QtWidgets import QMenu, QAction
from PySide2.QtWidgets import QTreeWidgetItem, QTreeWidget, QTreeView, QTableWidget, QComboBox
from PySide2.shiboken2 import wrapInstance

rl_py_timer = None
timer_callback = None

jcm_manager_dlg = None

event_list = []

avatar = RLPy.RScene.FindObject(RLPy.EObjectType_Avatar, "Motion_Dummy_Female")

skeleton_bones = avatar.GetSkeletonComponent().GetSkinBones()
motion_bones = avatar.GetSkeletonComponent().GetMotionBones()
morph_component = avatar.GetMorphComponent()

print (type(avatar))

class RLPyTimerCallback(RLPy.RPyTimerCallback):
    def __init__(self):
        RLPy.RPyTimerCallback.__init__(self)
        self.time_timeout_func = None
        
    def Timeout(self):
        self.time_timeout_func()
        
    def register_time_out(self, func):
        self.time_timeout_func = func
        
def update_skeleton():
    print ("update_skeleton")

        
class JcmWidget(QWidget):
    global rl_py_timer
    global timer_callback
    def __init__(self):
        super().__init__()
        self.button_apply = QtWidgets.QPushButton("Apply Joint Ccontrol Morph")
        self.button_cancel = QtWidgets.QPushButton("Cancel")
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.button_apply)
        self.layout.addWidget(self.button_cancel)
        
        self.setLayout(self.layout)
        
        self.button_apply.clicked.connect(self.apply)
        self.button_cancel.clicked.connect(self.cancel)
        
    def apply(self):
        #rl_py_timer.Start()
        self.propA = RLPy.RScene.FindObject( RLPy.EObjectType_Prop, "Ball_000" )
        self.propB = RLPy.RScene.FindObject( RLPy.EObjectType_Prop, "Ball_000(0)" )
        
        control = self.propA.GetControl("Transform")
        controlb = self.propB.GetControl("Transform")
        
        #transform_key = RLPy.RTransformKey()
        
        rts = RLPy.RTransform( RLPy.RTransform.IDENTITY )
        ret = control.GetValue(RLPy.RGlobal.GetTime(), rts)
        
        rtsb = RLPy.RTransform( RLPy.RTransform.IDENTITY )
        retb = controlb.GetValue(RLPy.RGlobal.GetTime(), rtsb)
        
        #test = [ math.degrees(rts.R().x), math.degrees(rts.R().y), math.degrees(rts.R().z) ]
        #print ((rts.R().ToEulerAngle(0,0,0,0)))
        #aaa = RLPy.RMatrix3.ToEulerAngle(rts.R())
        #print(test)
        test = rts.R().ToRotationMatrix().ToEulerAngle(0,0,0,0)
        
        testb = rtsb.R().ToRotationMatrix().ToEulerAngle(0,0,0,0)
        
        test2 = [ math.degrees(test[0]), math.degrees(test[1]), math.degrees(test[2]) ]
        test2b = [ math.degrees(testb[0]), math.degrees(testb[1]), math.degrees(testb[2]) ]
        
        
        aa = [rts.T().x, rts.T().y, rts.T().z]
        bb = [rtsb.T().x, rtsb.T().y, rtsb.T().z]
        
        print (test2)
        
        print (aa)
        print (bb)
        
        print (math.degrees(self.angle(aa,bb)))
        #print (self.propA.LocalTransform().T())
        #print (self.propA.LocalTransform().R())
    
    def cancel(self):
        #rl_py_timer.Stop()
        pass
    
    def dotproduct(self, v1, v2):
        return sum((a*b) for a, b in zip(v1, v2))

    def length(self, v):
        return math.sqrt(self.dotproduct(v, v))
    
    def angle(self, v1, v2):
        return math.acos(self.dotproduct(v1, v2) / (self.length(v1) * self.length(v2)))
        
def run_script():
    global rl_py_timer
    global timer_callback
    
    #rl_py_timer = RLPy.RPyTimer()
    #rl_py_timer.SetInterval( 100 )
    #timer_callback = RLPyTimerCallback()
    #rl_py_timer.RegisterPyTimerCallback(timer_callback) 
    #timer_callback.register_time_out(update_skeleton)
    
    global jcm_manager_dlg

    jcm_manager_dlg = RLPy.RUi.CreateRDialog()
    jcm_manager_dlg.SetWindowTitle("Joint Control Morph")
    
    main_pyside_dlg = wrapInstance(int(jcm_manager_dlg.GetWindow()), PySide2.QtWidgets.QDialog)
    main_pyside_layout = main_pyside_dlg.layout()
    
    jcm_manager_widget = JcmWidget()

    main_pyside_layout.addWidget(jcm_manager_widget)
    main_pyside_dlg.adjustSize()
    
    jcm_manager_dlg.Show()
    
    
    