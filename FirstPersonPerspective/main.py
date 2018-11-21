import os
import sys
import RLPy
import PySide2
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtWidgets import QWidget
from PySide2.QtQuickWidgets import QQuickWidget
from PySide2.QtCore import QResource
from PySide2.shiboken2 import wrapInstance
from enum import IntEnum
    
# RL API data member
open_ui_kit = RLPy.RUi

app = PySide2.QtWidgets.QApplication.instance()
if not app:
    app = PySide2.QtWidgets.QApplication([])

# RL Ui    
camera_pyside_dlg = None
 
# Object
camera_object = None
camera_control = None
camera_transform = None

# main window
main_widget = None
width = 400
height = 200

class MoveDirection(IntEnum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

class MainDialog(PySide2.QtWidgets.QDialog):
    def __init__(self, parent=None):
        global width
        global height
        super(MainDialog, self).__init__(parent)
        self.pixmapOffset = PySide2.QtCore.QPoint()
        self.lastDragPos = PySide2.QtCore.QPoint()
        self.resize(width, height)
        self.move_offset = 10
        
    def keyPressEvent(self, event):
        if event.key() == PySide2.QtCore.Qt.Key_Left:
            camera_move_control(self.move_offset, MoveDirection.LEFT)
        elif event.key() == PySide2.QtCore.Qt.Key_Up:
            camera_move_control(self.move_offset, MoveDirection.UP)
        elif event.key() == PySide2.QtCore.Qt.Key_Right:
            camera_move_control(self.move_offset, MoveDirection.RIGHT)
        elif event.key() == PySide2.QtCore.Qt.Key_Down:
            camera_move_control(self.move_offset, MoveDirection.DOWN)

    def mouseMoveEvent(self, event):
        global camera_control
        global camera_transform
        global width
        global height
        self.pixmapOffset += event.pos() - self.lastDragPos
        self.lastDragPos = PySide2.QtCore.QPoint(event.pos())
        offset_x = (self.pixmapOffset.x() - width/2) / (width / 2)
        offset_y = (self.pixmapOffset.y() - height/2) / (height / 2)
        camera_rotate_control(offset_x, offset_y)

    def wheelEvent(self, event):
        global camera_object
        focal_length = camera_object.GetFocalLength(RLPy.RGlobal.GetTime())
        numDegrees = event.delta() / 8
        numSteps = numDegrees / 15.0
        focal_length += numSteps
        camera_object.SetFocalLength(RLPy.RGlobal.GetTime(), focal_length)    
        
def initialize_plugin():
    global open_ui_kit
    global camera_pyside_dlg
    global camera_transform
    global main_widget
    
    camera_pyside_dlg = MainDialog()
    camera_pyside_dlg.setObjectName("Camera First Control")
    camera_pyside_dlg.setWindowTitle("Camera First Control")
    
    plugin_menu = wrapInstance(int(open_ui_kit.AddMenu("Camera Control", RLPy.EMenu_Plugins)), PySide2.QtWidgets.QMenu)
    plugin_action = plugin_menu.addAction("Open Camera Control")
    plugin_action.triggered.connect(show_dlg)
    
def show_dlg():
    global camera_pyside_dlg
    camera_setting()
    camera_pyside_dlg.show()
    
def camera_setting():
    global camera_object
    global camera_control
    global camera_transform
    
    camera_object = RLPy.RScene.FindObject(RLPy.EObjectType_Camera, "Camera")
    camera_control = camera_object.GetControl("Transform")
    key = RLPy.RTransformKey().Clone()
    camera_control.GetKeyAt(0, key)
    time = key.GetTime()
    camera_transform = RLPy.RTransform.IDENTITY
    camera_control.GetValue(time, camera_transform)

def camera_rotate_control(offset_x, offset_y):
    global camera_control
    data_block = camera_control.GetDataBlock()
    float_control_x = data_block.GetControl('Rotation/RotationX')
    float_control_z = data_block.GetControl('Rotation/RotationZ')

    float_control_z.SetValue(RLPy.RGlobal.GetTime(), -offset_x)
    float_control_x.SetValue(RLPy.RGlobal.GetTime(), -offset_y+1.5)

def camera_move_control(offset, direction):
    global camera_transform
    global camera_control
    camera_control.GetValue(RLPy.RGlobal.GetTime(), camera_transform)
    if direction == MoveDirection.UP:
        camera_transform.T().y += offset
        camera_control.SetValue(RLPy.RGlobal.GetTime(), camera_transform)
    elif direction == MoveDirection.DOWN:
        camera_transform.T().y -= offset
        camera_control.SetValue(RLPy.RGlobal.GetTime(), camera_transform)
    elif direction == MoveDirection.RIGHT:
        camera_transform.T().x += offset
        camera_control.SetValue(RLPy.RGlobal.GetTime(), camera_transform)   
    elif direction == MoveDirection.LEFT:
        camera_transform.T().x -= offset
        camera_control.SetValue(RLPy.RGlobal.GetTime(), camera_transform)   