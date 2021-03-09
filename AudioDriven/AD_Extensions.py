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

# Extends upon base classes in QtWdigets.
# Provides common operational functions

import RLPy, math, json, os
from functools import *
from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.shiboken2 import wrapInstance


def Lerp(value1, value2, amount):
    return value1 + (value2 - value1) * amount


class Switch(QtWidgets.QWidget):
    def __init__(self, label="Switch", on=True, parent=None):
        super(Switch, self).__init__()

        self.__on = not on

        plate = QtWidgets.QPushButton()
        switch = QtWidgets.QPushButton()
        background = QtWidgets.QFrame()

        background.setFixedSize(64, 20)
        switch.setFixedSize(30, 18)
        switch.setStyleSheet("border: 2px solid #282828; border-radius: 9px; background-color: #c8c8c8;")
        plate.setFixedSize(30, 20)
        plate.setStyleSheet("font: bold; font-size: 10px; border: 0; background-color: rgba(0, 0, 0, 0); color: #c8c8c8;")
  
        background.setLayout(QtWidgets.QHBoxLayout())
        background.layout().addWidget(switch)
        background.layout().addWidget(plate)
        background.layout().setSpacing(0)
        background.layout().setContentsMargins(2, 0, 2, 0)

        self.setFixedHeight(25)
        self.setLayout(QtWidgets.QHBoxLayout())
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(QtWidgets.QLabel(label))
        self.layout().addStretch()
        self.layout().addWidget(background)

        def toggle():
            self.__on = not self.__on
            background.layout().removeWidget(switch)
            if self.__on:
                background.layout().addWidget(switch)
                plate.setText("ON")
                background.setStyleSheet("border: 0; border-radius: 10px; background-color: #505050;")
            else:
                background.layout().insertWidget(0, switch)
                plate.setText("OFF")
                background.setStyleSheet("border: 0; border-radius: 10px; background-color: #505050;")

        plate.clicked.connect(toggle)
        switch.clicked.connect(toggle)

        toggle()

        if parent:
            parent.addWidget(self)

    @property
    def value(self):
        return self.__on


class Button(QtWidgets.QPushButton):

    def __init__(self, label="Button", enabled=True, parent=None):
        super(Button, self).__init__(label)

        self.setFixedHeight(25)
        self.setEnabled(enabled)

        if parent:
            parent.addWidget(self)


class ProgressBar(QtWidgets.QProgressBar):

    def __init__(self, label=None, visible=True, parent=None):
        super(ProgressBar, self).__init__()

        self.__label = label

        self.setRange(0, 1000)
        self.setValue(0)
        self.setFixedHeight(25)
        self.setStyleSheet("""font-style: bold; color: black; border: 1px solid black;
        background-color: grey; ::chunk { width: 1px; background-color: #a2ec13}""")
        self.setVisible(visible)

        if parent:
            parent.addWidget(self)

    @property
    def value(self):
        return self.value()

    @value.setter
    def value(self, v):
        self.setValue(v * 1000)
        if self.__label:
            self.setFormat(f"{self.__label}: {round(v * 100)}%")
        else:
            self.setFormat(f"{round(v * 100)}%")

    @property
    def label(self):
        return self.__label

    @label.setter
    def label(self, text):
        self.__label = text
        self.value = 0


class FileControl(QtWidgets.QWidget):

    valueChanged = QtCore.Signal(str)

    def __init__(self, label="File", extensions="All files (*.*)", parent=None):
        super(FileControl, self).__init__()

        self.__path = None
        self.__extensions = extensions

        bot_half = QtWidgets.QHBoxLayout()
        self.lineEdit = QtWidgets.QLineEdit(readOnly=True)
        self.button = QtWidgets.QPushButton("....")
        self.button.setFixedSize(25, 25)
        self.button.clicked.connect(self.open_file)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(QtWidgets.QLabel(label))
        self.layout().addLayout(bot_half)

        bot_half.addWidget(self.lineEdit)
        bot_half.addWidget(self.button)

        if parent:
            parent.addWidget(self)

    def open_file(self):
        file_path = RLPy.RUi.OpenFileDialog(self.__extensions)

        if file_path is not "":
            self.__path = file_path
            self.lineEdit.setText(os.path.basename(self.__path))
            self.valueChanged.emit(self.__path)

    @property
    def value(self):
        return self.__path


