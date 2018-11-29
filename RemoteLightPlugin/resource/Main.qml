import QtQuick 2.5
import QtQuick.Controls 1.5
import QtQuick.Layouts 1.3
import QtQuick.Controls.Styles 1.4
import QtQml 2.2

Rectangle{
    id: remoteLightRect
    width: 350
    height: 780
    visible: true
    color: "#282828"
    border.width: 1
    border.color: "#505050"

    property var isConnected : false
    property var currentIp : "192.168.1.3"


    Image {
        id: status
        x: 15
        y: 43
        width: 15
        height: 15
        fillMode: Image.Stretch
        source: isConnected ? "Light_On.svg" : "Light.svg"
    }

    Label {
        id: ipLabel
        x: 49
        y: 39
        font.pixelSize: 20
        font.family: "Arial"
        color: "#c8c8c8"
        text: qsTr("Your IP address:")
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }

    Text {
        id: ipAddress
        x: 204
        y: 41
        width: 138
        height: 19
        color: "#c8c8c8"
        text: currentIp
        font.family: "Times New Roman"
        font.italic: false
        font.bold: false
        horizontalAlignment: Text.AlignLeft
        font.pixelSize: 20
    }

    function setIpAddress(ip){
        currentIp = ip
    }

    function updateConnectStatus(status) {
        isConnected = status
    }
}
