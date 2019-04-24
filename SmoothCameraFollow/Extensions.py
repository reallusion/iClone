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

# Extend upon base classes in RLPy & QtWdigets.
# These extensions can exist independently of other scripts.


import RLPy
from math import *
# -- Pyside QT Modules
from PySide2 import QtWidgets
from PySide2.QtCore import *


def inverseLerp(a, b, v):
    if RLPy.RMath.Abs(b-a) < 0:
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

class Vector3(RLPy.RVector3):

    # Inherit and extend on the RLPy vector3 class
    def __str__(self):
        # For debugging: pretty print for the Vector3 values
        return "({0},{1},{2})".format(str(self.x), str(self.y), str(self.z))

    # Static for scale vector: iClone default scale is not [100,100,100] as shown in the UI
    one = RLPy.RVector3(1, 1, 1)

    # Static for up vector: iClone is Z-up application
    up = RLPy.RVector3(0, 0, 1)

    def ToQuaternion(self):
        # yaw (Z), pitch (X), roll (Y)
        cy = cos(self.z * 0.5)
        sy = sin(self.z * 0.5)
        cp = cos(self.x * 0.5)
        sp = sin(self.x * 0.5)
        cr = cos(self.y * 0.5)
        sr = sin(self.y * 0.5)

        q = RLPy.RQuaternion()
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


class Quaternion(RLPy.RQuaternion):

    def __str__(self):
        # For debugging: pretty print for the Quaternion values
        return "({0},{1},{2},{3})".format(self.x, self.y, self.z, self.w)

    def Lerp(self, quat_to, f_interpolation):
        f_invert_interpolation = 1 - f_interpolation
        q = RLPy.RQuaternion()
        # Are we on the right (1) side of the graph or the left side (-1)? 
        direction = (((self.x * quat_to.x) + (self.y * quat_to.y)
                 ) + (self.z * quat_to.z)) + (self.w * quat_to.w)
        if direction >= 0:
            q.x = (f_invert_interpolation * self.x) + (f_interpolation * quat_to.x)
            q.y = (f_invert_interpolation * self.y) + (f_interpolation * quat_to.y)
            q.z = (f_invert_interpolation * self.z) + (f_interpolation * quat_to.z)
            q.w = (f_invert_interpolation * self.w) + (f_interpolation * quat_to.w)
        else:
            q.x = (f_invert_interpolation * self.x) - (f_interpolation * quat_to.x)
            q.y = (f_invert_interpolation * self.y) - (f_interpolation * quat_to.y)
            q.z = (f_invert_interpolation * self.z) - (f_interpolation * quat_to.z)
            q.w = (f_invert_interpolation * self.w) - (f_interpolation * quat_to.w)
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

class TimeLine():

    def __init__(self):
        self.__fps = RLPy.RGlobal.GetFps()
        self.__start_time = RLPy.RGlobal.GetStartTime()
        self.__end_time = RLPy.RGlobal.GetEndTime()
        self.__start_frame = RLPy.RTime.GetFrameIndex(
            self.__start_time, self.__fps)
        self.__end_frame = RLPy.RTime.GetFrameIndex(
            self.__end_time, self.__fps)
        self.__delta_time = 1 / self.__fps

    @property
    def start_frame(self):
        return self.__start_frame

    @property
    def end_frame(self):
        return self.__end_frame

    @property
    def delta_time(self):
        return self.__delta_time

    @property
    def start_time(self):
        return self.__start_time

    @property
    def end_time(self):
        return self.__end_time

    def IndexedFrameTime(self, frame_index):
        return RLPy.RTime.IndexedFrameTime( int(frame_index), self.__fps)


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


class NodeListComboBoxControl(QtWidgets.QGroupBox):
    # This control evaluates the scene for nodes of the specified type and lists them
    valueChanged = Signal(RLPy._object)
    # Default to the prop node type

    def __init__(self, label=None, nodeType=RLPy.EObjectType_Prop, parent=None):
        super(NodeListComboBoxControl, self).__init__(parent)
        # Create a Horizontal Box Layout
        parent_layout = QtWidgets.QHBoxLayout()

        # Private attribute(s)
        self.__objectList = {}
        self.__nodeType = nodeType
        # Create and setup widgets
        self._comboBox = QtWidgets.QComboBox()

        self.refresh()

        self._comboBox.currentIndexChanged.connect(self.__changeValue)

        parent_layout.addWidget(self._comboBox)

        # Configure the Group Box parent widget
        _nodeType = {RLPy.EObjectType_Avatar: "Avatar", RLPy.EObjectType_Prop: "Prop",
                     RLPy.EObjectType_Camera: "Camera", RLPy.EObjectType_Particle: "Particle"}[nodeType]
        self.setTitle("{0} ({1}) :".format(label, _nodeType))
        self.setLayout(parent_layout)
        self.setStyleSheet("QGroupBox  {color: #a2ec13;}")

    @property
    # Return the object reference for this UI, there is no getter for this
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
        self.__objectList = {0: None}
        # Search the scene for the node type specificed when initialized
        results = RLPy.RScene.FindObjects(self.__nodeType)

        for i in range(len(results)):
            self.__objectList[i+1] = results[i]
            self._comboBox.addItem(results[i].GetName())

        self._comboBox.blockSignals(False)
        self._comboBox.setCurrentIndex(0)


class IntSliderControl(QtWidgets.QGroupBox):
    # iClone inspired slider with float spin box, takes a range/span for min/max values
    valueChanged = Signal(int)

    def __init__(self, label=None, span=(0, 10), parent=None):
        # Span should be a value between 0 and 1
        super(IntSliderControl, self).__init__(parent)
        # Create a Horizontal Box Layout
        parent_layout = QtWidgets.QHBoxLayout()

        self._slider = QtWidgets.QSlider(
            orientation=Qt.Horizontal, singleStep=1, maximum=span[1], minimum=span[0])
        self._slider.valueChanged.connect(lambda x: self.__changeValue(x))
        self._double_spinBox = QtWidgets.QDoubleSpinBox(
            singleStep=1, decimals=0, maximum=span[1], minimum=span[0])
        self._double_spinBox.valueChanged.connect(
            lambda x: self.__changeValue(x, False))

        parent_layout.addWidget(self._slider)
        parent_layout.addWidget(self._double_spinBox)

        # Configure the Group Box parent widget
        self.setTitle("{0} :".format(label))
        self.setLayout(parent_layout)
        self.setStyleSheet("QGroupBox  {color: #a2ec13}")

        # Private attribute(s)
        self.__value = span[0]
        self.__span = span

    def __blockSignals(self, cond=True):
        self._double_spinBox.blockSignals(cond)
        self._slider.blockSignals(cond)

    def __changeValue(self, val, slider=True):
        self.__blockSignals()
        if slider:
            self.__value = val
            self._double_spinBox.setValue(self.__value)
        else:
            self.__value = val
            self._slider.setValue(val)
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
        self._slider.setValue(self.__value)
        self.valueChanged.emit(self.__value)
        self.__blockSignals(False)


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
        self.setStyleSheet("QGroupBox  {color: #a2ec13;}")

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
