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
    visible:!mainStackBridge.closePopUp[0]
    closePolicy:Popup.NoAutoClose

    GridLayout{
        id: popupGrid
        rows: 2
        flow: GridLayout.TopToBottom
        anchors.centerIn:parent


        RowLayout {
            Layout.fillWidth: true
            Layout.alignment:Qt.AlignHCenter
            Rectangle{
                color:"transparent"
                width:30
                height:30
                AnimatedImage{
                    source: "/usr/lib/python3/dist-packages/bellscheduler/rsrc/loading.gif"
                    transform: Scale {xScale:0.45;yScale:0.45}
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.alignment:Qt.AlignHCenter

            Text{
                id:popupText
                text:getTextMessage()
                font.pointSize: 10
                Layout.alignment:Qt.AlignHCenter
            }
        }
    }

    function getTextMessage(){
        switch (mainStackBridge.closePopUp[1]){
            case 7:
                var msg=i18nd("lliurex-guard","Changing Lliurex Guard mode. Wait a moment...")
                break;
            case 11:
                var msg=i18nd("lliurex-guard","Loading the information from the list. Wait a moment...")
                break;
            case 14:
                var msg=i18nd("lliurex-guard","Loading file. Wait a moment...")
                break;
            case 15:
                var msg=i18nd("lliurex-guard","Applying changes. Wait a moment...")
                break;
            case 17:
                var msg=i18nd("lliurex-guard","Changing Lliurex Guard mode. Wait a moment...")
                break;
            case 18:
                var msg=i18nd("lliurex-guard","Selecting lists to change the activation status. Wait a moment...")
                break;
            case 19:
                var msg=i18nd("lliurex-guard","Selecting lists to be deleted. Wait a moment...")
                break;
            case 20:
                var msg=i18nd("lliurex-guard","Selecting lists not to be deleted. Wait a moment...")
                break;
            default:
                var msg=""
                break;
        }
        return msg
    }
}
