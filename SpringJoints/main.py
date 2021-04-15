import RLPy
import math
from PySide2 import QtWidgets
from PySide2.QtCore import Qt
from shiboken2 import wrapInstance

import ExtensionsForSpring as Ext

# Widgets
spring_ui = {}  # User interface globals
spring_callbacks = {}  # Global for callbacks, events

bone_tree_view = None
bounciness_control = None
stiffness_control = None
dampness_control = None
stiffness_scale_control = None
bounciness_scale_control = None
apply_setting_button = None
stop_simulation_button = None
start_simulation_button = None
clear_key_button = None
progress_bar = None
message = None

# Callback
timer = None
timer_callback = None

event_list = []
event_callback = None
dialog_event_callback = None

# Global value
api_version = None
current_time = None
bone_hierarchy = None
timeline = None

last_x = None
last_y = None
last_z = None


class MyPyTimerCallback(RLPy.RPyTimerCallback):
    def __init__(self):
        RLPy.RPyTimerCallback.__init__(self)
        self.timeout_func = None

    def Timeout(self):
        self.timeout_func()

    def register_timeout_func(self, func):
        self.timeout_func = func


class MyEventCallback(RLPy.REventCallback):
    def __init__(self):
        RLPy.REventCallback.__init__(self)
        self.file_loaded_func = None
        self.undo_redo_done_func = None
        self.object_deleted_func = None
        self.object_added_func = None
        self.hierarchy_changed_func = None

    def OnFileLoaded(self, nFileType):
        self.file_loaded_func()

    def register_file_loaded_func(self, func):
        self.file_loaded_func = func

    def OnUndoRedoDone(self):
        self.undo_redo_done_func()

    def register_undo_redo_done_func(self, func):
        self.undo_redo_done_func = func

    def OnObjectDeleted(self):
        self.object_deleted_func()

    def register_object_deleted_func(self, func):
        self.object_deleted_func = func

    def OnObjectAdded(self):
        self.object_added_func()

    def register_object_added_func(self, func):
        self.object_added_func = func
    
    def OnHierarchyChanged(self):
        self.hierarchy_changed_func()

    def register_hierarchy_changed_func(self, func):
        self.hierarchy_changed_func = func


class DialogEventCallback(RLPy.RDialogCallback):
    def __init__(self):
        RLPy.RDialogCallback.__init__(self)
        self.show_event_fptr = None
        self.hide_event_fptr = None

    def OnDialogShow(self):
        if self.show_event_fptr != None:
            self.show_event_fptr()

    def OnDialogHide(self):
        stop_simulate()
        global event_list
        for evt in event_list:
            RLPy.REventHandler.UnregisterCallback(evt)
        event_list = []

    def OnDialogHide(self):
        if self.hide_event_fptr != None:
            return self.hide_event_fptr()
        else:
            return True

    def register_show_event_callback(self, show_function):
        self.show_event_fptr = show_function

    def register_hide_event_callback(self, hide_function):
        self.hide_event_fptr = hide_function


def matrix3_to_eulerAngle(matrix3):
    x = y = z = 0
    a = matrix3.ToEulerAngle(RLPy.EEulerOrder_XYZ, x, y, z)
    return RLPy.RVector3(a[0], a[1], a[2])


def quaternion_to_matrix(quaterion):
    matrix4 = RLPy.RMatrix4()
    matrix4.MakeIdentity()
    matrix3 = quaterion.ToRotationMatrix()
    matrix4.SetSR(matrix3)
    return matrix4


def from_to_rotation(from_vector, to_vector):
    # Points the from axis towards the to vector, returns a Quaternion
    result = RLPy.RQuaternion()
    from_vector.Normalize()
    to_vector.Normalize()
    up_axis = RLPy.RVector3(RLPy.RVector3.UNIT_Z)
    angle = RLPy.RMath_ACos(from_vector.Dot(to_vector))
    if RLPy.RMath.AlmostZero(angle - RLPy.RMath.CONST_PI) or RLPy.RMath.AlmostZero(angle):
        result.FromAxisAngle(up_axis, angle)
    else:
        normal = from_vector.Cross(to_vector)
        normal.Normalize()
        result.FromAxisAngle(normal, angle)
    return result


