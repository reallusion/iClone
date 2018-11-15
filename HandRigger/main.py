import os
import sys
import RLPy
import handrigger
from handrigger import HandRigger
import PySide2
from PySide2.QtCore import *
from PySide2.QtCore import QResource
from PySide2.QtGui import *
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QWidget
from PySide2.shiboken2 import wrapInstance

sys.dont_write_bytecode = True

# register QML resource
exe_parent_path = os.path.abspath(os.path.join(sys.executable, os.pardir))
resoruce_path = exe_parent_path + "\\OpenPlugin\\HandRigger\\resource"
sys.path.insert(0, resoruce_path)
QResource.registerResource(resoruce_path + "\\handrigger.rcc")

# dialog
main_dlg_view = None
root_context = None
qml_module = None

# RL API data member
ui_kit = RLPy.RUi

# other global data
app = None
hand_rigger = None


def initialize_plugin():
    global app
    global main_dlg_view
    global root_context
    global qml_module
    global ui_kit
    global hand_rigger

    print('initialize plugin ...')
    
    app = PySide2.QtWidgets.QApplication.instance()
    if not app:
        app = PySide2.QtWidgets.QApplication([])
    app.aboutToQuit.connect(close_application)

    # init mainwindow
    main_widget = wrapInstance(int(ui_kit.GetMainWindow()), PySide2.QtWidgets.QWidget)

    main_dlg = ui_kit.CreateRDialog()
    main_dlg.SetWindowTitle('HandRigger')
    hand_rigger = HandRigger(main_dlg)

    # menu
    menu = wrapInstance(int(ui_kit.AddMenu('Hand Rigger', RLPy.EMenu_Plugins)), PySide2.QtWidgets.QMenu)
    menu_action = menu.addAction('HandRigger')
    menu_action.triggered.connect(show_main_dlg)

    # inject Python data into QML
    main_dlg_view = hand_rigger.get_main_dlg()
    root_context = main_dlg_view.rootContext()
    qml_module = HandRigQmlModule()
    root_context.setContextProperty("handRigger", qml_module)


def uninitialize_plugin():
    print('uninitialize "HandRigger" plugin')

def show_main_dlg():
    global hand_rigger
    hand_rigger.show()

def close_application():
    print('close "HandRigger"')

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

#####################  HandRig Kit  #####################
class HandRigQmlModule(PySide2.QtCore.QObject):
    @PySide2.QtCore.Slot('QVariantList')
    def process_data(self, square_dist):
        global hand_rigger
        if hand_rigger is not None:
            hand_rigger.process_data(square_dist)
