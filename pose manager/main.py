# Copyright 2020 The Reallusion Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License")
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================


import RLPy
from enum import Enum
import os
import json
from PySide2 import *
from PySide2.shiboken2 import wrapInstance
from PySide2.QtCore import Qt, QByteArray, QBuffer, QIODevice

pc_ui = {}
pc_events = {}
pc_lib = []
pc_mask = []


class MaskOperation(Enum):
    CLEAR = 1
    INVERT = 2
    ALL = 3


class MirrorOperation(Enum):
    LEFT = 1
    RIGHT = 2
    BOTH = 3


class SaveDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(SaveDialog, self).__init__(parent)

    def save_library(self):
        global pc_lib
        global pc_ui

        directory, ext = QtWidgets.QFileDialog.getSaveFileName(self, 'Save Files', os.path.dirname(__file__), "Pose Library(*.poslib)", '*.poslib')

        if directory is not '':
            for entry in pc_lib:
                # Convert Pixmap to Byte Array
                byte_array = QByteArray()
                buffer = QBuffer(byte_array)
                buffer.open(QIODevice.WriteOnly)
                entry["preview"].save(buffer, 'PNG')
                encoded = buffer.data().toBase64()
                entry["preview"] = encoded.data().decode("utf8")
            # Write data to file
            f = open(directory, "w")
            f.write(json.dumps(pc_lib))
            f.close()
            # Reload the pose libary
            load_library(directory)


class TimerCallback(RLPy.RPyTimerCallback):
    def __init__(self, callback):
        RLPy.RPyTimerCallback.__init__(self)
        self.callback = callback

    def Timeout(self):
        global pc_events

        self.callback()
        pc_events["timer"].Stop()


def avatar_selection_check(message="Avatar not selected!"):
    items = RLPy.RScene.GetSelectedObjects()

    if len(items) == 1:
        object_type = items[0].GetType()

        if object_type == RLPy.EObjectType_Avatar:
            return items[0]

    RLPy.RUi.ShowMessageBox(
        "Pose Manager - Operation error!",
        message,
        RLPy.EMsgButton_Ok)
    return None


def move_pose_up():
    global pc_lib
    global pc_ui

    index = pc_ui["widget"].list.currentRow()
    entry = pc_lib.pop(index)
    new_index = max(index - 1, 0)
    pc_lib.insert(new_index, entry)
    pc_ui["widget"].list.setCurrentRow(new_index)
    update_window()


def move_pose_down():
    global pc_lib
    global pc_ui

    index = pc_ui["widget"].list.currentRow()
    entry = pc_lib.pop(index)
    new_index = min(index + 1, len(pc_lib))
    pc_lib.insert(new_index, entry)
    pc_ui["widget"].list.setCurrentRow(new_index)
    update_window()


def remove_pose():
    global pc_lib
    global pc_ui

    index = pc_ui["widget"].list.currentRow()
    del pc_lib[index]
    pc_ui["widget"].list.setCurrentRow(index-1)
    update_window()


def rename_pose(item):
    global pc_lib
    global pc_ui

    max_chars = 25  # Limit the length of the pose name.
    index = pc_ui["widget"].list.currentRow()
    name = item.text()
    name = (name[:max_chars] + '..') if len(name) > max_chars else name
    item.setText(name)
    pc_lib[index]["name"] = item.text()


def edit_pose():
    global pc_ui

    item = pc_ui["widget"].list.selectedItems()[0]
    pc_ui["widget"].list.editItem(item)


