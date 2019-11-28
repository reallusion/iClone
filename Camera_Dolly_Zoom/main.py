# Copyright 2019 The Reallusion Authors. All Rights Reserved.
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

import RLPy
import os
from PySide2 import *
from PySide2.shiboken2 import wrapInstance

cdz_ui = {}  # User interface globals
cdz_callbacks = {}  # Global for callbacks, events, and timers
cdz_undo = {}  # Container for undo information


def relational_position(parent_obj, child_obj):
    '''
    Converts world-space point to local-space position relative to the transform-space.

    Args:
        parent_obj (RIObject): Object with transform-space for world to local point conversion.
        child_obj (RIObject): Object as the point in world-space that needs to be converted to local-space.

    Returns:
        RVector3: The world-space point converted to local-space.
    '''
    parent_transform = parent_obj.WorldTransform()
    child_transform = child_obj.WorldTransform()

    parent_matrix = parent_transform.Matrix()
    child_matrix = child_transform.Matrix()

    local_position = child_matrix.GetTranslate() - parent_matrix.GetTranslate()  # Can also use transform.T()
    parent_matrix.SetTranslate(RLPy.RVector3.ZERO)  # Zero out transform matrix translation

    # New matrix4 for the local position
    point_world_matrix = RLPy.RMatrix4()
    point_world_matrix.MakeIdentity()
    point_world_matrix.SetTranslate(local_position)

    # Convert local space to transform space
    point_transform_matrix = point_world_matrix * parent_matrix.Inverse()

    # Return the translation element of the combined matrix4
    return point_transform_matrix.GetTranslate()


def dolly_zoom_offset(target_focal_length, start_focal_length, start_distance):
    '''
    Calculate the camera distance to simulate the dolly zoom effect

    Args:
        target_focal_length (float): the desired focal-length for which a new distance is calculated for
        start_focal_length (float): the current focal-length of the camera
        start_distance (float): the current distance between the view the target object

    Returns:
        Float: a new distance between the view and the target object based on the target focal-length
    '''
    target_distance = target_focal_length / start_focal_length * start_distance
    offset = target_distance - start_distance
    return offset


def local_move(obj, translation):
    '''
    Calculate the world-space position for an object that is locally translated

    Args:
        obj (RIObject): the iClone object that serves as the transform space
        translation (RVector3): point in local-space

    Returns:
        RVector3: the world-space position for the object after local translation is applied
    '''
    transform = obj.WorldTransform()
    matrix = transform.Matrix()
    matrix.SetTranslate(RLPy.RVector3.ZERO)  # Zero out transform matrix translation

    # New matrix for the local translation
    local_matrix = RLPy.RMatrix4()
    local_matrix.MakeIdentity()
    local_matrix.SetTranslate(translation)

    # Get the world-space offset position for the local movement
    offset_matrix = local_matrix * matrix

    # Return the final position for the object
    return transform.T() - offset_matrix.GetTranslate()


class TimerCallback(RLPy.RPyTimerCallback):
    def __init__(self):
        RLPy.RPyTimerCallback.__init__(self)

    def Timeout(self):
        update_ui()


class DialogEventCallback(RLPy.RDialogCallback):
    def __init__(self):
        RLPy.RDialogCallback.__init__(self)

    def OnDialogHide(self):
        pass

    def OnDialogClose(self):
        global cdz_callbacks, cdz_ui

        cdz_callbacks["timer"].UnregisterPyTimerCallback()
        # Clear all globals
        cdz_ui.clear()
        cdz_callbacks.clear()
        return True


