import os
import sys
import RLPy
import PySide2
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtWidgets import QWidget
from PySide2.shiboken2 import wrapInstance
from enum import IntEnum

# RL Ui    
camera_pyside_dlg = None
 
# Object
camera_object = None
camera_control = None
camera_transform = None

# main window
width = 400
height = 200

# move offset
move_offset = 10

class MoveDirection(IntEnum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

class FirstPersonDialog(PySide2.QtWidgets.QDialog):
    def __init__(self, parent=None):
        global width
        global height
        global move_offset
        super(FirstPersonDialog, self).__init__(parent)
        self.pixmapOffset = PySide2.QtCore.QPoint()
        self.lastDragPos = PySide2.QtCore.QPoint()
        self.resize(width, height)
        self.move_offset = move_offset
    
    def keyPressEvent(self, event):
        if event.key() == PySide2.QtCore.Qt.Key_Left:
            camera_move_control(self.move_offset, MoveDirection.LEFT)
        elif event.key() == PySide2.QtCore.Qt.Key_Up:
            camera_move_control(self.move_offset, MoveDirection.UP)
        elif event.key() == PySide2.QtCore.Qt.Key_Right:
            camera_move_control(self.move_offset, MoveDirection.RIGHT)
        elif event.key() == PySide2.QtCore.Qt.Key_Down:
            camera_move_control(self.move_offset, MoveDirection.DOWN)

    def mousePressEvent(self, event):
        self.lastDragPos = PySide2.QtCore.QPoint(event.pos())
            
    def mouseMoveEvent(self, event):
        global camera_transform
        global width
        global height

        # Record previous offset data
        offset_y = self.pixmapOffset.y()
        offset_x = self.pixmapOffset.x()
        # Calculate new mouse move offset
        self.pixmapOffset += event.pos() - self.lastDragPos
        self.lastDragPos = PySide2.QtCore.QPoint(event.pos())
        offset_x -= self.pixmapOffset.x()
        offset_y -= self.pixmapOffset.y()

        camera_rotate_control(offset_x, offset_y)

    def mouseReleaseEvent(self, event):
        self.pixmapOffset += event.pos() - self.lastDragPos
        self.lastDragPos = PySide2.QtCore.QPoint()

    # Using mouse wheel to control camera focal length
    def wheelEvent(self, event):
        global camera_object
        focal_length = camera_object.GetFocalLength(RLPy.RGlobal.GetTime())
        # Mouse types work in steps of 15 degrees, in which case the delta value is a multiple of 120
        numDegrees = event.delta() / 8
        numSteps = numDegrees / 15.0
        focal_length += numSteps
        camera_object.SetFocalLength(RLPy.RGlobal.GetTime(), focal_length)    

def initialize_plugin():
    global open_ui_kit
    global camera_pyside_dlg
    global camera_transform

    # Create Camera Control Panel
    camera_pyside_dlg = FirstPersonDialog()
    camera_pyside_dlg.setWindowTitle("Camera First Control")

    # Add Menu to iClone
    plugin_menu = wrapInstance(int(RLPy.RUi.AddMenu("Camera Control", RLPy.EMenu_Plugins)), PySide2.QtWidgets.QMenu)
    plugin_action = plugin_menu.addAction("Open Camera Control")
    plugin_action.triggered.connect(show_dlg)

def show_dlg():
    global camera_pyside_dlg
    camera_setting()
    camera_pyside_dlg.show()

# Find Camera and get camera transform control
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

# Calculate the camera rotation by mouse move
def camera_rotate_control(offset_x, offset_y):
    global camera_control
    rotation_x = 0.0
    rotation_z = 0.0
    data_block = camera_control.GetDataBlock()
    float_control_x = data_block.GetControl('Rotation/RotationX')
    float_control_z = data_block.GetControl('Rotation/RotationZ')
    
    # Get camera currrent rotation
    temp_x = float_control_x.GetValue(RLPy.RGlobal.GetTime(), rotation_x)
    temp_z = float_control_z.GetValue(RLPy.RGlobal.GetTime(), rotation_z)
    
    # degree to radians and add offset
    rotation_x = temp_x[1]*180/3.14 + offset_y
    rotation_z = temp_z[1]*180/3.14 + offset_x
    
    # radians to degree
    float_control_x.SetValue(RLPy.RGlobal.GetTime(), rotation_x/180*3.14)
    float_control_z.SetValue(RLPy.RGlobal.GetTime(), rotation_z/180*3.14)

# Calculate the camera translate by key
def camera_move_control(offset, direction):
    global camera_transform
    global camera_control
    camera_control.GetValue(RLPy.RGlobal.GetTime(), camera_transform)
    if direction == MoveDirection.UP:
        camera_transform.T().y += offset
    elif direction == MoveDirection.DOWN:
        camera_transform.T().y -= offset
    elif direction == MoveDirection.RIGHT:
        camera_transform.T().x += offset  
    elif direction == MoveDirection.LEFT:
        camera_transform.T().x -= offset
        
    camera_control.SetValue(RLPy.RGlobal.GetTime(), camera_transform)    