class SelectionControl(QtWidgets.QWidget):

    valueChanged = QtCore.Signal(list)

    def __init__(self, label="Selections", node_type=RLPy.EObjectType_Prop, height=60, parent=None):
        super(SelectionControl, self).__init__()

        self.__nodeType = node_type
        self.__objects = []
        self.listView = QtWidgets.QListView()

        self.setStyleSheet("QListView {border:1px solid rgb(72, 72, 72);}")
        self.listView.setFixedHeight(height)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(QtWidgets.QLabel(label))
        self.layout().addWidget(self.listView)

        if parent:
            parent.addWidget(self)

        self.refresh()

    def refresh(self):
        items = RLPy.RScene.GetSelectedObjects()
        selected_objects = []
        self.__objects.clear()
        for item in items:
            if item.GetType() == self.__nodeType:
                selected_objects.append(item.GetName())
                self.__objects.append(item)
        if len(self.__objects) > 0:
            self.listView.setModel(QtGui.QStringListModel(selected_objects))
            self.listView.setStyleSheet("")
        else:
            self.listView.setModel(
                QtGui.QStringListModel(["-- Nothing Selected --"]))
            self.listView.setStyleSheet("color: rgb(72, 72, 72);")
        self.valueChanged.emit(self.__objects)

    @property
    def value(self):
        return self.__objects


class GroupBox(QtWidgets.QGroupBox):

    def __init__(self, label="Group", parent=None):
        super(GroupBox, self).__init__(parent)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.setTitle(label)
        self.setStyleSheet("QGroupBox  {color: #a2ec13}")


class DropdownControl(QtWidgets.QWidget):

    def __init__(self, label="Select", entrys=["Option A", "Option B", "Option C"], selection=0, parent=None):

        super(DropdownControl, self).__init__()

        self.__currentText = entrys[selection]
        self.__currentIndex = selection

        label = QtWidgets.QLabel(label)
        comboBox = QtWidgets.QComboBox()
        comboBox.addItems(entrys)

        self.setLayout(QtWidgets.QHBoxLayout())
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(label)
        self.layout().addWidget(comboBox)

        def change_index():
            self.__currentText = comboBox.currentText()
            self.__currentIndex = comboBox.currentIndex()

        comboBox.currentIndexChanged.connect(change_index)
        
        if parent:
            parent.addWidget(self)

    @property
    def currentText(self):
        return self.__currentText

    @property
    def currentIndex(self):
        return self.__currentIndex


