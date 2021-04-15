# Copyright 2018 The Reallusion Authors. All Rights Reserved.
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

# Extend upon base classes in RLPy & QtWdigets.
# These extensions can exist independently of other scripts.


import RLPy
import math
import json
# -- Pyside QT Modules
from PySide2 import QtWidgets
from PySide2.QtCore import *
from PySide2 import QtCore
from shiboken2 import wrapInstance

_dockable_areas = {
    "None": RLPy.EDockWidgetAreas_NoDockwidgetArea,
    "Left": RLPy.EDockWidgetAreas_LeftDockWidgetArea,
    "Right": RLPy.EDockWidgetAreas_RightDockWidgetArea,
    "Top": RLPy.EDockWidgetAreas_TopDockWidgetArea,
    "Bottom": RLPy.EDockWidgetAreas_BottomDockWidgetArea,
    "All": RLPy.EDockWidgetAreas_AllFeatures
}

_object_types = {
    "Object": RLPy.EObjectType_Object,
    "Avatar": RLPy.EObjectType_Avatar,
    "Prop": RLPy.EObjectType_Prop,
    "Camera": RLPy.EObjectType_Camera,
    "Particle": RLPy.EObjectType_Particle,
    "Light": RLPy.EObjectType_Light,
    "SpotLight": RLPy.EObjectType_SpotLight,
    "PointLight": RLPy.EObjectType_PointLight,
    "DirectionalLight": RLPy.EObjectType_DirectionalLight
}


def toDegrees(radians):

    return radians * 57.295779513082320876798154814105


def toRadians(degrees):

    return degrees * 0.017453292519943295769236907684886


def inverseLerp(a, b, v):
    if math.fabs(b-a) < 0:
        return a
    return (v-a) / (b-a)


def lerp(value1, value2, amount):
    return value1 + (value2 - value1) * amount


def clamp(amount, value1, value2):
    __min = value1
    __max = value2
    if(value1 > value2):
        __max = value1
        __min = value2
    if(amount < __min):
        return __min
    if(amount > __max):
        return __max
    return amount


def setup_dock(title="Untitled", width=300, height=400, layout=QtWidgets.QVBoxLayout, dockable="None"):
    area = _dockable_areas[dockable]

    dock = RLPy.RUi.CreateRDockWidget()
    dock.SetWindowTitle(title)
    dock.SetAllowedAreas(area)

    qt_dock = wrapInstance(int(dock.GetWindow()), QtWidgets.QDockWidget)
    main_widget = QtWidgets.QWidget()
    qt_dock.setWidget(main_widget)
    qt_dock.setFixedWidth(width)
    qt_dock.setMinimumHeight(height)

    main_layout = layout()
    main_widget.setLayout(main_layout)

    return dock, main_layout


class TimeLine():

    def __init__(self):
        self.__fps = RLPy.RGlobal.GetFps()
        self.__start_time = RLPy.RGlobal.GetStartTime()
        self.__end_time = RLPy.RGlobal.GetEndTime()
        self.__current_time = RLPy.RGlobal.GetTime()
        self.__start_frame = RLPy.GetFrameIndex(
            self.__start_time, self.__fps)
        self.__end_frame = RLPy.GetFrameIndex(
            self.__end_time, self.__fps)
        self.__current_frame = RLPy.GetFrameIndex(
            self.__current_time, self.__fps)
        self.__delta_time =1/self.__fps.ToFloat()

    @property
    def start_frame(self):
        return self.__start_frame

    @property
    def end_frame(self):
        return self.__end_frame

    @property
    def current_frame(self):
        return self.__current_frame

    @property
    def delta_time(self):
        return self.__delta_time

    @property
    def start_time(self):
        return self.__start_time

    @property
    def end_time(self):
        return self.__end_time

    @property
    def current_time(self):
        return self.__current_time

    def IndexedFrameTime(self, frame_index):
        return RLPy.IndexedFrameTime(frame_index, self.__fps)


