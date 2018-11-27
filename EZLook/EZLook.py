import os
import sys
import RLPy
import PySide2
from PySide2.QtWidgets import QWidget
from PySide2.shiboken2 import wrapInstance

import EZLookManager


open_ui_kit = RLPy.RUi
plugin_menu = None

def run_script():
    menu_example()

def menu_example():
    global open_ui_kit
    global plugin_menu
    #AllMenu
    plugin_menu = open_ui_kit.AddMenu("New", RLPy.EMenu_Plugins)
    QQ = wrapInstance(int(plugin_menu), PySide2.QtWidgets.QMenu)
    #Menu1
    plugin_action = QQ.addAction("EZLook")
    plugin_action.triggered.connect(easyLook_click)
    #Menu2
    plugin_action2 = QQ.addAction("Close")
    plugin_action2.triggered.connect(close_click)

def easyLook_click():
    #open_viwer
    EZLookManager.open_Viwer()

def close_click():
    global plugin_menu
    open_ui_kit.RemoveMenu(plugin_menu)