def update_window(select="normal"):
    global pc_lib
    global pc_ui

    index = pc_ui["widget"].list.currentRow()
    index = max(0, min(index, pc_ui["widget"].list.count()))

    pc_ui["widget"].list.blockSignals(True)
    pc_ui["widget"].list.clear()
    for pose in pc_lib:
        listItem = QtWidgets.QListWidgetItem(pose["name"], pc_ui["widget"].list)
        listItem.setFlags(listItem.flags() | Qt.ItemIsEditable)

    pc_ui["widget"].list.setCurrentRow(index)

    library_exists = pc_ui["widget"].list.currentRow() > -1

    pc_ui["widget"].group_stored_poses.setEnabled(library_exists)
    pc_ui["widget"].group_masking.setEnabled(library_exists)
    pc_ui["widget"].group_right_hand.setEnabled(library_exists)
    pc_ui["widget"].group_left_hand.setEnabled(library_exists)

    if pc_ui["widget"].list.currentRow() != -1:
        pc_ui["widget"].preview.setPixmap(pc_lib[index]["preview"])
        pc_ui["widget"].library_save.setEnabled(True)
        pc_ui["widget"].library_new.setEnabled(True)
    else:
        pc_ui["widget"].preview.setPixmap(QtGui.QPixmap())  # Clear the preview panel
        pc_ui["widget"].library_save.setEnabled(False)
        pc_ui["widget"].library_new.setEnabled(False)
    pc_ui["widget"].list.blockSignals(False)


def get_bone_transform(bone):
    data = {}
    local_transform = bone.LocalTransform()
    local_translation = local_transform.T()
    local_rotation = local_transform.R()

    # Quaternions and Vector3 must be serialized for JSON
    data["r"] = [local_rotation.x, local_rotation.y, local_rotation.z, local_rotation.w]  # Bone Rotations
    data["t"] = [local_translation.x, local_translation.y, local_translation.z]  # Bone Translations

    return data


def center_bone_rotations(animation_clip, bone, time):
    bone_control = animation_clip.GetControl("Layer", bone)
    data_block = bone_control.GetDataBlock()

    data_block.GetControl("Rotation/RotationY").SetValue(time, 0)
    data_block.GetControl("Rotation/RotationZ").SetValue(time, 0)


def set_bone_transform(animation_clip, bone, time, pose, offset, mirror=False, ignoreFilters=False):
    global pc_ui

    bone_control = animation_clip.GetControl("Layer", bone)
    data_block = bone_control.GetDataBlock()

    q_pose = RLPy.RQuaternion(RLPy.RVector4(pose["r"][0], pose["r"][1], pose["r"][2], pose["r"][3]))
    q_offset = RLPy.RQuaternion(RLPy.RVector4(offset["r"][0], offset["r"][1], offset["r"][2], offset["r"][3]))
    q_real = q_pose.Multiply(q_offset.Inverse())
    m_real = q_real.ToRotationMatrix()
    x = y = z = 0
    r_real = m_real.ToEulerAngle(RLPy.EEulerOrder_XYZ, x, y, z)

    # Set key for the bone
    if pc_ui["widget"].rotation_x.isChecked() or ignoreFilters:
        data_block.GetControl("Rotation/RotationX").SetValue(time, r_real[0])
    if pc_ui["widget"].rotation_y.isChecked() or ignoreFilters:
        data_block.GetControl("Rotation/RotationY").SetValue(time, r_real[1] if mirror is False else -r_real[1])
    if pc_ui["widget"].rotation_z.isChecked() or ignoreFilters:
        data_block.GetControl("Rotation/RotationZ").SetValue(time, r_real[2] if mirror is False else -r_real[2])

    if data_block.GetControl("Position/PositionX") is not None:
        data_block.GetControl("Position/PositionX").SetValue(time, pose["t"][0] - offset["t"][0])
        data_block.GetControl("Position/PositionY").SetValue(time, pose["t"][1] - offset["t"][1])
        data_block.GetControl("Position/PositionZ").SetValue(time, pose["t"][2] - offset["t"][2])


def check_mask(name):
    global pc_mask

    for entry in pc_mask:
        if entry in name:
            return True

    return False


def force_update():
    # Force update the viewport and the timeline
    current_time = RLPy.RGlobal.GetTime()
    RLPy.RGlobal.Stop()
    RLPy.RGlobal.SetTime(current_time)


