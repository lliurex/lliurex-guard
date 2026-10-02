import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15


Popup {
    id:popUpWaiting
    width:570
    height:80
    anchors.centerIn: Overlay.overlay
    modal:true
    focus:true
    visible:!mainStackBridge.showPopUp.show
    closePolicy:Popup.NoAutoClose

    background: Rectangle {
        color: palette.window
        border.color: palette.mid
        radius: 4
    }

    ColumnLayout {
        anchors.centerIn: parent
        spacing: 10

        Image{
            id:spinnerImage
            source: "/usr/lib/python3/dist-packages/lliurexguardnatfree/rsrc/loading.png"
            Layout.preferredWidth: 24
            Layout.preferredHeight: 24
            Layout.alignment: Qt.AlignHCenter
            fillMode: Image.PreserveAspectFit
            smooth:false
            antialiasing:false

            rotation:0
        }
            
        Timer{
            id:rotationTimer
            running:(spinnerImage!==null && popUpWaiting!==null) && spinnerImage.visible && popUpWaiting.visible
            repeat:true
            interval:100

            onTriggered:{
                spinnerImage.rotation=(spinnerImage.rotation+330)%360
            }
        }

        Text {
            id: popupText
            text: getTextMessage()
            font.pointSize: 10
            color: palette.windowText
            Layout.alignment: Qt.AlignHCenter
            horizontalAlignment: Text.AlignHCenter
        }
    }

    function getTextMessage(){
        switch (mainStackBridge.showPopUp.msgCode){
            case 7:
                return i18nd("lliurex-guard-natfree","Changing Lliurex Guard mode. Wait a moment...")
            case 11:
                return i18nd("lliurex-guard-natfree","Loading the information from the list. Wait a moment...")
            case 14:
                return i18nd("lliurex-guard-natfree","Loading file. Wait a moment...")
            case 17:
                return i18nd("lliurex-guard-natfree","Applying changes. Wait a moment...")
            case 18:
                return i18nd("lliurex-guard-natfree","Selecting lists to change the activation status. Wait a moment...")
            case 19:
                return i18nd("lliurex-guard-natfree","Selecting lists to be deleted. Wait a moment...")
            case 20:
                return i18nd("lliurex-guard-natfree","Selecting lists to be restored. Wait a moment...")
            case 26:
                return i18nd("lliurex-guard-natfree","Saving changes. Wait a moment...")
            case 27:
                return i18nd("lliurex-guard-natfree","Updating white list dns. Wait a moment...")
            default:
                return ""
        }
    }
}
