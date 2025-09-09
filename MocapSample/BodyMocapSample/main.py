# Copyright 2022 The Reallusion Authors. All Rights Reserved.
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

import os
import sys
import json
import RLPy
import PySide2
# from PySide2 import *
from PySide2.QtCore import *
from PySide2.QtCore import QResource
from PySide2.QtCore import QFile
from PySide2.QtCore import QIODevice
from PySide2.QtGui import *
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import *
from shiboken2 import wrapInstance

rl_plugin_info = {"ap": "iClone", "ap_version": "8.0"}

mocap_dlg = None # mocap dialog
mocap_avatar = None # avatar
# network
exp_data = None
tcp_client = RLPy.RTcpClient()
network_callback = None
# mocap
mocap_manager = RLPy.RGlobal.GetMocapManager()
body_device = None
do_mocap = False
exp_count = 0

#{bone_name, parent_bone_name, Hik_bone_name}
hips = ["hips", "", "Hips"]
rightupleg = ["rightupleg", "hips", "RightUpLeg"]
rightleg = ["rightleg", "rightupleg", "RightLeg"]
rightfoot = ["rightfoot", "rightleg", "RightFoot"]
leftupleg = ["leftupleg", "hips", "LeftUpLeg"]
leftleg = ["leftleg", "leftupleg", "LeftLeg"]
leftfoot = ["leftfoot", "leftleg", "LeftFoot"]
spine = ["spine", "hips", "Spine"]
spine1 = ["spine1", "spine", "Spine3"]
spine2 = ["spine2", "spine1", "Spine6"]
spine3 = ["spine3", "spine2", "Spine9"]
neck = ["neck", "spine3", "Neck"]
head = ["head", "neck", "Head"]
rightshoulder = ["rightshoulder", "spine3", "RightShoulder"]
rightarm = ["rightarm", "rightshoulder", "RightArm"]
rightforearm = ["rightforearm", "rightarm", "RightForeArm"]
righthand = ["righthand", "rightforearm", "RightHand"]
righthandthumb1 = ["righthandthumb1", "righthand", "RightHandThumb1"]
righthandthumb2 = ["righthandthumb2", "righthandthumb1", "RightHandThumb2"]
righthandthumb3 = ["righthandthumb3", "righthandthumb2", "RightHandThumb3"]
rightinhandindex = ["rightinhandindex", "righthand", "RightInHandIndex"]
righthandindex1 = ["righthandindex1", "rightinhandindex", "RightHandIndex1"]
righthandindex2 = ["righthandindex2", "righthandindex1", "RightHandIndex2"]
righthandindex3 = ["righthandindex3", "righthandindex2", "RightHandIndex3"]
rightinhandmiddle = ["rightinhandmiddle", "righthand", "RightInHandMiddle"]
righthandmiddle1 = ["righthandmiddle1", "rightinhandmiddle", "RightHandMiddle1"]
righthandmiddle2 = ["righthandmiddle2", "righthandmiddle1", "RightHandMiddle2"]
righthandmiddle3 = ["righthandmiddle3", "righthandmiddle2", "RightHandMiddle3"]
rightinhandring = ["rightinhandring", "righthand", "RightInHandRing"]
righthandring1 = ["righthandring1", "rightinhandring", "RightHandRing1"]
righthandring2 = ["righthandring2", "righthandring1", "RightHandRing2"]
righthandring3 = ["righthandring3", "righthandring2", "RightHandRing3"]
rightinhandpinky = ["rightinhandpinky", "righthand", "RightInHandPinky"]
righthandpinky1 = ["righthandpinky1", "rightinhandpinky", "RightHandPinky1"]
righthandpinky2 = ["righthandpinky2", "righthandpinky1", "RightHandPinky2"]
righthandpinky3 = ["righthandpinky3", "righthandpinky2", "RightHandPinky3"]
leftshoulder = ["leftshoulder", "spine3", "LeftShoulder"]
leftarm = ["leftarm", "leftshoulder", "LeftArm"]
leftforearm = ["leftforearm", "leftarm", "LeftForeArm"]
lefthand = ["lefthand", "leftforearm", "LeftHand"]
lefthandthumb1 = ["lefthandthumb1", "lefthand", "LeftHandThumb1"]
lefthandthumb2 = ["lefthandthumb2", "lefthandthumb1", "LeftHandThumb2"]
lefthandthumb3 = ["lefthandthumb3", "lefthandthumb2", "LeftHandThumb3"]
leftinhandindex = ["leftinhandindex", "lefthand", "LeftInHandIndex"]
lefthandindex1 = ["lefthandindex1", "leftinhandindex", "LeftHandIndex1"]
lefthandindex2 = ["lefthandindex2", "lefthandindex1", "LeftHandIndex2"]
lefthandindex3 = ["lefthandindex3", "lefthandindex2", "LeftHandIndex3"]
leftinhandmiddle = ["leftinhandmiddle", "lefthand", "LeftInHandMiddle"]
lefthandmiddle1 = ["lefthandmiddle1", "leftinhandmiddle", "LeftHandMiddle1"]
lefthandmiddle2 = ["lefthandmiddle2", "lefthandmiddle1", "LeftHandMiddle2"]
lefthandmiddle3 = ["lefthandmiddle3", "lefthandmiddle2", "LeftHandMiddle3"]
leftinhandring = ["leftinhandring", "lefthand", "LeftInHandRing"]
lefthandring1 = ["lefthandring1", "leftinhandring", "LeftHandRing1"]
lefthandring2 = ["lefthandring2", "lefthandring1", "LeftHandRing2"]
lefthandring3 = ["lefthandring3", "lefthandring2", "LeftHandRing3"]
leftinhandpinky = ["leftinhandpinky", "lefthand", "LeftInHandPinky"]
lefthandpinky1 = ["lefthandpinky1", "leftinhandpinky", "LeftHandPinky1"]
lefthandpinky2 = ["lefthandpinky2", "lefthandpinky1", "LeftHandPinky2"]
lefthandpinky3 = ["lefthandpinky3", "lefthandpinky2", "LeftHandPinky3"]

