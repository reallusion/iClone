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
import tempfile
import sys
import json
import RLPy
import handrigger
# import cStringIO as StringIO
from handrigger import HandRigger
from handrigger import HandRiggerState
from handrigger import BlendMode

import PySide2
from PySide2 import *
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import QWidget
from PySide2.QtQuickWidgets import QQuickWidget
from PySide2.QtQuick import QQuickView
from PySide2.shiboken2 import wrapInstance
from enum import IntEnum

sys.dont_write_bytecode = True

temp_preset_file_path = f"{tempfile.gettempdir()}\\temp_preset.hgpp"
default_preset_file_path = f"{os.path.dirname(__file__)}/resource/presets/Default.hgpp"
icon_file_path = f"{os.path.dirname(__file__)}/resource/presets"
preset_file_path = f"{os.path.dirname(__file__)}/resource/presets"


class Mode(IntEnum):
    Stopped = 0
    Preview = 1
    Record = 2


# Globals
hgp_dialog = None
hgp_actions = {}  # Hotkey actions
hand_rigger = None  # Hand Rigger
hgp_timer = {}

# Callback
hand_rigger_callback = None
hand_rigger_callback_list = []

mode = Mode.Stopped


class SendDataTimerCallback(RLPy.RPyTimerCallback):
    def __init__(self):
        RLPy.RPyTimerCallback.__init__(self)

    def Timeout(self):
        global hand_rigger
        hand_rigger.process_data(-1)


timer_send_data = RLPy.RPyTimer()
timer_send_data.SetInterval(8)
timer_send_data.SetSingleShot(False)
timer_send_data_callback = SendDataTimerCallback()
timer_send_data.RegisterPyTimerCallback(timer_send_data_callback)


def initialize_plugin():
    add_menu('Python Samples', 'Hand Gestures Puppeteering', show_main_dlg)


def create_qml_embedded_dialog(title, obj_name, qml_file, qml_context_name, qml_context_value):

    main_dlg = RLPy.RUi.CreateRDialog()
    main_dlg.SetWindowTitle(title)  # title

    # wrapInstance
    main_pyside_dlg = wrapInstance(int(main_dlg.GetWindow()), PySide2.QtWidgets.QDialog)
    main_pyside_dlg.setObjectName(obj_name)  # obj_name

    # embed QML
    resource_path = os.path.dirname(__file__)
    main_dlg_view = PySide2.QtQuickWidgets.QQuickWidget()
    main_dlg_view.setSource(QUrl.fromLocalFile(resource_path+qml_file))  # qml_file
    main_dlg_view.setResizeMode(PySide2.QtQuickWidgets.QQuickWidget.SizeRootObjectToView)
    main_qml = main_dlg_view.rootObject()

    # add widget to layout
    main_layout = main_pyside_dlg.layout()
    main_layout.addWidget(main_dlg_view)
    main_pyside_dlg.adjustSize()

    # inject Python data into QML
    root_context = main_dlg_view.rootContext()
    root_context.setContextProperty(qml_context_name, qml_context_value)  # qml_context_name

    return [main_dlg, main_pyside_dlg, main_qml]


def add_menu(menu_title, action_name, trigger_func):
    ic_dlg = wrapInstance(int(RLPy.RUi.GetMainWindow()), PySide2.QtWidgets.QMainWindow)
    plugin_menu = ic_dlg.menuBar().findChild(PySide2.QtWidgets.QMenu, "pysample_menu")
    if plugin_menu is None:
        plugin_menu = wrapInstance(int(RLPy.RUi.AddMenu("Python Samples", RLPy.EMenu_Plugins)), PySide2.QtWidgets.QMenu)
        plugin_menu.setObjectName("pysample_menu")

    menu_action = plugin_menu.addAction(action_name)
    menu_action.triggered.connect(trigger_func)


