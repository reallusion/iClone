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

import os, math, RLPy, wave, wavio
import numpy as np
from scipy.fftpack import fft
from PySide2.QtMultimedia import QSound
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2 import QtWidgets, QtGui
from PySide2.shiboken2 import wrapInstance

# Utilize custom extension functions: more information in AD_Extensions.py
import AD_Extensions as Ext

ui = {}  # User Interface
all_events, dialog_event_callback, event_callback = [], None, None  # Events and callbacks
all_clones, audio_spectrogram, all_items = [], [], []  # Script related globals


class SelectionEventCallback(RLPy.REventCallback):
    def __init__(self):
        RLPy.REventCallback.__init__(self)

    def OnObjectSelectionChanged(self):
        global ui
        ui["selection"].refresh()
        ui["sync"].setVisible(len(ui["selection"].value) > 1)
        ui["sync"].window().adjustSize()


class DialogEventCallback(RLPy.RDialogCallback):
    def __init__(self):
        RLPy.RDialogCallback.__init__(self)

    def OnDialogHide(self):
        global all_events

        for event in all_events:
            RLPy.REventHandler.UnregisterCallback(event)
        all_events.clear()


def register_callbacks():
    global all_events, event_callback

    event_callback = SelectionEventCallback()
    ID = RLPy.REventHandler.RegisterCallback(event_callback)
    all_events.append(ID)


def show_dialog():
    global ui, dialog_event_callback

    # Create the Dialog window
    ui["dialog"] = RLPy.RUi.CreateRDialog()
    ui["dialog"].SetWindowTitle("Audio Driven")

    # Register dialog events
    dialog_event_callback = DialogEventCallback()
    dialog_event_id = ui["dialog"].RegisterEventCallback(dialog_event_callback)

    # Create Pyside layout for RDialog
    dialog = wrapInstance(int(ui["dialog"].GetWindow()), QtWidgets.QDialog)
    dialog.setFixedWidth(300)

    ui["wave_file"] = Ext.FileControl("WAV File :", "WAVE (*.wav)", dialog.layout())
    ui["selection"] = Ext.SelectionControl("Current Selections :", parent=dialog.layout())
    ui["sync"] = Ext.Switch("Syncronize Animations :", parent=dialog.layout())  # Sync the animations across clone groups
    ui["clones"] = Ext.SliderControl("Clones", (1, 20, 10), parent=dialog.layout())
    ui["spacing"] = Ext.SliderControl("Spacing", (-1000, 1000, 120), parent=dialog.layout())
    ui["alignment"] = Ext.DropdownControl("Alignment :", ["X", "Y", "Z"], parent=dialog.layout())
    ui["color"] = Ext.PalletControl("Transition Color :", (255, 0, 0), False, parent=dialog.layout())
    ui["ramp"] = Ext.SliderControl("Ramp & Fade (secs)", (0.1, 3, 0.5), 2, True, parent=dialog.layout())  # Ramp up and down time for the animation in seconds
    ui["move"] = Ext.Vector3Control("Move", (1, 9999, 500), 1, [False, False, False], parent=dialog.layout())
    ui["size"] = Ext.Vector3Control("Scale", (0, 999, 10), 0.5, [False, False, True], parent=dialog.layout())
    ui["apply"] = Ext.Button("Apply", False, dialog.layout())
    ui["progress"] = Ext.ProgressBar("Progress", False, dialog.layout())

    ui["wave_file"].valueChanged.connect(audio_to_spectrogram)
    ui["selection"].valueChanged.connect(check_criteria)
    ui["apply"].clicked.connect(drive_by_audio)
    ui["sync"].setVisible(len(ui["selection"].value) > 1)

    ui["dialog"].Show()

    register_callbacks()


def check_criteria():
    # Do we meet the criteria for executing this script?
    global ui

    cond = ui["wave_file"].value is not None and len(ui["selection"].value) > 0
    ui["apply"].setEnabled(cond)


