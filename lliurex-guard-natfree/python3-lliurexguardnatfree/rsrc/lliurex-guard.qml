import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15

ApplicationWindow {

    property bool closing: false
    id:mainWindow
    visible: true
    title: "LliureX-Guard"
    property int margin: 1
    width: mainLayout.implicitWidth + 2 * margin
    height: mainLayout.implicitHeight + 2 * margin
    minimumWidth: 800 + 2 * margin
    minimumHeight: 650 + 2 * margin
    Component.onCompleted: {
        x = Screen.width / 2  - minimumWidth/2
        y = Screen.height / 2 - minimumHeight/2
    }

    onClosing: {
        close.accepted = closing;
        if (!closing) {
            mainStackBridge.closeLliureXGuard();
            closeTimer.start();
        }
    }

    Timer {
        id: closeTimer
        interval: 100
        repeat: true
        onTriggered: {
            if (mainStackBridge.closeGui) {
                stop();
                mainWindow.closing = true;
                mainWindow.close();
            }
        }
    }

    ColumnLayout {
        id: mainLayout
        anchors.fill: parent

        Rectangle{
            color: "#000000"
            Layout.fillWidth: true
            Layout.preferredHeight: 120

            Image{
                id:banner
                source: "lliurex-guard_banner.png"
                asynchronous:true
                anchors.centerIn: parent
                fillMode: Image.PreserveAspectFit
            }
        }

        StackView {
            id: mainView
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.minimumHeight:550


            property int currentIndex:mainStackBridge.currentStack
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
                NumberAnimation {
                    property: "opacity"
                    from: 0
                    to: 1
                    duration: 60
                }
            }
            replaceExit: Transition {
                NumberAnimation { 
                    property: "opacity"
                    from: 1
                    to: 0
                    duration: 60
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

}

