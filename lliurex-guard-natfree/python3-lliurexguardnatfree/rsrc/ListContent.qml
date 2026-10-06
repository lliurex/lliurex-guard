import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQml.Models 2.8
import QtQuick.Layouts 1.15
import org.kde.plasma.components 3.0 as PC3
import org.kde.kirigami 2.16 as Kirigami


Rectangle {
    property alias listModel:filterModel.model
    property alias listCount:urlList.count
    color:"transparent"

    ColumnLayout{
        anchors.fill:parent
        spacing:10

        RowLayout{
            id:searchRow
            Layout.fillWidth:true
            spacing:10
            enabled:true

            Text{
                id:headText
                text:i18nd("lliurex-guard-natfree","Relationship of urls and domains:")
                Layout.fillWidth:true
            }

            PC3.TextField{
                id:listSearchEntry
                font.pointSize:10
                horizontalAlignment:TextInput.AlignLeft
                Layout.alignment:Qt.AlignRight
                focus:true
                width:100
                enabled:{
                    if (urlList.count===0){
                        if (listSearchEntry.text.length===0){
                            false
                        }else{
                            true
                        }
                    }else{
                        true
                    }
                }
                placeholderText:i18nd("lliurex-guard-natfree","Search...")
                onTextChanged:{
                    filterModel.update()
                }
                    
            }
        }

        RowLayout {
            id:entryRow
            Layout.alignment:Qt.AlignLeft
            visible:false
            Layout.rightMargin:addUrlBtn.width+25
            Layout.preferredWidth:urlList.implicitWidth

            TextField{
                id:urlEntry
                placeholderText:i18nd("lliurex-guard-natfree","Url separated by space")
                font.pointSize:10
                Layout.fillWidth:true
                focus:true
            }

            Button{
                id:applyUrlBtn
                display:AbstractButton.IconOnly
                icon.name:"dialog-ok"
                enabled:urlEntry.text.trim().length>0?true:false
                focus:true
                ToolTip.delay: 1000
                ToolTip.timeout: 3000
                ToolTip.visible: hovered
                ToolTip.text:i18nd("lliurex-guard-natfree","Click to add the urls to list")
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
                icon.name:"dialog-close"
                focus:true
                ToolTip.delay: 1000
                ToolTip.timeout: 3000
                ToolTip.visible: hovered
                ToolTip.text:i18nd("lliurex-guard-natfree","Click to close")
                Keys.onReturnPressed: cancelUserBtn.clicked()
                Keys.onEnterPressed: cancelUserBtn.clicked()
                onClicked:{
                    manageEntryRow(false)
                    listStackBridge.cancelUrlEdition()
                }
            }

        }

        RowLayout{
            Layout.alignment:Qt.AlignHCenter
            Layout.rightMargin:10

            Rectangle {
                id:listsTable
                visible: true
                Layout.fillHeight:true
                Layout.fillWidth:true
                color:"white"
                border.color: "#d3d3d3"

                PC3.ScrollView{
                    anchors.fill:parent
                    
                    ListView{
                        id: urlList

                        Timer {
                            id: searchTimer
                            interval: 150
                            repeat: false
                            onTriggered: filterModel.update()
                        }

                        model:FilterDelegateUrlModel{
                            id:filterModel
                            model:urlModel
                            role:"url"
                            search:listSearchEntry.text.trim()
                            externalTimer: searchTimer

                            delegate: ListDelegateUrlItem{
                                width:listsTable.width-18
                                urlId:model.urlId
                                url:model.url
                                
                            }
                        }

                        currentIndex:-1
                        enabled:true
                        clip: true
                        focus:true
                        boundsBehavior: Flickable.StopAtBounds
                        highlightFollowsCurrentItem:true
                        highlightMoveDuration: 0
                        highlightResizeDuration: 0

                        Kirigami.PlaceholderMessage { 
                            id: emptyHint
                            anchors.centerIn: parent
                            width: parent.width - (Kirigami.Units.largeSpacing * 4)
                            visible: urlList.count==0?true:false
                            text: listSearchEntry.text.length==0
                              ?i18nd("lliurex-guard-natfree","No url is configured")
                              :i18nd("lliurex-guard-natfree","No url found")
                            icon.name:"lliurex-guard-natfree"
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
                    icon.name:"list-add"
                    text:i18nd("lliurex-guard-natfree","Add url")
                    
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
                    icon.name:"delete"
                    text:i18nd("lliurex-guard-natfree","Remove list")
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
        dialogTitle:"lliurex-guard-natfree"+" - "+i18nd("lliurex-guard-natfree","Edit list")
        dialogMsg:i18nd("lliurex-guard-natfree","Do you want delete all urls from the list?")
        dialogVisible:false
        dialogWidth:480
        btnAcceptVisible:false
        btnAcceptText:""
        btnDiscardText:i18nd("lliurex-guard-natfree","Yes")
        btnDiscardIcon:"dialog-ok"
        btnDiscardVisible:true
        btnCancelText:i18nd("lliurex-guard-natfree","No")
        btnCancelIcon:"dialog-cancel"
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