def transform_point(world_transform, local_position):
    # Get the transform matrix4
    world_matrix = world_transform.Matrix()

    # New matrix4 for the local position
    point_world_matrix = RLPy.RMatrix4()
    point_world_matrix.MakeIdentity()
    point_world_matrix.SetTranslate(local_position)

    # Combine the 2 matrix4
    point_world_matrix = point_world_matrix * world_matrix

    # Return the translation element of the combined matrix4
    return RLPy.RVector3(point_world_matrix.GetTranslate())


def transform_point2(world_transform, specific_rotation, local_position):
    # Get the transform matrix4
    world_matrix = world_transform.Matrix()
    world_matrix.SetSR(specific_rotation)

    # New matrix4 for the local position
    point_world_matrix = RLPy.RMatrix4()
    point_world_matrix.MakeIdentity()
    point_world_matrix.SetTranslate(local_position)

    # Combine the 2 matrix4
    point_world_matrix = point_world_matrix * world_matrix

    # Return the translation element of the combined matrix4
    return RLPy.RVector3(point_world_matrix.GetTranslate())


def transform_direction(world_transform, local_position):
    # Get the transform rotation 3x3 matrix
    world_rot_matrix = world_transform.Rotate()

    # New matrix4 for world direction
    world_dir = RLPy.RMatrix4()
    world_dir.MakeIdentity()
    world_dir.SetSR(world_rot_matrix)

    # New matrix for the local position
    point_world_matrix = RLPy.RMatrix4()
    point_world_matrix.MakeIdentity()
    point_world_matrix.SetTranslate(local_position)

    # Combine the 2 matrix4
    point_world_matrix = point_world_matrix * world_dir

    # Return the translation element of the combined matrix4
    return RLPy.RVector3(point_world_matrix.GetTranslate())


def refresh_tree_view():
    global bone_tree_view
    bone_tree_view.refresh()


def initialize_plugin():
    global api_version
    api_version = RLPy.RApplication.GetApiVersion()
    # Create Pyside interface with iClone main window
    ic_dlg = wrapInstance(int(RLPy.RUi.GetMainWindow()), QtWidgets.QMainWindow)

    # Check if the menu item exists
    plugin_menu = ic_dlg.menuBar().findChild(QtWidgets.QMenu, "pysample_menu")
    if plugin_menu is None:

        # Create Pyside layout for QMenu named "Python Samples" and attach it to the Plugins menu
        plugin_menu = wrapInstance(int(RLPy.RUi.AddMenu("Python Samples", RLPy.EMenu_Plugins)), QtWidgets.QMenu)
        plugin_menu.setObjectName("pysample_menu")  # Setting an object name for the menu is equivalent to giving it an ID

    # Add the "Spring Joints" menu item to Plugins > Python Samples
    menu_action = plugin_menu.addAction("Spring Joints")

    # Show the dialog window when the menu item is triggered
    menu_action.triggered.connect(show_window)

    create_ui()

    global spring_ui
    global spring_callbacks
    spring_callbacks["dialog_events"] = DialogEventCallback()
    spring_callbacks["dialog_events"].register_show_event_callback(on_show_main_dlg)
    spring_callbacks["dialog_events"].register_hide_event_callback(on_close_main_dlg)
    spring_ui["dialog_window"].RegisterEventCallback(spring_callbacks["dialog_events"])

    register_event()


def run_script():
    initialize_plugin()