class Vector3(RLPy.RVector3):
    # Inherit and extend on the RLPy vector3 class

    # Static for scale vector: iClone default scale is not [100,100,100] as shown in the UI
    one = RLPy.RVector3(1, 1, 1)

    # Static for up vector: iClone is Z-up application
    up = RLPy.RVector3(0, 0, 1)

    # Static for forward vector
    forward = RLPy.RVector3(0, 1, 0)

    def __str__(self):
        # For debugging: pretty print for the Vector3 values
        x = round(self.x, 3)
        y = round(self.y, 3)
        z = round(self.z, 3)
        return "({0}, {1}, {2})".format(str(x), str(y), str(z))

    def __mul__(self, n):
        v3 = Vector3(
            self.x*n,
            self.y*n,
            self.z*n
        )
        return v3

    __rmul__ = __mul__

    def ToQuaternion(self):
        # yaw (Z), pitch (X), roll (Y)
        cy = cos(self.z * 0.5)
        sy = sin(self.z * 0.5)
        cp = cos(self.x * 0.5)
        sp = sin(self.x * 0.5)
        cr = cos(self.y * 0.5)
        sr = sin(self.y * 0.5)

        q = Quaternion()
        q.w = cy * cp * cr + sy * sp * sr
        q.x = cy * cp * sr - sy * sp * cr
        q.y = sy * cp * sr + cy * sp * cr
        q.z = sy * cp * cr - cy * sp * sr

        return q

    def Lerp(self, v3_to, f_interpolation):
        return Vector3(
            lerp(self.x, v3_to.x, f_interpolation),
            lerp(self.y, v3_to.y, f_interpolation),
            lerp(self.z, v3_to.z, f_interpolation)
        )

    def Scale(self, v3):
        return Vector3(
            self.x * v3.x,
            self.y * v3.y,
            self.z * v3.z
        )

    @property
    def normalized(self):
        norm = self
        norm.Normalize()
        return norm


class Quaternion(RLPy.RQuaternion):

    def __str__(self):
        # For debugging: pretty print for the Quaternion values
        return "({0},{1},{2},{3})".format(self.x, self.y, self.z, self.w)

    # Overload the multiplication operator
    def __mul__(self, val):
        if type(val) is RLPy.RVector3 or type(val) is Vector3:
            return self.MultiplyVector3(val)
        else:
            super().__mul__(val)

    __rmul__ = __mul__

    def MultiplyVector3(self, v3):
        n = self.x * 2
        n2 = self.y * 2
        n3 = self.z * 2
        n4 = self.x * n
        n5 = self.y * n2
        n6 = self.z * n3
        n7 = self.x * n2
        n8 = self.x * n3
        n9 = self.y * n3
        n10 = self.w * n
        n11 = self.w * n2
        n12 = self.w * n3
        result = Vector3()
        result.x = (1 - (n5 + n6)) * v3.x + (n7 - n12) * v3.y + (n8 + n11) * v3.z
        result.y = (n7 + n12) * v3.x + (1 - (n4 + n6)) * v3.y + (n9 - n10) * v3.z
        result.z = (n8 - n11) * v3.x + (n9 + n10) * v3.y + (1 - (n4 + n5)) * v3.z
        return result

    def ToEulerAngle(self):
        rm = self.ToRotationMatrix()
        x = 0
        y = 0
        z = 0
        v3 = rm.ToEulerAngle(RLPy.EEulerOrder_XYZ, x, y, z)
        # Result in radians
        return Vector3(v3[0], v3[1], v3[2])


class Transform(RLPy.RTransform):

    def __str__(self):
        # For debugging: pretty print for the Transform values
        return "({0})\n({1})\n({2})".format(
            Vector3(self.S()),
            Vector3(Quaternion(self.R()).ToEulerAngle()),
            Vector3(self.T()))

    def Lerp(self, trans_to, f_interpolation):
        # Scale, Rotation, Translation
        return Transform(
            Vector3(self.S()).Lerp(trans_to.S(), f_interpolation),
            Quaternion(self.R()).Lerp(trans_to.R(), f_interpolation),
            Vector3(self.T()).Lerp(trans_to.T(), f_interpolation)
        )

    def TransformDirection(self, v3_direction):
        # Transform direction from local space to world space.
        return Quaternion(self.R()) * v3_direction


