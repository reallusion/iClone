import os
from os import listdir
from os.path import isfile, join
import sys
import RLPy
import PySide2
from PySide2.QtCore import *
from PySide2.QtCore import QResource
from PySide2.QtCore import QFile
from PySide2.QtCore import QIODevice
from PySide2.QtGui import *
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import *
from PySide2.shiboken2 import wrapInstance

batch_render_dlg = None
render_files = []
def initialize_plugin():
    # Add menu
    plugin_menu = wrapInstance(int(RLPy.RUi.AddMenu("Batch Render", RLPy.EMenu_Plugins)), PySide2.QtWidgets.QMenu)
    plugin_action = plugin_menu.addAction("Batch Render")
    plugin_action.triggered.connect(show_dialog)

def uninitialize_plugin():
    print("uninitialize_plugin")

def show_dialog():
    global batch_render_dlg
    if batch_render_dlg is None:
        main_widget = wrapInstance(int(RLPy.RUi.GetMainWindow()), PySide2.QtWidgets.QWidget)    
        batch_render_dlg = PySide2.QtWidgets.QDialog(main_widget)
        
        ui_file = QFile(os.path.dirname(__file__) + "/BatchRender.ui")
        ui_file.open(QFile.ReadOnly)
        ui_widget = PySide2.QtUiTools.QUiLoader().load(ui_file)
        ui_file.close()
        ui_layout = PySide2.QtWidgets.QVBoxLayout()
        ui_layout.setContentsMargins( 0, 0, 0, 0 )
        ui_layout.addWidget(ui_widget)
        batch_render_dlg.setLayout(ui_layout)
        setup_dialog(batch_render_dlg)
        batch_render_dlg.resize(ui_widget.size().width(), ui_widget.size().height())
        batch_render_dlg.setMinimumSize(ui_widget.size())
        batch_render_dlg.setMaximumSize(ui_widget.size())
        
    if batch_render_dlg.isVisible():
        batch_render_dlg.hide()
    else:
        batch_render_dlg.show()
        
def setup_dialog(ui_widget):
    # connect button signals
    ui_sel_folder_btn = ui_widget.findChild(PySide2.QtWidgets.QPushButton, "qtFolderBtn")
    if ui_sel_folder_btn:
        ui_sel_folder_btn.clicked.connect(do_select_folder)
    ui_render_btn = ui_widget.findChild(PySide2.QtWidgets.QPushButton, "qtRenderButton")
    if ui_render_btn:
        ui_render_btn.clicked.connect(do_batch_render)

def do_select_folder():
    global batch_render_dlg
    global render_files
    render_folder = PySide2.QtWidgets.QFileDialog.getExistingDirectory()
    ui_lineedit = batch_render_dlg.findChild(PySide2.QtWidgets.QLineEdit, "qtFolderEdit")
    if ui_lineedit:
        ui_lineedit.setText(render_folder)
    ui_render_edit = batch_render_dlg.findChild(PySide2.QtWidgets.QTextEdit, "qtRenderText")
    for file in listdir(render_folder):
        if isfile(join(render_folder, file)) and file.lower().endswith(".iproject"):
            render_files.append(render_folder + "/" + file)
    if ui_render_edit:
        ui_render_edit.insertPlainText("Select %d project files\n" % (len(render_files)))
    
def do_batch_render():
    global render_files
    ui_render_edit = batch_render_dlg.findChild(PySide2.QtWidgets.QTextEdit, "qtRenderText")
    for file in render_files:
        if ui_render_edit:
            ui_render_edit.insertPlainText("Loading %s...\n" % (file))
        if RLPy.RFileIO.LoadFile(file):
            if ui_render_edit:
                ui_render_edit.insertPlainText("Rendering %s...\n" % (file))
            RLPy.RGlobal.RenderVideo()
    if ui_render_edit:
        ui_render_edit.insertPlainText("Render completed!")
    
def main():
    initialize_plugin()

# For run script
if __name__ == '__main__':
    main()