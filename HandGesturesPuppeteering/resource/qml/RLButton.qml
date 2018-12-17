import QtQuick 2.5
import QtQuick.Controls 1.5
import QtQuick.Layouts 1.3
import QtQuick.Controls.Styles 1.4
import QtQml 2.2


Button {
    property int borderRadius:0
    property string fontSize: "middleWord"

    style: middleStyle
    Component{
        id: middleStyle
        ButtonStyle {

            background: Rectangle {
                implicitHeight: 25
                border.width: 1
                border.color: control.enabled ? control.checked ? "#505050" : control.pressed ? "#505050" : control.hovered ? "#505050" : "#505050" : "#464646"
                color: control.enabled ? control.checked ? "#c8c8c8" : control.pressed ? "#c8c8c8" : control.hovered ? "#505050" : "transparent" : "transparent"
                radius: borderRadius

            }

            label: Text {
                font.family: "Arial"
                font.pixelSize: 12
                font.bold: false
                color: control.enabled ? control.checked ? "#000000" : control.pressed ? "#000000" : control.hovered ? "#c8c8c8" : "#c8c8c8" : "#464646"
                text: control.text
                anchors.centerIn: parent
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                renderType: Text.NativeRendering
            }
        }
    }

}
