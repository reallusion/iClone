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

excute_parent_path = os.path.abspath(os.path.join(sys.executable, os.pardir))
res_path = excute_parent_path + "\\OpenPlugin\\FirstPersonPerspective\\resource"
sys.path.insert(0, res_path)
QResource.registerResource(res_path + "\\resource.rcc")
    
# RL API data member
mocap_manager = RLPy.RGlobal.GetMocapManager()
open_ui_kit = RLPy.RUi

app = PySide2.QtWidgets.QApplication.instance()
if not app:
    app = PySide2.QtWidgets.QApplication([])

# RL Ui    
camera_dlg = None
camera_dlg_view = None
caemra_dlg_root = None
camera_dlg_context = None
camera_pyside_dlg = None
 
# Object
camera_object = None
camera_control = None
camera_transform = None
cameraModule = None

# main window
main_widget = None

class MainView(QQuickWidget):
    def __init__(self, url):
        super().__init__()
        self.setSource(url)
        self.setResizeMode(PySide2.QtQuickWidgets.QQuickWidget.SizeRootObjectToView)
        self.pixmapOffset = PySide2.QtCore.QPoint()
        self.lastDragPos = PySide2.QtCore.QPoint()
        
    def keyPressEvent(self, event):
        print(event.key())
        
    def mouseMoveEvent(self, event):
        global camera_control
        global camera_transform
        self.pixmapOffset += event.pos() - self.lastDragPos
        self.lastDragPos = PySide2.QtCore.QPoint(event.pos())
        camera_rotate_control(( self.pixmapOffset.x() - 200 ) / 200, ( self.pixmapOffset.y() - 100 ) / 100)
        
    def mousePressEvent(self, event):
        print(event.button())
        
    def wheelEvent(self, event):
        global camera_object
        focal_length = camera_object.GetFocalLength(RLPy.RGlobal.GetTime())
        numDegrees = event.delta() / 8
        numSteps = numDegrees / 15.0
        focal_length += numSteps
        camera_object.SetFocalLength(RLPy.RGlobal.GetTime(), focal_length)
        # print(focal_length)
        
def initialize_plugin():
    global open_ui_kit
    global camera_dlg
    global camera_dlg_view
    global caemra_dlg_root
    global camera_dlg_context
    global camera_pyside_dlg
    global camera_transform
    global cameraModule
    global main_widget
    
    camera_dlg = open_ui_kit.CreateRDialog()
    camera_dlg.SetWindowTitle("Camera Control")
    
    camera_dlg_url = QUrl("qrc:/main/qml/main.qml")
    camera_dlg_view = MainView(camera_dlg_url)
    
    caemra_dlg_root = camera_dlg_view.rootObject()
    
    camera_pyside_dlg = wrapInstance(int(camera_dlg.GetWindow()), PySide2.QtWidgets.QDialog)
    camera_pyside_dlg.setObjectName("Camera First Control")
    camera_layout = camera_pyside_dlg.layout()
    camera_layout.addWidget(camera_dlg_view)
    camera_pyside_dlg.adjustSize()
    
    plugin_menu = wrapInstance(int(open_ui_kit.AddMenu("Camera Control", RLPy.EMenu_Plugins)), PySide2.QtWidgets.QMenu)
    plugin_action = plugin_menu.addAction("Open Camera Control")
    plugin_action.triggered.connect(show_dlg)
    
    cameraModule = CameraModule()
    camera_dlg_context = camera_dlg_view.rootContext()
    camera_dlg_context.setContextProperty("cameraModule", cameraModule)
    
def show_dlg():
    global camera_dlg
    camera_setting()
    camera_dlg.Show()

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
    
class CameraModule(PySide2.QtCore.QObject):
    @PySide2.QtCore.Slot()
    def camera_forward(self):
        global camera_transform
        global camera_control
        camera_transform.T().y += 5
        camera_control.SetValue(RLPy.RGlobal.GetTime(), camera_transform)
        
    @PySide2.QtCore.Slot()
    def camera_back(self):
        global camera_transform
        global camera_control
        camera_transform.T().y -= 5
        camera_control.SetValue(RLPy.RGlobal.GetTime(), camera_transform)