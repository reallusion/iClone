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

# Smooth Camera Follow allows the user to pick a camera/view and a prop/target to follow.
# Use Offset values to create a distance between the view and target.
# Use the Delay value to create a lag between the view and target.

import RLPy
import os
from math import *
from PySide2 import *
from PySide2.shiboken2 import wrapInstance

ui = {}  # User interface globals
events = {}  # Callback event globals
all_cameras = [None]
all_props = [None]


def lerp(value1, value2, amount):
    return value1 + (value2 - value1) * amount


def vector3_lerp(v3_from, v3_to, x):
    return RLPy.RVector3(
        lerp(v3_from.x, v3_to.x, x),
        lerp(v3_from.y, v3_to.y, x),
        lerp(v3_from.z, v3_to.z, x)
    )


def transform_lerp(trans_from, trans_to, x):
    return RLPy.RTransform(  # Scale, Rotation, Translation
        vector3_lerp(trans_from.S(), trans_to.S(), x),
        quaternion_lerp(trans_from.R(), trans_to.R(), x),
        vector3_lerp(trans_from.T(), trans_to.T(), x)
    )


def quaternion_lerp(quat_from, quat_to, f_interpolation):
    f_invert_interpolation = 1 - f_interpolation
    q = RLPy.RQuaternion()
    # Are we on the right (1) side of the graph or the left side (-1)?
    direction = (((quat_from.x * quat_to.x) + (quat_from.y * quat_to.y)
                  ) + (quat_from.z * quat_to.z)) + (quat_from.w * quat_to.w)
    if direction >= 0:
        q.x = (f_invert_interpolation * quat_from.x) + (f_interpolation * quat_to.x)
        q.y = (f_invert_interpolation * quat_from.y) + (f_interpolation * quat_to.y)
        q.z = (f_invert_interpolation * quat_from.z) + (f_interpolation * quat_to.z)
        q.w = (f_invert_interpolation * quat_from.w) + (f_interpolation * quat_to.w)
    else:
        q.x = (f_invert_interpolation * quat_from.x) - (f_interpolation * quat_to.x)
        q.y = (f_invert_interpolation * quat_from.y) - (f_interpolation * quat_to.y)
        q.z = (f_invert_interpolation * quat_from.z) - (f_interpolation * quat_to.z)
        q.w = (f_invert_interpolation * quat_from.w) - (f_interpolation * quat_to.w)
    # Now that we have the lerped coordinates what side of the graph are we on?
    side = (((q.x * q.x) + (q.y * q.y)
             ) + (q.z * q.z)) + (q.w * q.w)
    # We have to adjust the quaternion values depending on the side we are on
    orientation = 1 / sqrt((side))
    q.x *= orientation
    q.y *= orientation
    q.z *= orientation
    q.w *= orientation
    return q


class EventCallback(RLPy.REventCallback):
    def __init__(self):
        RLPy.REventCallback.__init__(self)

    def OnObjectAdded(self):
        update_ui()

    def OnObjectDeleted(self):
        update_ui()


class DialogCallback(RLPy.RDialogCallback):

    def __init__(self):
        RLPy.RDialogCallback.__init__(self)
        self.__closed = False

    def OnDialogHide(self):
        global events
        if self.__closed:
            RLPy.REventHandler.UnregisterCallback(events["callback_id"])
            events.clear()
            ui.clear()

    def OnDialogShow(self):
        try:
            global ui
            if "dialog" in ui and "window" in ui:
                if ui["window"].IsFloating():
                    ui["dialog"].adjustSize()
        except Exception as e:
            print(e)

    def OnDialogClose(self):
        ui["window"].UnregisterAllEventCallbacks()
        self.__closed = True
        return True


def look_at_right_handed(view_position, view_target, view_up_vector, lookup_offset=0):
    # Look at takes two positional vectors and calculates the facing direction
    forward = (view_position - view_target) - RLPy.RVector3(0, 0, lookup_offset)
    forward.Normalize()
    right = view_up_vector.Cross(forward)
    right.Normalize()
    up = forward.Cross(right)

    # Retun a right-handed look-at rotational matrix
    return RLPy.RMatrix3(right.x, right.y, right.z,
                         up.x, up.y, up.z,
                         forward.x, forward.y, forward.z)


def destination_transform():
    # Destination transform is where the camera/view should be at when aligned with the target prop
    global ui

    prop_transform = all_props[ui["widget"].prop.currentIndex()].WorldTransform()
    # Position vector is where the prop is plus the offset values
    pos = prop_transform.T() + RLPy.RVector3(ui["widget"].offset_x.value(), ui["widget"].offset_y.value(), ui["widget"].offset_z.value())
    # Orientation matrix is the camera/view facing the prop position
    orientation = look_at_right_handed(pos, prop_transform.T(), RLPy.RVector3(0, 0, 1), ui["widget"].elevation.value())
    # Extrapolate the Quaternion rotations from the orientation matrix
    rot = RLPy.RQuaternion().FromRotationMatrix(orientation)
    # Return a Transform class with scale, rotation, and positional values
    return RLPy.RTransform(RLPy.RVector3(1, 1, 1), rot, pos)


