import QtQuick 2.5
import QtQuick.Controls 1.5
import QtQuick.Layouts 1.3
import QtQuick.Controls.Styles 1.4
import QtQml 2.2

Rectangle{
    id: simpleLayerManagerDialog
    width: 250
    height: 150
    visible: true
    color: "#282828"
    border.width: 1
    border.color: "#505050"

    property var selectAllBtnActive: false
    property var selectAvatarsBtnActive: false
    property var selectPropsBtnActive: false

    property var visibleChkEnabledStatus: false
    property var visibleChkCheckedStatus: True

    property var checkedDefault: "qrc:///slmlite/icon/CheckOn_sel.svg"
    property var checkedHover: "qrc:///slmlite/icon/CheckOn_hov.svg"
    property var checkedDisable: "qrc:///slmlite/icon/CheckOn_dis.svg"
    property var uncheckedDefault: "qrc:///slmlite/icon/CheckOff.svg"
    property var uncheckedHover: "qrc:///slmlite/icon/CheckOff_hov.svg"
    property var uncheckedDisable: "qrc:///slmlite/icon/CheckOff_dis.svg"

    ColumnLayout {
            id: mainLayout
            spacing: 10
            width: parent.width
            height: parent.height
            RowLayout {
                id: selectDescriptionLayout
                width: parent.width
                height: 20
                spacing: 10
                Layout.alignment: Qt.AlignLeft
                Label {
                    id: selectLabel
                    font.pixelSize: 20
                    font.family: "Arial"
                    color: "#c8c8c8"
                    text: qsTr("Choose Object Type what you want:")
                    verticalAlignment: Text.AlignBottom
                }
            }

            RowLayout {
                id: selectChoosenLayout
                width: parent.width
                Layout.alignment: Qt.AlignCenter
                Button {
                    id: selectAllButton
                    text: qsTr("All")
                    enabled: true
                    style: ButtonStyle {
                        background: Rectangle {
                            implicitHeight: 25
                            border.width: 1
                            border.color: control.enabled ? control.pressed ? "#505050" : selectAllBtnActive ? "#82be0f" : control.hovered ? "#505050" : "#505050" : "#464646"
                            color: control.enabled ? control.checked ? "#c8c8c8" : control.pressed ? "#c8c8c8" : control.hovered ? "#505050" : "transparent" : "transparent"
                        }

                        label: Text {
                            font.family: "Arial"
                            font.pixelSize: 25
                            font.bold: true
                            color: control.enabled ? control.pressed ? "#000000" : selectAllBtnActive ? "#82be0f" : control.hovered ? "#c8c8c8" : "#c8c8c8" : "#464646"
                            text: control.text
                            anchors.centerIn: parent
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                            renderType: Text.NativeRendering
                        }
                    }
                    onClicked: {
                        if (!selectAllBtnActive) {
                            selectAllBtnActive = true;
                            selectAvatarsBtnActive = true;
                            selectPropsBtnActive = true;
                        }
                        else {
                            selectAllBtnActive = false;
                            selectAvatarsBtnActive = false;
                            selectPropsBtnActive = false;
                        }
                        smlLiteModule.get_all_objects(selectAllBtnActive);
                    }
                }
                Button {
                    id: selectAvatarButton
                    text: qsTr("Avatar")
                    enabled: true
                    style: ButtonStyle {
                        background: Rectangle {
                            implicitHeight: 25
                            border.width: 1
                            border.color: control.enabled ? control.pressed ? "#505050" : selectAvatarsBtnActive ? "#82be0f" : control.hovered ? "#505050" : "#505050" : "#464646"
                            color: control.enabled ? control.checked ? "#c8c8c8" : control.pressed ? "#c8c8c8" : control.hovered ? "#505050" : "transparent" : "transparent"
                        }

                        label: Text {
                            font.family: "Arial"
                            font.pixelSize: 25
                            font.bold: true
                            color: control.enabled ? control.pressed ? "#000000" : selectAvatarsBtnActive ? "#82be0f" : control.hovered ? "#c8c8c8" : "#c8c8c8" : "#464646"
                            text: control.text
                            anchors.centerIn: parent
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                            renderType: Text.NativeRendering
                        }
                    }
                    onClicked: {
                        if (!selectAllBtnActive) {
                            selectAvatarsBtnActive = !selectAvatarsBtnActive;
                        }
                        else {
                            selectAllBtnActive = false;
                            selectPropsBtnActive = false;
                        }
                        smlLiteModule.get_avatars(selectAvatarsBtnActive);
                    }
                }
                Button {
                    id: selectPropButton
                    text: qsTr("Prop")
                    enabled: true
                    style:ButtonStyle {
                        background: Rectangle {
                            implicitHeight: 25
                            border.width: 1
                            border.color: control.enabled ? control.pressed ? "#505050" : selectPropsBtnActive ? "#82be0f" : control.hovered ? "#505050" : "#505050" : "#464646"
                            color: control.enabled ? control.checked ? "#c8c8c8" : control.pressed ? "#c8c8c8" : control.hovered ? "#505050" : "transparent" : "transparent"
                        }

                        label: Text {
                            font.family: "Arial"
                            font.pixelSize: 25
                            font.bold: true
                            color: control.enabled ? control.pressed ? "#000000" : selectPropsBtnActive ? "#82be0f" : control.hovered ? "#c8c8c8" : "#c8c8c8" : "#464646"
                            text: control.text
                            anchors.centerIn: parent
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                            renderType: Text.NativeRendering
                        }
                    }
                    onClicked: {
                        if (!selectAllBtnActive) {
                            selectPropsBtnActive = !selectPropsBtnActive;
                        }
                        else {
                            selectAllBtnActive = false;
                            selectAvatarsBtnActive = false;
                        }
                        smlLiteModule.get_props(selectPropsBtnActive);
                    }
                }
            }

            RowLayout {
                id: visibleLayout
                width: parent.width
                Layout.alignment: Qt.AlignCenter
                CheckBox {
                    id: visibleCheckBox
                    height: 20
                    implicitWidth: 20
                    style: customCheckBoxStyle
                    text: qsTr("Visible")
                    enabled: visibleChkEnabledStatus
                    checked: visibleChkCheckedStatus
                    onCheckedChanged: {
                        smlLiteModule.set_visible(checked);
                        console.log("[QML] visibleCheckBox onCheckedChanged");
                    }
                    Component.onCompleted:{
                        console.log("[QML] visibleCheckBox Component onCompleted.");
                    }
                    Component {
                        id: customCheckBoxStyle
                        CheckBoxStyle {
                            indicator: Image {
                                sourceSize.width: 18
                                sourceSize.height: 18
                                source: control.checked ? control.enabled ? control.hovered ? checkedHover :  checkedDefault : checkedDisable :
                                        control.enabled ? control.hovered ? uncheckedHover : uncheckedDefault : uncheckedDisable
                            }

                            label: Text {
                                id: text
                                text: control.text
                                color: control.enabled ? "#c8c8c8" : "#464646"
                                font.family: "Arial"
                                font.pixelSize: 20
                                font.bold : false
                                wrapMode: Text.Wrap
                            }
                            spacing: 6
                        }
                    }
                }
            }
            Item { Layout.fillHeight: true }
    }

    function updateVisibleChkStatus(chkStatus) {
        visibleChkEnabledStatus = chkStatus;
        visibleChkCheckedStatus = chkStatus;
        console.log("[QML] visibleCheckBox enabled status: " + visibleCheckBox.enabled);
        console.log("[QML] visibleCheckBox checked status: " + visibleCheckBox.checked);
    }
}