class SkeletonTreeViewControl(QtWidgets.QGroupBox):

    def __str__(self):
        string = ''
        # For debugging: pretty pring for value output
        for x in self.value:
            string += str(x) + '\n'
            for y in self.value[x]:
                string += ' - '+y["root"].GetName() + ">>"+y["bone"].GetName()

        return string

    def __init__(self, parent=None):
        super(SkeletonTreeViewControl, self).__init__(parent)
        # Create a Vertical Box Layout
        parent_layout = QtWidgets.QVBoxLayout()

        # Private attribute(s)
        self.__objectList = {}

        # Create and setup widgets
        self._treeWidget = QtWidgets.QTreeWidget()
        self._treeWidget.setHeaderHidden(True)

        parent_layout.addWidget(self._treeWidget)

        self.refresh()

        # Signal callback methods
        self._treeWidget.itemClicked.connect(
            lambda x: self.__draw_bone(x.__object))

        self._treeWidget.itemChanged.connect(
            lambda x: self.__changeValue(x)
            #lambda tree_widget_item: self.__changeValue(tree_widget_item)
        )

        # Configure the Group Box parent wdiget
        self.setTitle("Bones")
        self.setLayout(parent_layout)
        self.setStyleSheet(
            "QGroupBox  {color: #a2ec13} QTreeView{border:none}")

    @property
    # Return the dictionary of checked objects
    def value(self):
        sorted_object_list = {
            k: self.__objectList[k] for k in sorted(self.__objectList)}
        return sorted_object_list

    def __default_tree_widget_item(self, parent, obj, root_obj, checkable=True, expanded=True):
        item = QtWidgets.QTreeWidgetItem(parent)
        # Dont use Qt.ItemIsTristate, otherwise enabling any item will enable the entire hierarchy.
        if checkable:
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(0, Qt.Unchecked)
        item.setText(0, obj.GetName())
        item.setExpanded(expanded)
        item.__object = obj
        item.__root_object = root_obj
        # Dont double underscore index otherwise 'hasattr' wont work
        if hasattr(parent, '_index'):
            item._index = parent._index + 1
        else:
            item._index = 0
        return item

    # Reserved for bone HUD display. Not implemented at this time.
    # Not implemented due to lack of reliable draw methods within the current API.
    # Custom implementation: draw an object to represent the world transformation of the bone.
    # Drawback: no relative pathing for loading custom props to represent the bone.
    # Remember to set proper flags for the widget items.
    def __draw_bone(self, bone):
        return

    def __blockSignals(self, cond=True):
        self._treeWidget.blockSignals(cond)

    def __changeValue(self, item):
        if item.checkState(0) == Qt.Checked:
            item_entry = {}
            item_entry["bone"] = item.__object
            item_entry["root"] = item.__root_object
            if item._index in self.__objectList:
                self.__objectList[item._index].append(item_entry)
            else:
                self.__objectList[item._index] = [item_entry]
        else:
            if len(self.__objectList[item._index]) == 1:
                del self.__objectList[item._index]
            else:
                self.__objectList[item._index].remove(item_entry)

    # Recursive loop through the hierarchy.  Becareful, must have a stop measure!
    def __hierarchy_walk_down(self, parent_widget, node, root_node, callback):
        children = node.GetChildren()
        for child in children:
            __parent_widget = callback(parent_widget, child, root_node)
            self.__hierarchy_walk_down(
                __parent_widget, child, root_node, callback)

    # We don't really need to specify a callback, just demonstrating that you can
    def __callback_func(self, parent_widget, node, root_node):
        return self.__default_tree_widget_item(parent_widget, node, root_node)

    def refresh(self):
        self.__blockSignals()
        self._treeWidget.clear()
        # Search the scene for avatars and props
        objs = RLPy.RScene.FindObjects(
            RLPy.EObjectType_Avatar | RLPy.EObjectType_Prop)

        for obj in objs:
            rootBone = obj.GetSkeletonComponent().GetRootBone()
            if rootBone != None:
                parent_item = self.__default_tree_widget_item(
                    self._treeWidget, rootBone, obj, False, False)
                self.__hierarchy_walk_down(
                    parent_item, rootBone, obj, self.__callback_func)
        self.__blockSignals(False)


