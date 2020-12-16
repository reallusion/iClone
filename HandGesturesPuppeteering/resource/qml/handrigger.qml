import QtQuick 2.5
//import QtQuick 2.15
import QtQuick.Controls 1.5
import QtQuick.Layouts 1.3
import QtQuick.Controls.Styles 1.4

Item {
    id: control
    property var keys: []
    property var squareDist: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  // square distance from mouse to key
    property var weights: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]     // weight return from Python
    property var center: Qt.point(rectbackground.width/2,rectbackground.height/2)
    property var radius: 135                                      // radius of background circle
    property var keyRadius: 6
    property var mousePos: Qt.point(0, 0)
    property var handRiggerState: 0                               // Disable = 0, Ready = 1, ReadToRun = 2, Preview = 3, Record = 4
    
    property var backgroundColor: Qt.hsla(0.28, 0.9, 0.8, 0.25)   // Qt.hsla: hue, saturation, lightness, alpha
    
    property var backgroundDisabledColor: Qt.hsla(0.28, 0.0, 0.8, 0.25)
    property var keyDisabledFillColor: Qt.hsla(0.055, 0.0, 0.6, 1.0)
    property var keyDisabledStrokeColor: Qt.hsla(0.055, 0.0, 0.4, 1.0)
    property var lineColor: Qt.hsla(0.0, 0.0,0.5, 0.9)

    property int gesturex:121
    property int gesturey:42
    property int gesturev:52
    property int gesturey2:37

    property int blendMode: 1
    property int joinMode: 0
    property bool isInitialized: false

    width: 400
    height: 485
    enabled: true

    Rectangle {
        id: container
        height: 485
        color: "#282828"
        anchors.rightMargin: 0
        anchors.leftMargin: 0
        anchors.topMargin: 0
        anchors.bottomMargin: -6
        anchors.fill: parent
        border.width: 0

        Rectangle {
            id: rectbackground
            x: 13
            y: 10
            color: "transparent"
            border.width: 1
            border.color:"#505050"
            Layout.fillWidth: true
            Layout.fillHeight:  true
            width: 374
            height: 312
            Image {
                height: parent.height-36
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter
                source: "images/Circle_bg.png"
            }
            Canvas {
                id: canvas
                anchors.rightMargin: 0
                anchors.bottomMargin: 2
                anchors.leftMargin: 0
                anchors.topMargin: -2
                anchors.fill: parent

                onPaint: {
                    var ctx = getContext("2d")
                    ctx.reset()

                    if (handRiggerState >= 3) {
                        // draw lines
                        ctx.strokeStyle = lineColor
                        for (var i=0; i<keys.length; ++i) {
                            if (weights[i] === 0.0) {
                                continue
                            }
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
                    cursorShape:(handRiggerState >=2)? Qt.BlankCursor:Qt.ArrowCursor

                    onPositionChanged:
                    {
                        mousePos.x = mouse.x
                        mousePos.y = mouse.y

                        if (handRiggerState >= 2)
                        {
                            cursor.x = mouse.x-10
                            cursor.y = mouse.y-10
                        }
                        else
                        {
                            cursor.x = center.x - 10
                            cursor.y = center.y - 10
                        }

                        for (var i=0; i<keys.length; ++i) {
                            var x_dist = keys[i].x - mouse.x
                            var y_dist = keys[i].y - mouse.y
                            squareDist[i] = x_dist * x_dist + y_dist * y_dist
                        }
                        weights = handRigger.calculate_weights(squareDist)
                        canvas.requestPaint()
                    }
                }
            }

            RLKey {
                id: hand00
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter
                source_image: "images/hand00.png"
                scaleFunction: (function(){ return (handRiggerState > 1) ? lerp(50, 64, weights[0]) : 55})
                clickFunction: (function(){ handRigger.replace_gesture(0) })
            }

            RLKey{
                id: hand01
                x: parent.width-gesturev
                anchors.verticalCenter: parent.verticalCenter
                source_image: "images/hand01.png"
                scaleFunction: (function(){ return (handRiggerState > 1) ? lerp(50, 64, weights[1]) : 55 })
                clickFunction: (function(){ handRigger.replace_gesture(1) })
            }

            RLKey{
                id: hand02
                x:parent.width-hand03.x
                y:parent.height - gesturey2
                source_image: "images/hand02.png"
                scaleFunction: (function(){ return (handRiggerState > 1) ? lerp(50, 64, weights[2]) : 55 })
                clickFunction: (function(){ handRigger.replace_gesture(2) })
            }

            RLKey{
                id: hand03
                x:hand05.x
                y:parent.height-gesturey2
                source_image: "images/hand03.png"
                scaleFunction: (function(){ return (handRiggerState > 1) ? lerp(50, 64, weights[3]) : 55 })
                clickFunction: (function(){ handRigger.replace_gesture(3) })
            }

            RLKey{
                id: hand04
                x:parent.width-hand01.x
                anchors.verticalCenter: parent.verticalCenter
                source_image: "images/hand04.png"
                scaleFunction: (function(){ return (handRiggerState > 1) ? lerp(50, 64, weights[4]) : 55 })
                clickFunction: (function(){ handRigger.replace_gesture(4) })
            }

            RLKey{
                id: hand05
                x:gesturex
                y:gesturey
                source_image: "images/hand05.png"
                scaleFunction: (function(){ return (handRiggerState > 1) ? lerp(50, 64, weights[5]) : 55 })
                clickFunction: (function(){ handRigger.replace_gesture(5) })
            }

            RLKey{
                id:hand06
                x: parent.width-gesturex
                y: hand05.y
                source_image: "images/hand06.png"
                scaleFunction: (function(){ return (handRiggerState > 1) ? lerp(50, 64, weights[6]) : 55 })
                clickFunction: (function(){ handRigger.replace_gesture(6) })
            }

            Rectangle{
                id:cursor
                Image {
                    source: (handRiggerState == 0) ? "images/dot_dis.png" : "images/dot_Default.png"
                }
            }
        }

        RowLayout {
            id: rowLayout
            y: 336
            anchors.right: parent.right
            anchors.rightMargin: 40
            anchors.left: parent.left
            anchors.leftMargin: 40

            ColumnLayout {
                id: columnLayout
                height: 63
                Layout.fillWidth: false

                Text {
                    id: element
                    width: 100
                    color: "#ffffff"
                    text: qsTr("Hand:")
                    font.family: "Arial"
                    Layout.minimumWidth: 100
                    verticalAlignment: Text.AlignVCenter
                    Layout.fillHeight: true
                    Layout.fillWidth: false
                    font.pixelSize: 12
                }

                Text {
                    id: element1
                    width: 100
                    color: "#ffffff"
                    text: qsTr("Blend Mode:")
                    font.family: "Arial"
                    Layout.minimumWidth: 100
                    verticalAlignment: Text.AlignVCenter
                    Layout.fillHeight: true
                    Layout.fillWidth: false
                    font.pixelSize: 12
                }
            }

            ColumnLayout {
                id: columnLayout1
                Layout.fillWidth: false

                ComboBox {
                    id: handJoinCombo
                    width: 250
                    height: 32
                    Layout.maximumWidth: 204
                    Layout.minimumWidth: 200
                    Layout.fillHeight: false
                    Layout.fillWidth: true
                    activeFocusOnPress: false
                    editable: false
                    implicitWidth: (parent.width-15)/3
                    model: ListModel {
                        id: handJoinModeItems
                        ListElement { text: "Both Hands"; join_mode: 0;}
                        ListElement { text: "Right Hand Only"; join_mode:1;}
                        ListElement { text: "Left Hand Only"; join_mode:2;}
                    }
                    onCurrentIndexChanged: {
                        if(isInitialized){
                            joinMode = handJoinModeItems.get(currentIndex).join_mode
                            handRigger.set_join_mode(joinMode)
                        }
                    }
                    Component.onCompleted: {
                        isInitialized = true;
                    }
                }

                RowLayout {
                    id: rowLayout1
                    Layout.fillHeight: true

                    RLButton{
                        id:multisideModeButton
                        width: (parent.width-15)/2
                        text:qsTr("Multi-Point")
                        Layout.minimumWidth: 100
                        Layout.fillHeight: true
                        checked:true
                        onClicked:{
                            twosideModeButton.checked=false
                            multisideModeButton.checked=true
                            blendMode = 0
                            handRigger.set_blend_mode(blendMode)
                        }
                    }

                    RLButton{
                        id:twosideModeButton
                        width: (parent.width-15)/2
                        text:qsTr("2-Point")
                        Layout.minimumWidth: 100
                        Layout.fillHeight: true
                        Layout.fillWidth: false
                        checked:false
                        onClicked:{
                            multisideModeButton.checked=false
                            twosideModeButton.checked=true
                            blendMode = 1
                            handRigger.set_blend_mode(blendMode)
                        }
                    }

                }
            }
        }

        Rectangle {
            id: record
            x: 202
            y: 427
            width: 150
            height: 50
            color: "#282828"
            Layout.fillHeight: true
            Layout.minimumHeight: 25
            Layout.minimumWidth: 100
            Layout.fillWidth: true
            radius: 8
            border.width: 1
            border.color:"#505050"

            MouseArea{
                anchors.fill: parent
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter
                hoverEnabled: true
                onEntered: parent.color = "#505050"
                onExited: {
                    parent.color = "#282828"
                    canvas.requestPaint()
                }
                onClicked: {
                    handRigger.record_mode()
                    handRiggerState = 2  //ready to run
                    showPreviewRecord(false, "Press Spacebar to Record")
                }
            }

            Image {
                id: record_icon
                x: 28
                y: 9
                width: 32
                height: 32
                sourceSize.height: 32
                sourceSize.width: 32
                fillMode: Image.PreserveAspectFit
                source: "images/Record.png"
                opacity: parent.enabled ? 1 : 0.25
            }

            Text {
                id: record_lable
                x: 71
                y: 16
                color: parent.enabled ? "#ffffff" : "#505050"
                text: qsTr("Record")
                font.family: "Arial"
                font.pixelSize: 13
            }
        }

        Rectangle {
            id: preview
            x: 40
            y: 426
            width: 150
            height: 50
            color: "#282828"
            Layout.minimumHeight: 25
            Layout.minimumWidth: 100
            Layout.fillWidth: true
            Layout.fillHeight: true
            radius: 8
            border.width: 1
            border.color: "#505050"

            MouseArea{
                anchors.fill: parent
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter
                hoverEnabled: true
                onEntered: parent.color = "#505050"
                onExited: parent.color = "#282828"
                onClicked: {
                    handRigger.preview_mode()
                    handRiggerState = 2  //ready to run
                    showPreviewRecord(false, "Press Spacebar to Preview")
                }
            }

            Image {
                id: preview_icon
                x: 28
                y: 9
                width: 32
                height: 32
                sourceSize.height: 32
                sourceSize.width: 32
                fillMode: Image.PreserveAspectFit
                source: "images/Preview.png"
                opacity: parent.enabled ? 1 : 0.25
            }

            Text {
                id: preview_label
                x: 71
                y: 16
                color: parent.enabled ? "#ffffff" : "#505050"
                text: qsTr("Preview")
                font.family: "Arial"
                font.pixelSize: 13
            }
        }

        Text {
            id: message
            x: 40
            y: 416
            width: 312
            height: 50
            color: "#ffffff"
            text: qsTr("")
            font.family: "Arial"
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignHCenter
            font.pixelSize: 14
        }

        SpinBox {
            id: transition_frames
            x: 306
            y: 394
            width: 46
            height: 20
            activeFocusOnPress: true
            maximumValue: 60
            value: 6
            onValueChanged: {
                handRigger.set_transition_frames(value)
            }
            onEditingFinished:
            {
                focus = false;
                container.focus = true;
            }
            Keys.onReleased: {
                event.accepted
                if ( event.key === Qt.Key_Enter || event.key === Qt.Key_Return || event.key === Qt.Key_Shift ){
                    focus = false;
                    container.focus = true;
                }
            }
        }

        Text {
            id: transition_message
            x: 40
            y: 395
            width: 100
            color: "#ffffff"
            text: qsTr("Blend Out Recording with Original Clip (frames):")
            font.family: "Arial"
            verticalAlignment: Text.AlignVCenter
            Layout.fillWidth: false
            font.pixelSize: 12
            Layout.fillHeight: true
            Layout.minimumWidth: 100
        }

    }

    Button{
        id: save_preset
        x: 356
        y: 16
        width: 24
        height: 24
        iconSource: "images/save_file.png"
        tooltip: qsTr("Save a Preset File...")

        style: ButtonStyle{
            background: Rectangle{
                color: control.hovered ? "black" : "transparent"
                border.width: 1
                border.color: "#505050"
            }
        }
        onClicked: handRigger.save_preset()
    }

    Button{
        id: load_preset
        x: 320
        y: 16
        width: 24
        height: 24
        iconSource: "images/load_file.png"
        tooltip: qsTr("Load a Preset File...")

        style: ButtonStyle{
            background: Rectangle{
                color: control.hovered ? "black" : "transparent"
                border.width: 1
                border.color: "#505050"
            }
        }
        onClicked: handRigger.load_preset()
    }

    Button {
        id: reset_to_default_preset
        x: 23
        y: 19
        width: 24
        height: 24
        iconSource: "images/reset_to_default.png"
        tooltip: "Reset to Default Presets"
        style: ButtonStyle {
            background: Rectangle {
                color: control.hovered ? "black" : "transparent"
                border.width: 1
                border.color: "#505050"
            }
        }
        onClicked: handRigger.reset_to_defaults()
    }


    Component.onCompleted: {
        keys.push(center)
        for ( var i=0; i<6; ++i ) {
            var key = Qt.point(0,0)
            key.x = center.x + radius * Math.cos( ( i*60) * Math.PI / 180)
            key.y = center.y + radius * Math.sin( ( i*60) * Math.PI / 180)
            keys.push(key)
        }
    }

    function resetIcons(){
        hand00.source_image = "images/hand00.png"
        hand01.source_image = "images/hand01.png"
        hand02.source_image = "images/hand02.png"
        hand03.source_image = "images/hand03.png"
        hand04.source_image = "images/hand04.png"
        hand05.source_image = "images/hand05.png"
        hand06.source_image = "images/hand06.png"
    }

    function updateHandRiggerState( state )
    {
        handRiggerState = state

        switch (handRiggerState) {
        case 0: // Disabled
            cursor.x = center.x - 10
            cursor.y = center.y - 10
            break
        case 1: // Ready
            enableControls(true)
            cursor.x = center.x - 10
            cursor.y = center.y - 10
            break
        case 2: //ReadyToRun
            break;
        case 3: // Preview
            break
        case 4: // Record
            break
        }

        container.enabled = state > 0
        canvas.requestPaint()
    }

    function setBlendMode( mode )
    {
        blendMode = mode
        twosideModeButton.checked = (blendMode == 1)
        multisideModeButton.checked = (blendMode == 0)
    }

    function getSmoothBlend(){
        return smoothSpin.value
    }

    function enableControls(enable){
        handJoinCombo.enabled = enable
        twosideModeButton.enabled = enable
        multisideModeButton.enabled = enable
        preview.enabled = enable
        record.enabled = enable
        hand00.enabled = enable
        load_preset.enabled = enable
        save_preset.enabled = enable
        hand00.active = enable
        hand01.active = enable
        hand02.active = enable
        hand03.active = enable
        hand04.active = enable
        hand05.active = enable
        hand06.active = enable
    }

    function showPreviewRecord(visible, text){
        preview.visible = visible
        record.visible = visible
        message.text = qsTr(text)
        transition_frames.enabled = visible
    }

    function changeIcon(index, image){
        image = "file:"+image
        switch(index){
        case 0:
            hand00.source_image = ""
            hand00.source_image = image
            break
        case 1:
            hand01.source_image = ""
            hand01.source_image = image
            break
        case 2:
            hand02.source_image = ""
            hand02.source_image = image
            break
        case 3:
            hand03.source_image = ""
            hand03.source_image = image
            break
        case 4:
            hand04.source_image = ""
            hand04.source_image = image
            break
        case 5:
            hand05.source_image = ""
            hand05.source_image = image
            break
        case 6:
            hand06.source_image = ""
            hand06.source_image = image
            break
        }
    }

    function lerp(v0, v1, t){
        return (1-t) * v0 + t * v1
    }

    function iconLinks(){
        return [
                    hand00.source_image,
                    hand01.source_image,
                    hand02.source_image,
                    hand03.source_image,
                    hand04.source_image,
                    hand05.source_image,
                    hand06.source_image
                ]
    }

    function updateUI(joinValue, blendValue, clipTransitionValue){
        handJoinCombo.currentIndex = joinValue
        twosideModeButton.checked= blendValue === 1
        multisideModeButton.checked= blendValue === 0
        transition_frames.value = clipTransitionValue
    }

}