class PalletControl(QtWidgets.QWidget):
    def __init__(self, label="Color", color=(255, 255, 255), expanded=True, enabled=True, parent=None):
        super(PalletControl, self).__init__()

        self.__color = QtGui.QColor()
        self.__color.setRgb(color[0], color[1], color[2])
        self.__enabled = enabled

        top_layout = QtWidgets.QHBoxLayout()
        rgb_layout = QtWidgets.QVBoxLayout()
        hsv_layout = QtWidgets.QVBoxLayout()

        widget = QtWidgets.QWidget()

        button = QtWidgets.QPushButton()
        pallet = QtWidgets.QPushButton()
        carot = QtWidgets.QPushButton("-" if expanded else "+")
        rgb = []
        hsv = []
        pallet.setFixedSize(64, 64)
        button.setFixedSize(64, 18)
        pallet.setStyleSheet("background-color:rgb(%d,%d,%d)" %
                             (color[0], color[1], color[2]))
        button.setStyleSheet("background-color:rgb(%d,%d,%d)" %
                             (color[0], color[1], color[2]))

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addLayout(top_layout)
        self.layout().addWidget(widget)

        for layout in [self.layout(), rgb_layout, hsv_layout]:
            layout.setSpacing(0)
            layout.setContentsMargins(0, 0, 0, 0)

        checkBox = QtWidgets.QCheckBox()
        title = QtWidgets.QLabel(label)
        checkBox.setChecked(enabled)
        carot.setFixedSize(16, 16)

        top_layout.addWidget(checkBox)
        top_layout.addWidget(title)
        top_layout.addStretch()
        top_layout.addWidget(button)
        top_layout.addSpacing(4)
        top_layout.addWidget(carot)

        widget.setLayout(QtWidgets.QHBoxLayout())
        widget.layout().addWidget(pallet)
        widget.layout().addStretch()
        widget.layout().addLayout(rgb_layout)
        widget.layout().addLayout(hsv_layout)

        widget.setVisible(expanded)
        button.setVisible(not expanded)

        def expand_collapse():
            expanded = not widget.isVisible()
            widget.setVisible(expanded)
            QtCore.QTimer.singleShot(10, lambda: self.window().adjustSize())
            carot.setText("-" if expanded else "+")
            button.setVisible(expanded)
            button.setVisible(not expanded)

        def set_rgb():
            self.__color.setRgb(rgb[0].value(), rgb[1].value(), rgb[2].value())
            button.setStyleSheet(
                "background-color: {}".format(self.__color.name()))
            pallet.setStyleSheet(
                "background-color: {}".format(self.__color.name()))
            for i in range(3):
                hsv[i].blockSignals(True)
                hsv[i].setValue(self.__color.getHsv()[i])
                hsv[i].blockSignals(False)

        def set_hsv():
            self.__color.setHsv(hsv[0].value(), hsv[1].value(), hsv[2].value())
            button.setStyleSheet(
                "background-color: {}".format(self.__color.name()))
            pallet.setStyleSheet(
                "background-color: {}".format(self.__color.name()))
            for i in range(3):
                rgb[i].blockSignals(True)
                rgb[i].setValue(self.__color.getRgb()[i])
                rgb[i].blockSignals(False)

        for index, channel in {0: "R", 1: "G", 2: "B"}.items():
            child_layout = QtWidgets.QHBoxLayout()
            child_spinBox = QtWidgets.QSpinBox(
                minimum=0, maximum=255, value=color[index])
            child_spinBox.valueChanged.connect(set_rgb)
            rgb.append(child_spinBox)
            child_layout.addWidget(QtWidgets.QLabel(
                channel + " : ", alignment=(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)))
            child_layout.addWidget(child_spinBox)
            rgb_layout.addLayout(child_layout)

        for index, channel in {0: "H", 1: "S", 2: "V"}.items():
            child_layout = QtWidgets.QHBoxLayout()
            child_spinBox = QtWidgets.QSpinBox(
                minimum=0, maximum=255, value=self.__color.getHsv()[index])
            child_spinBox.valueChanged.connect(set_hsv)
            hsv.append(child_spinBox)
            child_layout.addWidget(QtWidgets.QLabel(
                channel + " : ", alignment=(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)))
            child_layout.addWidget(child_spinBox)
            hsv_layout.addLayout(child_layout)

        def interactable(state):
            widget.setEnabled(state)
            button.setEnabled(state)
            self.__enabled = state
            if(state):
                button.setStyleSheet(
                    "background-color: {}".format(self.__color.name()))
                pallet.setStyleSheet(
                    "background-color: {}".format(self.__color.name()))
            else:
                button.setStyleSheet("background-color:{0,0,0,0}")
                pallet.setStyleSheet("background-color:{0,0,0,0}")

        def on_clicked():
            self.__color = QtWidgets.QColorDialog(self.__color).getColor()
            if self.__color.isValid():
                button.setStyleSheet(
                    "background-color: {}".format(self.__color.name()))
                pallet.setStyleSheet(
                    "background-color: {}".format(self.__color.name()))
                for i in range(3):
                    rgb[i].blockSignals(True)
                    hsv[i].blockSignals(True)
                    rgb[i].setValue(self.__color.getRgb()[i])
                    hsv[i].setValue(self.__color.getHsv()[i])
                    rgb[i].blockSignals(False)
                    hsv[i].blockSignals(False)

        checkBox.stateChanged.connect(lambda x: interactable(x))
        button.clicked.connect(on_clicked)
        pallet.clicked.connect(on_clicked)
        carot.clicked.connect(expand_collapse)

        if parent:
            parent.addWidget(self)

    @property
    def rgba(self):
        return self.__color.getRgb()

    @property
    def hsv(self):
        return self.__color.getHsv()

    @property
    def hsl(self):
        return self.__color.getHsl()

    @property
    def enabled(self):
        return self.__enabled


