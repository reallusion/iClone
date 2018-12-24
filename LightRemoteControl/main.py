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

import sys
import os
import socket
import RLPy
import PySide2
from PySide2.QtCore import *
from PySide2.QtCore import QResource
from PySide2.QtGui import *
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QWidget
from PySide2.shiboken2 import wrapInstance
from PySide2.QtNetwork import QTcpServer
from PySide2.QtNetwork import QTcpSocket
from os import listdir
from os.path import isfile, join

sys.dont_write_bytecode = True
#exe_parent_path = os.path.abspath(os.path.join(sys.executable, os.pardir))
res_path = os.path.dirname(__file__)+ "/resource/"

main_dlg = None
main_qml = None
main_pyside_dlg = None

tcp_server = None
client = None

directional_lights = []
point_lights = []
spot_lights = []

def initialize_plugin():
    global main_dlg
    global main_qml
    global main_pyside_dlg
    global res_path
    global tcp_server
    # Prepare main dialog
    main_dlg = RLPy.RUi.CreateRDialog()
    main_dlg.SetWindowTitle("Light Remote Control")
    
    # Create a Pyside2 Quickwidget and get root object from qml
    main_dlg_view = PySide2.QtQuickWidgets.QQuickWidget()
    main_dlg_view.setSource(QUrl.fromLocalFile(res_path+"Main.qml"))
    main_dlg_view.setResizeMode(PySide2.QtQuickWidgets.QQuickWidget.SizeRootObjectToView)
    main_qml = main_dlg_view.rootObject()
    
    # wrapInstance
    main_pyside_dlg = wrapInstance(int(main_dlg.GetWindow()), PySide2.QtWidgets.QDialog)
    main_pyside_dlg.setObjectName("Remote Light Plugin")
    
    # add widget to layout 
    main_layout = main_pyside_dlg.layout()
    main_layout.addWidget(main_dlg_view)
    main_pyside_dlg.adjustSize()

    # prepare menu and connect action
    ic_dlg = wrapInstance(int(RLPy.RUi.GetMainWindow()), PySide2.QtWidgets.QMainWindow)
    plugin_menu = ic_dlg.menuBar().findChild(PySide2.QtWidgets.QMenu, "pysample_menu")
    if (plugin_menu == None):
        plugin_menu = wrapInstance(int(RLPy.RUi.AddMenu("Python Samples", RLPy.EMenu_Plugins)), PySide2.QtWidgets.QMenu)
        plugin_menu.setObjectName("pysample_menu")
        
    plugin_action = plugin_menu.addAction("Light Remote Control")
    plugin_action.setIcon((QIcon(res_path+"icon.svg")))
    plugin_action.triggered.connect(show_main_dlg)
    
    main_qml.setIpAddress(socket.gethostbyname(socket.gethostname()))

    tcp_server = QTcpServer()
    tcp_server.listen( PySide2.QtNetwork.QHostAddress.Any, 7701 )
    tcp_server.newConnection.connect( add_new_device )

def uninitialize_plugin():
    global tcp_server
    if tcp_server.isListening():
        tcp_server.close()
    if client != None:
        client.close()

def show_main_dlg():
    global main_dlg
    global main_qml
    main_qml.setIpAddress(socket.gethostbyname(socket.gethostname()))
    main_dlg.Show()

def add_new_device():
    global client
    client = tcp_server.nextPendingConnection()
    client.readyRead.connect( on_data_ready )
    main_qml.updateConnectStatus(True)

def on_data_ready():
    global client
    if client != None:
        data = client.readAll()
        if data != None:
            update_light_list()
        control_light(data.data().decode('utf8'))

def control_light(all_command):
    global directional_lights
    global point_lights
    global spot_lights
    if all_command == "" or ( directional_lights == [] and point_lights == [] and spot_lights == [] ):
        return
    command_list = all_command.split(",")
    target_lights = []
    for command in command_list:
        command_pair = command.split(":")
        if len(command_pair) != 2:
            continue
        if command_pair[0] == "Type":
            if command_pair[1] == "Directional":
                target_lights = directional_lights
            elif command_pair[1] == "Point":
                target_lights = point_lights
            elif command_pair[1] == "Spot":
                target_lights = spot_lights
            else:
                pass
        elif command_pair[0] == "Power":
            active = str_to_bool(command_pair[1])
            for light in target_lights:
                light.SetActive(active)
        elif command_pair[0] == "Intensity":
            intensity = float(command_pair[1])
            for light in target_lights:
                light.SetMultiplier(RLPy.RGlobal.GetTime(), intensity)

def update_light_list():
    global directional_lights
    global point_lights
    global spot_lights
    directional_lights = []
    point_lights = []
    spot_lights = []
    
    all_lights = RLPy.RScene.FindObjects(RLPy.EObjectType_Light)
    for light in all_lights:
        if light.GetType() == RLPy.EObjectType_SpotLight:
            spot_lights.append(light)
        elif light.GetType() == RLPy.EObjectType_PointLight:
            point_lights.append(light)
        elif light.GetType() == RLPy.EObjectType_DirectionalLight:
            directional_lights.append(light)

def str_to_bool(s):
    if s == "True":
         return True
    else:
         return False

def run_script():
    initialize_plugin()