def show_main_dlg():
    global hgp_dialog, hgp_actions
    global hand_rigger_callback, hand_rigger_callback_list

    if not hasattr(RLPy.RISkeletonComponent, "BreakClip"):
        RLPy.RUi.ShowMessageBox("Hand Gestures Puppeteering", "In order for this script to work as intended, please upgrade to iClone 7.83.", RLPy.EMsgButton_Ok)

    if hgp_dialog is None:
        # create dialog
        hgp_dialog = {}
        hgp_dialog["qml module"] = HandRigQmlModule()
        dialog_globals = create_qml_embedded_dialog('Hand Gestures Puppeteering',
                                                    'Hand Gestures Puppeteering',
                                                    '/resource/qml/handrigger.qml',
                                                    'handRigger',
                                                    hgp_dialog["qml module"])
        hgp_dialog["main dialog"] = dialog_globals[0]
        hgp_dialog["main pyside dialog"] = dialog_globals[1]
        hgp_dialog["main qml"] = dialog_globals[2]

        register_dialog_callback()
        register_hand_rigger_callback()

        hgp_actions["QT space"] = RLPy.RUi.AddHotKey("Space")
        hgp_actions["space"] = wrapInstance(int(hgp_actions["QT space"]), PySide2.QtWidgets.QAction)
        hgp_actions["space"].triggered.connect(space_function)

        hgp_actions["QT escape"] = RLPy.RUi.AddHotKey("Escape")
        hgp_actions["escape"] = wrapInstance(int(hgp_actions["QT escape"]), PySide2.QtWidgets.QAction)
        hgp_actions["escape"].triggered.connect(stop_mode)

    hgp_dialog["main dialog"].Show()


def update_hand_rigger_state():
    global hgp_dialog, hand_rigger

    if hand_rigger is not None:
        hand_rigger.update_state()
        hgp_dialog["main qml"].updateHandRiggerState(hand_rigger.get_state())


def set_hand_rigger_state(state):
    global hgp_dialog, hand_rigger

    if hand_rigger is not None:
        hand_rigger.set_state(state)
        hgp_dialog["main qml"].updateHandRiggerState(hand_rigger.get_state())


def preview():
    global hand_rigger, hgp_dialog, hgp_timer

    hgp_timer["start time"] = RLPy.RGlobal.GetTime()

    if hand_rigger is not None:
        if hand_rigger.get_state() == HandRiggerState.Ready or hand_rigger.get_state() == HandRiggerState.ReadyToRun:
            check_play_time()
            run(HandRiggerState.Preview)
            hgp_dialog["main qml"].enableControls(False)
            hgp_dialog["main qml"].showPreviewRecord(False, "Previewing.....\nPress Spacebar to Stop")
        else:
            stop_mode()


def record():
    global hand_rigger, hgp_dialog

    if hand_rigger is not None:
        if hand_rigger.get_state() == HandRiggerState.Ready or hand_rigger.get_state() == HandRiggerState.ReadyToRun:
            check_play_time()
            run(HandRiggerState.Record)
            hgp_dialog["main qml"].enableControls(False)
            hgp_dialog["main qml"].showPreviewRecord(False, "Recording.....\nPress Spacebar to Stop")
        else:
            stop_mode()


def space_function():
    global mode

    if mode == Mode.Preview:
        preview()
    elif mode == Mode.Record:
        record()
    elif mode == Mode.Stopped:
        play_timeline()


def stop_preview_record():
    global mode, hand_rigger

    if hand_rigger is not None:
        if hand_rigger.get_state() != HandRiggerState.Preview and hand_rigger.get_state() != HandRiggerState.Record:
            return

    if mode == Mode.Preview:
        preview()
    elif mode == Mode.Record:
        record()


def stop_mode():
    global hgp_dialog, mode

    run(HandRiggerState.Ready)
    hgp_dialog["main qml"].showPreviewRecord(True, "")
    hgp_dialog["main qml"].enableControls(True)
    mode = Mode.Stopped