def apply_pose():
    global pc_lib
    global pc_ui
    global pc_mask

    avatar = avatar_selection_check("Please select a valid Avatar to apply a pose.")
    if avatar is not None:
        current_time = RLPy.RGlobal.GetTime()
        clip_time = RLPy.RTime.IndexedFrameTime(1, RLPy.RGlobal.GetFps())  # Clip must occupy more than 1 frame to show the transition region
        motion_bones = avatar.GetSkeletonComponent().GetMotionBones()
        index = pc_ui["widget"].list.currentRow()
        pose = pc_lib[index]
        current_pose = {}

        for bone in motion_bones:
            current_pose[bone.GetName()] = get_bone_transform(bone)

        animation_clip = avatar.GetSkeletonComponent().AddClip(current_time)  # Reset the character to default pose
        avatar.Update()  # Important: Write control data to the bones

        for bone in motion_bones:
            name = bone.GetName()
            masked = check_mask(name)

            if name in pose["bones"]:
                default_data = get_bone_transform(bone)

                if masked:
                    set_bone_transform(animation_clip, bone, clip_time, current_pose[name], default_data, False, True)
                else:
                    set_bone_transform(animation_clip, bone, clip_time, pose["bones"][name], default_data)

        force_update()


def mirror_pose(operation=MirrorOperation.BOTH):
    avatar = avatar_selection_check("Please select a valid Avatar to mirror its pose.")

    if avatar is not None:
        current_time = RLPy.RGlobal.GetTime()
        clip_time = RLPy.RTime.IndexedFrameTime(1, RLPy.RGlobal.GetFps())  # Clip must occupy more than 1 frame to show the transition region
        motion_bones = avatar.GetSkeletonComponent().GetMotionBones()
        bone_mapping = {}

        for bone in motion_bones:  # Record all of the bone transformations
            name = bone.GetName()
            bone_mapping[name] = get_bone_transform(bone)

        animation_clip = avatar.GetSkeletonComponent().AddClip(current_time)  # Clear the current clip
        avatar.Update()  # Important: Write control data to the bones

        default_mapping = {}

        for bone in motion_bones:  # Record all of the bone default positions
            name = bone.GetName()
            default_mapping[name] = get_bone_transform(bone)

        for bone in motion_bones:
            name = bone.GetName()
            opposite_side = ""

            if "_L_" in name and operation is not MirrorOperation.RIGHT:
                opposite_side = name.replace("_L_", "_R_")

            if "_R_" in name and operation is not MirrorOperation.LEFT:
                opposite_side = name.replace("_R_", "_L_")

            if opposite_side in bone_mapping:
                set_bone_transform(animation_clip, bone, clip_time, bone_mapping[opposite_side], default_mapping[opposite_side], True, True)
            else:
                if operation is MirrorOperation.BOTH:
                    set_bone_transform(animation_clip, bone, clip_time, bone_mapping[name], default_mapping[name], True, True)
                else:
                    set_bone_transform(animation_clip, bone, clip_time, bone_mapping[name], default_mapping[name], False, True)

                    if "_L_" not in name and "_R_" not in name:
                        center_bone_rotations(animation_clip, bone, clip_time)

        force_update()


def generate_pose_name(num=0):
    name = "pose{0}".format(num)

    # Recursively add to the suffix number of the name, until it is unique
    for i in range(pc_ui["widget"].list.count()):
        if pc_ui["widget"].list.item(i).text() == name:
            return generate_pose_name(num+1)

    return name


def viewport_screen_shot():
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
    size = min(render_view.geometry().height(), render_view.geometry().width())
    left = render_view.width() * 0.5 - size * 0.5
    top = render_view.height() * 0.5 - size * 0.5
    crop = 0  # Pixels from the edges
    pixmap = QtGui.QPixmap.grabWindow(render_view.winId(), left + crop * 0.5, top + crop * 0.5, size - crop, size - crop)

    return pixmap.scaled(128, 128)


