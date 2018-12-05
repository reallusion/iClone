import os
import sys
import RLPy
import visibleObjectKit
from visibleObjectKit import ObjectKit
from visibleObjectKit import ObjectKitQmlModule
import PySide2
from PySide2.QtCore import *
from PySide2.QtCore import QResource
from PySide2.QtGui import *
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QWidget
from PySide2.shiboken2 import wrapInstance

sys.dont_write_bytecode = True
app = None

# Load Visible Object Kit rcc
execute_parent_path = os.path.abspath(os.path.join(sys.executable, os.pardir))
res_path = execute_parent_path + "\\OpenPlugin\\VisibleObjectKit\\resource"
sys.path.insert(0, res_path)
QResource.registerResource(execute_parent_path + "\\OpenPlugin\\VisibleObjectKit\\resource\\resource.rcc")

# Visible Object Kit dialog
main_dlg_view = None
main_dlg_context = None

# context module
objKitModule = None

# RL API data member
ui_kit = RLPy.RUi

# Object kit instance
obj_kit = None

def initialize_plugin():
    print("start_initialize_plugin")
    global app
    global main_dlg_view
    global main_dlg_context
    global objKitModule
    global ui_kit
    global obj_kit

    app = PySide2.QtWidgets.QApplication.instance()
    if not app:
        app = PySide2.QtWidgets.QApplication([])
    app.aboutToQuit.connect(close_application)

    # Init mainwindow
    main_widget = wrapInstance(int(ui_kit.GetMainWindow()), PySide2.QtWidgets.QWidget)

    # Init Visible object kit dialog
    main_dlg = ui_kit.CreateRDialog()
    main_dlg.SetWindowTitle("Visible Object Kit")
    obj_kit = ObjectKit(main_dlg)

    # Menu
    plugin_menu = wrapInstance(int(ui_kit.AddMenu("Visible Object Kit", RLPy.EMenu_Plugins)), PySide2.QtWidgets.QMenu)
    plugin_action = plugin_menu.addAction("Visible Object Kit")
    plugin_action.setIcon((QIcon(":/objKit/icon/objKit.svg")))
    plugin_action.triggered.connect(show_main_dlg)

    # Inject Python data into QML
    main_dlg_view = obj_kit.get_main_dlg()
    main_dlg_context = main_dlg_view.rootContext()
    objKitModule = ObjectKitQmlModule()
    main_dlg_context.setContextProperty("objKitModule", objKitModule)
    print("end_initialize_plugin")

def uninitialize_plugin():
    print("uninitialize_plugin")

def show_main_dlg():
    global obj_kit
    obj_kit.show()
    print("show_main_dlg")

def close_application():
    print("close_application")

def main():
    global app
    app = PySide2.QtWidgets.QApplication.instance()
    if not app:
        app = PySide2.QtWidgets.QApplication([])
    initialize_plugin()
    show_main_dlg()

# For run script
if __name__ == '__main__':
    main()