def update_ui():
    camera = RLPy.RScene.GetCurrentCamera()
    keyable = True

    if camera.GetName() == "Preview Camera":
        cdz_ui["widget"].currentCamera.clear()
        cdz_ui["widget"].focalLength.setEnabled(False)
        cdz_ui["widget"].focalLengthSlider.setEnabled(False)
        cdz_ui["widget"].focalLengthLabel.setEnabled(False)
        keyable = False
    else:
        cdz_ui["widget"].currentCamera.setText(camera.GetName())
        cdz_ui["widget"].focalLength.setEnabled(True)
        cdz_ui["widget"].focalLengthSlider.setEnabled(True)
        cdz_ui["widget"].focalLengthLabel.setEnabled(True)

        cdz_ui["widget"].focalLength.blockSignals(True)
        focal_length = camera.GetFocalLength(RLPy.RGlobal.GetTime())
        cdz_ui["widget"].focalLengthSlider.setValue(round(focal_length * 100, 2))
        cdz_ui["widget"].focalLength.blockSignals(False)

    items = RLPy.RScene.GetSelectedObjects()

    if len(items) > 0:
        object_type = items[0].GetType()

        # If the object is valid: avatar or prop, then set it as the target object
        if object_type == RLPy.EObjectType_Avatar or object_type == RLPy.EObjectType_Prop:
            distance = relational_position(camera, items[0])
            cdz_ui["widget"].targetObject.setText(items[0].GetName())
            cdz_ui["widget"].viewDistance.setText(str(distance.z))
            cdz_ui["widget"].keyDollyZoom.setEnabled(keyable)
            return

    cdz_ui["widget"].targetObject.clear()
    cdz_ui["widget"].viewDistance.clear()
    cdz_ui["widget"].keyDollyZoom.setEnabled(False)


def lerp(value1, value2, amount):
    return value1 + (value2 - value1) * amount


def update_focal_length_slider(x):
    global cdz_ui

    camera = RLPy.RScene.GetCurrentCamera()

    cdz_ui["widget"].focalLengthSlider.setValue(x * 100)
    camera.SetFocalLength(RLPy.RGlobal.GetTime(), x)

    # Force update iClone's native UI
    RLPy.RGlobal.SetTime(RLPy.RGlobal.GetTime() + RLPy.RTime(1))
    RLPy.RGlobal.SetTime(RLPy.RGlobal.GetTime() - RLPy.RTime(1))


def update_focal_length(x):
    global cdz_ui

    cdz_ui["widget"].focalLength.setValue(x * 0.01)


def key_camera_distance():
    camera = RLPy.RScene.GetCurrentCamera()

    if camera.GetName() == "Preview Camera":
        RLPy.RUi.ShowMessageBox(
            "Camera Dolly Zoom - Operation Error",
            "This script is not compatible with the Preview Camera.  Please create a new camera and try again.",
            RLPy.EMsgButton_Ok)
        return

    camera_transform = camera.WorldTransform()
    camera_position = camera_transform.T()

    # Assign time and frame variables we'll need to animate the camera
    current_time = RLPy.RGlobal.GetTime()
    fps = RLPy.RGlobal.GetFps()
    start_frame = RLPy.RTime.GetFrameIndex(current_time, fps)
    end_frame = start_frame + cdz_ui["widget"].frameDuration.value()
    end_time = RLPy.RTime().IndexedFrameTime(end_frame, fps)

    # Calculate the offset position for the camera based on the target focal-length
    start_focal_length = camera.GetFocalLength(current_time)
    start_distance = float(cdz_ui["widget"].viewDistance.text())
    end_distance = dolly_zoom_offset(cdz_ui["widget"].targetFocalLength.value(), start_focal_length, start_distance)
    end_position = local_move(camera, RLPy.RVector3(0, 0, end_distance))

    # Key the begining position for the camera position
    t_control = camera.GetControl("Transform")
    t_data_block = t_control.GetDataBlock()
    t_data_block.SetData("Position/PositionX", current_time, RLPy.RVariant(camera_position.x))
    t_data_block.SetData("Position/PositionY", current_time, RLPy.RVariant(camera_position.y))
    t_data_block.SetData("Position/PositionZ", current_time, RLPy.RVariant(camera_position.z))
    t_control.SetKeyTransition(current_time, RLPy.ETransitionType_Linear, 1.0)

    # Key the final position for the camera position
    t_data_block.SetData("Position/PositionX", end_time, RLPy.RVariant(end_position.x))
    t_data_block.SetData("Position/PositionY", end_time, RLPy.RVariant(end_position.y))
    t_data_block.SetData("Position/PositionZ", end_time, RLPy.RVariant(end_position.z))
    t_control.SetKeyTransition(end_time, RLPy.ETransitionType_Linear, 1.0)

    # DOF keys for Focus Distance (optional)
    if cdz_ui["widget"].keyFocusDistance.isChecked():
        dof = camera.GetDOFData()
        cdz_undo["start_dof"] = camera.GetDOFData()
        dof.SetEnable(True)
        dof.SetFocus(-start_distance)

        # Set the first DOF key
        key = RLPy.RKey()
        key.SetTime(current_time)
        camera.AddDofKey(key, dof)

        # Readjust the DOF and key objects and set another key
        dof.SetFocus(-(start_distance + end_distance))
        key.SetTime(end_time)
        camera.AddDofKey(key, dof)

    # The focal-length parameter must be keyed on every frame because it uses a preconfigured transition curve that is inaccessible
    for i in range(cdz_ui["widget"].frameDuration.value()+1):
        ratio = i/cdz_ui["widget"].frameDuration.value()
        focal_length = lerp(start_focal_length, cdz_ui["widget"].targetFocalLength.value(), ratio)
        time = RLPy.RTime().IndexedFrameTime(start_frame + i, fps)
        camera.SetFocalLength(time, focal_length)

    # Record custom operation for undo
    record_operation(camera, current_time, cdz_ui["widget"].frameDuration.value(), fps)
    RLPy.RGlobal.Play(current_time, end_time)  # Playback to view the result


