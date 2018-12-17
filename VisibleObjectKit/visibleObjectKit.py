# Copyright 2018 The Reallusion Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

import os
import sys
import RLPy
import PySide2
from PySide2.QtCore import *
from PySide2.QtCore import QResource
from PySide2.QtGui import *
from PySide2.QtWidgets import QWidget
from PySide2.QtQuickWidgets import QQuickWidget
from PySide2.QtQuick import QQuickView
from PySide2.shiboken2 import wrapInstance

sys.dont_write_bytecode = True

# Load Visible Object Kit rcc
execute_parent_path = os.path.abspath(os.path.join(sys.executable, os.pardir))
res_path = execute_parent_path + "\\OpenPlugin\\VisibleObjectKit\\resource"
sys.path.insert(0, res_path)
QResource.registerResource(execute_parent_path + "\\OpenPlugin\\VisibleObjectKit\\resource\\resource.rcc")

# Dialog param
dialog_show_first_time = False

# Visible Object Kit dialog
main_dlg = None
main_pyside_dlg = None
main_dlg_view = None
main_dlg_root = None

# HotKey
esc_action = None

# RL API data member
ui_kit = RLPy.RUi

# Data member
get_all_objects_last_time = False

selected_objects = []
avatar_list = []
prop_list = []
event_list = []

# Callback
obj_kit_callback = None

class ObjectKit(object):
    def __init__(self, _main_dlg):
        global main_dlg
        global main_pyside_dlg
        global main_dlg_view
        global main_dlg_root
        global esc_action
        global ui_kit

        main_dlg = _main_dlg

        # Create an URL to the QML file
        main_dlg_url = QUrl("qrc:/objKit/qml/Main.qml")
        main_dlg_view = PySide2.QtQuickWidgets.QQuickWidget()
        main_dlg_view.setSource(main_dlg_url)
        main_dlg_view.setResizeMode(PySide2.QtQuickWidgets.QQuickWidget.SizeRootObjectToView)

        # Python get Main.qml object
        main_dlg_root = main_dlg_view.rootObject()

        # Set dialog Layout with titlebar
        main_pyside_dlg = wrapInstance(int(main_dlg.GetWindow()), PySide2.QtWidgets.QDialog)
        main_pyside_dlg.setObjectName("Visible Object Kit")

        # HotKey
        esc_action = wrapInstance(int(ui_kit.AddHotKey("Escape")), PySide2.QtWidgets.QAction)
        esc_action.triggered.connect(self.hide)
        esc_action.setEnabled(False)

        # Generate custom dialog
        self.main_layout = main_pyside_dlg.layout()
        self.main_layout.addWidget(main_dlg_view)
        main_pyside_dlg.adjustSize()

    def show(self):
        global dialog_show_first_time
        global main_dlg
        global main_pyside_dlg
        global esc_action

        if main_pyside_dlg.isVisible():
            esc_action.setEnabled(False)
            main_pyside_dlg.hide()
        else:
            if not dialog_show_first_time:
                register_event_handler()
                dialog_show_first_time = True
            main_dlg.Show()
            esc_action.setEnabled(True)
            global_update_visible_chk_status()

    def hide(self):
        global main_pyside_dlg
        global esc_action

        if main_pyside_dlg.isVisible():
            esc_action.setEnabled(False)
            main_pyside_dlg.hide()

    def get_main_dlg(self):
        global main_dlg_view
        return main_dlg_view

class ObjectKitQmlModule(PySide2.QtCore.QObject):
    @PySide2.QtCore.Slot(bool)
    def get_all_objects(self, active):
        global get_all_objects_last_time

        global_get_avatars(active)
        global_get_props(active)
        global_select_objects()
        get_all_objects_last_time = True

    @PySide2.QtCore.Slot(bool)
    def get_avatars(self, active):
        global get_all_objects_last_time

        if get_all_objects_last_time:
            clear_data_list()
            get_all_objects_last_time = False
        global_get_avatars(active)
        global_select_objects()

    @PySide2.QtCore.Slot(bool)
    def get_props(self, active):
        global get_all_objects_last_time

        if get_all_objects_last_time:
            clear_data_list()
            get_all_objects_last_time = False
        global_get_props(active)
        global_select_objects()

    @PySide2.QtCore.Slot(bool)
    def set_visible(self, visible):
        global selected_objects
        selected_objects = []
        selected_objects = RLPy.RScene.GetSelectedObjects()
        if len(selected_objects) > 0:
            for i in range(len(selected_objects)):
                if visible:
                    RLPy.RScene.Show(selected_objects[i])
                else:
                    RLPy.RScene.Hide(selected_objects[i])

class ObjectKitCallback(RLPy.REventCallback):
    def __init__(self):
        RLPy.REventCallback.__init__(self)

    def OnObjectSelectionChanged(self):
        global_update_visible_chk_status()

def global_get_avatars(active):
    global avatar_list
    avatar_list = []
    if active:
        avatar_type = RLPy.EAvatarType_Standard | RLPy.EAvatarType_NonStandard | RLPy.EAvatarType_StandardSeries
        avatar_list = RLPy.RScene.GetAvatars(avatar_type)

def global_get_props(active):
    global prop_list
    prop_list = []
    if active:
        prop_list = RLPy.RScene.GetProps()

def global_select_objects():
    global avatar_list
    global prop_list

    total_list = []
    if len(avatar_list) > 0 and len(prop_list) > 0:
        total_list = avatar_list + prop_list
    elif len(avatar_list) > 0:
        total_list = avatar_list
    elif len(prop_list) > 0:
        total_list = prop_list
    RLPy.RScene.SelectObjects(total_list)

def global_update_visible_chk_status():
    global main_pyside_dlg
    global main_dlg_root

    if main_dlg_root != None and main_pyside_dlg.isVisible():
        selected_objects_count = len(RLPy.RScene.GetSelectedObjects())
        main_dlg_root.updateVisibleChkStatus(selected_objects_count > 0)

def clear_data_list():
    global avatar_list
    global prop_list

    avatar_list = []
    prop_list = []

def register_event_handler():
    global obj_kit_callback
    global event_list

    obj_kit_callback = ObjectKitCallback()
    callback_id = RLPy.REventHandler.RegisterCallback(obj_kit_callback)
    event_list.append(callback_id)

def unregister_event_handler():
    global event_list

    if len(event_list) != 0:
        RLPy.REventHandler.UnRegisterCallbacks(event_list)
