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

# Smooth Camera Follow allows the user to pick a camera/view and a prop/target to follow.
# Use Offset values to create a distance between the view and target.
# Use the Delay value to create a lag between the view and target.

import RLPy
from PySide2 import QtWidgets
from PySide2.shiboken2 import wrapInstance

# Utilize custom extension functions: more information in Extensions.py
import Extensions as Ext

# Widgets
smooth_camera_dock = None
follow_control = None
camera_control = None
delay_control = None
tautness_control = None
offset_control = None
progress_bar = None
message = None

def look_at_right_handed(view_position, view_target, view_up_vector):
    # Look at takes two positional vectors and calculates the facing direction
    forward = (view_position - view_target)
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
    # Retrieve RIObject for the camera and the target prop
    prop = follow_control.value
    camera = camera_control.value
    # Position vector is where the prop is plus the offset values
    pos = prop.WorldTransform().T() + offset_control.value
    # Orientation matrix is the camera/view facing the prop position
    orientation = look_at_right_handed(
        pos, prop.WorldTransform().T(), Ext.Vector3.up)
    # Extrapolate the Quaternion rotations from the orientation matrix
    rot = RLPy.RQuaternion().FromRotationMatrix(orientation)
    # Return a Transform class with scale, rotation, and positional values
    return RLPy.RTransform(Ext.Vector3.one, rot, pos)


def key_camera():

    # Store a convenient custom timeline object
    timeline = Ext.TimeLine()
    key_interval = delay_control.value
    # How many keys are needed to create the whole animation from start to finish?
    total_keys = int(RLPy.RMath.Ceil(
        (timeline.end_frame - timeline.start_frame) / key_interval))
    # Show the progress bar
    progress_bar.setRange(0, total_keys)
    progress_bar.setHidden(False)
    message.setHidden(True)

    # Iterate over every keyframe
    for key in range(0, total_keys):
        current_frame = timeline.start_frame + key * key_interval
        current_time = timeline.IndexedFrameTime(current_frame)
        view_transform = camera_control.value.WorldTransform()
        target_transform = destination_transform()
        # Step forward in the timeline
        RLPy.RGlobal.SetTime(current_time)
        progress_bar.setValue(key)
        # Lerp between the current camera position and its destination using tautness as the interpolate
        new_transform = Ext.Transform(view_transform).Lerp(
            target_transform, tautness_control.value)
        # Key the camera's transform for animation
        camera_control.value.GetControl(
            "Transform").SetValue(current_time, new_transform)

    # Hide the progress bar
    progress_bar.setHidden(True)
    message.setHidden(False)
    progress_bar.reset()
    # Playback to see the final result
    RLPy.RGlobal.Play(timeline.start_time, timeline.end_time)


def scf_refresh():
    # Refresh the UI to include all of the relevant assets in the scene
    follow_control.refresh()
    camera_control.refresh()


def scf_setup():
    # If the camera/view and follow/target is designated
    if follow_control.value is not None and camera_control.value is not None:
        # Stop the timeline playback as foolproof measure
        RLPy.RGlobal.Stop()
        # Position the camera/view designated by the offset on the in-mark of the timeline
        RLPy.RGlobal.SetTime(RLPy.RGlobal.GetStartTime())
        camera_controller = camera_control.value.GetControl("Transform")
        camera_controller.ClearKeys()
        # Position the camera on the start frame
        camera_controller.SetValue(
            RLPy.RGlobal.GetStartTime(), destination_transform())

        key_camera()

    else:
        # Request for the missing camera/view and follow/target assets
        RLPy.RUi.ShowMessageBox(
            "Smooth Cam Follow Error", "Please select a Control(Camera) and Follow(Prop) in the scene.", RLPy.EMsgButton_Ok)


def initialize_plugin():
    # Create Pyside layout for QMenu named "Python Samples" and attach it to the Plugins menu
    plugin_menu = wrapInstance(int(RLPy.RUi.AddMenu(
        "Python Samples", RLPy.EMenu_Plugins)), QtWidgets.QMenu)
    # Add the "Smooth Camera Follow" menu item to Plugins > Python Samples
    plugin_action = plugin_menu.addAction("Smooth Camera Follow")
    # Show the dialog window when the menu item is triggered
    plugin_action.triggered.connect(show_dialog)


def show_dialog():
    global smooth_camera_dock
    global follow_control
    global camera_control
    global delay_control
    global offset_control
    global tautness_control
    global progress_bar
    global message

    # Create an iClone Dock Widget
    smooth_camera_dock = RLPy.RUi.CreateRDockWidget()
    smooth_camera_dock.SetWindowTitle("Smooth Cam Follow")
    # Allow this the window to be dockable to the right
    smooth_camera_dock.SetAllowedAreas(
        RLPy.EDockWidgetAreas_RightDockWidgetArea)

    # Create Pyside layout for RDockWidget
    dock = wrapInstance(int(smooth_camera_dock.GetWindow()),
                        QtWidgets.QDockWidget)
    main_widget = QtWidgets.QWidget()
    dock.setWidget(main_widget)
    dock.setFixedWidth(350)

    main_widget_layout = QtWidgets.QVBoxLayout()
    main_widget.setLayout(main_widget_layout)

    # Create widgets
    follow_control = Ext.NodeListComboBoxControl(label="Follow")

    camera_control = Ext.NodeListComboBoxControl(
        label="Control", nodeType=RLPy.EObjectType_Camera)

    delay_control = Ext.IntSliderControl(label="Frame Delay", span=(1, 30))
    delay_control.value = 5

    tautness_control = Ext.FloatSliderControl(
        label="Tautness", span=(0.05, 0.95))
    tautness_control.value = 0.5

    offset_control = Ext.Vector3Control(label="Offset", maxRange=3000)
    offset_control.value = RLPy.RVector3(0, -1000, 350)

    reset_button = QtWidgets.QPushButton(text="Refresh")
    reset_button.clicked.connect(scf_refresh)

    setup_button = QtWidgets.QPushButton(text="Setup")
    setup_button.clicked.connect(scf_setup)

    progress_bar = QtWidgets.QProgressBar()
    progress_bar.setTextVisible(True)
    progress_bar.setHidden(True)

    usage_instructions = """    1) Create a camera and an animated prop.
    2) Click the [Refresh] button to refresh the UI.
    3) Choose a Control (Camera) and Follow (Prop).
    4) Click the [Setup] button.
    5) Playback the timeline to view the results.
    6) Adjust Frame Delay, Tautness, and Offset if needed.
    7) Repeat steps 4 to 6 and adjust to your liking."""

    message = QtWidgets.QLabel(wordWrap=True, text=usage_instructions)
    message.setStyleSheet("color: grey;")

    # Add all of the widgets in one go
    for widget in [camera_control, follow_control, delay_control, tautness_control, offset_control, reset_button, setup_button, progress_bar, message]:
        main_widget_layout.addWidget(widget)

    # Add a stretch space under the other widgets to prevent spacing between the widgets
    main_widget_layout.addStretch()

    smooth_camera_dock.Show()


def run_script():
    initialize_plugin()