def key_camera():
    global ui

    # Get the frame and time duration of the target prop only
    fps = RLPy.RGlobal.GetFps()
    start_time = RLPy.RTime.IndexedFrameTime(ui["widget"].start_frame.value(), fps)
    end_time = RLPy.RTime.IndexedFrameTime(ui["widget"].end_frame.value(), fps)

    # How many keys are needed to create the whole animation from start to finish?
    key_interval = ui["widget"].delay.value()
    total_keys = int(RLPy.RMath.Ceil((ui["widget"].end_frame.value() - ui["widget"].start_frame.value()) / key_interval))

    # Show the progress bar
    ui["widget"].progress.setRange(0, total_keys)
    ui["widget"].progress.setHidden(False)
    ui["widget"].message.setHidden(True)

    camera = all_cameras[ui["widget"].camera.currentIndex()]

    # Iterate over every keyframe
    for key in range(0, total_keys):
        current_frame = ui["widget"].start_frame.value() + key * key_interval
        current_time = RLPy.RTime.IndexedFrameTime(int(current_frame), fps)
        view_transform = camera.WorldTransform()
        target_transform = destination_transform()
        # Step forward in the timeline
        RLPy.RGlobal.SetTime(current_time)
        ui["widget"].progress.setValue(key)
        # Lerp between the current camera position and its destination using tautness as the interpolate
        new_transform = transform_lerp(view_transform, target_transform, ui["widget"].tautness.value())
        # Key the camera's transform for animation
        camera.GetControl("Transform").SetValue(current_time, new_transform)

    # Post-process frame reduction
    if ui["widget"].reduction.value() > 0:
        control = camera.GetControl("Transform")
        key_count = control.GetKeyCount()
        interval = ui["widget"].reduction.value() + 1
        key_times = []

        for index in range(0, key_count):
            if index % interval != 0:
                key_times.append(RLPy.RTime())
                control.GetKeyTimeAt(index, key_times[len(key_times) - 1])

        for time in range(0, len(key_times)):
            control.RemoveKey(key_times[time])

    # Hide the progress bar
    ui["widget"].progress.setHidden(True)
    ui["widget"].message.setHidden(False)
    ui["widget"].progress.reset()
    # Playback to see the final result
    RLPy.RGlobal.Play(start_time, end_time)


def setup():
    # Stop the timeline playback as foolproof measure
    RLPy.RGlobal.Stop()
    # Position the camera/view designated by the offset on the in-mark of the timeline
    RLPy.RGlobal.SetTime(RLPy.RGlobal.GetStartTime())
    # camera_controller = camera_control.value.GetControl("Transform")
    camera_controller = all_cameras[ui["widget"].camera.currentIndex()].GetControl("Transform")
    camera_controller.ClearKeys()
    # Position the camera on the start frame
    camera_controller.SetValue(RLPy.RGlobal.GetStartTime(), destination_transform())

    key_camera()


def initialize_plugin():
    # Create Pyside interface with iClone main window
    ic_dlg = wrapInstance(int(RLPy.RUi.GetMainWindow()), QtWidgets.QMainWindow)
    # Check if the menu item exists
    plugin_menu = ic_dlg.menuBar().findChild(QtWidgets.QMenu, "pysample_menu")
    if plugin_menu is None:
        # Create Pyside layout for QMenu named "Python Samples" and attach it to the Plugins menu
        plugin_menu = wrapInstance(int(RLPy.RUi.AddMenu("Python Samples", RLPy.EMenu_Plugins)), QtWidgets.QMenu)
        plugin_menu.setObjectName("pysample_menu")  # Setting an object name for the menu is equivalent to giving it an ID
    # Add the "Smooth Camera Follow" menu item to Plugins > Python Samples
    menu_action = plugin_menu.addAction("Smooth Camera Follow")
    # Show the dialog window when the menu item is triggered
    menu_action.triggered.connect(show_window)


def reset_ui():
    global ui

    # Dropdowns
    ui["widget"].camera.setCurrentIndex(0)
    ui["widget"].prop.setCurrentIndex(0)

    # Sliders
    ui["widget"].delay.setValue(5)
    ui["widget"].tautness.setValue(0.5)
    ui["widget"].reduction.setValue(0)

    # X,Y,Z offset
    ui["widget"].offset_x.setValue(0)
    ui["widget"].offset_y.setValue(0)
    ui["widget"].offset_z.setValue(0)
    ui["widget"].elevation.setValue(0)

    # Frame Duration
    start_frame = RLPy.RTime.GetFrameIndex(RLPy.RGlobal.GetStartTime(), RLPy.RGlobal.GetFps())
    end_frame = RLPy.RTime.GetFrameIndex(RLPy.RGlobal.GetEndTime(), RLPy.RGlobal.GetFps())
    ui["widget"].start_frame.setValue(start_frame)
    ui["widget"].end_frame.setValue(end_frame)

    update_ui()