def check_play_time():
    start_time = RLPy.RGlobal.GetStartTime()
    end_time = RLPy.RGlobal.GetEndTime()
    if hasattr( RLPy.RGlobal, "GetPreviewStartTime" ):
        start_time = RLPy.RGlobal.GetPreviewStartTime()
        end_time = RLPy.RGlobal.GetPreviewEndTime()
    if RLPy.RGlobal.GetTime() == end_time:
        RLPy.RGlobal.SetTime(start_time)


def run(state):
    global hgp_dialog, hand_rigger

    if hand_rigger is not None:
        hand_rigger.run(state)
        hgp_dialog["main qml"].updateHandRiggerState(hand_rigger.get_state())

        if hand_rigger.state == HandRiggerState.Preview or hand_rigger.state == HandRiggerState.Record:
            timer_send_data.Start()
        else:
            timer_send_data.Stop()


def on_show():
    global hand_rigger

    if hand_rigger is None:
        hand_rigger = HandRigger()

    update_hand_rigger_state()

    hgp_dialog["main qml"].updateUI(
        int(hand_rigger.join_mode),
        int(hand_rigger.blend_mode),
        hand_rigger.clip_transition_frames
    )

    load_preset()


def on_hide():
    global hand_rigger

    if hand_rigger is not None:
        if hand_rigger.get_state() is HandRiggerState.Preview or hand_rigger.get_state() is HandRiggerState.Record:
            set_hand_rigger_state(HandRiggerState.Disable)
        # del hand_rigger
        # hand_rigger = None


def on_close():
    global hgp_dialog, hgp_actions, hand_rigger_callback_list

    stop_mode()

    # clear callbacks
    # hgp_dialog["main dialog"].UnregisterAllEventCallbacks() # BUG: causes crash in 7.8
    hgp_dialog["main dialog"].UnregisterEventCallback(hgp_dialog["callback id"])
    RLPy.REventHandler.UnregisterCallbacks(hand_rigger_callback_list)
    hand_rigger_callback_list = []

    # clear hotkeys
    RLPy.RUi.RemoveHotKey(hgp_actions["QT space"])
    RLPy.RUi.RemoveHotKey(hgp_actions["QT escape"])

    hgp_dialog = None


class DialogCallback(RLPy.RDialogCallback):
    def __init__(self):
        RLPy.RDialogCallback.__init__(self)
        self.show_fptr = None
        self.hide_fptr = None
        self.close_fptr = None

    def OnDialogShow(self):
        if self.show_fptr is not None:
            self.show_fptr()

    def OnDialogHide(self):
        if self.hide_fptr is not None:
            self.hide_fptr()

    def OnDialogClose(self):
        if self.close_fptr is not None:
            self.close_fptr()
        return True

    def register_show_callback(self, show_function):
        self.show_fptr = show_function

    def register_hide_callback(self, hide_function):
        self.hide_fptr = hide_function

    def register_close_callback(self, close_function):
        self.close_fptr = close_function


class HandRiggerCallback(RLPy.REventCallback):
    def __init__(self):
        RLPy.REventCallback.__init__(self)

    def OnObjectSelectionChanged(self):
        update_hand_rigger_state()

    def OnStopped(self):
        stop_preview_record()


def register_dialog_callback():
    global hgp_dialog

    hgp_dialog["callback"] = DialogCallback()
    hgp_dialog["callback"].register_show_callback(on_show)
    hgp_dialog["callback"].register_hide_callback(on_hide)
    hgp_dialog["callback"].register_close_callback(on_close)
    hgp_dialog["callback id"] = hgp_dialog["main dialog"].RegisterEventCallback(hgp_dialog["callback"])


def register_hand_rigger_callback():
    global hand_rigger_callback, hand_rigger_callback_list

    hand_rigger_callback = HandRiggerCallback()
    callback_id = RLPy.REventHandler.RegisterCallback(hand_rigger_callback)
    hand_rigger_callback_list.append(callback_id)


