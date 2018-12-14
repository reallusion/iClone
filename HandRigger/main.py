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
record_action = None
record_qaction = None
blend_action = None
blend_qaction = None

# other global data
hand_rigger = None

def initialize_plugin():
    add_menu('Python Samples', 'Hand Gestures Puppeteering', show_main_dlg)
    print('"Hand Gestures Puppeteering" initialization done!')

def uninitialize_plugin():
    print('uninitialize "Hand Gestures Puppeteering"')

def create_qml_embedded_dialog(title, obj_name, qml_file, qml_context_name, qml_context_value):
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
    root_context = main_dlg_view.rootContext()
    root_context.setContextProperty(qml_context_name, qml_context_value) #qml_context_name

    return [main_dlg, main_pyside_dlg, main_qml]

def add_menu(menu_title, action_name, trigger_func):
    menu = wrapInstance(int(RLPy.RUi.AddMenu(menu_title, RLPy.EMenu_Plugins)), PySide2.QtWidgets.QMenu)
    menu_action = menu.addAction(action_name)
    menu_action.triggered.connect(trigger_func)

def add_hotkey(hotkey, trigger_func):
    qaction = RLPy.RUi.AddHotKey(hotkey)
    action = wrapInstance(int(qaction), PySide2.QtWidgets.QAction)
    action.triggered.connect(trigger_func)
    return [qaction, action]

def show_main_dlg():
    global main_dlg
    global main_pyside_dlg
    global main_qml
    global qml_module
    global main_dlg_callback
    global hand_rigger_callback
    global hand_rigger_callback_list
    global preview_action
    global preview_qaction
    global record_action
    global record_qaction
    global blend_action
    global blend_qaction

    if main_dlg is None:
        # create dialog
        qml_module = HandRigQmlModule()
        dialog_globals = create_qml_embedded_dialog('Hand Gestures Puppeteering',
                                                    'Hand Gestures Puppeteering',
                                                    '/resource/qml/handrigger.qml',
                                                    'handRigger',
                                                    qml_module)
        main_dlg        = dialog_globals[0]
        main_pyside_dlg = dialog_globals[1]
        main_qml        = dialog_globals[2]

        register_dialog_callback()
        register_hand_rigger_callback()

        # add hotkey 'P'
        preview_actions = add_hotkey('P', preview)
        preview_qaction = preview_actions[0]
        preview_action = preview_actions[1]
        preview_action.setEnabled(False)

        # add hotkey 'Space'
        record_actions = add_hotkey('Space', record)
        record_qaction = record_actions[0]
        record_action = record_actions[1]
        record_action.setEnabled(False)

        # add hotkey 'B'
        blend_actions = add_hotkey('B', switch_blend_mode)
        blend_qaction = blend_actions[0]
        blend_action = blend_actions[1]
        blend_action.setEnabled(False)

    if main_dlg.IsVisible():
        # clear callbacks
        main_dlg.UnregisterAllEventCallbacks()
        RLPy.REventHandler.UnregisterCallbacks(hand_rigger_callback_list)
        hand_rigger_callback_list = []

        # clear hotkeys
        RLPy.RUi.RemoveHotKey(preview_qaction)
        RLPy.RUi.RemoveHotKey(record_qaction)
        RLPy.RUi.RemoveHotKey(blend_qaction)

        #main_dlg.Hide()
        main_dlg.Close()

        del main_dlg_callback
        del hand_rigger_callback
        del main_dlg
        del main_pyside_dlg
        del main_qml
        del qml_module
        del preview_action
        del preview_qaction
        del record_action
        del record_qaction
        del blend_action
        del blend_qaction

        main_dlg_callback = None
        hand_rigger_callback = None
        main_dlg = None
        main_pyside_dlg = None
        main_qml = None
        qml_module = None
        preview_action = None
        preview_qaction = None
        record_action = None
        record_qaction = None
        blend_action = None
        blend_qaction = None

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
        if hand_rigger.get_state() is HandRiggerState.Preview or hand_rigger.get_state() is HandRiggerState.Record:
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
    global preview_action
    global record_action
    global hand_rigger

    if hand_rigger is not None:
        if hand_rigger.get_state() is HandRiggerState.Disable:
            preview_action.setEnabled(False)
            record_action.setEnabled(False)
        else:
            preview_action.setEnabled(True)
            record_action.setEnabled(True)

def preview():
    global hand_rigger
    if hand_rigger is not None:
        if hand_rigger.get_state() == HandRiggerState.Preview or hand_rigger.get_state() == HandRiggerState.Record:
            run(HandRiggerState.Ready)
        else:
            run(HandRiggerState.Preview)

def record():
    global hand_rigger
    if hand_rigger is not None:
        if hand_rigger.get_state() == HandRiggerState.Preview or hand_rigger.get_state() == HandRiggerState.Record:
            run(HandRiggerState.Ready)
        else:
            run(HandRiggerState.Record)

def run(state):
    global main_qml
    global hand_rigger
    if hand_rigger is not None:
        hand_rigger.run(state)
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
    @PySide2.QtCore.Slot(int)        
    def set_blend_mode(self, mode):
        global hand_rigger
        if hand_rigger is not None:
            hand_rigger.set_blend_mode(mode)
            main_qml.setBlendMode(hand_rigger.get_blend_mode())

def run_script():
    initialize_plugin()
