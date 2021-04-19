import RLPy
import math
import os
import sys
from PySide2 import QtWidgets
from PySide2 import QtSvg
from PySide2 import QtGui
from PySide2.QtCore import Qt
from PySide2.shiboken2 import wrapInstance


import Extensions as Ext

popcornfx_sequencer_ui = {}  # User interface globals
popcornfx_sequencer_callbacks = {}  # Global for callbacks, events

popcorn_list_tree_view = None
custom_life_cycle_table_view = None
emit_control = None
enable_loop_control = None
delay_time_control = None
loop_interval_control = None

reset_to_default_button = None
apply_setting_button = None
clear_key_button = None

add_emit_key_button = None
delete_emit_key_button = None


# Callback
event_list = []
event_callback = None
dialog_event_callback = None

# Global value
execute_parent_path = ""
timeline = None
particle_emit_dic = {}
particle_delay_dic = {}
particle_loop_dic = {}
particle_emit_key_dic = {}


class MyEventCallback(RLPy.REventCallback):
    def __init__(self):
        RLPy.REventCallback.__init__(self)
        self.file_loaded_func = None
        self.undo_redo_done_func = None
        self.object_deleted_func = None
        self.object_added_func = None

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


class DialogEventCallback(RLPy.RDialogCallback):
    def __init__(self):
        RLPy.RDialogCallback.__init__(self)

    def OnDialogHide(self):
        global event_list
        for evt in event_list:
            RLPy.REventHandler.UnregisterCallback(evt)
        event_list = []
        pass


class PopcornManagerListTreeWidget(QtWidgets.QTreeWidget):
    def __init__(self):
        super().__init__()

        # -----QTreeWidget Property settings-----
        self.setHeaderHidden(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.viewport().setAcceptDrops(True)
        self.__objectList = []
        self._dict = {}
        self.refresh()

    @property
    # Return a list of checked particles.
    def value(self):
        self.__objectList = []
        item_count = self.topLevelItemCount()
        for i in range(self.topLevelItemCount()):
            _ui_item = self.topLevelItem(i)
            if _ui_item.checkState(0) == Qt.Checked:
                self.__objectList.append(self._dict[_ui_item.text(0)])

        return self.__objectList

    # Return the selected particles by name
    def get_particle(self, name):
        return self._dict[name]

    def __blockSignals(self, cond=True):
        self.blockSignals(cond)

    def refresh(self):

        # Before we refresh the list, we need to save the list oreder and unchecked states
        particle_order_list = []
        particle_uncheck_list = []
        item_count = self.topLevelItemCount()
        for i in range(self.topLevelItemCount()):
            _ui_item = self.topLevelItem(i)
            particle_order_list.append(_ui_item.text(0))
            if _ui_item.checkState(0) != Qt.Checked:
                particle_uncheck_list.append(_ui_item.text(0))

        self.__blockSignals()
        self.clear()
        self._dict = {}
        self.scene_objects = RLPy.RScene.FindObjects(RLPy.EObjectType_PopcornFX)

        # -----Create item for all scene objects-----
        for item in self.scene_objects:
            _name = item.GetName()
            temp_item = QtWidgets.QTreeWidgetItem()
            temp_item.setText(0, _name)
            temp_item.setFlags(temp_item.flags() & ~Qt.ItemIsDropEnabled)
            temp_item.setFlags(temp_item.flags() | Qt.ItemIsUserCheckable)

            # Take the previous unchecked list and set the check state.  
            # When a particle is not part of this list, it means it is new and it is, by default, checked. 
            if _name in particle_uncheck_list:
                temp_item.setCheckState(0, Qt.Unchecked)
            else:
                temp_item.setCheckState(0, Qt.Checked)

            if _name in particle_order_list:  # Indicates the originally saved particles
                insert_order = particle_order_list.index(_name)
                insert_done = False

                item_count = self.topLevelItemCount()

                for j in range(item_count):
                    current_particle_name = self.topLevelItem(j).text(0)

                    if current_particle_name in particle_order_list:
                        current_particle_order = particle_order_list.index(current_particle_name)

                        if insert_order < current_particle_order:
                            self.insertTopLevelItem(j, temp_item)
                            insert_done = True
                    else:
                        self.insertTopLevelItem(j, temp_item)
                        insert_done = True
                if not insert_done:
                    self.addTopLevelItem(temp_item)

            else:
                self.addTopLevelItem(temp_item)

            self._dict[_name] = item
        self.__blockSignals(False)

    def dropEvent(self, evt):
        item = self.itemAt(evt.pos())
        super().dropEvent(evt)


class PopcornManagerCustomLifeCycleTableWidget(QtWidgets.QTableWidget):
    def __init__(self):
        super().__init__()
        self.setColumnCount(2)
        self.setHorizontalHeaderLabels(['Emit', 'Delay Time'])
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)

    def create_table(self, data_list):
        self.setRowCount(0)

        for data in data_list:
            item_off = QtWidgets.QTableWidgetItem()
            item_off.setText("Off")
            item_off.setFlags(Qt.ItemIsEnabled)
            item_on = QtWidgets.QTableWidgetItem()
            item_on.setText("On")
            item_off.setFlags(Qt.ItemIsEnabled)
            item_time = QtWidgets.QTableWidgetItem()
            item_time.setText(str(data))

            row_count = self.rowCount()
            self.setRowCount(row_count + 1)
            if row_count % 2 == 0:
                self.setItem(row_count, 0, item_off)
            else:
                self.setItem(row_count, 0, item_on)

            self.setItem(row_count, 1, item_time)


