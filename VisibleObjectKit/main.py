import os
import sys
import RLPy
import slmlite
from slmlite import SLMLite
from slmlite import SMLLiteQmlModule
import PySide2
from PySide2.QtCore import *
from PySide2.QtCore import QResource
from PySide2.QtGui import *
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QWidget
from PySide2.shiboken2 import wrapInstance

sys.dont_write_bytecode = True
app = None

# Load Simple Layer Manager Lite rcc
execute_parent_path = os.path.abspath(os.path.join(sys.executable, os.pardir))
print("execute_parent_path: " + execute_parent_path.replace('\\','/'))
res_path = execute_parent_path + "\\OpenPlugin\\SimpleLayerManagerLite\\resource"
sys.path.insert(0, res_path)
QResource.registerResource(execute_parent_path + "\\OpenPlugin\\SimpleLayerManagerLite\\resource\\resource.rcc")

# Simple Layer Manager Lite dialog
main_dlg_view = None
main_dlg_context = None

# context module
smlLiteModule = None

# RL API data member
ui_kit = RLPy.RUi

# Simple Layer Manager Lite object
slm_lite = None

def initialize_plugin():
    print("start_initialize_plugin")
    global app
    global main_dlg_view
    global main_dlg_context
    global smlLiteModule
    global ui_kit
    global slm_lite

    app = PySide2.QtWidgets.QApplication.instance()
    if not app:
        app = PySide2.QtWidgets.QApplication([])
    app.aboutToQuit.connect(close_application)

    # Init mainwindow
    main_widget = wrapInstance(int(ui_kit.GetMainWindow()), PySide2.QtWidgets.QWidget)

    # Init SLM dialog
    main_dlg = ui_kit.CreateRDialog()
    main_dlg.SetWindowTitle("Simple Layer Manager")
    slm_lite = SLMLite(main_dlg)

    # Menu
    plugin_menu = wrapInstance(int(ui_kit.AddMenu("Simple Layer Manager Lite", RLPy.EMenu_Plugins)), PySide2.QtWidgets.QMenu)
    plugin_action = plugin_menu.addAction("Simple Layer Manager Lite")
    plugin_action.setIcon((QIcon(":/slmlite/icon/SLMLite.svg")))
    plugin_action.triggered.connect(show_main_dlg)

    # Inject Python data into QML
    main_dlg_view = slm_lite.get_main_dlg()
    main_dlg_context = main_dlg_view.rootContext()
    smlLiteModule = SMLLiteQmlModule()
    main_dlg_context.setContextProperty("smlLiteModule", smlLiteModule)
    print("end_initialize_plugin")

def uninitialize_plugin():
    print("uninitialize_plugin")

def show_main_dlg():
    global slm_lite
    slm_lite.show()
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