class NodeListComboBoxControl(QtWidgets.QGroupBox):
    # This control evaluates the scene for nodes of the specified type and lists them
    valueChanged = Signal(RLPy.RIObject)
    # Default to the prop node type

    def __init__(self, label=None, nodeType="Prop", parent=None):
        super(NodeListComboBoxControl, self).__init__(parent)
        # Create a Horizontal Box Layout
        parent_layout = QtWidgets.QHBoxLayout()

        # Private attribute(s)
        self.__objectList = {}
        self.__nodeType = _object_Types[nodeType]

        # Create and setup widgets
        self._comboBox = QtWidgets.QComboBox()

        self.refresh()

        self._comboBox.currentIndexChanged.connect(self.__changeValue)

        parent_layout.addWidget(self._comboBox)

        # Configure the Group Box parent widget
        self.setTitle("{0} ({1}) :".format(label, nodeType))
        self.setLayout(parent_layout)
        self.setStyleSheet("QGroupBox  {color: #a2ec13}")

    @property
    # Return the object reference for this UI, there is no setter for this
    def value(self):
        return self.__objectList[self._comboBox.currentIndex()]

    # Private change value callback function

    def __changeValue(self):
        if(self.value != None):
            self.valueChanged.emit(self.value)

    # Public ui refresh command

    def refresh(self):
        self._comboBox.blockSignals(True)
        self._comboBox.clear()
        self._comboBox.addItem("None")
        # First item in the node list is always None
        self.__objectList = {0: None}
        # Search the scene for the node type specificed when initialized
        results = RLPy.RScene.FindObjects(self.__nodeType)

        for i in range(len(results)):
            self.__objectList[i+1] = results[i]
            self._comboBox.addItem(results[i].GetName())

        self._comboBox.blockSignals(False)
        self._comboBox.setCurrentIndex(0)


class IntegerSpinBoxControl(QtWidgets.QFrame):
    # Sliderless float spin box
    valueChanged = Signal(float)

    def __init__(self, label=None, span=(0, 100), singleStep=1, parent=None):
        super(IntegerSpinBoxControl, self).__init__(parent)

        fixed_height = 36
        # Span is Range, but Range is reserved Python keyword
        if span[1] < span[0]:
            span = (span[1], span[1] + 1)
        # Create a Horizontal Box Layout
        parent_layout = QtWidgets.QHBoxLayout()

        # Create and setup widgets
        self._double_spinBox = QtWidgets.QDoubleSpinBox()
        self._double_spinBox.setSingleStep(singleStep)
        self._double_spinBox.setDecimals(0)
        self._double_spinBox.setRange(span[0], span[1])
        self._double_spinBox.valueChanged.connect(
            lambda x: self.__changeValue(x))
        parent_layout.addWidget(QtWidgets.QLabel("{0} :".format(label)))
        parent_layout.addWidget(self._double_spinBox)

        # Configure the QFrame parent widget
        self.setLayout(parent_layout)
        self.setFixedHeight(fixed_height)

        # Private attribute(s)
        self.__value = span[0]
        self.__span = span

    @property
    def value(self):
        return self.__value

    # Double/float type expected
    @value.setter
    def value(self, val):
        self.__value = clamp(val, self.__span[0], self.__span[1])
        self._double_spinBox.setValue(self.__value)
        self.valueChanged.emit(self.__value)

    # Emit the stored double/float value
    def __changeValue(self, val):
        self.__value = val
        self.valueChanged.emit(self.__value)


class FloatSpinBoxControl(QtWidgets.QFrame):
    # Sliderless float spin box
    valueChanged = Signal(float)

    def __init__(self, label=None, span=(0, 100), singleStep=1, parent=None):
        super(FloatSpinBoxControl, self).__init__(parent)

        fixed_height = 36
        # Span is Range, but Range is reserved Python keyword
        if span[1] < span[0]:
            span = (span[1], span[1] + 1)
        # Create a Horizontal Box Layout
        parent_layout = QtWidgets.QHBoxLayout()

        # Create and setup widgets
        self._double_spinBox = QtWidgets.QDoubleSpinBox()
        self._double_spinBox.setSingleStep(singleStep)
        self._double_spinBox.setRange(span[0], span[1])
        self._double_spinBox.valueChanged.connect(
            lambda x: self.__changeValue(x))
        parent_layout.addWidget(QtWidgets.QLabel("{0} :".format(label)))
        parent_layout.addWidget(self._double_spinBox)

        # Configure the QFrame parent widget
        self.setLayout(parent_layout)
        self.setFixedHeight(fixed_height)

        # Private attribute(s)
        self.__value = span[0]
        self.__span = span

    @property
    def value(self):
        return self.__value

    # Double/float type expected
    @value.setter
    def value(self, val):
        self.__value = clamp(val, self.__span[0], self.__span[1])
        self._double_spinBox.setValue(self.__value)
        self.valueChanged.emit(self.__value)

    # Emit the stored double/float value
    def __changeValue(self, val):
        self.__value = val
        self.valueChanged.emit(self.__value)