def refresh_list_view():
    global popcorn_list_tree_view
    popcorn_list_tree_view.refresh()


def initialize_plugin():
    global execute_parent_path
    execute_parent_path = os.path.abspath(os.path.join(sys.executable, os.pardir))
    # Create Pyside interface with iClone main window
    ic_dlg = wrapInstance(int(RLPy.RUi.GetMainWindow()), QtWidgets.QMainWindow)

    # Check if the menu item exists
    plugin_menu = ic_dlg.menuBar().findChild(QtWidgets.QMenu, "pysample_menu")
    if plugin_menu is None:

        # Create Pyside layout for QMenu named "Python Samples" and attach it to the Plugins menu
        plugin_menu = wrapInstance(int(RLPy.RUi.AddMenu("Python Samples", RLPy.EMenu_Plugins)), QtWidgets.QMenu)
        plugin_menu.setObjectName("pysample_menu")  # Setting an object name for the menu is equivalent to giving it an ID

    # Add the "Popcorn Script Manager" menu item to Plugins > Python Samples
    menu_action = plugin_menu.addAction("PopcornFX Sequencer (Demo)")

    # Show the dialog window when the menu item is triggered
    menu_action.triggered.connect(show_window)


def create_ui():
    global popcorn_list_tree_view
    global custom_life_cycle_table_view
    global emit_control
    global enable_loop_control
    global loop_interval_control
    global delay_time_control
    global reset_to_default_button
    global apply_setting_button
    global clear_key_button
    global add_emit_key_button
    global delete_emit_key_button
    global timeline
    global popcornfx_sequencer_ui

    popcornfx_sequencer_ui["dialog_window"], popcornfx_sequencer_ui["main_layout"] = Ext.setup_dock(title="PopcornFX Sequencer (Demo)", dockable="None", height=600)

    emitter_priority_label = QtWidgets.QLabel(wordWrap=True, text="Emitter Priority:")
    custom_life_cycle_label = QtWidgets.QLabel(wordWrap=True, text="Custom Life Cycle:")
    line_label = QtWidgets.QLabel(wordWrap=True, text="_______________________________________")

    popcorn_list_tree_view = PopcornManagerListTreeWidget()
    popcorn_list_tree_view.itemSelectionChanged.connect(update_data)

    custom_life_cycle_table_view = PopcornManagerCustomLifeCycleTableWidget()
    custom_life_cycle_table_view.setFixedHeight(110)
    custom_life_cycle_table_view.itemChanged.connect(edit_emit_on_off_key)

    emit_control = QtWidgets.QCheckBox("Override Emit On/Off")
    emit_control.setChecked(True)
    emit_control.toggled.connect(set_emit)

    enable_loop_control = QtWidgets.QCheckBox("Auto Loop")
    enable_loop_control.setChecked(False)
    enable_loop_control.toggled.connect(set_loop_interval)

    loop_interval_control = Ext.IntegerSpinBoxControl(label="Interval (Sec)", span=(0, 99))
    loop_interval_control.value = 1
    loop_interval_control.setEnabled(False)
    loop_interval_control.valueChanged.connect(set_loop_interval)

    delay_time_control = Ext.FloatSliderControl(label="Delay with Previous Emitter", span=(0, 20))
    delay_time_control.value = 0.0
    delay_time_control.valueChanged.connect(set_delay_time)

    timeline = Ext.TimeLine()

    apply_setting_button = QtWidgets.QPushButton(text="Apply")
    apply_setting_button.setFixedHeight(26)
    apply_setting_button.clicked.connect(apply_setting)

    clear_key_button = QtWidgets.QPushButton(text="Clear Key")
    clear_key_button.setFixedHeight(26)
    clear_key_button.clicked.connect(clear_current_key)

    reset_to_default_button = QtWidgets.QPushButton()
    reset_to_default_button.setFixedHeight(26)
    reset_to_default_button.setFixedWidth(26)
    reset_to_default_button.setIcon(QtGui.QIcon(execute_parent_path + '\\OpenPlugin\\PopcornFX_Sequencer_Demo\\Reset.svg'))
    reset_to_default_button.clicked.connect(reset_to_default)

    add_emit_key_button = QtWidgets.QPushButton(text="Add")
    add_emit_key_button.setFixedHeight(26)
    add_emit_key_button.clicked.connect(add_emit_on_off_key)

    delete_emit_key_button = QtWidgets.QPushButton(text="Delete")
    delete_emit_key_button.setFixedHeight(26)
    delete_emit_key_button.clicked.connect(delete_emit_on_off_key)

    horizontal_layout1 = QtWidgets.QHBoxLayout()
    horizontal_layout1.addWidget(emit_control)
    horizontal_layout1.addWidget(reset_to_default_button)

    horizontal_layout2 = QtWidgets.QHBoxLayout()
    horizontal_layout2.addSpacing(20)
    horizontal_layout2.addWidget(delay_time_control)

    horizontal_layout3 = QtWidgets.QHBoxLayout()
    horizontal_layout3.addSpacing(20)
    horizontal_layout3.addWidget(loop_interval_control)

    horizontal_layout4 = QtWidgets.QHBoxLayout()
    horizontal_layout4.addWidget(add_emit_key_button)
    horizontal_layout4.addWidget(delete_emit_key_button)

    vertical_layout2 = QtWidgets.QVBoxLayout()
    vertical_layout2.addWidget(custom_life_cycle_table_view)
    vertical_layout2.addLayout(horizontal_layout4)
    group_box = QtWidgets.QGroupBox()
    group_box.setLayout(vertical_layout2)

    popcornfx_sequencer_ui["main_layout"].addWidget(emitter_priority_label)
    popcornfx_sequencer_ui["main_layout"].addWidget(popcorn_list_tree_view)
    popcornfx_sequencer_ui["main_layout"].addLayout(horizontal_layout1)
    popcornfx_sequencer_ui["main_layout"].addLayout(horizontal_layout2)
    popcornfx_sequencer_ui["main_layout"].addWidget(line_label)
    popcornfx_sequencer_ui["main_layout"].addWidget(enable_loop_control)
    popcornfx_sequencer_ui["main_layout"].addLayout(horizontal_layout3)
    popcornfx_sequencer_ui["main_layout"].addWidget(custom_life_cycle_label)
    popcornfx_sequencer_ui["main_layout"].addWidget(group_box)
    popcornfx_sequencer_ui["main_layout"].addWidget(apply_setting_button)
    popcornfx_sequencer_ui["main_layout"].addWidget(clear_key_button)