bone_list = [hips, rightupleg, rightleg, rightfoot, leftupleg, leftleg, leftfoot, spine, spine1, spine2,
    spine3, neck, head, rightshoulder, rightarm, rightforearm, righthand, righthandthumb1,
    righthandthumb2, righthandthumb3, rightinhandindex, righthandindex1, righthandindex2,
    righthandindex3, rightinhandmiddle, righthandmiddle1, righthandmiddle2, righthandmiddle3,
    rightinhandring, righthandring1, righthandring2, righthandring3, rightinhandpinky,
    righthandpinky1, righthandpinky2, righthandpinky3, leftshoulder, leftarm, leftforearm,
    lefthand, lefthandthumb1, lefthandthumb2, lefthandthumb3, leftinhandindex, lefthandindex1,
    lefthandindex2, lefthandindex3, leftinhandmiddle, lefthandmiddle1, lefthandmiddle2,
    lefthandmiddle3, leftinhandring, lefthandring1, lefthandring2, lefthandring3, leftinhandpinky,
    lefthandpinky1, lefthandpinky2, lefthandpinky3]

t_pose_data = [0.0, 105.85, 0.0, 0, 0, 0, -11.5, -1.85, 0.0, 0, 0, 0, 0.0, -48.0, 0.0, 0, 0, 0, 0.0, -48.0, 0.0, 0, 0, 0, 11.5, -1.85, 0.0, 0, 0, 0, 0.0, -48.0, 0.0, 0, 0, 0, 0.0, -48.0, 0.0, 0, 0, 0.0, 0.0, 16.654, 0.0, 0, 0, 0, 0.0, 11.312, 0.0, 0, 0, 0, 0.0, 11.78, 0.0, 0, 0, 0, 0.0, 11.312, 0.0, 0, 0, 0, 0.0, 12.091, 0.0, 0, 0, 0, 0.0, 9.0, 0.0, 0, 0, 0, -3.5, 8.061, 0.0, 0, 0, 0, -14.0, 0.0, 0.0, 0, 0, 0, -29.0, 0.0, 0.0, 0, 0, 0, -28.0, 0.0, 0.0, 0, 0, 0, -2.702, 0.206, 3.388, 0, 30, 0, -3.998, 0.0, 0.0, 0, 0, 0, -2.778, 0.0, 0.0, 0, 0, 0, -3.5, 0.552, 2.148, 0, 0, 0, -5.664, -0.099, 1.085, 0, 0, 0, -3.93, 0.0, 0.0, 0, 0, 0, -2.228, 0.0, 0.0, 0, 0, 0, -3.672, 0.562, 0.822, 0, 0, 0, -5.618, -0.091, 0.341, 0, 0, 0, -4.288, 0.0, 0.0, 0, 0, 0, -2.688, 0.0, 0.0, 0, 0, 0, -3.654, 0.584, -0.14, 0, 0, 0, -5.032, -0.024, -0.52, 0, 0, 0, -3.737, 0.0, 0.0, 0, 0, 0, -2.593, 0.0, 0.0, 0, 0, 0, -3.432, 0.51, -1.305, 0, 0, 0, -4.496, -0.024, -1.184, 0, 0, 0, -2.993, 0.0, 0.0, 0, 0, 0, -1.891, 0.0, 0.0, 0, 0, 0, 3.5, 8.061, 0.0, 0, 0, 0, 14.0, 0.0, 0.0, 0, 0, 0, 29.0, 0.0, 0.0, 0, 0, 0, 28.0, 0.0, 0.0, 0, 0, 0, 2.702, 0.206, 3.388, 0, -30, 0, 3.998, 0.0, 0.0, 0, 0, 0, 2.778, 0.0, 0.0, 0, 0, 0, 3.5, 0.552, 2.148, 0, 0, 0, 5.664, -0.099, 1.085, 0, 0, 0, 3.93, 0.0, 0.0, 0, 0, 0, 2.228, 0.0, 0.0, 0, 0, 0, 3.672, 0.562, 0.822, 0, 0, 0, 5.618, -0.091, 0.341, 0, 0, 0, 4.288, 0.0, 0.0, 0, 0, 0, 2.688, 0.0, 0.0, 0, 0, 0, 3.654, 0.584, -0.14, 0, 0, 0, 5.032, -0.024, -0.52, 0, 0, 0, 3.737, 0.0, 0.0, 0, 0, 0, 2.593, 0.0, 0.0, 0, 0, 0, 3.432, 0.51, -1.305, 0, 0, 0, 4.496, -0.024, -1.184, 0, 0, 0, 2.993, 0.0, 0.0, 0, 0, 0, 1.891, 0.0, 0.0, 0, 0, 0]

