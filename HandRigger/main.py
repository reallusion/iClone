import os
import sys
import RLPy
import handrigger
from handrigger import HandRigger
from handrigger import HandRiggerState
from handrigger import BlendMode

import PySide2
from PySide2.QtCore import *
from PySide2.QtCore import QResource
from PySide2.QtGui import *
from PySide2.QtWidgets import QWidget
from PySide2.QtQuickWidgets import QQuickWidget
from PySide2.QtQuick import QQuickView
from PySide2.shiboken2 import wrapInstance

sys.dont_write_bytecode = True

# Dialog
main_dlg = None
main_pyside_dlg = None
main_qml = None
qml_module = None

# Callback
main_dlg_callback = None
hand_rigger_callback = None
hand_rigger_callback_list = []

# Hotkey action
space_action = None
blend_action = None

# other global data
hand_rigger = None

def initialize_plugin():
    global space_action
    global blend_action
    global hand_rigger

    # Menu
    add_menu('Hand Rigger', 'Hand Rigger', show_main_dlg)

    # HotKey
    space_action = add_hotkey('Space', run)
    space_action.setEnabled(False)
    blend_action = add_hotkey('B', switch_blend_mode)
    blend_action.setEnabled(False)

    # create HandRigger
    hand_rigger = HandRigger()

    print('"Hand Rigger" initialization done!')

def uninitialize_plugin():
    print('uninitialize "Hand Rigger"')

def create_qml_embedded_dialog(title, obj_name, qml_file, qml_context_name, qml_context_value):
    global main_dlg
    global main_pyside_dlg
    global main_qml
    global qml_module

    main_dlg = RLPy.RUi.CreateRDialog()
    main_dlg.SetWindowTitle(title)                                      #title

    # wrapInstance
    main_pyside_dlg = wrapInstance(int(main_dlg.GetWindow()), PySide2.QtWidgets.QDialog)
    main_pyside_dlg.setObjectName(obj_name)                             #obj_name

    # embed QML
    resource_path = os.path.dirname(__file__)
    main_dlg_view = PySide2.QtQuickWidgets.QQuickWidget()
    main_dlg_view.setSource(QUrl.fromLocalFile(resource_path+qml_file)) #qml_file
    main_dlg_view.setResizeMode(PySide2.QtQuickWidgets.QQuickWidget.SizeRootObjectToView)
    main_qml = main_dlg_view.rootObject()
    
    # add widget to layout
    main_layout = main_pyside_dlg.layout()
    main_layout.addWidget(main_dlg_view)
    main_pyside_dlg.adjustSize()

    # inject Python data into QML
    qml_module = qml_context_value                                      #save qml_context_value to a global variable
    root_context = main_dlg_view.rootContext()
    root_context.setContextProperty(qml_context_name, qml_module)       #qml_context_name

def add_menu(menu_title, action_name, trigger_func):
    menu = wrapInstance(int(RLPy.RUi.AddMenu(menu_title, RLPy.EMenu_Plugins)), PySide2.QtWidgets.QMenu)
    menu_action = menu.addAction(action_name)
    menu_action.triggered.connect(trigger_func)
    
def add_hotkey(hotkey, trigger_func):
    action = wrapInstance(int(RLPy.RUi.AddHotKey(hotkey)), PySide2.QtWidgets.QAction)
    action.triggered.connect(trigger_func)
    return action