def show_window():
    global popcornfx_sequencer_ui
    global popcornfx_sequencer_callbacks
    global event_callback
    global event_list

    if "dialog_window" in popcornfx_sequencer_ui:  # If the window already exists...
        if popcornfx_sequencer_ui["dialog_window"].IsVisible():
            RLPy.RUi.ShowMessageBox(
                "PopcornFx Sequencer - Operation Error",
                "The current PopcornFx Sequencer session is still running.  You must first close the window to start another session.",
                RLPy.EMsgButton_Ok)
    else:
        create_ui()
        popcornfx_sequencer_callbacks["dialog_events"] = DialogEventCallback()
        popcornfx_sequencer_ui["dialog_window"].RegisterEventCallback(popcornfx_sequencer_callbacks["dialog_events"])

    event_callback = MyEventCallback()
    event_callback.register_file_loaded_func(refresh_list_view)
    event_callback.register_undo_redo_done_func(refresh_list_view)
    event_callback.register_object_deleted_func(refresh_list_view)
    event_callback.register_object_added_func(refresh_list_view)

    id = RLPy.REventHandler.RegisterCallback(event_callback)
    event_list.append(id)

    popcornfx_sequencer_ui["dialog_window"].Show()
    update_data()


def run_script():
    initialize_plugin()


