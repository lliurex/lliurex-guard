import org.kde.plasma.core as PlasmaCore
import org.kde.kirigami as Kirigami
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window

ApplicationWindow {

    property bool closing: false
    id:mainWindow
    visible: true
    title: "LliureX-Guard"
    property int margin: 1
    width: mainLayout.implicitWidth + 2 * margin
    height: mainLayout.implicitHeight + 2 * margin
    minimumWidth: mainLayout.Layout.minimumWidth + 2 * margin
    minimumHeight: mainLayout.Layout.minimumHeight + 2 * margin
    Component.onCompleted: {
        x = Screen.width / 2  - minimumWidth/2
        y = Screen.height / 2 - minimumHeight/2
    }

    onClosing:(close)=> {
        close.accepted=closing;
        mainStackBridge.closeLliureXGuard()
        delay(100, function() {
            if (mainStackBridge.closeGui){
                closing=true,
                closeTimer.stop(),           
                mainWindow.close();
            }
        })
    }

    ColumnLayout {
        id: mainLayout
        anchors.fill: parent
        anchors.margins: margin
        Layout.minimumWidth:800
        Layout.minimumHeight:650

        RowLayout {
            id: bannerBox
            Layout.alignment:Qt.AlignTop

            Rectangle{
                color: "#000000"
                Layout.minimumWidth:mainLayout.width
                Layout.preferredWidth:mainLayout.width
                Layout.fillWidth:true
                Layout.minimumHeight:120
                Layout.maximumHeight:120
                Image{
                    id:banner
                    source: "/usr/lib/python3.12/dist-packages/lliurexguard/rsrc/lliurex-guard_banner.png"
                    asynchronous:true
                    anchors.centerIn:parent
                }
            }
        }

        StackView {
            id: mainView
            property int currentIndex:mainStackBridge.currentStack
            Layout.alignment:Qt.AlignHCenter|Qt.AlignVCenter
            Layout.leftMargin:0
            Layout.fillWidth:true
            Layout.fillHeight: true
            initialItem:loadView
            onCurrentIndexChanged:{
                switch (currentIndex){
                    case 0:
                        mainView.replace(loadView)
                        break;
                    case 1:
                        mainView.replace(menuView)
                        break;
                    case 2:
                        mainView.replace(listView)
                        break;
                }
            }
            replaceEnter: Transition {
                PropertyAnimation {
                    property: "opacity"
                    from: 0
                    to:1
                    duration: 600
                }
            }
            replaceExit: Transition {
                PropertyAnimation {
                    property: "opacity"
                    from: 1
                    to:0
                    duration: 600
                }
            }

           Component{
               id:loadView
               LoadWaiting{
                   id:loadWaiting
               }
           }
           Component{
               id:menuView
               MainOptions{
                   id:mainOptions
               }
           }
           Component{
               id:listView
               ListOptions{
                   id:listOptions
               }
           }
        }

    }


    CustomPopUp{
        id:waitingPopUp
    }

    Timer{
        id:closeTimer
    }

    function delay(delayTime,cb){
        closeTimer.interval=delayTime;
        closeTimer.repeat=true;
        closeTimer.triggered.connect(cb);
        closeTimer.start()
    }

}