class FloatSliderControl(QtWidgets.QGroupBox):
    # iClone inspired slider with float spin box, takes a range/span for min/max values
    valueChanged = Signal(float)

    def __init__(self, label=None, span=(0, 1), parent=None):
        # Span should be a value between 0 and 1
        super(FloatSliderControl, self).__init__(parent)
        factor = 1000
        # Create a Horizontal Box Layout
        parent_layout = QtWidgets.QHBoxLayout()

        self._slider = QtWidgets.QSlider(
            orientation=Qt.Horizontal, singleStep=1, maximum=span[1] * factor, minimum=span[0] * factor)
        self._slider.valueChanged.connect(lambda x: self.__changeValue(x))
        self._double_spinBox = QtWidgets.QDoubleSpinBox(
            singleStep=0.025, decimals=3, maximum=span[1], minimum=span[0])
        self._double_spinBox.valueChanged.connect(
            lambda x: self.__changeValue(x, False))

        parent_layout.addWidget(self._slider)
        parent_layout.addWidget(self._double_spinBox)

        # Configure the Group Box parent widget
        self.setTitle("{0} :".format(label))
        self.setLayout(parent_layout)
        self.setStyleSheet("QGroupBox  {color: #a2ec13}")

        # Private attribute(s)
        self.__factor = factor
        self.__value = span[0]
        self.__span = span

    def __blockSignals(self, cond=True):
        self._double_spinBox.blockSignals(cond)
        self._slider.blockSignals(cond)

    def __changeValue(self, val, slider=True):
        self.__blockSignals()
        if slider:
            self.__value = val / self.__factor
            self._double_spinBox.setValue(self.__value)
        else:
            self.__value = val
            self._slider.setValue(val * self.__factor)
        self.__blockSignals(False)
        self.valueChanged.emit(self.__value)

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, val):
        self.__value = clamp(val, self.__span[0], self.__span[1])
        self.__blockSignals()
        self._double_spinBox.setValue(self.__value)
        self._slider.setValue(self.__value * self.__factor)
        self.valueChanged.emit(self.__value)
        self.__blockSignals(False)


class Vector3Control(QtWidgets.QGroupBox):
    # iClone inspired vector3 input suitable for transformations
    valueChanged = Signal(RLPy.RVector3)

    def __init__(self, label=None, maxRange=1000, singleStep=0.025, parent=None):
        super(Vector3Control, self).__init__(parent)
        # Create a Horizontal Box Layout
        parent_layout = QtWidgets.QHBoxLayout()

        # Create and setup individual float spin box widgets
        self._x = QtWidgets.QDoubleSpinBox()
        self._y = QtWidgets.QDoubleSpinBox()
        self._z = QtWidgets.QDoubleSpinBox()
        for k, v in {"X": self._x, "Y": self._y, "Z": self._z}.items():
            v.setRange(-maxRange, maxRange)
            v.setSingleStep(singleStep)
            v.valueChanged.connect(self.__changeValue)
            parent_layout.addWidget(QtWidgets.QLabel(k))
            parent_layout.addWidget(v)

        # Configure the Group Box parent widget
        self.setTitle("{0} :".format(label))
        self.setLayout(parent_layout)
        self.setStyleSheet("QGroupBox  {color: #a2ec13}")

        # Private attribute(s)
        self.__value = RLPy.RVector3(0, 0, 0)

    @property
    def value(self):
        return self.__value

    # Vector3 value type expected
    @value.setter
    def value(self, val):
        self.__value = val
        self._x.setValue(val.x)
        self._y.setValue(val.y)
        self._z.setValue(val.z)
        self.valueChanged.emit(self.__value)

    # Emit the stored Vector3 value
    def __changeValue(self):
        self.__value = RLPy.RVector3(
            self._x.value(),
            self._y.value(),
            self._z.value())
        self.valueChanged.emit(self.__value)
