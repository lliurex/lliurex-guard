import org.kde.kirigami as Kirigami
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts


Rectangle{
    color:"transparent"

    Text{ 
        text:i18nd("lliurex-guard","Edit list")
        font.pointSize: 16
    }

    GridLayout{
        id:generalLayout
        rows:3
        flow: GridLayout.TopToBottom
        rowSpacing:15
        width:parent.width-10
        height:listStackBridge.showUrlsList?parent.height-90:0
        anchors.horizontalCenter:parent.horizontalCenter

        Kirigami.InlineMessage {
            id: messageLabel
            visible:listStackBridge.showListFormMessage[0]
            text:getMessageText()
            type:getTypeMessage()
            Layout.minimumWidth:650
            Layout.fillWidth:true
            Layout.topMargin: 40
        }

        GridLayout{
            id:optionsGrid
            columns:2
            flow: GridLayout.LeftToRight
            columnSpacing:5
            enabled:listStackBridge.enableForm
            Layout.topMargin: messageLabel.visible?0:40
            Layout.alignment:Qt.AlignHCenter
            onEnabledChanged:{
                nameEntry.forceActiveFocus()
            }

            Text{
                id:name
                text:i18nd("lliurex-guard","Name:")
                Layout.alignment:Qt.AlignRight
            }
            TextField{
                id:nameEntry
                text:listStackBridge.listName
                horizontalAlignment:TextInput.AlignLeft
                implicitWidth:400
                onTextChanged:{
                    listStackBridge.updateListName(nameEntry.text)
                }

            }
            Text{
                id:description
                text:i18nd("lliurex-guard","Description: ")
                Layout.alignment:Qt.AlignRight
            }
            TextField{
                id:descriptionEntry
                text:listStackBridge.listDescription
                horizontalAlignment:TextInput.AlignLeft
                implicitWidth:400
                onTextChanged:{
                    listStackBridge.updateListDescription(descriptionEntry.text)
                }

            }
            Text{
                id:listContentText
                text:i18nd("lliurex-guard","Relationship of urls and domains:")
                Layout.alignment:Qt.AlignRight
                visible:!listStackBridge.showUrlsList
            }

            Button{
                id:openFileBtn
                visible:!listStackBridge.showUrlsList
                display:AbstractButton.TextBesideIcon
                icon.name:"dialog-edit.svg"
                text:i18nd("lliurex-guard","Clic to see/edit the list")
                Layout.preferredHeight:40
                Layout.alignment:Qt.AlignLeft
                enabled:true
                onClicked:listStackBridge.openListFile()

            }
       
        }

        ListContent{
            id:listContent
            listModel:listStackBridge.urlModel
            Layout.fillHeight:true
            Layout.fillWidth:true
            visible:listStackBridge.showUrlsList
            Layout.rightMargin:10
        }
              
    }
    RowLayout{
        id:btnBox
        anchors.bottom: parent.bottom
        anchors.right:parent.right
        anchors.bottomMargin:15
        anchors.rightMargin:10
        spacing:10

        Button {
            id:applyBtn
            visible:true
            display:AbstractButton.TextBesideIcon
            icon.name:"document-save.svg"
            text:i18nd("lliurex-guard","Save")
            Layout.preferredHeight:40
            enabled:listStackBridge.arePendingChangesInList
            
            onClicked:{
                closeTimer.stop()
                listStackBridge.saveListChanges()
                
            }
        }
        Button {
            id:cancelBtn
            visible:true
            display:AbstractButton.TextBesideIcon
            icon.name:"dialog-cancel.svg"
            text:i18nd("lliurex-guard","Cancel")
            Layout.preferredHeight: 40
            enabled:listStackBridge.arePendingChangesInList

            onClicked:{
               listStackBridge.cancelListChanges()
            }
            
        }
    } 

    ChangesDialog{
        id:settingsChangesDialog
        dialogIcon:"/usr/share/icons/breeze/status/64/dialog-warning.svg"
        dialogTitle:"LliureX-Guard"+" - "+i18nd("lliurex-guard","List edition")
        dialogVisible:listStackBridge.showChangesInListDialog
        dialogMsg:i18nd("lliurex-guard","The are pending changes to save.\nDo you want save the changes or discard them?")
        dialogWidth:400
        btnAcceptVisible:true
        btnAcceptText:i18nd("lliurex-guard","Apply")
        btnDiscardText:i18nd("lliurex-guard","Discard")
        btnDiscardIcon:"delete.svg"
        btnDiscardVisible:true
        btnCancelText:i18nd("lliurex-guard","Cancel")
        btnCancelIcon:"dialog-cancel.svg"
        Connections{
            target:settingsChangesDialog
            function onApplyDialogClicked(){
                listStackBridge.manageChangesInListDialog("Apply")
            }
            function onDiscardDialogClicked(){
                listStackBridge.manageChangesInListDialog("Discard")           
            }
            function onRejectDialogClicked(){
                closeTimer.stop()
                listStackBridge.manageChangesInListDialog("Cancel")       
            }

        }
   }

   function getMessageText(){

        switch (listStackBridge.showListFormMessage[1]){
                
            case -1:
                var msg=i18nd("lliurex-guard","You must indicate a name for the list")
                break;
            case -2:
                var msg=i18nd("lliurex-guard","The name of the list is duplicate")
                break;
            case -27:
                var msg=i18nd("lliurex-guard","The loaded file is empty")
                break;
            case -31:
                var msg=i18nd("lliurex-guard","It is not possible to edit the list.\nThe file size exceeds the recommended limit of 28 Mb")
                break;
            case -32:
                var msg=i18nd("lliurex-guard","Duplicate url have not been added to the list")
                break;
            case -33:
                var msg=i18nd("lliurex-guard","The url entered already exists in the list")
                break;
            case -35:
                var msg=i18nd("lliurex-guard","The url list is empty")
                break;
            case -36:
                var msg=i18nd("lliurex-guard","Duplicate url and url with incorrect format have not been added to the list")
                break;
            case -37:
                var msg=i18nd("lliurex-guard","Url with incorrect format have not been added to the list")
                break;
            case -38:
                var msg=i18nd("lliurex-guard","The url entered is not in the correct format")
                break;
            case 6:
                var msg=i18nd("lliurex-guard","Waiting while viewing / editing the list. To continue close the file")
                break
            default:
                var msg=""
                break
        }
        return msg    

    }

    function getTypeMessage(){

        switch (listStackBridge.showListFormMessage[2]){
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
