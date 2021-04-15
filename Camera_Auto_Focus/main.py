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
from shiboken2 import wrapInstance

caf_ui = {}  # User interface globals
caf_callbacks = {}  # Global for callbacks, events, and timers


def world_to_local_point(transform, world_point):
    '''
    Converts world-space point to local-space position relative to the transform-space.

    Args:
        transform (RTransform): Transform space for world to local point conversion.
        world_point (RVector3): The point in world-space that needs to be converted to local-space.

    Returns:
        RVector3: The world-space point converted to local-space.
    '''
    transform_matrix = transform.Matrix()
    local_position = world_point - transform_matrix.GetTranslate()  # Can also use transform.T()
    transform_matrix.SetTranslate(RLPy.RVector3.ZERO)  # Zero out transform matrix translation

    # New matrix4 for the local position
    point_world_matrix = RLPy.RMatrix4()
    point_world_matrix.MakeIdentity()
    point_world_matrix.SetTranslate(local_position)

    # Convert local space to transform space
    point_transform_matrix = point_world_matrix * transform_matrix.Inverse()

    # Return the translation element of the combined matrix4
    return point_transform_matrix.GetTranslate()


class EventCallback(RLPy.REventCallback):
    def __init__(self):
        RLPy.REventCallback.__init__(self)

    def OnObjectDataChanged(self):
        update_ui()

    def OnCurrentTimeChanged(self, fTime):
        update_ui()


class AutoFocusTimerCallback(RLPy.RPyTimerCallback):
    def __init__(self):
        RLPy.RPyTimerCallback.__init__(self)

    def Timeout(self):
        automation()


class MessageCallback(RLPy.RPyTimerCallback):
    def __init__(self):
        RLPy.RPyTimerCallback.__init__(self)

    def Timeout(self):
        global caf_ui

        if caf_ui["widget"].autoFocus_group.isChecked() or caf_ui["widget"].autoRange_group.isChecked():
            caf_ui["widget"].status.setStyleSheet("color: lime; font: bold;")

            # Flash the auto-key reminder by oscillating between text and no text
            if caf_ui["widget"].status.text() == "":
                caf_ui["widget"].status.setText("Auto-key ON!")
            else:
                caf_ui["widget"].status.setText("")
        else:  # If both automatic settings are turned off, then notify the user and don't flash the message
            caf_ui["widget"].status.setText("Auto-key OFF")
            caf_ui["widget"].status.setStyleSheet("color: grey; font: bold;")


class DialogEventCallback(RLPy.RDialogCallback):
    def __init__(self):
        RLPy.RDialogCallback.__init__(self)

    def OnDialogShow(self):
        global caf_ui

        if caf_ui["window"].IsFloating():
            caf_ui["dock"].adjustSize()

    def OnDialogClose(self):
        global caf_callbacks

        caf_ui["window"].UnregisterAllEventCallbacks()
        caf_callbacks["timer"].UnregisterPyTimerCallback()
        caf_callbacks["flash_message"].UnregisterPyTimerCallback()
        RLPy.REventHandler.UnregisterCallback(caf_callbacks["events_id"])
        # Clear all globals
        caf_ui.clear()
        caf_callbacks.clear()
        return True


def automation():
    camera = RLPy.RScene.GetCurrentCamera()
    dof = camera.GetDOFData()
    items = RLPy.RScene.GetSelectedObjects()
    set_key = False  # Did the parameters change, forcing an update?

    caf_ui["window"].SetWindowTitle("Camera Auto-Focus { %s }" % camera.GetName())
    caf_ui["widget"].targetObject.clear()
    caf_ui["widget"].distance.clear()

    if len(items) > 0:
        object_type = items[0].GetType()

        if object_type == RLPy.EObjectType_Avatar or object_type == RLPy.EObjectType_Prop:  # If the object is valid: avatar or prop
            camera_transform = camera.WorldTransform()
            target_transform = items[0].WorldTransform()
            local_point = world_to_local_point(camera_transform, target_transform.T())

            # Update the UI
            caf_ui["widget"].targetObject.setText(items[0].GetName())
            caf_ui["widget"].distance.setText(str(round(-local_point.z, 2)))

            if caf_ui["widget"].autoFocus_group.isChecked():  # Automatic calculation of the DOF distance
                # Caculate auto-focus based on parameter settings
                focus_distance = -local_point.z * caf_ui["widget"].autoDistance.value()
                focus_distance = max(min(focus_distance, 5000), 2)  # iClone Focus Distance value is between 2 and 5,000

                if dof.GetFocus() != focus_distance:
                    # Apply a Focus Distance key to the camera
                    dof.SetFocus(focus_distance)
                    set_key = True  # Parameters don't match, we'll need to update

            if caf_ui["widget"].autoRange_group.isChecked():  # Automatic calculation of the DOF range
                # Get the bounding size of the picked object
                max_point = RLPy.RVector3()
                cen_point = RLPy.RVector3()
                min_point = RLPy.RVector3()

                status = items[0].GetBounds(max_point, cen_point, min_point)

                if status == RLPy.RStatus.Success:
                    focus_range = ((max_point.x - cen_point.x) + (max_point.y - cen_point.y) + (max_point.z - cen_point.z)) / 3
                    focus_range *= caf_ui["widget"].autoRange.value()
                    focus_range = max(min(focus_range, 1000), 0)  # iClone Focus Range value is between 0 and 1,000

                    if dof.GetRange() != focus_range:
                        # Apply a Focus Range key to the camera
                        dof.SetRange(focus_range)
                        set_key = True  # Parameters don't match, we'll need to update

            if set_key:
                # Create and set a DOF key
                dof.SetEnable(True)
                key = RLPy.RKey()
                key.SetTime(RLPy.RGlobal.GetTime())
                camera.AddDofKey(key, dof)