def audio_to_spectrogram(path):
    global audio_spectrogram

    audio_spectrogram.clear()

    # Create an audio object in the scene
    audio_object = RLPy.RAudio.CreateAudioObject()
    audio_object.Load(path)

    # Process the wave audio file
    try:
        wav = wave.open(path, "rb")  # Open the wave file in read-only mode.
        framerate, nframes = wav.getparams()[2:4]  # Grab sampling frequency and number of frames
        duration = int(nframes*(1/framerate) * 1000)  # Duration of audio in milliseconds
        fps_ratio = int(framerate / RLPy.RGlobal.GetFps())  # Wave vs iClone fps ratio, ex: 44100 / 60 = 735
        wav_bytes = wav.readframes(nframes)  # Reads and returns at most n frames of audio, as a bytes object.
        sampwidth = wav.getsampwidth()
        wav.close()  # Close the wave file, we don't need it anymore
    except Exception as e:
        RLPy.RUi.ShowMessageBox("File error", str(e), RLPy.EMsgButton_Close)

    
    wav_data = wavio.read(path).data
    # print('wave data:', wav_data)
    # wav_bytes = wav_bytes.replace('\x', ' \x')
    # wav_data = np.fromstring(wav_bytes, dtype=np.int32)  # Turn 8 bits to a numpy integer array
    if wav_data.shape[0] * wav_data.shape[1] % 2 != 0:
        # wav_data = np.append(wav_data, [wav_data[-1]], axis=0)
        wav_data = np.append(wav_data, np.zeros((1, wav_data.shape[1])), axis=0)

    wav_data.shape = -1, 2  # Shape the data into tupples with indefinite rows and 2 columns
    wav_data = wav_data.T  # Turn the 2 separate array data into a single dual channel audio data array

    wav_frame = 0
    while(wav_frame < len(wav_data[0])):
        # Derive frequency domain from a segment of 160 signals
        wav_fft = fft(wav_data[0][wav_frame: wav_frame+fps_ratio-1])
        half_len = int(len(wav_fft)/2) - 1  # Cut the signal by half for the positive side
        fft_abs = abs(wav_fft[:half_len]) * 2 / (256*(half_len))
        audio_spectrogram.append(fft_abs)
        wav_frame += fps_ratio

    check_criteria()


def reset():
    global all_events, all_clones, all_items
    global ui

    progress = 0
    processes = sum(len(i) for i in all_clones)
    ui["progress"].label = "Removing Clones"
    ui["progress"].value = 0

    for g in all_clones:
        for c in g:
            if RLPy.RScene.FindObject(RLPy.EObjectType_Prop, c.GetName()):
                RLPy.RScene.RemoveObject(c)
            progress += 1
            ui["progress"].value = progress/processes
    for item in all_items:
        item.SetDummy(False)
    all_items.clear()


def spectrogram_to_value(value=0):
    # Derive a value from audio spectrogram that can be used for animations
    global audio_spectrogram, all_clones

    max_freqs = []
    all_avg_freqs = []
    
    # print('sum(len(j) for j in all_clones):', sum(len(j) for j in all_clones))
    for i in range(len(audio_spectrogram)):
        object_amount = sum(len(j) for j in all_clones)
        # print('i:', i)

        freq_step = 50 // object_amount   # 50 is around 3000 Hz on the soundwave, ex: 366 /10 = 36 % 6 without the remainder
        avg_freqs = []
        for x in range(object_amount):
            # print('x:', x)
            freq = np.mean(audio_spectrogram[i][freq_step * (x+1): freq_step * (x+2)])
            avg_freqs.append(freq)
        if len(avg_freqs) > 0:
            max_freqs.append(max(avg_freqs))
            all_avg_freqs.append(avg_freqs)

    amplitude = value / max(max_freqs) if len(max_freqs) else value
    converted_data = []

    for k in range(len(all_avg_freqs)):
        converted_data.append([i*amplitude for i in all_avg_freqs[k]])

    return converted_data


def set_transform_key(clone, time, transform):
    key = RLPy.RTransformKey()
    key.SetTime(time)
    key.SetTransform(transform)
    control = clone.GetControl("Transform")
    control.AddKey(key, RLPy.RGlobal.GetFps())
    control.SetKeyTransition(time, RLPy.ETransitionType_Ease_Out, 1.0)


