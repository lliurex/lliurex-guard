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
            text:getTextMessage()
            type:getTypeMessage()
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
            display:AbstractButton.TextBesideIcon
            icon.name:"list-add.svg"
            text:i18nd("lliurex-guard","New List")
            Layout.preferredHeight:40
            onClicked:editMenu.open()
            enabled:{
                if (guardOptionsStackBridge.guardMode!="DisableMode"){
                    true
                }else{
                    false
                }
            }

            Menu{
                id:editMenu
                y: -newBtn.height*1.7
                x: newBtn.width/2

                MenuItem{
                    icon.name:"document-edit.svg"
                    text:i18nd("lliurex-guard","Add custom list")
                    onClicked:listStackBridge.addNewList("")
                }

                MenuItem{
                    icon.name:"document-import.svg"
                    text:i18nd("lliurex-guard","Add custom list from file")
                    onClicked:loadFileDialog.open()
                }
            } 
        }

        Button {
            id:actionsBtn
            visible:true
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
                    enabled:!guardOptionsStackBridge.enableListsStatusOptions[0]
                    onClicked:guardOptionsStackBridge.changeListStatus([true,true])
                }

                MenuItem{
                    icon.name:"lliurex-guard-disable-mode.svg"
                    text:i18nd("lliurex-guard","Disable all lists")
                    enabled:!guardOptionsStackBridge.enableListsStatusOptions[1]
                    onClicked:guardOptionsStackBridge.changeListStatus([true,false])

                }
                MenuItem{
                    icon.name:"delete.svg"
                    text:i18nd("lliurex-guard","Delete all lists")
                    enabled:guardOptionsStackBridge.enableRemoveListsOption
                    onClicked:guardOptionsStackBridge.removeLists([true])
                }
                MenuItem{
                    icon.name:"restoration.svg"
                    text:i18nd("lliurex-guard","Restore all lists")
                    enabled:guardOptionsStackBridge.enableRestoreListsOption
                    onClicked:guardOptionsStackBridge.restoreLists([true])
                }
                MenuItem{
                    icon.name:"view-refresh.svg"
                    text:i18nd("lliurex-guard","Update white list dns")
                    onClicked:guardOptionsStackBridge.updateWhiteListDNS()
                    visible:guardOptionsStackBridge.showUpdateDnsOption
                }
            }
           
        }
        Button {
            id:modeBtn
            visible:true
            display:AbstractButton.TextBesideIcon
            icon.name:{
                switch(guardOptionsStackBridge.guardMode){
                    case "BlackMode":
                        "security-high.svg"
                        break
                    case "WhiteMode":
                        "lliurex-guard-white-mode.svg"
                        break
                    case "DisableMode":
                        "lliurex-guard-disable-mode.svg"
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
            enabled:!guardOptionsStackBridge.arePendingChanges
            Layout.preferredHeight:40
            Layout.rightMargin:rectLayout.width-(actionsBtn.width+modeBtn.width+newBtn.width+applyBtn.width+40)
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
                    icon.name:"lliurex-guard-white-mode.svg"
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
                    icon.name:"lliurex-guard-disable-mode.svg"
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
            enabled:guardOptionsStackBridge.arePendingChanges
            display:AbstractButton.TextBesideIcon
            icon.name:"dialog-ok.svg"
            text:i18nd("lliurex-guard","Apply")
            Layout.preferredHeight:40
            onClicked:guardOptionsStackBridge.applyChanges()
        }
        
    }

    FileDialog{
        id:loadFileDialog
        folder:shortcuts.home
        nameFilters:["Test files (*txt)"]
        onAccepted:{
            var selectedPath=""
            selectedPath=loadFileDialog.fileUrl.toString()
            selectedPath=selectedPath.replace(/^(file:\/{2})/,"")
            listStackBridge.addNewList(selectedPath)
        }
      
    } 


    ChangesDialog{
        id:changeModeDialog
        dialogIcon:"/usr/share/icons/breeze/status/64/dialog-warning.svg"
        dialogTitle:"Lliurex-Guard"+" - "+i18nd("lliurex-guard","Change Mode")
        dialogMsg:{
            switch(guardOptionsStackBridge.showChangeModeDialog[1]){
                case "BlackMode":
                    i18nd("lliurex-guard","Do yo want to change to black list mode?\nIf you activate this mode, you will not be able to access the urls contained in the active lists")
                    break;
                case "WhiteMode":
                    i18nd("lliurex-guard","Do yo want to change to white list mode?\nIf you activate this mode, you can only access the urls contained in the active lists")
                    break;
                case "DisableMode":
                    i18nd("lliurex-guard","Do you want to deactivate LliureX Guard?\nIf you deactivate it, no filter will be applied")
                    break;
                default:
                    ""
                    break
            }
        }
        dialogVisible:guardOptionsStackBridge.showChangeModeDialog[0]
        dialogWidth:650
        btnAcceptVisible:false
        btnAcceptText:""
        btnDiscardText:i18nd("lliurex-guard","Accept")
        btnDiscardIcon:"dialog-ok.svg"
        btnDiscardVisible:true
        btnCancelText:i18nd("lliurex-guard","Cancel")
        btnCancelIcon:"dialog-cancel.svg"
        Connections{
           target:changeModeDialog
           function onDiscardDialogClicked(){
                guardOptionsStackBridge.manageChangeModeDialog('Accept')         
           }
           function onRejectDialogClicked(){
                guardOptionsStackBridge.manageChangeModeDialog('Cancel')       
           }

        }
    } 

    ChangesDialog{

        id:pendingChangesDialog
        dialogIcon:"/usr/share/icons/breeze/status/64/dialog-warning.svg"
        dialogTitle:"Lliurex-Guard"+" - "+i18nd("lliurex-guard","Pending changes")
        dialogMsg:i18nd("lliurex-guard","There are pendin changes to apply.\nDo you want to apply the changes or discard them?")
        dialogVisible:guardOptionsStackBridge.showPendingChangesDialog
        dialogWidth:500
        btnAcceptVisible:true
        btnAcceptText:i18nd("lliurex-guard","Apply")
        btnDiscardText:i18nd("lliurex-guard","Discard")
        btnDiscardIcon:"delete.svg"
        btnDiscardVisible:true
        btnCancelText:i18nd("lliurex-guard","Cancel")
        btnCancelIcon:"dialog-cancel.svg"
        Connections{
           target:pendingChangesDialog
           function onApplyDialogClicked(){
                guardOptionsStackBridge.managePendingChangesDialog("Apply")
           }
           function onDiscardDialogClicked(){
                guardOptionsStackBridge.managePendingChangesDialog('Discard')         
           }
           function onRejectDialogClicked(){
                closeTimer.stop()
                guardOptionsStackBridge.managePendingChangesDialog('Cancel')       
           }

        }
    } 

    ChangesDialog{
        id:removeListsDialog
        dialogIcon:"/usr/share/icons/breeze/status/64/dialog-warning.svg"
        dialogTitle:"Lliurex-Guard"+" - "+i18nd("lliurex-guard","Remove Lists")
        dialogMsg:guardOptionsStackBridge.showRemoveListsDialog[1]?i18nd("lliurex-guard","Do you want select alls list to be remove?"):i18nd("lliurex-guard","Do you want select the list to be remove?")
        dialogVisible:guardOptionsStackBridge.showRemoveListsDialog[0]
        dialogWidth:500
        btnAcceptVisible:false
        btnAcceptText:""
        btnDiscardText:i18nd("lliurex-guard","Yes")
        btnDiscardIcon:"dialog-ok.svg"
        btnDiscardVisible:true
        btnCancelText:i18nd("lliurex-guard","No")
        btnCancelIcon:"dialog-cancel.svg"
        Connections{
           target:removeListsDialog
           function onDiscardDialogClicked(){
                guardOptionsStackBridge.manageRemoveListsDialog('Apply')         
           }
           function onRejectDialogClicked(){
                guardOptionsStackBridge.manageRemoveListsDialog('Cancel')       
           }

        }
    } 
    ChangesDialog{
        id:restoreListsDialog
        dialogIcon:"/usr/share/icons/breeze/status/64/dialog-warning.svg"
        dialogTitle:"Lliurex-Guard"+" - "+i18nd("lliurex-guard","Restore Lists")
        dialogMsg:i18nd("lliurex-guard","Do you want select alls list not to be remove?")
        dialogVisible:guardOptionsStackBridge.showRestoreListsDialog
        dialogWidth:500
        btnAcceptVisible:false
        btnAcceptText:""
        btnDiscardText:i18nd("lliurex-guard","Yes")
        btnDiscardIcon:"dialog-ok.svg"
        btnDiscardVisible:true
        btnCancelText:i18nd("lliurex-guard","No")
        btnCancelIcon:"dialog-cancel.svg"
        Connections{
           target:restoreListsDialog
           function onDiscardDialogClicked(){
                guardOptionsStackBridge.manageRestoreListsDialog('Apply')         
           }
           function onRejectDialogClicked(){
                guardOptionsStackBridge.manageRestoreListsDialog('Cancel')       
           }

        }
    } 

    ChangesDialog{
        id:updateDnsDialog
        dialogIcon:"/usr/share/icons/breeze/status/64/dialog-warning.svg"
        dialogTitle:"Lliurex-Guard"+" - "+i18nd("lliurex-guard","Update whitelists dns")
        dialogMsg:i18nd("lliurex-guard","Do you want to update white list dns?")
        dialogVisible:guardOptionsStackBridge.showUpdateDnsDialog
        dialogWidth:500
        btnAcceptVisible:false
        btnAcceptText:""
        btnDiscardText:i18nd("lliurex-guard","Accept")
        btnDiscardIcon:"dialog-ok.svg"
        btnDiscardVisible:true
        btnCancelText:i18nd("lliurex-guard","Cancel")
        btnCancelIcon:"dialog-cancel.svg"
        Connections{
           target:updateDnsDialog
           function onDiscardDialogClicked(){
                guardOptionsStackBridge.manageUpdateDnsDialog('Accept')         
           }
           function onRejectDialogClicked(){
                guardOptionsStackBridge.manageUpdateDnsDialog('Cancel')       
           }

        }
    }

    function getTextMessage(){
        switch (guardOptionsStackBridge.showMainMessage[1]){
            case -5:
                var msg=i18nd("lliurex-guard","Error saving the changes of the list:")+" "+guardOptionsStackBridge.showMainMessage[3]
                break;
            case -9:
                var msg=i18nd("lliurex-guard","Error changing Lliurex Guard mode:")+" "+guardOptionsStackBridge.showMainMessage[3]
                break;
            case -10:
                var msg=i18nd("lliurex-guard","Error restarting dnsmasq. Lliurex Guard and the lists have been disabled:")+" "+guardOptionsStackBridge.showMainMessage[3]
                break;
            case -13:
                var msg=i18nd("lliurex-guard","Error loading the information from the list:")+" "+guardOptionsStackBridge.showMainMessage[3]
                break;
            case -16:
                var msg=i18nd("lliurex-guard","Error loading file:")
                " "+guardOptionsStackBridge.showMainMessage[3]
                break;
            case -19:
                var msg=i18nd("lliurex-guard","Error removing lists:")+" "+guardOptionsStackBridge.showMainMessage[3]
                break;
            case -20:
                var msg=i18nd("lliurex-guard","Error activating lists:")+" "+guardOptionsStackBridge.showMainMessage[3]
                break;
            case -21:
                var msg=i18nd("lliurex-guard","Error deactivating lists:")+" "+guardOptionsStackBridge.showMainMessage[3]
                break;
            case -23:
                var msg=i18nd("lliurex-guard","Error reading Lliurex Guard mode:")+" "+guardOptionsStackBridge.showMainMessage[3]
                break;
            case -25:
                var msg=i18nd("lliurex-guard","Error reading list headers:")+" "+guardOptionsStackBridge.showMainMessage[3]
                break;
            case -27:
                var msg=i18nd("lliurex-guardd","The file loaded is empty or the url than containt do not have the correct format")
                break;
            case -30:
                var msg=i18nd("lliurex-guard","It is not possible to load the selected file.\nIts size exceeds the recommended limit of 28 Mb")
                break;
            case -34:
                var msg=i18nd("lliurex-guard","It is not possible to update white list dns")+" "+guardOptionsStackBridge.showMainMessage[3]
                break;
            case -35:
                var msg=i18nd("lliurex-guard","The url list is empty. Urls entered with wrong format have been removed")
                break;
            case 3:
                var msg=i18nd("lliurex-guard","List created successfully")
                break;
            case 4:
                var msg=i18nd("lliurex-guard","List edited successfully")
                break;
            case 8:
                var msg=i18nd("lliurex-guard","The change of Lliurex Guard mode has been successfull")
                break;
            case 18:
                var msg=i18nd("lliurex-guard","Changes applied successfully")
                break;
            case 35:
                var msg=i18nd("lliurex-guard","The white list dns update was successful")
                break;
          default:
              var msg=""
              break;
        }
        return msg
    } 

    function getTypeMessage(){

        switch (guardOptionsStackBridge.showMainMessage[2]){
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
