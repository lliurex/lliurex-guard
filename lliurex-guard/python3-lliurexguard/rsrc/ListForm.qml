import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import org.kde.kirigami as Kirigami

Rectangle{
    color:"transparent"

    Timer{
        id:debounceTimer
        interval:500
        repeat:false
        property var callback
        onTriggered: if (callback) callback()

    }

    ColumnLayout{
        id: mainContent
        anchors.fill:parent
        anchors.leftMargin:5
        anchors.rightMargin:15
        anchors.bottomMargin:15
        spacing: 15

        Text{ 
            text:i18nd("lliurex-guard","Edit list")
            font.pointSize: 16
        }

        Kirigami.InlineMessage {
            id: messageLabel
            visible:listStackBridge.showListFormMessage.show
            text:getMessageText()
            type:getTypeMessage()
            Layout.fillWidth:true
        }

        GridLayout{
            id:optionsGrid
            columns:2
            rowSpacing:10
            columnSpacing:10
            Layout.topMargin:5
            Layout.alignment: Qt.AlignHCenter

            Text{
                id:name
                text:i18nd("lliurex-guard","Name:")
                Layout.alignment:Qt.AlignRight | Qt.AlignVCenter
            }

            TextField{
                id:nameEntry
                text:listStackBridge.listName
                horizontalAlignment:TextInput.AlignLeft
                Layout.preferredWidth:400
                onTextChanged: {
                    if (activeFocus){
                        debounceTimer.callback= ()=>listStackBridge.updateListName(nameEntry.text)
                        debounceTimer.restart()
                    }
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
                Layout.preferredWidth:400

                onTextChanged: {
                    if (activeFocus){
                        debounceTimer.callback= ()=> listStackBridge.updateListDescription(descriptionEntry.text)
                        debounceTimer.restart()
                    }
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
                icon.name:"dialog-edit"
                text:i18nd("lliurex-guard","Clic to see/edit the list")
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
            Layout.bottomMargin:10
        }

        Item{
            Layout.fillHeight:true
        }

        RowLayout{
            id:btnBox
            Layout.alignment: Qt.AlignRight
            spacing:10

            Button {
                id:applyBtn
                visible:true
                display:AbstractButton.TextBesideIcon
                icon.name:"document-save"
                text:i18nd("lliurex-guard","Save")
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
                icon.name:"dialog-cancel"
                text:i18nd("lliurex-guard","Cancel")
                enabled:listStackBridge.arePendingChangesInList
                onClicked:{
                   listStackBridge.cancelListChanges()
                }
                
            }
        }
    }

    ChangesDialog{
        id:settingsChangesDialog
        dialogIcon:"dialog-warning"
        dialogVisible:listStackBridge.showChangesInListDialog
        dialogMsg:i18nd("lliurex-guard","The are pending changes to save.\nDo you want save the changes or discard them?")
        dialogWidth:400
        btnAcceptVisible:true
        btnAcceptText:i18nd("lliurex-guard","Apply")
        btnDiscardText:i18nd("lliurex-guard","Discard")
        btnDiscardIcon:"delete"
        btnDiscardVisible:true
        btnCancelText:i18nd("lliurex-guard","Cancel")
        btnCancelIcon:"dialog-cancel"
        Connections{
            target:settingsChangesDialog
            function onDialogApplyClicked(){
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

        switch (listStackBridge.showListFormMessage.msgCode){
                
            case -1:
               return i18nd("lliurex-guard","You must indicate a name for the list")
            case -2:
               return i18nd("lliurex-guard","The name of the list is duplicate")
            case -27:
               return i18nd("lliurex-guard","The loaded file is empty")
            case -31:
               return i18nd("lliurex-guard","It is not possible to edit the list.\nThe file size exceeds the recommended limit of 28 Mb")
            case -32:
               return i18nd("lliurex-guard","Duplicate url have not been added to the list")
            case -33:
               return i18nd("lliurex-guard","The url entered already exists in the list")
            case -35:
               return i18nd("lliurex-guard","The url list is empty")
            case -36:
               return i18nd("lliurex-guard","Duplicate url and url with incorrect format have not been added to the list")
            case -37:
               return i18nd("lliurex-guard","Url with incorrect format have not been added to the list")
            case -38:
               return i18nd("lliurex-guard","The url entered is not in the correct format")
            case 6:
               return i18nd("lliurex-guard","Waiting while viewing / editing the list. To continue close the file")
            default:
               return ""
        }

    }

    function getTypeMessage(){

        switch (listStackBridge.showListFormMessage.type){
            case 0:
                return Kirigami.MessageType.Positive
            case 1:
                return Kirigami.MessageType.Error
            case 2:
                return Kirigami.MessageType.Warning
            case 3:
            default:
                return Kirigami.MessageType.Information
        }
    }
   
}