def update_behavior_state():
    emit_control.blockSignals(True)
    enable_loop_control.blockSignals(True)
    loop_interval_control.blockSignals(True)
    delay_time_control.blockSignals(True)

    if emit_control.isChecked():
        enable_loop_control.setEnabled(True)
        loop_interval_control.setEnabled(True)
        delay_time_control.setEnabled(True)

        if enable_loop_control.isChecked():
            loop_interval_control.setEnabled(True)
        else:
            loop_interval_control.setEnabled(False)
    else:
        enable_loop_control.setEnabled(False)
        loop_interval_control.setEnabled(False)
        delay_time_control.setEnabled(False)

    emit_control.blockSignals(False)
    enable_loop_control.blockSignals(False)
    loop_interval_control.blockSignals(False)
    delay_time_control.blockSignals(False)


def apply_setting():

    global timeline
    timeline = Ext.TimeLine()
    current_frame = timeline.current_frame

    current_time = timeline.IndexedFrameTime(current_frame)
    RLPy.RGlobal.SetTime(current_time)

    accumulate_dalay = 0
    selected_popcorns = popcorn_list_tree_view.value
    for popcorn in selected_popcorns:
        popcorn_name = popcorn.GetName()
        popcorn.RemoveEmitKeys()

        emit = True
        if popcorn_name in particle_emit_dic:
            emit = particle_emit_dic[popcorn_name]
        if emit:
            if popcorn_name in particle_delay_dic:
                accumulate_dalay = accumulate_dalay + particle_delay_dic[popcorn_name]
            popcorn.SetEmit(RLPy.RTime(accumulate_dalay * 1000) + current_time, True)

            is_particle_loop = False
            if popcorn_name in particle_loop_dic:
                loop_interval = particle_loop_dic[popcorn_name]
                if loop_interval == -1:
                    popcorn.SetLoop(False)
                else:
                    is_particle_loop = True
                    popcorn.SetLoop(True)
                    popcorn.SetLoopInterval(loop_interval)
            else:
                popcorn.SetLoop(False)

            repeat_emit_delay_time = 0
            on_off_index = 0
            if not(is_particle_loop):
                if popcorn_name in particle_emit_key_dic:
                    particle_emit_key_time_list = particle_emit_key_dic[popcorn_name]
                    for key_time in particle_emit_key_time_list:
                        repeat_emit_delay_time = repeat_emit_delay_time + key_time
                        if on_off_index % 2 == 0:
                            popcorn.SetEmit(RLPy.RTime((accumulate_dalay + repeat_emit_delay_time) * 1000) + current_time, False)
                        else:
                            popcorn.SetEmit(RLPy.RTime((accumulate_dalay + repeat_emit_delay_time) * 1000) + current_time, True)
                        on_off_index = on_off_index + 1

        popcorn.Update()

    RLPy.RGlobal.Play(timeline.start_time, timeline.end_time)


