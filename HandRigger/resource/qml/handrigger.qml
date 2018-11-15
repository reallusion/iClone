import QtQuick 2.5
import QtQuick.Controls 1.5
import QtQuick.Layouts 1.3
import QtQuick.Controls.Styles 1.4

Item {
    id: item
    property var keys: []
    property var squareDist: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  //square distance from key to mouse
    property var center: Qt.point(width/2, height/2)
    property var radius: 185                                      // radius of background circle
    property var keyRadius: 6
    property var mousePos: Qt.point(0, 0)
    property var handRiggerState: 0                               // Disable = 0, Ready = 1, Running = 2
    property var strDisable: qsTr("<< Select an avater >>")
    property var strReady: qsTr("<< Press space to Start/Stop >>")

    property var backgroundColor: Qt.hsla(0.28, 0.9, 0.8, 0.25)   // Qt.hsla: hue, saturation, lightness, alpha
                                                                  // another way to set color: Qt.rgba(1.0, 1.0, 1.0, 1.0)

    property var backgroundColor2: Qt.hsla(0.28, 0.0, 0.8, 0.25)  // *Color2: color when handrigger is disabled
    property var keyFillColor: Qt.hsla(0.055, 0.97, 0.6, 1.0)
    property var keyFillColor2: Qt.hsla(0.055, 0.0, 0.6, 1.0)
    property var keyStrokeColor: Qt.hsla(0.055, 0.8, 0.4, 1.0)
    property var keyStrokeColor2: Qt.hsla(0.055, 0.0, 0.4, 1.0)
    property var lineColor: Qt.hsla(0.0, 0.0, 0.5, 0.9)

    width: 400
    height: 400
    enabled: true

    Rectangle {
        id: rect
        color: "#101010"
        anchors.fill: parent
        border.width: 0

        Canvas {
            id: canvas
            anchors.fill: parent

            onPaint: {
                var ctx = getContext("2d")
                // clear
                ctx.reset()

                // draw background circle
                ctx.fillStyle = handRiggerState ? backgroundColor : backgroundColor2
                ctx.ellipse(center.x-radius, center.y-radius, 2*radius, 2*radius)
                ctx.fill()

                // draw 7 keys
                ctx.lineWidth = 1
                ctx.strokeStyle = handRiggerState ? keyStrokeColor : keyStrokeColor2
                ctx.fillStyle = handRiggerState ? keyFillColor : keyFillColor2
                for (var i=0; i<keys.length; ++i) {
                    ctx.beginPath()
                    ctx.ellipse(keys[i].x-keyRadius, keys[i].y-keyRadius, 2*keyRadius, 2*keyRadius)
                    ctx.fill()
                    ctx.stroke()
                }

                if (handRiggerState == 2) {
                    // draw lines
                    ctx.strokeStyle = lineColor
                    for (var i=0; i<keys.length; ++i) {
                        ctx.beginPath()
                        ctx.moveTo(mousePos.x, mousePos.y)
                        ctx.lineTo(keys[i].x, keys[i].y)
                        ctx.stroke()
                    }
                }
            }

            MouseArea {
                id: ma
                hoverEnabled: true
                opacity: 0
                anchors.fill: parent

                onPositionChanged:
                {
                    if (handRiggerState == 2) {
                        mousePos.x = mouse.x
                        mousePos.y = mouse.y
                        label.text = "(" + mouse.x.toString() + ", " + mouse.y.toString() + ")"
                        for (var i=0; i<keys.length; ++i) {
                            var x_dist = keys[i].x - mouse.x
                            var y_dist = keys[i].y - mouse.y
                            squareDist[i] = x_dist * x_dist + y_dist * y_dist
                        }
                        handRigger.process_data(squareDist)
                    }
                    canvas.requestPaint()
                }
            }
        }

        Label {
            id: label
            x: 162
            y: 240
            width: 200
            height: 25
            color: "#cccccc"
            text: qsTr("<< Press space to Start/Stop >>")
            visible: true
            font.pointSize: 12
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignHCenter
            anchors.horizontalCenter: parent.horizontalCenter
            //anchors.verticalCenter: parent.verticalCenter
        }
    }
    Component.onCompleted: {
        keys.push(center)
        for ( var i=0; i<6; ++i ) {
            var key = Qt.point(0,0)
            key.x = center.x + radius * Math.cos( (90 + i*60) * Math.PI / 180)
            key.y = center.y + radius * Math.sin( (90 + i*60) * Math.PI / 180)
            keys.push(key)
        }
    }

    function setHandRiggerState( state )
    {
        handRiggerState = state
        switch (handRiggerState) {
            case 0:
                label.text = strDisable
                break
            case 1:
                label.text = strReady
                break
            case 2:
                label.text = qsTr("Running")
                break
        }
        item.enabled = state > 0
        canvas.requestPaint()
    }
}