def create_ui():
    global spring_ui
    global message
    global bone_tree_view
    global stiffness_control
    global bounciness_control
    global stiffness_scale_control
    global bounciness_scale_control
    global dampness_control
    global start_simulation_button
    global stop_simulation_button
    global apply_setting_button
    global clear_key_button
    global progress_bar
    global timeline

    spring_ui["dialog_window"], main_layout = Ext.setup_dock(title="Spring Joints", dockable="Right", height=600)

    usage_instructions = """    1) Select joints from the list below.
    2) Adjust the settings as you see fit.
    3) Press the [Apply Settings] button.
    * Damping: reduces spring joint inertia."""
    message = QtWidgets.QLabel(wordWrap=True, text=usage_instructions)
    message.setStyleSheet("color: grey;")

    simulation_instructions = "Simulation mode allows you to preview the spring effect in real-time by moving the parent joint around in the viewport.  Reduce Idle Load should be disabled to properly run the simulation (under Preference > Real-time Render Options)."
    simulation_message = QtWidgets.QLabel(wordWrap=True, text=simulation_instructions)
    simulation_message.setStyleSheet("color: grey;")

    bone_tree_view = Ext.SkeletonTreeViewControl()

    stiffness_control = Ext.FloatSpinBoxControl(label="Stiffness", span=(0, 10000))
    stiffness_control.value = 400

    stiffness_scale_control = Ext.FloatSpinBoxControl(label="Stiffness Scale", span=(0.01, 10))
    stiffness_scale_control.value = 1

    bounciness_control = Ext.FloatSpinBoxControl(label="Bounciness", span=(0, 1000))
    bounciness_control.value = 100

    bounciness_scale_control = Ext.FloatSpinBoxControl(label="Bounciness Scale", span=(0.01, 10))
    bounciness_scale_control.value = 1

    dampness_control = Ext.FloatSliderControl(label="Damping", span=(0, 0.99))
    dampness_control.value = 0.0

    start_simulation_button = QtWidgets.QPushButton(text="Start Simulation")
    start_simulation_button.setFixedHeight(26)
    start_simulation_button.clicked.connect(start_simulate)

    stop_simulation_button = QtWidgets.QPushButton(text="Stop Simulation")
    stop_simulation_button.setFixedHeight(26)
    stop_simulation_button.clicked.connect(stop_simulate)
    stop_simulation_button.setEnabled(False)  # Initialize as disabled

    timeline = Ext.TimeLine()

    apply_setting_button = QtWidgets.QPushButton(text="Apply Settings")
    apply_setting_button.setFixedHeight(26)
    apply_setting_button.clicked.connect(apply_setting)

    clear_key_button = QtWidgets.QPushButton(text="Clear Keys")
    clear_key_button.setFixedHeight(26)
    clear_key_button.clicked.connect(clear_current_key)

    progress_bar = QtWidgets.QProgressBar()
    progress_bar.setTextVisible(True)
    progress_bar.setHidden(True)

    # No need to add a stretch to this layout because the tree widget comes with stretch enabled
    for widget in [message, bone_tree_view, stiffness_control, stiffness_scale_control, bounciness_control, bounciness_scale_control, dampness_control, simulation_message, start_simulation_button, stop_simulation_button, apply_setting_button, clear_key_button, progress_bar]:
        main_layout.addWidget(widget)


def show_window():
    global spring_ui
    if "dialog_window" in spring_ui:  # If the window already exists...
        if spring_ui["dialog_window"].IsVisible():
            return

    register_event()

    refresh_tree_view()

    spring_ui["dialog_window"].Show()


def on_show_main_dlg():
    register_event()


def on_close_main_dlg():
    unregister_event()


def unregister_event():
    global event_list
    for evt in event_list:
        RLPy.REventHandler.UnregisterCallback(evt)
    event_list = []


def register_event():
    global event_callback
    global event_list
    if not event_list:
        event_callback = MyEventCallback()
        event_callback.register_file_loaded_func(refresh_tree_view)
        event_callback.register_undo_redo_done_func(refresh_tree_view)
        event_callback.register_object_deleted_func(refresh_tree_view)
        event_callback.register_object_added_func(refresh_tree_view)
        event_callback.register_hierarchy_changed_func(refresh_tree_view)
        
        id = RLPy.REventHandler.RegisterCallback(event_callback)
        event_list.append(id)