def record_operation(camera, start_time, frame_range, fps):
    cdz_undo["camera"] = camera
    cdz_undo["start_time"] = start_time
    cdz_undo["frame_range"] = frame_range
    cdz_undo["fps"] = fps
    # Allow for undoing the last operation
    cdz_ui["widget"].clearDollyZoom.setEnabled(True)


def undo_last_operation():
    # Disable the undo button after the undo operation
    cdz_ui["widget"].clearDollyZoom.setEnabled(False)

    if cdz_undo["camera"].IsValid() is False:
        RLPy.RUi.ShowMessageBox(
            "Camera Dolly Zoom - Error",
            "Clear operation cancelled - the camera can not be found.",
            RLPy.EMsgButton_Ok)
        return

    start_frame = RLPy.RTime.GetFrameIndex(cdz_undo["start_time"], cdz_undo["fps"])
    end_frame = start_frame + cdz_undo["frame_range"]
    end_time = RLPy.RTime().IndexedFrameTime(end_frame, cdz_undo["fps"])

    # Remove the Camera transform key
    t_control = cdz_undo["camera"].GetControl("Transform")
    t_control.RemoveKey(end_time)

    # Remove all DOF keys
    key = RLPy.RKey()
    key.SetTime(cdz_undo["start_time"])
    cdz_undo["camera"].RemoveDofKey(key)
    key.SetTime(end_time)
    cdz_undo["camera"].RemoveDofKey(key)

    # Revert to original DOF settings
    dof_key = RLPy.RKey()
    dof_key.SetTime(cdz_undo["start_time"])
    cdz_undo["camera"].AddDofKey(dof_key, cdz_undo["start_dof"])

    # Remove all focus length keys
    start_focal_length = cdz_undo["camera"].GetFocalLength(cdz_undo["start_time"])

    for i in range(cdz_undo["frame_range"]+1):
        time = RLPy.RTime().IndexedFrameTime(start_frame + i, cdz_undo["fps"])
        cdz_undo["camera"].RemoveFocalLengthKey(time)

    # Revert to original Focal Length settings
    cdz_undo["camera"].SetFocalLength(cdz_undo["start_time"], start_focal_length)

    # Reset the time to when the operation was executed
    RLPy.RGlobal.SetTime(cdz_undo["start_time"])


