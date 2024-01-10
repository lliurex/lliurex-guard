import org.kde.kirigami 2.16 as Kirigami
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15


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
            type:Kirigami.MessageType.Error
            Layout.minimumWidth:650
            Layout.fillWidth:true
            Layout.topMargin: 40
        }

        GridLayout{
            id:optionsGrid
            columns:2
            flow: GridLayout.LeftToRight
            columnSpacing:5
            Layout.topMargin: messageLabel.visible?0:40
            Layout.alignment:Qt.AlignHCenter

            Text{
                id:name
                text:i18nd("lliurex-guard","Name:")
                Layout.alignment:Qt.AlignRight
            }
            TextField{
                id:nameEntry
                text:listStackBridge.listName
                horizontalAlignment:TextInput.AlignLeft
                focus:true
                implicitWidth:400

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
                focus:true
                implicitWidth:400

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
                focus:true
                display:AbstractButton.TextBesideIcon
                icon.name:"dialog-ok.svg"
                text:i18nd("lliurex-guard","Clic to see/edit the list")
                Layout.preferredHeight:40
                Layout.alignment:Qt.AlignLeft
                enabled:true
                Keys.onReturnPressed: applyBtn.clicked()
                Keys.onEnterPressed: applyBtn.clicked()

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
            focus:true
            display:AbstractButton.TextBesideIcon
            icon.name:"dialog-ok.svg"
            text:i18nd("lliurex-guard","Apply")
            Layout.preferredHeight:40
            enabled:listStackBridge.changesInList
            Keys.onReturnPressed: applyBtn.clicked()
            Keys.onEnterPressed: applyBtn.clicked()
            
            onClicked:{
                closeTimer.stop()
                listStackBridge.applyListChanges()
                
            }
        }
        Button {
            id:cancelBtn
            visible:true
            focus:true
            display:AbstractButton.TextBesideIcon
            icon.name:"dialog-cancel.svg"
            text:i18nd("lliurex-guard","Cancel")
            Layout.preferredHeight: 40
            enabled:listStackBridge.changesInList
            Keys.onReturnPressed: cancelBtn.clicked()
            Keys.onEnterPressed: cancelBtn.clicked()

            onClicked:{
               listStackBridge.cancelListChanges()
            }
            
        }
    } 
    /*
    ChangesDialog{
        id:settingsChangesDialog
        dialogIcon:"/usr/share/icons/breeze/status/64/dialog-warning.svg"
        dialogTitle:"LliureX-Guard"+" - "+i18nd("lliurex-guard","List")
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
            function onDialogApplyClicked(){
                listStackBridge.manageChangesDialog("Accept")
            }
            function onDiscardDialogClicked(){
                listStackBridge.manageChangesDialog("Discard")           
            }
            function onRejectDialogClicked(){
                closeTimer.stop()
                listStackBridge.manageChangesDialog("Cancel")       
            }

        }
   }
   */


    function getMessageText(){

         switch (listStackBridge.showListFormMessage[1]){
                
            default:
                var msg=""
                break
        }
        return msg    

    }
   
}