def collect_parameters(apply):
    # collect parameters and perform initialization
    global last_x
    global last_y
    global last_z

    global bone_hierarchy
    # Return an ordered bone hierarchy based on what was selected in the UI
    bone_hierarchy = bone_tree_view.value

    for i in bone_hierarchy:
        for bone in bone_hierarchy[i]:
            # Get the datablock for the current bone
            animation_clip = bone["root"].GetSkeletonComponent().GetClip(0)
            if apply:
                animation_clip.SetLength(timeline.end_time)
            control = animation_clip.GetControl("Layer", bone["bone"])
            if not control:
                return
            control.ClearKeys()
            wt = bone["bone"].WorldTransform()

            last_x = bone["root"].WorldTransform().T().x
            last_y = bone["root"].WorldTransform().T().y
            last_z = bone["root"].WorldTransform().T().z

            lt = bone["bone"].LocalTransform()
            bone["data block"] = control.GetDataBlock()
            bone["velocity"] = RLPy.RVector3(0, 0, 0)  # Start off with zero velocity
            bone["current tip pos local"] = RLPy.RVector3(lt.T().x, lt.T().y, lt.T().z)
            bone["current tip pos world"] = transform_point(wt, bone["current tip pos local"])
            bone["stiffness"] = transform_point(wt, bone["current tip pos local"]) - wt.T()
            bone["stiff force"] = RLPy.RVector3(0, 0, 0)
            bone["original world transform"] = wt.R().ToRotationMatrix()


def start_simulate():
    progress_bar.setHidden(True)
    enable_disable_UI(False, True, False)

    global current_time
    current_time = timeline.IndexedFrameTime(timeline.start_frame)
    RLPy.RGlobal.SetTime(current_time)

    # collect parameters and do initialization
    collect_parameters(False)
    global timer
    global timer_callback
    timer = RLPy.RPyTimer()
    timer.SetInterval(16)  # 60Fps = 16.666ms/per frame, we use 16ms to update
    timer_callback = MyPyTimerCallback()
    timer.RegisterPyTimerCallback(timer_callback)
    timer_callback.register_timeout_func(iterate_simulate)
    timer.Start()


def iterate_simulate():
    RLPy.RGlobal.SetTime(current_time)
    do_calculation(current_time, 0.016)


def stop_simulate():
    global timer
    timer.Stop()
    enable_disable_UI(True, False, True)


def apply_setting():
    enable_disable_UI(False, False, False)
    progress_bar.setHidden(False)

    global timeline
    timeline = Ext.TimeLine()
    start_frame = timeline.start_frame
    end_frame = timeline.end_frame

    current_time = timeline.IndexedFrameTime(start_frame)
    RLPy.RGlobal.SetTime(current_time)

    collect_parameters(True)

    for time in range(start_frame, end_frame):
        progress_bar.setValue((time - start_frame) / (end_frame - start_frame) * 100)
        compute_time = timeline.IndexedFrameTime(time)
        RLPy.RGlobal.SetTime(compute_time)
        do_calculation(compute_time, timeline.delta_time)

    if api_version[1] >= 7 and api_version[2] >= 7:
        for i in bone_hierarchy:
            for bone in bone_hierarchy[i]:
                RLPy.RGlobal.ObjectModified(bone["root"], RLPy.EObjectModifiedType_Transform | RLPy.EObjectModifiedType_Attribute)
    else:
        RLPy.RGlobal.Stop()
        RLPy.RGlobal.SetTime(current_time)

    RLPy.RGlobal.Play(timeline.start_time, timeline.end_time)
    progress_bar.reset()
    progress_bar.setHidden(True)
    enable_disable_UI(True, False, True)


