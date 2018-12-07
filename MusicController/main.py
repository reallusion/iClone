import os
import sys
import math
import RLPy
import PySide2
from PySide2.QtMultimedia import QSound
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2 import QtWidgets, QtGui
from PySide2.QtWidgets import QWidget, QAbstractItemView 
from PySide2.QtWidgets import QMenu, QAction, QPushButton
from PySide2.QtWidgets import QTreeWidgetItem, QTreeWidget, QTreeView, QTableWidget, QComboBox
from PySide2.shiboken2 import wrapInstance

music_control_widget = None

class KeyControlButton(QPushButton):
    def __init__(self, text, wav, key_prop, parent):
        super().__init__(text)
        self.text = text
        self.parent = parent
        self.parent.addWidget(self)
        self.clicked.connect(self.play)
        self.key_prop = key_prop
        
        self.hot_key_address = RLPy.RUi.AddHotKey(self.text)
        self.hot_key_action = wrapInstance(int(self.hot_key_address), PySide2.QtWidgets.QAction)
        self.hot_key_action.triggered.connect(self.play)
        
        self.audio_path = os.path.dirname(os.path.abspath(__file__))+"\\wav\\"+ wav+".wav"
    
    def mousePressEvent(self, event):
        print ("mousePressEvent")
        self.play()
    
    def mouseReleaseEvent(self, event):
        print ("mouseReleaseEvent")
        self.stop()
    
    def play(self):
        control = self.key_prop.GetControl("Transform")
        prop_transform = self.key_prop.LocalTransform()
        
        prop_transform.R().SetX(0.035)
        prop_transform.R().SetY(0)
        prop_transform.R().SetZ(0)
        prop_transform.R().SetW(1)

        key = RLPy.RTransformKey()
        key.SetTime(RLPy.RGlobal.GetTime())
        key.SetTransform(prop_transform)
        control.AddKey(key, RLPy.RGlobal.GetFps())
        
        QSound.play(self.audio_path)
        
    def stop(self):
        control = self.key_prop.GetControl("Transform")
        prop_transform = self.key_prop.LocalTransform()
        
        prop_transform.R().SetX(0)
        prop_transform.R().SetY(0)
        prop_transform.R().SetZ(0)
        prop_transform.R().SetW(0)

        key = RLPy.RTransformKey()
        key.SetTime(RLPy.RGlobal.GetTime())
        key.SetTransform(prop_transform)
        control.AddKey(key, RLPy.RGlobal.GetFps())
        
class MusicController(QWidget):
    def __init__(self):
        super().__init__()
        
        self.layout = QtWidgets.QHBoxLayout()

        self.keyA_prop = RLPy.RScene.FindObject(RLPy.EObjectType_Prop, "Key_A")
        self.keyB_prop = RLPy.RScene.FindObject(RLPy.EObjectType_Prop, "Key_B")
        self.keyC_prop = RLPy.RScene.FindObject(RLPy.EObjectType_Prop, "Key_C")
        self.keyD_prop = RLPy.RScene.FindObject(RLPy.EObjectType_Prop, "Key_D")
        self.keyE_prop = RLPy.RScene.FindObject(RLPy.EObjectType_Prop, "Key_E")
        
        self.button_a = KeyControlButton("A", "do", self.keyA_prop, self.layout)
        self.button_s = KeyControlButton("S", "re", self.keyB_prop, self.layout)
        self.button_d = KeyControlButton("D", "mi", self.keyC_prop, self.layout)
        self.button_f = KeyControlButton("F", "fa", self.keyD_prop, self.layout)
        self.button_g = KeyControlButton("G", "so", self.keyE_prop, self.layout)
        
        self.setLayout(self.layout)
    
def run_script():
    # global music_control_widget
    # music_control_widget = MusicController()
    # music_control_widget.show()
    
    global music_controller_dlg
    music_controller_widget = MusicController()
    
    #create RDialog
    music_controller_dlg = RLPy.RUi.CreateRDialog()
    music_controller_dlg.SetWindowTitle("Music Controller")
    #wrap RDialog to Pyside Dialog
    main_pyside_dlg = wrapInstance(int(music_controller_dlg.GetWindow()), QtWidgets.QDialog)
    main_pyside_layout = main_pyside_dlg.layout()

    main_pyside_layout.addWidget(music_controller_widget)
    main_pyside_dlg.setFixedWidth(300)
    #show dialog
    music_controller_dlg.Show()
    
    
    
    
    
