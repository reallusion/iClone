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

music_controller_widget = None

event_list = []

event_callback = None

music_controller_dlg = None
dialog_event_callback = None

class REventCallbackSampleCode(RLPy.REventCallback):
    def __init__(self):
        RLPy.REventCallback.__init__(self)
    def OnPlayed(self):
        #print('Play')
        pass
    def OnStopped(self):
        global music_controller_widget
        music_controller_widget.record()
        #print('Stop')
        

class DialogEventCallback(RLPy.RDialogCallback):
    def __init__(self):
        RLPy.RDialogCallback.__init__(self)

    def OnDialogHide(self):
        global music_controller_widget
        music_controller_widget.release_keyboard()
        global event_list
        for evt in event_list:
            RLPy.REventHandler.UnregisterCallback(evt)
        event_list = []
        pass


class KeyControlButton(QPushButton):
    def __init__(self, hokey, text, wav, key_prop, parent):
        super().__init__(text)
        self.text = text
        self.hokey = hokey
        self.parent = parent
        self.parent.addWidget(self)
        self.clicked.connect(self.play)
        self.key_prop = key_prop
        self.isPressed = False
        
        self.key_list = []
        
        self.audio_path = os.path.dirname(os.path.abspath(__file__))+"\\wav\\"+ wav+".wav"
        self.audio_object = RLPy.RAudio.CreateAudioObject()
        self.audio_object.Load(self.audio_path)
        
    def mousePressEvent(self, event):
        self.play()
    
    def mouseReleaseEvent(self, event):
        self.stop()
    
    def keyPress(self, event):
        if (event.key() == self.hokey and ~self.isPressed and event.isAutoRepeat()!=True):
            self.play()
            self.isPressed = True
    
    def keyRelease(self, event):
        if (event.key() == self.hokey and event.isAutoRepeat()!=True):
            self.stop()
            self.isPressed = False
    
    def play(self):
        control = self.key_prop.GetControl("Transform")
        prop_transform = self.key_prop.LocalTransform()
        
        prop_transform.R().SetX(0.035)
        prop_transform.R().SetY(0)
        prop_transform.R().SetZ(0)
        prop_transform.R().SetW(1)

        key = RLPy.RTransformKey()
        time = RLPy.RGlobal.GetTime()
        key.SetTime(time)
        key.SetTransform(prop_transform)
        control.AddKey(key, RLPy.RGlobal.GetFps())
        control.SetKeyTransition(time, RLPy.ETransitionType_Step, 1.0)
        
        self.key_list.append(time)
        
        #RLPy.RAudio.LoadAudioToObject(self.key_prop, self.audio_object, time)
        
        QSound.play(self.audio_path)
    
    def stop(self):
        control = self.key_prop.GetControl("Transform")
        prop_transform = self.key_prop.LocalTransform()
        
        prop_transform.R().SetX(0)
        prop_transform.R().SetY(0)
        prop_transform.R().SetZ(0)
        prop_transform.R().SetW(0)

        key = RLPy.RTransformKey()
        time = RLPy.RGlobal.GetTime()
        key.SetTime(time)
        key.SetTransform(prop_transform)
        control.AddKey(key, RLPy.RGlobal.GetFps())
        control.SetKeyTransition(time, RLPy.ETransitionType_Step, 1.0)
    
    def record(self):
        if (RLPy.RGlobal.IsPlaying() == False):
            for key_time in self.key_list:
                RLPy.RAudio.LoadAudioToObject(self.key_prop, self.audio_object, key_time)
                #pass
            #print (self.key_list)
        self.key_list = []
        
class MusicController(QWidget):
    def __init__(self):
        super().__init__()
        self.setFocusPolicy(Qt.StrongFocus)
        
        self.layout = QtWidgets.QHBoxLayout()

        self.keyC_prop = RLPy.RScene.FindObject(RLPy.EObjectType_Prop, "Key_C")
        self.keyD_prop = RLPy.RScene.FindObject(RLPy.EObjectType_Prop, "Key_D")
        self.keyE_prop = RLPy.RScene.FindObject(RLPy.EObjectType_Prop, "Key_E")
        self.keyF_prop = RLPy.RScene.FindObject(RLPy.EObjectType_Prop, "Key_F")
        self.keyG_prop = RLPy.RScene.FindObject(RLPy.EObjectType_Prop, "Key_G")
        self.keyA_prop = RLPy.RScene.FindObject(RLPy.EObjectType_Prop, "Key_A")
        self.keyB_prop = RLPy.RScene.FindObject(RLPy.EObjectType_Prop, "Key_B")

        self.button_a = KeyControlButton(49, "C", "C4", self.keyC_prop, self.layout)
        self.button_s = KeyControlButton(50, "D", "D4", self.keyD_prop, self.layout)
        self.button_d = KeyControlButton(51, "E", "E4", self.keyE_prop, self.layout)
        self.button_f = KeyControlButton(52, "F", "F4", self.keyF_prop, self.layout)
        self.button_g = KeyControlButton(53, "G", "G4", self.keyG_prop, self.layout)
        self.button_h = KeyControlButton(54, "A", "A4", self.keyA_prop, self.layout)
        self.button_j = KeyControlButton(55, "B", "B4", self.keyB_prop, self.layout)
        
        self.setLayout(self.layout)
    
        self.grabKeyboard()
    
    def record(self):
        self.button_a.record()
        self.button_s.record()
        self.button_d.record()
        self.button_f.record()
        self.button_g.record()
        self.button_h.record()
        self.button_j.record()
    
    def release_keyboard(self):
        print ("release_keyboard")
        self.releaseKeyboard()
    
    def keyPressEvent(self, event):
        self.button_a.keyPress(event)
        self.button_s.keyPress(event)
        self.button_d.keyPress(event)
        self.button_f.keyPress(event)
        self.button_g.keyPress(event)
        self.button_h.keyPress(event)
        self.button_j.keyPress(event)
        
    def keyReleaseEvent(self, event):
        self.button_a.keyRelease(event)
        self.button_s.keyRelease(event)
        self.button_d.keyRelease(event)
        self.button_f.keyRelease(event)
        self.button_g.keyRelease(event)
        self.button_h.keyRelease(event)
        self.button_j.keyRelease(event)
        
def run_script():
    global music_controller_dlg
    global music_controller_widget
    global dialog_event_callback
    global event_callback
    
    music_controller_widget = MusicController()
    
    #create RDialog
    music_controller_dlg = RLPy.RUi.CreateRDialog()
    music_controller_dlg.SetWindowTitle("Music Controller")
    
    # register dialog event
    dialog_event_callback = DialogEventCallback()
    dialog_register_id = music_controller_dlg.RegisterEventCallback(dialog_event_callback)

    #wrap RDialog to Pyside Dialog
    main_pyside_dlg = wrapInstance(int(music_controller_dlg.GetWindow()), QtWidgets.QDialog)
    main_pyside_layout = main_pyside_dlg.layout()
    
    main_pyside_layout.addWidget(music_controller_widget)
    main_pyside_dlg.setFixedWidth(300)
    
    event_callback = REventCallbackSampleCode()
    id = RLPy.REventHandler.RegisterCallback(event_callback)
    global event_list
    event_list.append(id)
    #RLPy.REventHandler.UnregisterCallback(id)
    #show dialog
    music_controller_dlg.Show()

    