class SliderControl(QtWidgets.QWidget):

    def __init__(self, label="Value", span=(0, 10, 0), decimals=0, checkbox=False, parent=None):

        super(SliderControl, self).__init__()

        self.__value = span[2]
        self.__enabled = True

        factor = 10 ** decimals if decimals > 0 else 1
        top_layout = QtWidgets.QHBoxLayout()
        bot_layout = QtWidgets.QHBoxLayout()
        checkBox = QtWidgets.QCheckBox()
        title = QtWidgets.QLabel(label, alignment=QtCore.Qt.AlignVCenter)
        slider = QtWidgets.QSlider(orientation=QtCore.Qt.Horizontal,
                                   singleStep=1, minimum=span[0] * factor, maximum=span[1] * factor, value=span[2] * factor)
        spinBox = QtWidgets.QDoubleSpinBox(
            singleStep=1, decimals=decimals, maximum=span[1], minimum=span[0], value=span[2])

        checkBox.setChecked(True)
        checkBox.stateChanged.connect(
            lambda x: [slider.setEnabled(x), spinBox.setEnabled(x), setEnabled(x)])
        checkBox.setVisible(checkbox)
        slider.valueChanged.connect(lambda x: spinBox.setValue(x / factor))
        spinBox.valueChanged.connect(lambda x: [slider.setValue(x * factor), change_value(x)])

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addLayout(top_layout)
        self.layout().addLayout(bot_layout)

        top_layout.addWidget(checkBox)
        top_layout.addWidget(title)
        top_layout.addStretch()

        bot_layout.addWidget(slider)
        bot_layout.addWidget(spinBox)

        if parent:
            parent.addWidget(self)

        def change_value(value):
            value = value if decimals > 0 else int(value)
            self.__value = value
            
        def setEnabled(value):
            self.__enabled = value

    @property
    def value(self):
        return self.__value
    
    @property
    def enabled(self):
        return self.__enabled


class Vector3Control(QtWidgets.QWidget):

    def __init__(self, label="Vector", span=(-1000, 1000, 0), singleStep=0.025, checked=[True, True, True], parent=None):
        super(Vector3Control, self).__init__()

        self.__enabled = [checked[0], checked[1], checked[2]]
        self.__value = [span[2], span[2], span[2]]
        self.__vector = {"x": span[2], "y": span[2], "z": span[2]}

        self.setLayout(QtWidgets.QHBoxLayout())
        self.layout().setSpacing(2)
        self.layout().setContentsMargins(0, 0, 0, 0)

        def enable_disable(spinBox, axis, cond):
            spinBox.setEnabled(cond)
            index = {"X": 0, "Y": 1, "Z": 2}[axis]
            self.__enabled[index] = cond > 0

        def change_value(axis, value):
            self.__vector[axis.lower()] = value
            index = {"X": 0, "Y": 1, "Z": 2}[axis]
            self.__value[index] = value

        for axis, checked in {"X": checked[0], "Y": checked[1], "Z": checked[2]}.items():
            layout = QtWidgets.QVBoxLayout()
            top_layout = QtWidgets.QHBoxLayout()
            checkbox = QtWidgets.QCheckBox()
            spinBox = QtWidgets.QDoubleSpinBox(
                minimum=span[0], maximum=span[1], value=span[2])

            top_layout.addWidget(checkbox)
            top_layout.addWidget(QtWidgets.QLabel("%s %s :" % (label, axis)))
            top_layout.addStretch()

            layout.addLayout(top_layout)
            layout.addWidget(spinBox)

            checkbox.setChecked(checked)
            spinBox.setEnabled(checked)

            checkbox.stateChanged.connect(
                partial(enable_disable, spinBox, axis))
            spinBox.valueChanged.connect(partial(change_value, axis))

            self.layout().addLayout(layout)

        if parent:
            parent.addWidget(self)

    @property
    def value(self):
        return self.__value

    @property
    def vector(self):
        return self.__vector

    @property
    def enabled(self):
        return self.__enabled