def drive_by_audio():
    global ui, audio_spectrogram, all_clones

    ui["apply"].setVisible(False)
    ui["progress"].setVisible(True)
    reset()

    all_clones = clone_and_offset()
    final_time = RLPy.RGlobal.GetTime()
    start_time = RLPy.RGlobal.GetTime()
    start_frame = RLPy.RTime.GetFrameIndex(start_time, RLPy.RGlobal.GetFps())
    ui["progress"].label = "Applying Animations"
    processes = sum(len(i) for i in all_clones) * len(audio_spectrogram)
    progress = 0

    audio_move = {  # Build movement tuples list from the audio data
        "x": spectrogram_to_value(ui["move"].value[0]),
        "y": spectrogram_to_value(ui["move"].value[1]),
        "z": spectrogram_to_value(ui["move"].value[2])
    }
    # print("audio_move:", audio_move)

    audio_scale = {  # Build scale tuples list from the audio data
        "x": spectrogram_to_value(ui["size"].value[0]),
        "y": spectrogram_to_value(ui["size"].value[1]),
        "z": spectrogram_to_value(ui["size"].value[2])
    }
    # print("audio_scale:", audio_scale)

    for c in all_clones:
        for i in range(len(c)):
            control = c[i].GetControl("Transform")
            transform = c[i].LocalTransform()
            animation = RLPy.RTransform(transform)
            key = RLPy.RTransformKey()

            for f in range(len(audio_spectrogram)):
                animation.T().SetXYZ(
                    audio_move["x"][f][i] + transform.T().x if ui["move"].enabled[0] else transform.T().x,
                    audio_move["y"][f][i] + transform.T().y if ui["move"].enabled[1] else transform.T().y,
                    audio_move["z"][f][i] + transform.T().z if ui["move"].enabled[2] else transform.T().z
                )
                animation.S().SetXYZ(
                    audio_scale["x"][f][i] + transform.S().x if ui["size"].enabled[0] else transform.S().x,
                    audio_scale["y"][f][i] + transform.S().y if ui["size"].enabled[1] else transform.S().y,
                    audio_scale["z"][f][i] + transform.S().z if ui["size"].enabled[2] else transform.S().z
                )
                frame = start_frame + f + 1  # Shift 1 frame forward
                time = RLPy.RTime(RLPy.RTime.IndexedFrameTime(frame, RLPy.RGlobal.GetFps()))
                key.SetTime(time)
                key.SetTransform(animation)
                control.AddKey(key, RLPy.RGlobal.GetFps())
                control.SetKeyTransition(time, RLPy.ETransitionType_Linear, 1.0)
                final_time = time
                progress += 1
                ui["progress"].value = progress / processes

            if ui["ramp"].enabled:
                start_time = RLPy.RGlobal.GetTime() - ui["ramp"].value * 1000
                final_time = final_time + ui["ramp"].value * 1000
            else:
                start_time = RLPy.RGlobal.GetTime() - 1
                final_time = final_time + 1

            set_transform_key(c[i], start_time, transform)
            set_transform_key(c[i], final_time, transform)

    audio_object = RLPy.RAudio.CreateAudioObject()
    audio_object.Load(ui["wave_file"].value)
    RLPy.RAudio.LoadAudioToObject(all_clones[0][0], audio_object, RLPy.RGlobal.GetTime())
    RLPy.RGlobal.Play(start_time, final_time)

    ui["apply"].setVisible(True)
    ui["progress"].setVisible(False)

def clone_and_offset():
    global ui, all_items

    clones = []

    for item in ui["selection"].value:
        all_items.append(item)
        control = item.GetControl("Transform")
        data_block = control.GetDataBlock()
        transform = item.LocalTransform()
        position = {"X": item.LocalTransform().T().x, "Y": item.LocalTransform().T().y, "Z": item.LocalTransform().T().z}

        entry = []
        if ui["sync"].value:
            clones.append(entry)
        else:
            if len(clones) is 0:
                clones.append(entry)
            else:
                entry = clones[0]

        for i in range(ui["clones"].value):
            clone = item.Clone()
            entry.append(clone)
            control = clone.GetControl("Transform")
            control.SetValue(RLPy.RGlobal.GetStartTime(), transform)
            data_block = control.GetDataBlock()
            offset = position[ui["alignment"].currentText] + ui["spacing"].value * i
            data_block.GetControl("Position/Position"+ui["alignment"].currentText).SetValue(RLPy.RGlobal.GetStartTime(), offset)
            step = i/(ui["clones"].value-1)

            if ui["color"].enabled:
                new_item = RLPy.RScene.FindObject(RLPy.EObjectType_Prop, clone.GetName())  # Workaround for clone reference bug
                if new_item is None:
                    continue
                mesh_names = new_item.GetMeshNames()
                if len(mesh_names) == 0:
                    continue
                material_component = new_item.GetMaterialComponent()
                material_names = material_component.GetMaterialNames(mesh_names[0])
                if len(material_names) == 0:
                    continue
                color = material_component.GetDiffuseColor(mesh_names[0], material_names[0])
                r = Ext.Lerp(color.Red(), ui["color"].rgba[0], step) / 255
                g = Ext.Lerp(color.Green(), ui["color"].rgba[1], step) / 255
                b = Ext.Lerp(color.Blue(), ui["color"].rgba[2], step) / 255
                transition_color = RLPy.RRgb(r, g, b)
                material_component.AddDiffuseKey(RLPy.RKey(), mesh_names[0], material_names[0], transition_color)

        item.SetDummy(True)

    return clones


def initialize_plugin():
    # Create Pyside interface with iClone main window
    ic_dlg = wrapInstance(int(RLPy.RUi.GetMainWindow()), QtWidgets.QMainWindow)
    # Check if the menu item exists
    plugin_menu = ic_dlg.menuBar().findChild(QtWidgets.QMenu, "pysample_menu")
    if plugin_menu is None:
        # Create Pyside layout for QMenu named "Python Samples" and attach it to the Plugins menu
        plugin_menu = wrapInstance(int(RLPy.RUi.AddMenu("Python Samples", RLPy.EMenu_Plugins)), QtWidgets.QMenu)
        plugin_menu.setObjectName("pysample_menu")  # Setting an object name for the menu is equivalent to giving it an ID
    # Add the "Audio Driven" menu item to Plugins > Python Samples
    menu_action = plugin_menu.addAction("Audio Driven")
    # Show the dialog window when the menu item is triggered
    menu_action.triggered.connect(show_dialog)


def run_script():
    initialize_plugin()
