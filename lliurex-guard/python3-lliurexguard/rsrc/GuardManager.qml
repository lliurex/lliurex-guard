import org.kde.kirigami 2.16 as Kirigami
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Dialogs 1.3

Rectangle{
    id:rectLayout
    color:"transparent"
    Text{ 
        text:i18nd("lliurex-guard","Current configuration")
        font.pointSize: 16
    }

    GridLayout{
        id:generalGuardLayout
        rows:2
        flow: GridLayout.TopToBottom
        rowSpacing:10
        anchors.left:parent.left
        width:parent.width-10
        height:parent.height-90
        enabled:true
        Kirigami.InlineMessage {
            id: messageLabel
            visible:guardOptionsStackBridge.showMainMessage[0]
            text:getTextMessage(guardOptionsStackBridge.showMainMessage[1])
            type:getTypeMessage(guardOptionsStackBridge.showMainMessage[2])
            Layout.minimumWidth:650
            Layout.fillWidth:true
            Layout.topMargin: 40
        }
        
       GuardLists{
            id:guardLists
            listsModel:guardOptionsStackBridge.listsModel
            Layout.fillHeight:true
            Layout.fillWidth:true
            Layout.topMargin: messageLabel.visible?0:40
       }
       
    }
    
    RowLayout{
        id:btnBox
        anchors.bottom: parent.bottom
        anchors.fill:parent.fill
        anchors.bottomMargin:15
        spacing:10

        Button {
            id:newBtn
            visible:true
            focus:true
            display:AbstractButton.TextBesideIcon
            icon.name:"list-add.svg"
            text:i18nd("lliurex-guard","New List")
            Layout.preferredHeight:40
            Keys.onReturnPressed: applyBtn.clicked()
            Keys.onEnterPressed: applyBtn.clicked()
            onClicked:editMenu.open()

            Menu{
                id:editMenu
                y: -newBtn.height*1.7
                x: newBtn.width/2

                MenuItem{
                    icon.name:"document-edit.svg"
                    text:i18nd("lliurex-guard","Add custom list")
                    onClicked:guardOptionsStackBridge.addCustomList()
                }

                MenuItem{
                    icon.name:"document-import.svg"
                    text:i18nd("lliurex-guard","Add custom list from file")
                    onClicked:guardOptionsStackBridge.addCustomListFromFile()
                }
            } 
        }

        Button {
            id:actionsBtn
            visible:true
            focus:true
            display:AbstractButton.TextBesideIcon
            icon.name:"configure.svg"
            text:i18nd("lliurex-guard","Global Options")
            Layout.preferredHeight:40
            enabled:guardOptionsStackBridge.enableGlobalOptions
            onClicked:actionsMenu.open()
            
            Menu{
                id:actionsMenu
                y: -actionsBtn.height*2.5
                x: actionsBtn.width/2

                MenuItem{
                    icon.name:"security-high.svg"
                    text:i18nd("lliurex-guard","Enable all list")
                    onClicked:guardOptionsStackBridge.changeListStatus([true,true])
                }

                MenuItem{
                    icon.name:"security-low.svg"
                    text:i18nd("lliurex-guard","Disable all lists")
                    onClicked:guardOptionsStackBridge.changeListStatus([true,false])

                }

               MenuItem{
                    icon.name:"delete.svg"
                    text:i18nd("lliurex-guard","Delete all lists")
                    onClicked:guardOptionsStackBridge.removeList([true])
                }
            }
           
        }
        Button {
            id:modeBtn
            visible:true
            focus:true
            display:AbstractButton.TextBesideIcon
            icon.name:{
                switch(guardOptionsStackBridge.guardMode){
                    case "BlackMode":
                        "security-high.svg"
                        break
                    case "WhiteMode":
                        "security-high.svg"
                        break
                    case "DisableMode":
                        "security-low.svg"
                        break
                }
            }
            text:{
                switch(guardOptionsStackBridge.guardMode){
                    case "BlackMode":
                        i18nd("lliurex-guard","Black List mode")
                        break;
                    case "WhiteMode":
                        i18nd("lliurex-guard","White list mode")
                        break;
                    case "DisableMode":
                        i18nd("lliurex-guard","Lliurex Guard is disabled")
                        break
                }
            }
 
            Layout.preferredHeight:40
            Layout.rightMargin:rectLayout.width-(actionsBtn.width+modeBtn.width+newBtn.width+applyBtn.width+40)
            Keys.onReturnPressed: applyBtn.clicked()
            Keys.onEnterPressed: applyBtn.clicked()
            onClicked:modeMenu.open()

            Menu{
               id:modeMenu
               y: -modeBtn.height*1.7
               x: modeBtn.width/2

               MenuItem{
                   icon.name:"security-high.svg"
                   text:i18nd("lliurex-guard","Activate BackList mode")
                   visible:{
                        if (guardOptionsStackBridge.guardMode=="BlackMode"){
                            false
                        }else{
                            true
                        }
                    }
                    onClicked:guardOptionsStackBridge.changeGuardMode("BlackMode")
               }

               MenuItem{
                    icon.name:"security-high.svg"
                    text:i18nd("lliurex-guard","Activate WhiteList mode")
                    visible:{
                        if (guardOptionsStackBridge.guardMode=="WhiteMode"){
                            false
                        }else{
                            true
                        }
                    }
                    onClicked:guardOptionsStackBridge.changeGuardMode("WhiteMode")
               }

               MenuItem{
                    icon.name:"security-low.svg"
                    text:i18nd("lliurex-guard","Disable LliureX-Guard")
                    visible:{
                        if (guardOptionsStackBridge.guardMode=="DisableMode"){
                            false
                        }else{
                            true
                        }
                    }
                    onClicked:guardOptionsStackBridge.changeGuardMode("DisableMode")
               }
            }

        }

        Button {
            id:applyBtn
            visible:true
            focus:true
            enabled:true
            display:AbstractButton.TextBesideIcon
            icon.name:"dialog-ok.svg"
            text:i18nd("lliurex-guard","Apply")
            Layout.preferredHeight:40
            Keys.onReturnPressed: applyBtn.clicked()
            Keys.onEnterPressed: applyBtn.clicked()
            onClicked:guardOptionsStackBridge.applyChanges()
        }
        
    }

 
    function getTextMessage(msgCode){
        switch (msgCode){
          default:
              var msg=""
              break;
        }
        return msg
    } 

    function getTypeMessage(msgType){

        switch (msgType){
            case "Information":
                return Kirigami.MessageType.Information
            case "Ok":
                return Kirigami.MessageType.Positive
            case "Error":
                return Kirigami.MessageType.Error
            case "Warning":
                return Kirigami.MessageType.Warning
        }
    }

} 