def update_data():
    emit_control.blockSignals(True)
    enable_loop_control.blockSignals(True)
    loop_interval_control.blockSignals(True)
    delay_time_control.blockSignals(True)

    selected = popcorn_list_tree_view.selectedItems()
    if selected:
        popcorn_name = selected[0].text(0)
        particle = popcorn_list_tree_view.get_particle(popcorn_name)
        RLPy.RScene.SelectObject(particle)
        emit_control.setEnabled(True)

        emit = True
        if popcorn_name in particle_emit_dic:
            emit = particle_emit_dic[popcorn_name]
        emit_control.setChecked(emit)

        if emit:
            enable_loop_control.setEnabled(True)
            delay_time_control.setEnabled(True)

            if popcorn_name in particle_delay_dic:
                delay_time_control.value = particle_delay_dic[popcorn_name]
            else:
                delay_time_control.value = 0

            if popcorn_name in particle_loop_dic:

                if particle_loop_dic[popcorn_name] == -1:
                    enable_loop_control.setChecked(False)
                    loop_interval_control.setEnabled(False)
                    set_emit_key_related_control_status(True, popcorn_name)
                else:
                    enable_loop_control.setChecked(True)
                    loop_interval_control.setEnabled(True)
                    loop_interval_control.value = particle_loop_dic[popcorn_name]
                    set_emit_key_related_control_status(False)
            else:
                enable_loop_control.setChecked(False)
                loop_interval_control.setEnabled(False)
                set_emit_key_related_control_status(True, popcorn_name)
        else:
            enable_loop_control.setEnabled(False)
            loop_interval_control.setEnabled(False)
            delay_time_control.setEnabled(False)
            set_emit_key_related_control_status(False)
    else:
        emit_control.setEnabled(False)
        enable_loop_control.setEnabled(False)
        loop_interval_control.setEnabled(False)
        delay_time_control.setEnabled(False)
        set_emit_key_related_control_status(False)

    emit_control.blockSignals(False)
    enable_loop_control.blockSignals(False)
    loop_interval_control.blockSignals(False)
    delay_time_control.blockSignals(False)

    custom_life_cycle_table_view.blockSignals(True)
    update_repeat_emit_table()
    custom_life_cycle_table_view.blockSignals(False)


def set_emit_key_related_control_status(enableUI, popcorn_name=""):
    add_emit_key_button.blockSignals(True)
    delete_emit_key_button.blockSignals(True)
    custom_life_cycle_table_view.blockSignals(True)

    if enableUI:
        add_emit_key_button.setEnabled(True)
        custom_life_cycle_table_view.setEnabled(True)

        if popcorn_name in particle_emit_key_dic:
            particle_emit_key_time_list = particle_emit_key_dic[popcorn_name]
            if len(particle_emit_key_time_list) == 0:
                delete_emit_key_button.setEnabled(False)
            else:
                delete_emit_key_button.setEnabled(True)
        else:
            delete_emit_key_button.setEnabled(False)

    else:
        add_emit_key_button.setEnabled(False)
        delete_emit_key_button.setEnabled(False)
        custom_life_cycle_table_view.setEnabled(False)

    add_emit_key_button.blockSignals(False)
    delete_emit_key_button.blockSignals(False)
    custom_life_cycle_table_view.blockSignals(False)