def update_ui():
    camera = RLPy.RScene.GetCurrentCamera()
    dof = camera.GetDOFData()

    # Block the signals before adjusting the UI
    caf_ui["widget"].focusDistance.blockSignals(True)
    caf_ui["widget"].perfectFocusRange.blockSignals(True)
    caf_ui["widget"].nearTransitionRegion.blockSignals(True)
    caf_ui["widget"].farTransitionRegion.blockSignals(True)
    caf_ui["widget"].nearBlurStrength.blockSignals(True)
    caf_ui["widget"].farBlurStrength.blockSignals(True)

    # Update interface based on current camera settings
    caf_ui["widget"].focusDistance_slider.setValue(dof.GetFocus())
    caf_ui["widget"].perfectFocusRange_slider.setValue(dof.GetRange())
    caf_ui["widget"].nearTransitionRegion_slider.setValue(dof.GetNearTransitionRegion())
    caf_ui["widget"].farTransitionRegion_slider.setValue(dof.GetFarTransitionRegion())
    caf_ui["widget"].nearBlurStrength_slider.setValue(dof.GetNearBlurScale() * 1000)
    caf_ui["widget"].farBlurStrength_slider.setValue(dof.GetFarBlurScale() * 1000)

    # Unblock the signals
    caf_ui["widget"].focusDistance.blockSignals(False)
    caf_ui["widget"].perfectFocusRange.blockSignals(False)
    caf_ui["widget"].nearTransitionRegion.blockSignals(False)
    caf_ui["widget"].farTransitionRegion.blockSignals(False)
    caf_ui["widget"].nearBlurStrength.blockSignals(False)
    caf_ui["widget"].farBlurStrength.blockSignals(False)


def set_camera_dof():
    # Double spinbox and integer slider connection
    caf_ui["widget"].nearBlurStrength_slider.setValue(caf_ui["widget"].nearBlurStrength.value() * 1000)
    caf_ui["widget"].farBlurStrength_slider.setValue(caf_ui["widget"].farBlurStrength.value() * 1000)

    # Adjust current camera DOF settings
    camera = RLPy.RScene.GetCurrentCamera()
    dof = camera.GetDOFData()
    dof.SetFocus(caf_ui["widget"].focusDistance.value())
    dof.SetRange(caf_ui["widget"].perfectFocusRange.value())
    dof.SetNearTransitionRegion(caf_ui["widget"].nearTransitionRegion.value())
    dof.SetFarTransitionRegion(caf_ui["widget"].farTransitionRegion.value())
    dof.SetNearBlurScale(caf_ui["widget"].nearBlurStrength.value())
    dof.SetFarBlurScale(caf_ui["widget"].farBlurStrength.value())

    # Key the DOF settings back onto the current camera
    key = RLPy.RKey()
    key.SetTime(RLPy.RGlobal.GetTime())
    camera.AddDofKey(key, dof)


def toggle_autofocus_timer():
    caf_callbacks["timer"].Stop()

    if caf_ui["widget"].autoFocus_group.isChecked() or caf_ui["widget"].autoRange_group.isChecked():
        caf_callbacks["timer"].Start()


