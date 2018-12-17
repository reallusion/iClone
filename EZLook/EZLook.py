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

import os
import sys
import RLPy
import PySide2
from PySide2.QtWidgets import QWidget
from PySide2.shiboken2 import wrapInstance
import EZLookManager

plugin_menu = None

def run_script():
    menu_example()

def menu_example():
    global plugin_menu
    #CreateMenu
    plugin_menu = RLPy.RUi.AddMenu("EZLook", RLPy.EMenu_Plugins)
    EZLook_menu = wrapInstance(int(plugin_menu), PySide2.QtWidgets.QMenu)
    #CreateButton
    EZLook_action = EZLook_menu.addAction("EZLook")
    EZLook_action.triggered.connect(EZLook_button_click)

def EZLook_button_click():
    #OpenDialog
    EZLookManager.open_viewer()