def add_pose(replace=False):
    global pc_events

    avatar = avatar_selection_check("Please select a valid Avatar to save its current pose.")

    if avatar is not None:
        pc_events["selection"] = RLPy.RScene.GetSelectedObjects()
        RLPy.RScene.ClearSelectObjects()  # Temporarily hide the gizmos

        # Create a timer
        pc_events["timer"] = RLPy.RPyTimer()
        pc_events["timer"].SetInterval(60)  # Wait a few frames after the selection is cleared for screen redraw
        # Register a callback
        pc_events["timer_callback"] = TimerCallback(lambda: add_pose_entry(avatar, replace))
        pc_events["timer"].RegisterPyTimerCallback(pc_events["timer_callback"])
        # Start timer
        pc_events["timer"].Start()


def add_pose_entry(avatar=None, replace=False):
    '''
    Add a pose to the current library by recording the rotations of every motion bone.
    Default structure of the for a pose entry is:
        "pc_lib": [
            {   "name": "pose1",
                "preview": QPixmap
                "bones": {
                    "bone01" : {"r": [0.0, 0.0, 0.0, 0.0], "t": [0.0, 0.0, 0.0]},
                    "bone02" : {"r": [0.0, 0.0, 0.0, 0.0], "t": [0.0, 0.0, 0.0]}
                }
            }
        ]
    '''
    global pc_lib
    global pc_ui
    global pc_events

    current_time = RLPy.RGlobal.GetTime()
    motion_bones = avatar.GetSkeletonComponent().GetMotionBones()
    pose = {"name": generate_pose_name(), "preview": viewport_screen_shot(), "bones": {}}

    for bone in motion_bones:
        pose["bones"][bone.GetName()] = get_bone_transform(bone)

    if replace:
        index = pc_ui["widget"].list.currentRow()
        pose["name"] = pc_lib[index]["name"]
        pc_lib[index] = pose
        update_window()
    else:
        pc_lib.append(pose)
        update_window("last")
        pc_ui["widget"].list.setCurrentRow(pc_ui["widget"].list.count() - 1)  # Select the new entry which is also the last entry

    RLPy.RScene.SelectObjects(pc_events["selection"])


def library_new():
    global pc_lib
    global pc_ui

    response = RLPy.RUi.ShowMessageBox(
        "New Library",
        "Creating a new library will erase all pose entries for the current session.  Would you like to continue?",
        RLPy.EMsgButton_Yes | RLPy.EMsgButton_No)

    if response == RLPy.EMsgButton_Yes or response == RLPy.EMsgButton_Ok:
        pc_lib = []
        pc_ui["widget"].name.clear()
        update_window()


def load_library(directory=None):
    global pc_lib
    global pc_ui

    if directory is None:
        file_dialog = QtWidgets.QFileDialog()
        file_dialog.setNameFilter("*.poslib")
        file_dialog.exec()

        if len(file_dialog.selectedFiles()) is 0:
            return

        directory = file_dialog.selectedFiles()[0]

    pc_ui["widget"].name.setText(os.path.splitext(os.path.basename(directory))[0])
    f = open(directory, "r")
    data = f.read()  # Read the data in the file
    f.close()

    # Parse the data and convert Base64 encoded image to QPixmap
    pose_library = json.loads(data)
    for pose in pose_library:
        byte_array = QByteArray().fromBase64(pose["preview"])
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(byte_array)
        pose["preview"] = pixmap

    # Load library and update the window
    pc_lib = pose_library
    update_window()


def set_mask(keys, state):
    global pc_mask

    for key in keys:
        pc_mask.remove(key) if state else pc_mask.append(key)


def CreateIcon(icon_name):
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap(os.path.dirname(__file__) + "/Images/Enabled/" + icon_name + ".svg"), QtGui.QIcon.Active)
    icon.addPixmap(QtGui.QPixmap(os.path.dirname(__file__) + "/Images/Disabled/" + icon_name + ".svg"), QtGui.QIcon.Disabled)
    return icon