def set_emit():
    global particle_emit_dic
    update_behavior_state()
    selected = popcorn_list_tree_view.selectedItems()
    if selected:
        popcorn_name = selected[0].text(0)
        particle_emit_dic[popcorn_name] = emit_control.isChecked()

    update_data()


def set_delay_time():
    global particle_delay_dic
    selected = popcorn_list_tree_view.selectedItems()
    if selected:
        popcorn_name = selected[0].text(0)
        particle_delay_dic[popcorn_name] = delay_time_control.value


def set_loop_interval():
    global particle_loop_dic
    update_behavior_state()
    selected = popcorn_list_tree_view.selectedItems()
    if selected:
        popcorn_name = selected[0].text(0)
        if enable_loop_control.isChecked():
            particle_loop_dic[popcorn_name] = loop_interval_control.value
        else:
            particle_loop_dic[popcorn_name] = -1

    update_data()


def clear_current_key():
    selected_popcorns = popcorn_list_tree_view.value
    for popcorn in selected_popcorns:
        popcorn.RemoveEmitKeys()

    RLPy.RGlobal.Stop()


def reset_to_default():
    global particle_emit_dic
    global particle_delay_dic
    global particle_loop_dic
    global particle_emit_key_dic
    particle_emit_dic.clear()
    particle_delay_dic.clear()
    particle_loop_dic.clear()
    particle_emit_key_dic.clear()
    update_data()


def update_repeat_emit_table():
    global particle_emit_key_dic

    selected = popcorn_list_tree_view.selectedItems()
    if selected:
        popcorn_name = selected[0].text(0)
        if popcorn_name in particle_emit_key_dic:
            particle_emit_key_time_list = particle_emit_key_dic[popcorn_name]
        else:
            particle_emit_key_time_list = []

        custom_life_cycle_table_view.create_table(particle_emit_key_time_list)


def add_emit_on_off_key():
    global particle_emit_key_dic

    selected = popcorn_list_tree_view.selectedItems()
    if selected:
        popcorn_name = selected[0].text(0)
        if popcorn_name in particle_emit_key_dic:
            particle_emit_key_time_list = particle_emit_key_dic[popcorn_name]
        else:
            particle_emit_key_time_list = []

        particle_emit_key_time_list.append(0.5)
        particle_emit_key_dic[popcorn_name] = particle_emit_key_time_list
        custom_life_cycle_table_view.create_table(particle_emit_key_time_list)

    update_data()


def delete_emit_on_off_key():
    global particle_emit_key_dic

    selected = popcorn_list_tree_view.selectedItems()
    if selected:
        popcorn_name = selected[0].text(0)
        if popcorn_name in particle_emit_key_dic:
            particle_emit_key_time_list = particle_emit_key_dic[popcorn_name]
            particle_emit_key_time_list.pop()
            custom_life_cycle_table_view.create_table(particle_emit_key_time_list)

    update_data()


def edit_emit_on_off_key():
    global particle_emit_key_dic

    selected = popcorn_list_tree_view.selectedItems()
    if selected:
        popcorn_name = selected[0].text(0)
        if popcorn_name in particle_emit_key_dic:
            particle_emit_key_time_list = particle_emit_key_dic[popcorn_name]
            selected_keys = custom_life_cycle_table_view.selectedItems()
            if selected_keys:
                key_value = selected_keys[0].text()

                try:
                    val = float(key_value)
                except ValueError:
                    custom_life_cycle_table_view.blockSignals(True)
                    custom_life_cycle_table_view.create_table(particle_emit_key_time_list)
                    custom_life_cycle_table_view.blockSignals(False)

                if float(key_value) <= 0:
                    custom_life_cycle_table_view.blockSignals(True)
                    custom_life_cycle_table_view.create_table(particle_emit_key_time_list)
                    custom_life_cycle_table_view.blockSignals(False)
                else:
                    row_index = custom_life_cycle_table_view.currentRow()
                    particle_emit_key_time_list[row_index] = float(key_value)