def adjust_gesture_dialog(gesture_id):
    global hgp_dialog

    hgp_dialog["adjust gesture"] = RLPy.RUi.CreateRDialog()
    hgp_dialog["adjust gesture"].SetModal(True)
    hgp_dialog["adjust gesture"].SetWindowTitle("Adjust Gesture " + ["O", "D", "E", "F", "A", "B", "C"][gesture_id])

    qt_dialog = wrapInstance(int(hgp_dialog["adjust gesture"].GetWindow()), PySide2.QtWidgets.QDialog)
    qt_dialog.setFixedWidth(250)
    right_hand_button = PySide2.QtWidgets.QPushButton("Replace with Right Hand Gesture")
    left_hand_button = PySide2.QtWidgets.QPushButton("Replace with Left Hand Gesture")
    reset_button = PySide2.QtWidgets.QPushButton("Reset to Default Gesture")
    screenshot_button = PySide2.QtWidgets.QPushButton("Screenshot to Icon")
    load_icon_button = PySide2.QtWidgets.QPushButton("Change Icon Image...")

    right_hand_button.setFixedHeight(24)
    left_hand_button.setFixedHeight(24)
    reset_button.setFixedHeight(24)
    screenshot_button.setFixedHeight(24)
    load_icon_button.setFixedHeight(24)

    right_hand_button.clicked.connect(lambda: replace_gesture(True, gesture_id))
    left_hand_button.clicked.connect(lambda: replace_gesture(False, gesture_id))
    reset_button.clicked.connect(lambda: reset_gesture(gesture_id))
    screenshot_button.clicked.connect(lambda: screenshot_to_icon(gesture_id))
    load_icon_button.clicked.connect(lambda: change_icon(gesture_id))

    layout = qt_dialog.layout()
    for element in [right_hand_button, left_hand_button, reset_button, screenshot_button, load_icon_button]:
        layout.addWidget(element)

    hgp_dialog["adjust gesture"].Show()


def screenshot_to_icon(gesture_id):
    global hgp_dialog

    screenshot = viewport_screenshot(64, 64)
    screenshot = round_pixmap(screenshot)
    file_name = f"{tempfile.gettempdir()}\\hgp_icon_{gesture_id}.png"
    screenshot.save(file_name)
    hgp_dialog["main qml"].changeIcon(gesture_id, file_name)

    hgp_dialog["adjust gesture"].Close()
    save_preset()


def round_pixmap(pixmap):
    mask = QtGui.QPixmap(f"{os.path.dirname(__file__)}/resource/qml/images/Mask.png")
    pixmap.setMask(mask.mask())
    return pixmap


def change_icon(gesture_id):
    global hgp_dialog, icon_file_path

    file_path = RLPy.RUi.OpenFileDialog("Image File(*.jpg; *.jpeg; *.bmp; *.gif; *.png)", icon_file_path)

    if file_path:
        # Record the new file path
        head, tail = os.path.split(file_path)
        icon_file_path = head
        # Read image file
        f = open(file_path, "rb")
        data = f.read()
        f.close()
        # Convert image binary to Pixmap
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(data)
        pixmap = pixmap.scaled(64, 64)
        pixmap = round_pixmap(pixmap)
        # Save the Pixmap as PNG
        file_name = f"{tempfile.gettempdir()}\\hgp_icon_{gesture_id}.png"
        pixmap.save(file_name, 'png')
        # Change the icon on the QML side
        hgp_dialog["main qml"].changeIcon(gesture_id, file_name)

    hgp_dialog["adjust gesture"].Close()
    save_preset()