def update_ui():
    global ui, all_cameras, all_props

    current_camera = all_cameras[ui["widget"].camera.currentIndex()]
    all_cameras = [None]
    cameras = RLPy.RScene.FindObjects(RLPy.EObjectType_Camera)

    ui["widget"].camera.blockSignals(True)
    ui["widget"].camera.clear()
    ui["widget"].camera.addItem("None")

    i = 0
    for camera in cameras:
        if camera.GetName() != "Preview Camera":  # Don't include the preview camera
            all_cameras.append(camera)
            ui["widget"].camera.addItem(camera.GetName())
            if camera == current_camera:
                ui["widget"].camera.setCurrentIndex(i + 1)
            i += 1

    ui["widget"].camera.blockSignals(False)

    prop = all_props[ui["widget"].prop.currentIndex()]
    all_props = [None]
    props = RLPy.RScene.FindObjects(RLPy.EObjectType_Prop)

    ui["widget"].prop.blockSignals(True)
    ui["widget"].prop.clear()
    ui["widget"].prop.addItem("None")

    for i in range(len(props)):
        all_props.append(props[i])
        ui["widget"].prop.addItem(props[i].GetName())
        if props[i] == prop:
            ui["widget"].prop.setCurrentIndex(i + 1)

    ui["widget"].prop.blockSignals(False)

    enabled = True if ui["widget"].prop.currentIndex() > 0 and ui["widget"].camera.currentIndex() > 0 else False

    ui["widget"].follow.setEnabled(enabled)
    ui["widget"].use_current_offset.setEnabled(enabled)

    calculate_total_keys()


def calculate_total_keys():
    total_keys = (ui["widget"].end_frame.value() - ui["widget"].start_frame.value()) / ui["widget"].delay.value() / (ui["widget"].reduction.value() + 1)
    ui["widget"].total_keys.setText(f'Total Keys: {int(total_keys) + 1}')


def use_current_offset():
    global ui

    camera_transform = all_cameras[ui["widget"].camera.currentIndex()].WorldTransform()
    prop_transform = all_props[ui["widget"].prop.currentIndex()].WorldTransform()

    offset = camera_transform.T() - prop_transform.T()

    ui["widget"].offset_x.setValue(offset.x)
    ui["widget"].offset_y.setValue(offset.y)
    ui["widget"].offset_z.setValue(offset.z)


def show_window():
    global ui, events

    if "window" in ui:  # If the window already exists...
        if ui["window"].IsVisible():
            RLPy.RUi.ShowMessageBox(
                "Smooth Camera Follow - Operation Error",
                "The current Smooth Camera Follow session is still running.  You must first close the window to start another session.",
                RLPy.EMsgButton_Ok)
        else:
            ui["window"].Show()
        return

    # Create an iClone Dock Widget
    ui["window"] = RLPy.RUi.CreateRDockWidget()
    ui["window"].SetWindowTitle("Smooth Camera Follow")
    ui["window"].SetAllowedAreas(RLPy.EDockWidgetAreas_RightDockWidgetArea | RLPy.EDockWidgetAreas_LeftDockWidgetArea)

    # Load UI file
    ui_file = QtCore.QFile(os.path.dirname(__file__) + "/Smooth_Camera_Follow.ui")
    ui_file.open(QtCore.QFile.ReadOnly)
    ui["widget"] = QtUiTools.QUiLoader().load(ui_file)
    ui_file.close()

    # Assign the UI file to the Pyside dock widget and show it
    ui["dialog"] = wrapInstance(int(ui["window"].GetWindow()), QtWidgets.QDockWidget)
    ui["dialog"].setWidget(ui["widget"])
    ui["widget"].progress.setHidden(True)

    # Add UI functionality
    ui["widget"].camera.currentIndexChanged.connect(update_ui)
    ui["widget"].prop.currentIndexChanged.connect(update_ui)
    ui["widget"].tautness.valueChanged.connect(lambda x: ui["widget"].tautness_slider.setValue(x * 1000))
    ui["widget"].tautness_slider.valueChanged.connect(lambda x: ui["widget"].tautness.setValue(x * 0.001))
    ui["widget"].delay.valueChanged.connect(calculate_total_keys)
    ui["widget"].start_frame.valueChanged.connect(calculate_total_keys)
    ui["widget"].end_frame.valueChanged.connect(calculate_total_keys)
    ui["widget"].reduction.valueChanged.connect(calculate_total_keys)
    ui["widget"].use_current_offset.clicked.connect(use_current_offset)
    ui["widget"].reset.clicked.connect(reset_ui)
    ui["widget"].follow.clicked.connect(setup)

    # Register events
    events["callback"] = EventCallback()
    events["callback_id"] = RLPy.REventHandler.RegisterCallback(events["callback"])
    events["dialog_callback"] = DialogCallback()
    ui["window"].RegisterEventCallback(events["dialog_callback"])

    # Show the UI
    ui["window"].Show()
    reset_ui()


def run_script():
    initialize_plugin()