def show_window():
    global pc_ui

    if "dialog_window" in pc_ui:  # If the window already exists...
        if pc_ui["dialog_window"].IsVisible():
            RLPy.RUi.ShowMessageBox(
                "Pose Manager - Operation Error",
                "The current Pose Manager session is still running.  You must first close the window to start another session.",
                RLPy.EMsgButton_Ok)
        else:
            pc_ui["dialog_window"].Show()
        return

    pc_ui["dialog_window"] = RLPy.RUi.CreateRDialog()
    pc_ui["dialog_window"].SetWindowTitle("Pose Manager")

    # Create Pyside layout for RDialog
    dialog = wrapInstance(int(pc_ui["dialog_window"].GetWindow()), QtWidgets.QDialog)

    # Read and set the QT ui file from the script location
    qt_ui_file = QtCore.QFile(os.path.dirname(__file__) + "/pose_manager.ui")
    qt_ui_file.open(QtCore.QFile.ReadOnly)
    pc_ui["widget"] = QtUiTools.QUiLoader().load(qt_ui_file)
    qt_ui_file.close()
    dialog.layout().addWidget(pc_ui["widget"])

    # Set background images for mask controls
    pc_ui["widget"].mask_body.setPixmap(QtGui.QPixmap(os.path.dirname(__file__) + "/Images/Puppet.png"))
    pc_ui["widget"].mask_right_hand.setPixmap(QtGui.QPixmap(os.path.dirname(__file__) + "/Images/Hand_R.png"))
    pc_ui["widget"].mask_left_hand.setPixmap(QtGui.QPixmap(os.path.dirname(__file__) + "/Images/Hand_L.png"))

    # Assign button icons
    pc_ui["widget"].add.setIcon(CreateIcon("add-solid"))
    pc_ui["widget"].mirror.setIcon(CreateIcon("adjust"))
    pc_ui["widget"].rename.setIcon(CreateIcon("edit-pencil"))
    pc_ui["widget"].move_up.setIcon(CreateIcon("arrow-thick-up"))
    pc_ui["widget"].move_down.setIcon(CreateIcon("arrow-thick-down"))
    pc_ui["widget"].remove.setIcon(CreateIcon("trash"))
    pc_ui["widget"].replace.setIcon(CreateIcon("refresh"))
    pc_ui["widget"].library_load.setIcon(CreateIcon("folder-outline"))
    pc_ui["widget"].library_save.setIcon(CreateIcon("save-disk"))
    pc_ui["widget"].library_new.setIcon(CreateIcon("folder-outline-add"))
    pc_ui["widget"].clear_mask.setIcon(CreateIcon("close-solid"))
    pc_ui["widget"].invert_mask.setIcon(CreateIcon("minus-solid"))
    pc_ui["widget"].invert_r_fingers.setIcon(CreateIcon("minus-solid"))
    pc_ui["widget"].invert_l_fingers.setIcon(CreateIcon("minus-solid"))
    pc_ui["widget"].mirror_left.setIcon(CreateIcon("step-forward"))
    pc_ui["widget"].mirror_right.setIcon(CreateIcon("step-backward"))

    # Connect pose list commands
    pc_ui["widget"].list.itemChanged.connect(rename_pose)
    pc_ui["widget"].list.itemClicked.connect(apply_pose)
    # pc_ui["widget"].list.itemDoubleClicked.connect(temp)
    pc_ui["widget"].list.itemSelectionChanged.connect(update_window)

    # Connect button commands
    pc_ui["widget"].library_load.clicked.connect(load_library)
    pc_ui["widget"].library_save.clicked.connect(lambda:  SaveDialog().save_library())
    pc_ui["widget"].library_new.clicked.connect(library_new)
    pc_ui["widget"].add.clicked.connect(add_pose)
    pc_ui["widget"].remove.clicked.connect(remove_pose)
    pc_ui["widget"].rename.clicked.connect(edit_pose)
    pc_ui["widget"].move_down.clicked.connect(move_pose_down)
    pc_ui["widget"].move_up.clicked.connect(move_pose_up)
    pc_ui["widget"].replace.clicked.connect(lambda: add_pose(True))
    pc_ui["widget"].mirror.clicked.connect(mirror_pose)
    pc_ui["widget"].mirror_right.clicked.connect(lambda: mirror_pose(MirrorOperation.RIGHT))
    pc_ui["widget"].mirror_left.clicked.connect(lambda: mirror_pose(MirrorOperation.LEFT))

    # Connect mask-related buttons
    pc_ui["widget"].clear_mask.clicked.connect(lambda: modify_mask(MaskOperation.CLEAR))
    pc_ui["widget"].invert_mask.clicked.connect(lambda: modify_mask(MaskOperation.INVERT))
    pc_ui["widget"].invert_r_fingers.clicked.connect(lambda: invert_fingers_mask(True))
    pc_ui["widget"].invert_l_fingers.clicked.connect(lambda: invert_fingers_mask())
    pc_ui["widget"].mask_chest.toggled.connect(lambda x: set_mask(["Spine02"], x))
    pc_ui["widget"].mask_head.toggled.connect(lambda x: set_mask(["Head", "Neck"], x))
    pc_ui["widget"].mask_l_arm.toggled.connect(lambda x: set_mask(["L_Clavicle", "L_UpperArm"], x))
    pc_ui["widget"].mask_l_calf.toggled.connect(lambda x: set_mask(["L_Calf"], x))
    pc_ui["widget"].mask_l_foot.toggled.connect(lambda x: set_mask(["L_Foot", "L_Toe"], x))
    pc_ui["widget"].mask_l_forearm.toggled.connect(lambda x: set_mask(["L_Forearm"], x))
    pc_ui["widget"].mask_l_hand.toggled.connect(lambda x: set_mask(["L_Hand"], x))
    pc_ui["widget"].mask_l_thigh.toggled.connect(lambda x: set_mask(["L_Thigh"], x))
    pc_ui["widget"].mask_pelvis.toggled.connect(lambda x: set_mask(["Pelvis", "Hips"], x))
    pc_ui["widget"].mask_r_arm.toggled.connect(lambda x: set_mask(["R_Clavicle", "R_UpperArm"], x))
    pc_ui["widget"].mask_r_calf.toggled.connect(lambda x: set_mask(["R_Calf"], x))
    pc_ui["widget"].mask_r_foot.toggled.connect(lambda x: set_mask(["R_Foot", "R_Toe"], x))
    pc_ui["widget"].mask_r_forearm.toggled.connect(lambda x: set_mask(["R_Forearm"], x))
    pc_ui["widget"].mask_r_hand.toggled.connect(lambda x: set_mask(["R_Hand"], x))
    pc_ui["widget"].mask_r_thigh.toggled.connect(lambda x: set_mask(["R_Thigh"], x))
    pc_ui["widget"].mask_waist.toggled.connect(lambda x: set_mask(["Spine01", "Waist"], x))

    # Connect mask-related buttons for left hand
    pc_ui["widget"].mask_l_thumb.toggled.connect(lambda x: set_mask(["RL_L_Finger0"], x))
    pc_ui["widget"].mask_l_index.toggled.connect(lambda x: set_mask(["RL_L_Finger1"], x))
    pc_ui["widget"].mask_l_middle.toggled.connect(lambda x: set_mask(["RL_L_Finger2"], x))
    pc_ui["widget"].mask_l_ring.toggled.connect(lambda x: set_mask(["RL_L_Finger3"], x))
    pc_ui["widget"].mask_l_pinky.toggled.connect(lambda x: set_mask(["RL_L_Finger4"], x))

    # Connect mask-related buttons for right hand
    pc_ui["widget"].mask_r_thumb.toggled.connect(lambda x: set_mask(["RL_R_Finger0"], x))
    pc_ui["widget"].mask_r_index.toggled.connect(lambda x: set_mask(["RL_R_Finger1"], x))
    pc_ui["widget"].mask_r_middle.toggled.connect(lambda x: set_mask(["RL_R_Finger2"], x))
    pc_ui["widget"].mask_r_ring.toggled.connect(lambda x: set_mask(["RL_R_Finger3"], x))
    pc_ui["widget"].mask_r_pinky.toggled.connect(lambda x: set_mask(["RL_R_Finger4"], x))

    pc_ui["dialog_window"].Show()
    update_window()