def replace_gesture(right, gesture_id):
    global hgp_dialog, hand_rigger

    key_data = [
        0, 0, 0, 0, 0, 0,  # 0: forearm
        0, 0, 0, 0, 0, 0,  # 1: hand
        0, 0, 0, 0, 0, 0,  # 2: right_hand_thumb_1
        0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0,  # 5: right_in_hand_index
        0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0,  # 8: right_in_hand_middle
        0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0,  # 11: right_in_hand_ring
        0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0,  # 14 right_in_hand_pinky
        0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, ]

    avatar = RLPy.RScene.GetSelectedObjects()[0]
    motion_bones = avatar.GetSkeletonComponent().GetMotionBones()

    # get [forearm/hand] transform
    hand_bone_count = 0
    for bone in motion_bones:
        bone_data_idx = -1
        bone_name = bone.GetName()
        if ((bone_name == "RL_R_Forearm") and right) or ((bone_name == "RL_L_Forearm") and not right):
            bone_data_idx = 0
        elif ((bone_name == "RL_R_Hand") and right) or ((bone_name == "RL_L_Hand") and not right):
            bone_data_idx = 1

        if bone_data_idx > 0:
            translate, euler_angle = BoneWorldTransform(bone)
            key_data[6*bone_data_idx+0] = translate.x
            key_data[6*bone_data_idx+1] = translate.y
            key_data[6*bone_data_idx+2] = translate.z
            key_data[6*bone_data_idx+3] = euler_angle.x  # degree
            key_data[6*bone_data_idx+4] = euler_angle.y  # degree
            key_data[6*bone_data_idx+5] = euler_angle.z  # degree
            hand_bone_count += 1

            if hand_bone_count == 2:
                break

    # modify finger-bone transform
    prefix = "RL_R_Finger" if right else "RL_L_Finger"
    for bone in motion_bones:
        if(prefix in bone.GetName()):
            for finger in range(5):
                for joint in range(3):
                    if bone.GetName() == f"{prefix}{finger}{joint}":
                        joint_index = 12 + 18*finger + 6*joint  # 12: forearm & hand
                        translate, euler_angle = BoneWorldTransform(bone)
                        key_data[joint_index] = translate.x
                        key_data[joint_index+1] = translate.y
                        key_data[joint_index+2] = translate.z
                        key_data[joint_index+3] = euler_angle.x  # degree
                        key_data[joint_index+4] = euler_angle.y  # degree
                        key_data[joint_index+5] = euler_angle.z  # degree

    if not right:
        key_data = hand_rigger.mirror_hand_data(key_data)

    hand_rigger.replace_gesture(gesture_id, key_data)
    screenshot_to_icon(gesture_id)
    save_preset()


def BoneLocalTransform(bone):
    local_transform = bone.LocalTransform()
    rot_matrix = local_transform.Rotate()
    translate = local_transform.T()

    rx = ry = rz = 0
    euler_angle_result = rot_matrix.ToEulerAngle(RLPy.EEulerOrder_XYZ, rx, ry, rz)
    euler_angle = RLPy.RVector3(euler_angle_result[0]*RLPy.RMath.CONST_RAD_TO_DEG,
                                euler_angle_result[1]*RLPy.RMath.CONST_RAD_TO_DEG,
                                euler_angle_result[2]*RLPy.RMath.CONST_RAD_TO_DEG)
    return translate, euler_angle  # angle (degree)


def BoneWorldTransform(bone):
    world_transform = bone.WorldTransform()
    rot_matrix = world_transform.Rotate()
    translate = world_transform.T()

    rx = ry = rz = 0
    euler_angle_result = rot_matrix.ToEulerAngle(RLPy.EEulerOrder_XYZ, rx, ry, rz)
    euler_angle = RLPy.RVector3(euler_angle_result[0]*RLPy.RMath.CONST_RAD_TO_DEG,
                                euler_angle_result[1]*RLPy.RMath.CONST_RAD_TO_DEG,
                                euler_angle_result[2]*RLPy.RMath.CONST_RAD_TO_DEG)
    return translate, euler_angle  # angle (degree)


def play_timeline():
    if RLPy.RGlobal.IsPlaying():
        RLPy.RGlobal.Pause()
    else:
        RLPy.RGlobal.Play(RLPy.RGlobal.GetTime(), RLPy.RGlobal.GetEndTime())


