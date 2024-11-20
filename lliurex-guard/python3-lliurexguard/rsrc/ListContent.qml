import org.kde.plasma.components as PC
import org.kde.kirigami as Kirigami
import QtQuick
import QtQuick.Controls
import QtQml.Models
import QtQuick.Layouts


Rectangle {
    property alias listModel:filterModel.model
    property alias listCount:urlList.count
    color:"transparent"

    GridLayout{
        id:mainGrid
        rows:3
        flow: GridLayout.TopToBottom
        rowSpacing:10
        anchors.left:parent.left
        anchors.fill:parent

        RowLayout{
            id:searchRow
            Layout.alignment:Qt.AlignLeft
            visible:true
            Layout.rightMargin:addUrlBtn.width+40

            Text{
                id:headText
                text:i18nd("lliurex-guard","Relationship of urls and domains:")
                Layout.fillWidth:true
            }

            PC.TextField{
                id:listSearchEntry
                font.pointSize:10
                horizontalAlignment:TextInput.AlignLeft
                Layout.alignment:Qt.AlignRight
                focus:true
                width:100
                enabled:urlList.count==0?false:true
                placeholderText:i18nd("lliurex-guard","Search...")
                onTextChanged:{
                    filterModel.update()
                }
                    
            }
        }
        RowLayout {
            id:entryRow
            Layout.alignment:Qt.AlignLeft
            visible:false
            Layout.rightMargin:addUrlBtn.width+40

            TextField{
                id:urlEntry
                placeholderText:i18nd("lliurex-guard","Url separated by space")
                font.pointSize:10
                Layout.fillWidth:true
            }
            Button{
                id:applyUrlBtn
                display:AbstractButton.IconOnly
                icon.name:"dialog-ok.svg"
                enabled:urlEntry.text.trim().length>0?true:false
                ToolTip.delay: 1000
                ToolTip.timeout: 3000
                ToolTip.visible: hovered
                ToolTip.text:i18nd("lliurex-guard","Click to add the urls to list")
                Keys.onReturnPressed: applyUrlBtn.clicked()
                Keys.onEnterPressed: applyUrlBtn.clicked()
                onClicked:{
                    if (listStackBridge.enableUrlEdition){
                        listStackBridge.editUrl(urlEntry.text)
                        manageEntryRow(false)
                    }else{
                        listStackBridge.addNewUrl(urlEntry.text)
                        urlEntry.text=""
                        urlEntry.forceActiveFocus()
                    }
                }
            }

            Button{
                id:cancelUrlBtn
                display:AbstractButton.IconOnly
                icon.name:"dialog-close.svg"
                focus:true
                ToolTip.delay: 1000
                ToolTip.timeout: 3000
                ToolTip.visible: hovered
                ToolTip.text:i18nd("lliurex-guard","Click to close")
                Keys.onReturnPressed: cancelUserBtn.clicked()
                Keys.onEnterPressed: cancelUserBtn.clicked()
                onClicked:{
                    manageEntryRow(false)
                    listStackBridge.cancelUrlEdition()
                }
            }

        }
        RowLayout{

            Rectangle {
                id:listsTable
                visible: true
                Layout.fillHeight:true
                Layout.fillWidth:true
                color:"white"
                border.color: "#d3d3d3"

                PC.ScrollView{
                    implicitWidth:parent.width
                    implicitHeight:parent.height
                    anchors.leftMargin:10

                    ListView{
                        id: urlList
                        anchors.fill:parent
                        height: parent.height
                        enabled:true
                        currentIndex:-1
                        clip: true
                        focus:true
                        boundsBehavior: Flickable.StopAtBounds
                        highlight: Rectangle { color: "#add8e6"; opacity:0.8;border.color:"#53a1c9" }
                        highlightMoveDuration: 0
                        highlightResizeDuration: 0
                        model:FilterDelegateUrlModel{
                            id:filterModel
                            model:urlModel
                            role:"url"
                            search:listSearchEntry.text.trim()

                            delegate: ListDelegateUrlItem{
                                width:listsTable.width
                                urlId:model.urlId
                                url:model.url
                                
                            }
                        }
                        Kirigami.PlaceholderMessage { 
                            id: emptyHint
                            anchors.centerIn: parent
                            width: parent.width - (Kirigami.Units.largeSpacing * 4)
                            visible: urlList.count==0?true:false
                            text: i18nd("lliurex-guard","No url is configured")
                        }
                    } 
                 }
            }
            ColumnLayout{
                id:buttomLayout
                Layout.leftMargin:10

                Button{
                    id:addUrlBtn
                    visible:true
                    display:AbstractButton.TextBesideIcon
                    icon.name:"list-add.svg"
                    text:i18nd("lliurex-guard","Add url")
                    Layout.preferredHeight:40
                    
                    enabled:true
                    onClicked:{
                        manageEntryRow(true)
                        urlEntry.forceActiveFocus()
                        
                    }

                }
                Button{
                    id:deleteListBtn
                    visible:true
                    display:AbstractButton.TextBesideIcon
                    icon.name:"delete.svg"
                    text:i18nd("lliurex-guard","Remove list")
                    Layout.preferredHeight:40
                    enabled:{
                        if ((listCount>0)&&(!entryRow.visible)){
                            true
                        }else{
                            false
                        }
                    }
                    onClicked:{
                        emptyListDialog.dialogVisible=true
                    }

                }
            }
        }
    }

   ChangesDialog{
        id:emptyListDialog
        dialogIcon:"/usr/share/icons/breeze/status/64/dialog-warning.svg"
        dialogTitle:"Lliurex-Guard"+" - "+i18nd("lliurex-guard","Edit list")
        dialogMsg:i18nd("lliurex-guard","Do you want delete all urls from the list?")
        dialogVisible:false
        dialogWidth:480
        btnAcceptVisible:false
        btnAcceptText:""
        btnDiscardText:i18nd("lliurex-guard","Yes")
        btnDiscardIcon:"dialog-ok.svg"
        btnDiscardVisible:true
        btnCancelText:i18nd("lliurex-guard","No")
        btnCancelIcon:"dialog-cancel.svg"
        Connections{
           target:emptyListDialog
           function onDiscardDialogClicked(){
                emptyListDialog.dialogVisible=false
                listStackBridge.manageEmptyListDialog('Apply')         
           }
           function onRejectDialogClicked(){
                emptyListDialog.dialogVisible=false
                listStackBridge.manageEmptyListDialog('Cancel')       
           }

        }
    } 


    function manageEntryRow(enable){

         entryRow.visible=enable
         urlEntry.text=""
         searchRow.visible=!enable
         addUrlBtn.enabled=!enable

    }
}