def modify_mask(operation):
    for ui in [pc_ui["widget"].mask_chest, pc_ui["widget"].mask_head, pc_ui["widget"].mask_l_arm, pc_ui["widget"].mask_l_calf,
               pc_ui["widget"].mask_l_foot, pc_ui["widget"].mask_l_forearm, pc_ui["widget"].mask_l_hand, pc_ui["widget"].mask_l_thigh,
               pc_ui["widget"].mask_pelvis, pc_ui["widget"].mask_r_arm, pc_ui["widget"].mask_r_calf, pc_ui["widget"].mask_r_foot,
               pc_ui["widget"].mask_r_forearm, pc_ui["widget"].mask_r_hand, pc_ui["widget"].mask_r_thigh, pc_ui["widget"].mask_waist,
               pc_ui["widget"].mask_l_thumb, pc_ui["widget"].mask_l_index, pc_ui["widget"].mask_l_middle, pc_ui["widget"].mask_l_ring,
               pc_ui["widget"].mask_l_pinky, pc_ui["widget"].mask_r_thumb, pc_ui["widget"].mask_r_index, pc_ui["widget"].mask_r_middle,
               pc_ui["widget"].mask_r_ring, pc_ui["widget"].mask_r_pinky]:
        if operation == MaskOperation.ALL:
            ui.setChecked(False)
        if operation == MaskOperation.CLEAR:
            ui.setChecked(True)
        if operation == MaskOperation.INVERT:
            ui.setChecked(not ui.isChecked())