class NetworkEventCallback(RLPy.RTcpCallback):
    def __init__(self):
        RLPy.RTcpCallback.__init__(self)

    def OnStatusChanged(self, is_connected):
        global mocap_dlg

        print(is_connected)
        ui_connect_btn = mocap_dlg.findChild(PySide2.QtWidgets.QPushButton, "qtConnectBtn")
        if ui_connect_btn:
            if is_connected:
                ui_connect_btn.setText("Disconnect")
            else:
                ui_connect_btn.setText("Connect")                


    def OnFailMessageReceived(self, fail_message):
        print(fail_message)

    def OnDataReceived(self):
        global data
        global tcp_client
        global exp_count
        global do_mocap
        global body_device
        global fram2_data

        data = bytearray(tcp_client.GetDataSize(0)) #index 0 => get the first come in data
        tcp_client.GetDataAt(0, data)
        if not do_mocap or body_device == None or mocap_avatar == None:
            return
        try:
            receive_str = data.decode()
            print(receive_str)
            body_list = json.loads(receive_str)
            if isinstance(body_list, list) and len(body_list) == len(t_pose_data):
                body_device.ProcessData(0, body_list)
        except:
            pass

def show_dialog():
    global mocap_dlg
    global render_files
    if mocap_dlg is None:
        mocap_dlg = create_dialog()
        
    if mocap_dlg.isVisible():
        mocap_dlg.hide()
    else:
        update_dialog()
        mocap_dlg.show()

def update_dialog():
    global mocap_avatar
    global exp_count
    global body_device
    global t_pose_data
    global bone_list

    ui_log_edit = mocap_dlg.findChild(PySide2.QtWidgets.QTextEdit, "qtLogText")
    if ui_log_edit:
        ui_log_edit.clear()
    avatar_list = RLPy.RScene.GetAvatars()
    if len( avatar_list ) <= 0:
        show_log("Can't find any avatar, please load a avatar first!")
        return
    mocap_avatar = avatar_list[0]

    # init mocap data
    mocap_manager.RemoveAllDevices()    
    body_device = mocap_manager.AddBodyDevice("BodyDevice")
    body_device.AddAvatar(mocap_avatar)
    body_device.SetEnable(mocap_avatar, True)
    body_setting = body_device.GetBodySetting(mocap_avatar)
    body_setting.SetReferenceAvatar(mocap_avatar)
    body_setting.SetActivePart(RLPy.EBodyActivePart_FullBody)
    body_setting.SetMotionApplyMode(RLPy.EMotionApplyMode_ReferenceToCoordinate)
    body_device.SetBodySetting(mocap_avatar, body_setting)

    device_setting = body_device.GetDeviceSetting()
    device_setting.SetMocapCoordinate(RLPy.ECoordinateAxis_Y, RLPy.ECoordinateAxis_Z, RLPy.ECoordinateSystem_RightHand)
    device_setting.SetCoordinateOffset(0, [0, 0, 0])

    position_setting = device_setting.GetPositionSetting()
    rotation_setting = device_setting.GetRotationSetting()
    rotation_setting.SetType(RLPy.ERotationType_Euler)
    rotation_setting.SetUnit(RLPy.ERotationUnit_Degrees)
    rotation_setting.SetEulerOrder(RLPy.EEulerOrder_ZXY)
    rotation_setting.SetCoordinateSpace(RLPy.ECoordinateSpace_Local)
    position_setting.SetUnit(RLPy.EPositionUnit_Centimeters)
    position_setting.SetCoordinateSpace(RLPy.ECoordinateSpace_Local)

    body_device.Initialize(bone_list)
    body_device.SetTPoseData(mocap_avatar, t_pose_data)