def show_main_dlg():
    global main_dlg
    global main_pyside_dlg
    global main_qml
    global qml_module
    global main_dlg_callback
    global hand_rigger_callback
    global hand_rigger_callback_list

    if main_dlg is None:
        handrigger_qml_module = HandRigQmlModule()
        create_qml_embedded_dialog('Hand Rigger', 'Hand Rigger', '/resource/qml/handrigger.qml', 'handRigger', handrigger_qml_module)
        register_dialog_callback()
        register_hand_rigger_callback()

    if main_dlg.IsVisible():
        main_dlg.UnregisterAllEventCallbacks()
        RLPy.REventHandler.UnregisterCallbacks(hand_rigger_callback_list)
        hand_rigger_callback_list = []

        main_dlg.Hide()

        del main_dlg_callback
        del hand_rigger_callback
        del main_dlg
        del main_pyside_dlg
        del main_qml
        del qml_module

        main_dlg_callback = None
        hand_rigger_callback = None
        main_dlg = None
        main_pyside_dlg = None
        main_qml = None
        qml_module = None

    else:
        main_dlg.Show()

def on_show():
    global blend_action
    global hand_rigger

    if hand_rigger is None:
        hand_rigger = HandRigger()

    update_hand_rigger_state()
    blend_action.setEnabled(True)

def on_hide():
    global blend_action
    global hand_rigger

    if hand_rigger is not None:
        if hand_rigger.get_state() is HandRiggerState.Running:
            set_hand_rigger_state(HandRiggerState.Disable)
        del hand_rigger
        hand_rigger = None

    blend_action.setEnabled(False)

def update_hand_rigger_state():
    global main_qml
    global hand_rigger

    if hand_rigger is not None:
        hand_rigger.update_state()
        update_hotkey_state()
        main_qml.updateHandRiggerState(hand_rigger.get_state())

def set_hand_rigger_state(state):
    global main_qml
    global hand_rigger
    if hand_rigger is not None:
        hand_rigger.set_state(state)
        update_hotkey_state()
        main_qml.updateHandRiggerState(hand_rigger.get_state())

def update_hotkey_state():
    global space_action
    global hand_rigger

    if hand_rigger is not None:
        if hand_rigger.get_state() is HandRiggerState.Disable:
            space_action.setEnabled(False)
        else:
            space_action.setEnabled(True)

def run():
    global main_qml
    global hand_rigger
    hand_rigger.run()
    main_qml.updateHandRiggerState(hand_rigger.get_state())

def switch_blend_mode():
    global main_qml
    global hand_rigger

    if hand_rigger is not None:
        hand_rigger.set_blend_mode((hand_rigger.get_blend_mode()+1)%BlendMode.Count)
        main_qml.setBlendMode(hand_rigger.get_blend_mode())
    
class DialogCallback(RLPy.RDialogCallback):
    def __init__(self):
        RLPy.RDialogCallback.__init__(self)
        self.show_fptr = None
        self.hide_fptr = None

    def OnDialogShow(self):
        if self.show_fptr is not None:
            self.show_fptr()

    def OnDialogHide(self):
        if self.hide_fptr is not None:
            self.hide_fptr()

    def register_show_callback(self, show_function):
        self.show_fptr = show_function

    def register_hide_callback(self, hide_function):
        self.hide_fptr = hide_function

class HandRiggerCallback(RLPy.REventCallback):
    def __init__(self):
        RLPy.REventCallback.__init__(self)

    def OnObjectSelectionChanged(self):
        update_hand_rigger_state()

def register_dialog_callback():
    global main_dlg
    global main_dlg_callback
    main_dlg_callback = DialogCallback()
    main_dlg_callback.register_show_callback(on_show)
    main_dlg_callback.register_hide_callback(on_hide)
    main_dlg.RegisterEventCallback(main_dlg_callback)

def register_hand_rigger_callback():
    global hand_rigger_callback
    global hand_rigger_callback_list
    
    hand_rigger_callback = HandRiggerCallback()
    callback_id = RLPy.REventHandler.RegisterCallback(hand_rigger_callback)
    hand_rigger_callback_list.append(callback_id)

class HandRigQmlModule(PySide2.QtCore.QObject):
    @PySide2.QtCore.Slot('QVariantList', result='QVariantList')
    def process_data(self, square_dist):
        global hand_rigger
        if hand_rigger is not None:
            return hand_rigger.process_data(square_dist)

def run_script():
    initialize_plugin()
