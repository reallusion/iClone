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

