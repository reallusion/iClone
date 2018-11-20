import QtQuick 2.5
import QtQuick.Controls 1.5
import QtQuick.Layouts 1.3
import QtQuick.Controls.Styles 1.4
import QtQml 2.2

Rectangle{
    id: cameraDialog
    width: 150
    height: 200
    visible: true
    color: "#282828"
    border.width: 1
    border.color: "#505050"
    ColumnLayout {
        spacing: 10
        width: parent.width
        height: parent.height
        Button {
            id: forward
            text: qsTr("Go")
            Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
            onClicked:
            {
                cameraModule.camera_forward();
            }
        }

        Button {
            id: back
            text: qsTr("back")
            Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
            onClicked:
            {
                cameraModule.camera_back();
            }
        }
    }
}