def invert_fingers_mask(right_side=False):
    if(right_side):
        for ui in [pc_ui["widget"].mask_r_thumb, pc_ui["widget"].mask_r_index, pc_ui["widget"].mask_r_middle, pc_ui["widget"].mask_r_ring, pc_ui["widget"].mask_r_pinky]:
            ui.setChecked(not ui.isChecked())
    else:
        for ui in [pc_ui["widget"].mask_l_thumb, pc_ui["widget"].mask_l_index, pc_ui["widget"].mask_l_middle, pc_ui["widget"].mask_l_ring, pc_ui["widget"].mask_l_pinky]:
            ui.setChecked(not ui.isChecked())


def initialize_plugin():
    # Create Pyside interface with iClone main window
    ic_dlg = wrapInstance(int(RLPy.RUi.GetMainWindow()), QtWidgets.QMainWindow)

    plugin_menu = ic_dlg.menuBar().findChild(QtWidgets.QMenu, "pysample_menu")  # Check if the menu item exists
    if plugin_menu is None:

        # Create Pyside layout for QMenu named "Python Samples" and attach it to the Plugins menu
        plugin_menu = wrapInstance(int(RLPy.RUi.AddMenu("Python Samples", RLPy.EMenu_Plugins)), QtWidgets.QMenu)
        plugin_menu.setObjectName("pysample_menu")  # Setting an object name for the menu is equivalent to giving it an ID

    # Check if the menu action already exists
    menu_actions = plugin_menu.actions()
    for i in range(len(menu_actions)):
        if menu_actions[i].text() == "Pose Manager":
            plugin_menu.removeAction(menu_actions[i])  # Remove duplicate actions

    # Set up the menu action
    menu_action = plugin_menu.addAction("Pose Manager")
    menu_action.triggered.connect(show_window)


def run_script():
    initialize_plugin()