def create_dialog():
    # initialize dialog
    main_widget = wrapInstance(int(RLPy.RUi.GetMainWindow()), PySide2.QtWidgets.QWidget)    
    dlg = PySide2.QtWidgets.QDialog(main_widget)    # set parent to main window
    
    ui_file = QFile(os.path.dirname(__file__) + "/BodyMocap.ui")
    ui_file.open(QFile.ReadOnly)
    ui_widget = PySide2.QtUiTools.QUiLoader().load(ui_file) # load .ui file
    ui_file.close()
    ui_layout = PySide2.QtWidgets.QVBoxLayout()
    ui_layout.setContentsMargins( 0, 0, 0, 0 )
    ui_layout.addWidget(ui_widget)
    dlg.setLayout(ui_layout)
    dlg.setWindowTitle("Body Mocap Sample")
    dlg.resize(ui_widget.size().width(), ui_widget.size().height())
    dlg.setMinimumSize(ui_widget.size())
    dlg.setMaximumSize(ui_widget.size())

    # connect button signals
    ui_connect_btn = ui_widget.findChild(PySide2.QtWidgets.QPushButton, "qtConnectBtn")
    if ui_connect_btn:
        ui_connect_btn.clicked.connect(do_connect)
    ui_start_btn = ui_widget.findChild(PySide2.QtWidgets.QPushButton, "qtStartBtn")
    if ui_start_btn:
        ui_start_btn.clicked.connect(trigger_mocap)
    return dlg
        
def do_connect():
    global mocap_dlg
    global tcp_client
    global network_callback

    if tcp_client.IsConnected():
        tcp_client.Disconnect()
        show_log("Disconnect to server")
    else:
        ui_server_edit = mocap_dlg.findChild(PySide2.QtWidgets.QLineEdit, "qtServerEdit")
        if ui_server_edit == None:
            return

        # Tcp Network
        tcp_client.SetMaximumDataCount(100)
        if network_callback == None:
            network_callback = NetworkEventCallback()
            tcp_client.RegisterCallback(network_callback) # register network event callback

        ip_port = ui_server_edit.text().split(":")
        print(ip_port)
        if len(ip_port) != 2:
            return
        tcp_client.Connect(ip_port[0], int(ip_port[1])) # connect to server
        show_log("Connect to Server:"+ip_port[0]+" port:"+ip_port[1])
    
def trigger_mocap():
    global mocap_manager
    global do_mocap
    global mocap_dlg

    ui_start_btn = mocap_dlg.findChild(PySide2.QtWidgets.QPushButton, "qtStartBtn")
    ui_preview_btn = mocap_dlg.findChild(PySide2.QtWidgets.QRadioButton, "qtPreviewRdo")    
    preview_mode = False
    if ui_preview_btn:
        preview_mode = ui_preview_btn.isChecked()
    if not do_mocap:
        do_mocap = True
        if preview_mode:
            show_log("Start mocaping(Preview)...")        
            mocap_manager.Start(RLPy.EMocapState_Preview)
        else:
            show_log("Start mocaping(Record)...")        
            mocap_manager.Start(RLPy.EMocapState_Record)
        if ui_start_btn:
            ui_start_btn.setText("Cancel")
    else:
        do_mocap = False        
        mocap_manager.Stop()    
        show_log("End mocaping...")        
        if ui_start_btn:
            ui_start_btn.setText("Start")

def show_log(message):
    ui_log_edit = mocap_dlg.findChild(PySide2.QtWidgets.QTextEdit, "qtLogText")
    if ui_log_edit == None:
        return
    ui_log_edit.append(message)


# iClone python entry
def run_script():           # Menu > Script > Load Python
    initialize_plugin()

def initialize_plugin():    # put into ICPath\Bin64\OpenPlugin
    # Add menu
    ic_dlg = wrapInstance(int(RLPy.RUi.GetMainWindow()), PySide2.QtWidgets.QMainWindow)
    plugin_menu = ic_dlg.menuBar().findChild(PySide2.QtWidgets.QMenu, "pysample_menu")
    if (plugin_menu == None):
        plugin_menu = wrapInstance(int(RLPy.RUi.AddMenu("Python Samples", RLPy.EMenu_Plugins)), PySide2.QtWidgets.QMenu)
        plugin_menu.setObjectName("pysample_menu")

    body_mocap_action = plugin_menu.addAction("Body Mocap Sample")
    body_mocap_action.setObjectName("body_mocap_action")
    body_mocap_action.triggered.connect(show_dialog)
