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
    #create menu
    plugin_menu = open_ui_kit.AddMenu("New", RLPy.EMenu_Plugins)
    EZLook_menu = wrapInstance(int(plugin_menu), PySide2.QtWidgets.QMenu)
    #create button
    EZLook_action = EZLook_menu.addAction("EZLook")
    EZLook_action.triggered.connect(EZLook_button_click)

def EZLook_button_click():
    #open dialog
    EZLookManager.open_Viwer()