def load_preset_dialog():
    global preset_file_path

    file_path = RLPy.RUi.OpenFileDialog("Preset Files(*.hgpp)", preset_file_path)

    load_preset_dialog
    if file_path:
        # Record the new preset file path
        head, tail = os.path.split(file_path)
        preset_file_path = head
        # Load it and save it in temp
        load_preset(file_path)
        save_preset()


def load_preset(file_path=temp_preset_file_path):
    global hgp_dialog, hand_rigger

    if os.path.isfile(file_path) is False:
        file_path = default_preset_file_path

    # Read the json data from file
    f = open(file_path, "r")
    data = f.read()
    f.close()
    preset = json.loads(data)

    # Apply the data
    i = 0
    for entry in preset:
        # Replace the gesture key
        hand_rigger.replace_gesture(i, entry["key"])
        # Convert Base64 image to Pixmap
        byte_array = QByteArray().fromBase64(entry["icon"])
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(byte_array)
        # Save the Pixmap as PNG
        file_name = f"{tempfile.gettempdir()}\\hpg_icon_{i}.png"
        pixmap.save(file_name)
        # Change the icon on the QML side
        hgp_dialog["main qml"].changeIcon(i, file_name)
        i += 1

    save_preset()


def reset_gesture(gesture_id):
    global hgp_dialog, hand_rigger

    # Read the json data from file
    f = open(default_preset_file_path, "r")
    data = f.read()
    f.close()
    preset = json.loads(data)
    entry = preset[gesture_id]

    hand_rigger.replace_gesture(gesture_id, entry["key"])
    # Convert Base64 image to Pixmap
    byte_array = QByteArray().fromBase64(entry["icon"])
    pixmap = QtGui.QPixmap()
    pixmap.loadFromData(byte_array)
    # Save the Pixmap as PNG
    file_name = f"{tempfile.gettempdir()}\\hpg_icon_{gesture_id}.png"
    pixmap.save(file_name)
    # Change the icon on the QML side
    hgp_dialog["main qml"].changeIcon(gesture_id, file_name)

    hgp_dialog["adjust gesture"].Close()
    save_preset()


def save_preset(file_path=temp_preset_file_path):
    global hgp_dialog, hand_rigger
    '''
    Add a Hand Gestures Puppeteering preset file with the following data structure:
    [
        {
            'id': 0,
            'icon': QPixmap
            'key' : [0,0,0,0,0,0,0,0,0,0]
        }
    ]
    '''
    preset = []
    icon_links = hgp_dialog["main qml"].iconLinks()
    keys = hand_rigger.all_keys()
    i = 0
    for link in icon_links.toVariant():
        entry = {"id": i, "key": keys[i]}
        # Read the image binary data
        f = None
        if "file" in link:
            link = link.replace("file:", "")
            f = open(link, "rb")
        else:
            f = open(f"{os.path.dirname(__file__)}/resource/qml/{link}", "rb")
        data = f.read()
        f.close()
        # Convert binary to Pixmap
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(data)
        # Convert Pixmap to base64
        byte_array = QByteArray()
        buffer = QBuffer(byte_array)
        buffer.open(QIODevice.WriteOnly)
        pixmap.save(buffer, 'PNG')
        base64 = buffer.data().toBase64()
        entry["icon"] = base64.data().decode("utf8")
        # Append entry into the preset file for each key
        preset.append(entry)
        i += 1
    # Store the preset file
    f = open(file_path, "w")
    f.write(json.dumps(preset))
    f.close()


def save_preset_dialog():
    global preset_file_path

    file_path = RLPy.RUi.SaveFileDialog("Preset Files(*.hgpp)", preset_file_path)

    if file_path:
        # Record the new preset file path
        head, tail = os.path.split(file_path)
        preset_file_path = head
        # Save the preset
        save_preset(file_path)
        # Confirm preset file save
        RLPy.RUi.ShowMessageBox("Hand Gestures Puppeteering", f"Preset file has been saved:\n\n\t{file_path}", RLPy.EMsgButton_Ok)