def show_help_dialog():
    RLPy.RUi.ShowMessageBox(
        "Camera Dolly Zoom - Tips",
        "For optimal results:<br><br>"
        "Make sure the target object is squarely in view of the camera at a noticeable distance apart.<br><br>"
        "Do not translate the target object or the camera prior to operation.<br><br>"
        "<b>Clear Dolly Zoom</b> only removes keys for the last Dolly Zoom operation!",
        RLPy.EMsgButton_Ok)


def show_window():
    global cdz_ui

    if "dialog_window" in cdz_ui:  # If the window already exists...
        if cdz_ui["dialog_window"].IsVisible():
            RLPy.RUi.ShowMessageBox(
                "Camera Dolly Zoom - Operation Error",
                "The current Camera Dolly Zoom session is still running.  You must first close the window to start another session.",
                RLPy.EMsgButton_Ok)
        else:
            cdz_ui["dialog_window"].Show()
        return

    cdz_ui["dialog_window"] = RLPy.RUi.CreateRDialog()
    cdz_ui["dialog_window"].SetWindowTitle("Camera Dolly Zoom")

    # Create Pyside layout for RDialog
    dialog = wrapInstance(int(cdz_ui["dialog_window"].GetWindow()), QtWidgets.QDialog)
    dialog.setFixedWidth(350)

    # Read and set the QT ui file from the script location
    qt_ui_file = QtCore.QFile(os.path.dirname(__file__) + "/Camera_Dolly_Zoom.ui")
    qt_ui_file.open(QtCore.QFile.ReadOnly)
    cdz_ui["widget"] = QtUiTools.QUiLoader().load(qt_ui_file)
    qt_ui_file.close()
    dialog.layout().addWidget(cdz_ui["widget"])

    # Connect button commands
    cdz_ui["widget"].help.clicked.connect(show_help_dialog)
    cdz_ui["widget"].keyDollyZoom.clicked.connect(key_camera_distance)
    cdz_ui["widget"].clearDollyZoom.clicked.connect(undo_last_operation)
    cdz_ui["widget"].focalLength.valueChanged.connect(update_focal_length_slider)
    cdz_ui["widget"].focalLengthSlider.valueChanged.connect(update_focal_length)

    cdz_ui["dialog_window"].Show()

    # Register callbacks
    cdz_callbacks["dialog_events"] = DialogEventCallback()
    cdz_ui["dialog_window"].RegisterEventCallback(cdz_callbacks["dialog_events"])
    cdz_callbacks["timer"] = RLPy.RPyTimer()
    cdz_callbacks["timer"].SetInterval(17)  # Every frame of iClone is 16.66667 ms, which is an interval of 16 - 17
    cdz_callbacks["timer_callback"] = TimerCallback()
    cdz_callbacks["timer"].RegisterPyTimerCallback(cdz_callbacks["timer_callback"])
    cdz_callbacks["timer"].Start()

    update_ui()


def initialize_plugin():
    # Create Pyside interface with iClone main window
    ic_dlg = wrapInstance(int(RLPy.RUi.GetMainWindow()), QtWidgets.QMainWindow)

    # Check if the menu item exists
    plugin_menu = ic_dlg.menuBar().findChild(QtWidgets.QMenu, "pysample_menu")

    if plugin_menu is None:
        # Create Pyside layout for QMenu named "Python Samples" and attach it to the Plugins menu
        plugin_menu = wrapInstance(int(RLPy.RUi.AddMenu("Python Samples", RLPy.EMenu_Plugins)), QtWidgets.QMenu)
        plugin_menu.setObjectName("pysample_menu")  # Setting an object name for the menu is equivalent to giving it an ID

    # Add the "Camera Dolly Zoom" menu item to Plugins > Python Samples
    menu_action = plugin_menu.addAction("Camera Dolly Zoom")

    # Show the dialog window when the menu item is triggered
    menu_action.triggered.connect(show_window)


def run_script():
    initialize_plugin()