def clear_current_key():

    for i in bone_hierarchy:
        for bone in bone_hierarchy[i]:
            animation_clip = bone["root"].GetSkeletonComponent().GetClip(0)
            animation_clip.SetLength(RLPy.RTick.FromMilliSecond(1))

            bone["data block"].GetControl("Rotation/RotationX").ClearKeys()
            bone["data block"].GetControl("Rotation/RotationY").ClearKeys()
            bone["data block"].GetControl("Rotation/RotationZ").ClearKeys()

    if api_version[1] >= 7 and api_version[2] >= 7:
        for i in bone_hierarchy:
            for bone in bone_hierarchy[i]:
                RLPy.RGlobal.ObjectModified(bone["root"], RLPy.EObjectModifiedType_Transform | RLPy.EObjectModifiedType_Attribute)
    else:
        RLPy.RGlobal.Stop()
        RLPy.RGlobal.SetTime(current_time)


def do_calculation(current_time, delta_time):

    bone_index = 0
    for i in bone_hierarchy:

        for bone in bone_hierarchy[i]:

            wt = bone["bone"].WorldTransform()

            if not ("current tip pos world" in bone):
                return
            last_tip = bone["current tip pos world"]
            current_tip = transform_point2(wt, bone["original world transform"], bone["current tip pos local"])

            # spring force.
            tip_diff = current_tip - last_tip
            bounce_force = tip_diff * bounciness_control.value * pow(bounciness_scale_control.value, bone_index)

            # stiffness
            tip_diff_wt = bone["stiffness"]
            tip_diff_wt.Normalize()
            stiff_force = tip_diff_wt * stiffness_control.value * pow(stiffness_scale_control.value, bone_index)
            bone_index = bone_index + 1

            # force = force + (tip_diff_wt * stiffness_control.value)
            damp_force = -(bone["velocity"] * dampness_control.value)

            # v = v0 + at
            bone["velocity"] = bone["velocity"] + (bounce_force * delta_time)

            dot_result = bone["velocity"].Dot(tip_diff_wt)
            bone["velocity"] = bone["velocity"] - tip_diff_wt * dot_result

            # s = s0 + vt
            new_tip = last_tip + (bone["velocity"] * delta_time + stiff_force * delta_time + damp_force * delta_time)

            # clamp length.
            tip_diff_wt = new_tip - wt.T()
            tip_diff_wt.Normalize()
            spring_end_length = bone["current tip pos local"].Length()
            new_tip = tip_diff_wt * spring_end_length + wt.T()

            # calc local rotation
            point_from = transform_direction(wt, bone["current tip pos local"])
            point_from.Normalize()
            point_to = new_tip - wt.T()
            point_to.Normalize()

            q_rot = from_to_rotation(point_from, point_to)
            q_rot = q_rot.Multiply(wt.R())
            rotation_matrix = q_rot.ToRotationMatrix()

            parent = bone["bone"].GetParent()
            if parent:
                parent_wt = parent.WorldTransform()
                parent_inv = parent_wt.R().ToRotationMatrix().Inverse()
                rotation_matrix = rotation_matrix * parent_inv

            v3_rotation = matrix3_to_eulerAngle(rotation_matrix)
            # Now that we have the rotational values, let's perform the actual rotation on the bone
            bone["data block"].GetControl("Rotation/RotationX").SetValue(current_time, v3_rotation.x)
            bone["data block"].GetControl("Rotation/RotationY").SetValue(current_time, v3_rotation.y)
            bone["data block"].GetControl("Rotation/RotationZ").SetValue(current_time, v3_rotation.z)

            bone["current tip pos world"] = new_tip
            bone["bone"].Update()  # important, you need to update the new world matrix of your child bone


def enable_disable_UI(enable_start_simulation_btn, enable_stop_simulation_btn, enable_other_UI):
    start_simulation_button.setEnabled(enable_start_simulation_btn)
    stop_simulation_button.setEnabled(enable_stop_simulation_btn)
    bounciness_control.setEnabled(enable_other_UI)
    stiffness_control.setEnabled(enable_other_UI)
    dampness_control.setEnabled(enable_other_UI)
    apply_setting_button.setEnabled(enable_other_UI)
    bone_tree_view.setEnabled(enable_other_UI)
    clear_key_button.setEnabled(enable_other_UI)
    stiffness_scale_control.setEnabled(enable_other_UI)
    bounciness_scale_control.setEnabled(enable_other_UI)