def reset_to_defaults_dialog():
    global hgp_dialog, hand_rigger

    response = RLPy.RUi.ShowMessageBox(
        "Reset Preset",
        "Reset all gesture points to their default values?",
        RLPy.EMsgButton_Yes | RLPy.EMsgButton_No)

    if response == RLPy.EMsgButton_Yes:
        hgp_dialog["main qml"].resetIcons()
        load_preset(default_preset_file_path)
        save_preset()


def viewport_screenshot(width, height):
    '''
    Grabs a screen shot of the viewport render region and returns a Qt Pixmap.
    This is a rather flimsy implementation -changes to the render screen ratio can expose additional brittleness
    '''
    main_window_address = RLPy.RUi.GetMainWindow()
    main_window = wrapInstance(int(main_window_address), QtWidgets.QWidget)

    # iClone viewport is situated in the "centralwidget" Qt object
    viewport = main_window.findChild(QtWidgets.QWidget, "centralwidget")
    viewport_parts = viewport.findChildren(QtWidgets.QWidget, "")
    render_view = viewport_parts[0]

    # iClone doesn't have an object name for the render view so we have to hack a solution to find it
    for part in viewport_parts:
        if part.geometry().height() > viewport.geometry().height() * 0.20 or part.geometry().width() > viewport.geometry().width() * 0.20:
            if part.geometry().width() < render_view.geometry().width() or part.geometry().height() < render_view.geometry().height():
                render_view = part

    # Screenshot to Qt pixmap
    size = min(render_view.geometry().height(), render_view.geometry().width()) * 0.5
    left = render_view.width() * 0.5 - size * 0.5
    top = render_view.height() * 0.5 - size * 0.5
    crop = 0  # Pixels from the edges
    pixmap = QtGui.QPixmap.grabWindow(render_view.winId(), left + crop * 0.5, top + crop * 0.5, size - crop, size - crop)

    return pixmap.scaled(width, height, Qt.IgnoreAspectRatio, Qt.TransformationMode.FastTransformation)


def set_transition_frames(frames):
    global hand_rigger

    hand_rigger.set_clip_transition_frames(frames)


class HandRigQmlModule(PySide2.QtCore.QObject):
    @PySide2.QtCore.Slot('QVariantList', result='QVariantList')
    def calculate_weights(self, square_dist):
        global hand_rigger
        if hand_rigger is not None:
            return hand_rigger.calculate_weights(square_dist)

    @PySide2.QtCore.Slot(int)
    def set_blend_mode(self, mode):
        global hgp_dialog, hand_rigger
        if hand_rigger is not None:
            hand_rigger.set_blend_mode(mode)
            hgp_dialog["main qml"].setBlendMode(int(hand_rigger.blend_mode))

    @PySide2.QtCore.Slot(int)
    def set_join_mode(self, mode):
        global hand_rigger
        if hand_rigger is not None:
            hand_rigger.set_join_mode(mode)

    @PySide2.QtCore.Slot(int)
    def replace_gesture(self, gesture_id):
        adjust_gesture_dialog(gesture_id)

    @PySide2.QtCore.Slot()
    def record_mode(self):
        global mode, hand_rigger
        if hand_rigger is not None:
            hand_rigger.set_state(HandRiggerState.ReadyToRun)
        mode = Mode.Record
        RLPy.RGlobal.Pause()

    @PySide2.QtCore.Slot()
    def preview_mode(self):
        global mode, hand_rigger
        if hand_rigger is not None:
            hand_rigger.set_state(HandRiggerState.ReadyToRun)
        mode = Mode.Preview
        RLPy.RGlobal.Pause()

    @PySide2.QtCore.Slot()
    def load_preset(self):
        load_preset_dialog()

    @PySide2.QtCore.Slot()
    def save_preset(self):
        save_preset_dialog()

    @PySide2.QtCore.Slot()
    def reset_to_defaults(self):
        reset_to_defaults_dialog()

    @PySide2.QtCore.Slot(int)
    def set_transition_frames(self, frames):
        set_transition_frames(frames)


def run_script():
    initialize_plugin()
