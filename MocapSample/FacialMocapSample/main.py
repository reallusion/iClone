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
facial_device = None
do_mocap = False
exp_count = 0

class NetworkEventCallback(RLPy.RTcpCallback):
    def __init__(self):
        RLPy.RTcpCallback.__init__(self)

    def OnStatusChanged(self, is_connected):
        global mocap_dlg
        global tcp_client
        global mocap_avatar

        print(is_connected)
        ui_connect_btn = mocap_dlg.findChild(PySide2.QtWidgets.QPushButton, "qtConnectBtn")
        if ui_connect_btn:
            if is_connected:
                ui_connect_btn.setText("Disconnect")

                exp_names = mocap_avatar.GetFaceComponent().GetExpressionNames("", True)
                exp_names_str = ','.join(exp_names)
                print(exp_names_str)
                exp_names_bi = exp_names_str.encode()
                tcp_client.SendData(bytearray(exp_names_bi),len(exp_names_bi))
            else:
                ui_connect_btn.setText("Connect")                


    def OnFailMessageReceived(self, fail_message):
        print(fail_message)

    def OnDataReceived(self):
        global data
        global tcp_client
        global exp_count
        global do_mocap
        global facial_device

        data = bytearray(tcp_client.GetDataSize(0)) #index 0 => get the first come in data
        tcp_client.GetDataAt(0, data)
        if not do_mocap or facial_device == None or mocap_avatar == None:
            return

        try:
            receive_list = list(data)
            exp_list = [x/100 for x in receive_list]    # convert value range from 0~100 to 0~1
            print(exp_list)
            if isinstance(exp_list, list) and len(exp_list) == exp_count:
                facial_device.ProcessData(mocap_avatar, exp_list)
        except SyntaxError:
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
    global facial_device

    ui_log_edit = mocap_dlg.findChild(PySide2.QtWidgets.QTextEdit, "qtLogText")
    if ui_log_edit:
        ui_log_edit.clear()
    avatar_list = RLPy.RScene.GetAvatars()
    if len( avatar_list ) <= 0:
        show_log("Can't find any avatar, please load a avatar first!")
        return
    mocap_avatar = avatar_list[0]
    face_component = mocap_avatar.GetFaceComponent()

    # display avatar info
    show_log("Avatar: "+mocap_avatar.GetName()+" "+face_component.GetExpressionSetUid())
    exp_names = face_component.GetExpressionNames("", True)
    exp_count = len(exp_names)
    show_log("Expressions("+str(len(exp_names))+"):")
    show_log(str(exp_names))

    # init mocap data
    mocap_manager.RemoveAllDevices()
    facial_device = mocap_manager.AddFacialDevice("FacialDevice")
    facial_setting = RLPy.RFacialSetting()
    facial_setting.SetBlend(False)
    facial_device.AddAvatar(mocap_avatar)
    facial_device.SetFacialSetting(mocap_avatar, facial_setting)    
    facial_device.Initialize()
    facial_device.SetEnable(mocap_avatar, True)

def create_dialog():
    # initialize dialog
    main_widget = wrapInstance(int(RLPy.RUi.GetMainWindow()), PySide2.QtWidgets.QWidget)    
    dlg = PySide2.QtWidgets.QDialog(main_widget)    # set parent to main window
    
    ui_file = QFile(os.path.dirname(__file__) + "/FacialMocap.ui")
    ui_file.open(QFile.ReadOnly)
    ui_widget = PySide2.QtUiTools.QUiLoader().load(ui_file) # load .ui file
    ui_file.close()
    ui_layout = PySide2.QtWidgets.QVBoxLayout()
    ui_layout.setContentsMargins( 0, 0, 0, 0 )
    ui_layout.addWidget(ui_widget)
    dlg.setLayout(ui_layout)
    dlg.setWindowTitle("Facial Mocap Sample")
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

    facail_mocap_action = plugin_menu.addAction("Facial Mocap Sample")
    facail_mocap_action.setObjectName("facial_mocap_action")
    facail_mocap_action.triggered.connect(show_dialog)