def register_events():
    global caf_callbacks

    # Register timer callback for auto-focus updates
    caf_callbacks["timer"] = RLPy.RPyTimer()
    # Every frame of iClone is 16.66667 ms, which is an interval of 16
    # We can capture a key every 20 frames to prevent heavy scenes from freezing
    caf_callbacks["timer"].SetInterval(320)
    caf_callbacks["timer_callback"] = AutoFocusTimerCallback()
    caf_callbacks["timer"].RegisterPyTimerCallback(caf_callbacks["timer_callback"])
    caf_callbacks["timer"].Start()

    # Register timer callback for reminding the user that auto-key is on
    caf_callbacks["flash_message"] = RLPy.RPyTimer()
    caf_callbacks["flash_message"].SetInterval(500)  # Flash auto-key message every 500 ms -> 0.5 sec
    caf_callbacks["message_callback"] = MessageCallback()
    caf_callbacks["flash_message"].RegisterPyTimerCallback(caf_callbacks["message_callback"])
    caf_callbacks["flash_message"].Start()

    # Create Event
    caf_callbacks["events"] = EventCallback()
    caf_callbacks["events_id"] = RLPy.REventHandler.RegisterCallback(caf_callbacks["events"])

    # Double spinbox and integer slider connection
    caf_ui["widget"].autoDistance_slider.valueChanged.connect(lambda x: caf_ui["widget"].autoDistance.setValue(x * 0.001))
    caf_ui["widget"].autoRange_slider.valueChanged.connect(lambda x: caf_ui["widget"].autoRange.setValue(x * 0.001))
    caf_ui["widget"].nearBlurStrength_slider.valueChanged.connect(lambda x: caf_ui["widget"].nearBlurStrength.setValue(x * 0.001))
    caf_ui["widget"].farBlurStrength_slider.valueChanged.connect(lambda x: caf_ui["widget"].farBlurStrength.setValue(x * 0.001))
    caf_ui["widget"].autoDistance.valueChanged.connect(lambda x: caf_ui["widget"].autoDistance_slider.setValue(x * 1000))
    caf_ui["widget"].autoRange.valueChanged.connect(lambda x: caf_ui["widget"].autoRange_slider.setValue(x * 1000))

    # Call to update camera based on changes in custom parameters
    caf_ui["widget"].focusDistance.valueChanged.connect(set_camera_dof)
    caf_ui["widget"].perfectFocusRange.valueChanged.connect(set_camera_dof)
    caf_ui["widget"].nearTransitionRegion.valueChanged.connect(set_camera_dof)
    caf_ui["widget"].farTransitionRegion.valueChanged.connect(set_camera_dof)
    caf_ui["widget"].nearBlurStrength.valueChanged.connect(set_camera_dof)
    caf_ui["widget"].farBlurStrength.valueChanged.connect(set_camera_dof)

    # Start and stop the auto-focus timer depending on the automatic settings
    caf_ui["widget"].autoFocus_group.toggled.connect(toggle_autofocus_timer)
    caf_ui["widget"].autoRange_group.toggled.connect(toggle_autofocus_timer)

    update_ui()


def show_window():
    global caf_ui, caf_callbacks

    if "window" in caf_ui:  # If the window already exist...
        print("Camera Auto-Focus window session already exists!")
        return  # Exit before creating a duplicate window

    caf_ui["window"] = RLPy.RUi.CreateRDockWidget()

    # Register dialog events
    caf_callbacks["dock"] = DialogEventCallback()
    caf_ui["window"].RegisterEventCallback(caf_callbacks["dock"])
    caf_ui["window"].SetAllowedAreas(RLPy.EDockWidgetAreas_RightDockWidgetArea)

    # Create Pyside layout for RDialog
    caf_ui["dock"] = wrapInstance(int(caf_ui["window"].GetWindow()), QtWidgets.QDockWidget)

    # Read and set the QT ui file from the script location
    ui_file = QtCore.QFile(os.path.dirname(__file__) + "/Camera_Auto_Focus.ui")
    ui_file.open(QtCore.QFile.ReadOnly)
    caf_ui["widget"] = QtUiTools.QUiLoader().load(ui_file)
    ui_file.close()
    caf_ui["dock"].setWidget(caf_ui["widget"])

    caf_ui["window"].Show()

    register_events()  # Register all global callback events


def initialize_plugin():
    # Create Pyside interface with iClone main window
    ic_dlg = wrapInstance(int(RLPy.RUi.GetMainWindow()), QtWidgets.QMainWindow)

    # Check if the menu item exists
    plugin_menu = ic_dlg.menuBar().findChild(QtWidgets.QMenu, "pysample_menu")

    if plugin_menu is None:

        # Create Pyside layout for QMenu named "Python Samples" and attach it to the Plugins menu
        plugin_menu = wrapInstance(int(RLPy.RUi.AddMenu("Python Samples", RLPy.EMenu_Plugins)), QtWidgets.QMenu)
        plugin_menu.setObjectName("pysample_menu")  # Setting an object name for the menu is equivalent to giving it an ID

    # Add the "Camera Auto-Focus" menu item to Plugins > Python Samples
    menu_action = plugin_menu.addAction("Camera Auto-Focus")

    # Show the dialog window when the menu item is triggered
    menu_action.triggered.connect(show_window)


def run_script():
    initialize_plugin()
