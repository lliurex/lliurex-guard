import org.kde.plasma.components 3.0 as PC3
import org.kde.kirigami 2.16 as Kirigami
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQml.Models 2.8
import QtQuick.Layouts 1.15


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
            Layout.rightMargin:addUrlBtn.width+15

            Text{
                id:headText
                text:i18nd("lliurex-guard","Relationship of urls and domains:")
                Layout.fillWidth:true
            }

            PC3.TextField{
                id:listSearchEntry
                font.pointSize:10
                horizontalAlignment:TextInput.AlignLeft
                Layout.alignment:Qt.AlignRight
                focus:true
                width:100
                enabled:true
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
            Layout.rightMargin:addUrlBtn.width+15

            TextField{
                id:urlEntry
                placeholderText:i18nd("lliurex-guarad","Url separated by space")
                font.pointSize:10
                Layout.fillWidth:true
                focus:true
            }
            Button{
                id:applyUrlBtn
                display:AbstractButton.IconOnly
                icon.name:"dialog-ok.svg"
                enabled:urlEntry.text.trim().length>0?true:false
                focus:true
                ToolTip.delay: 1000
                ToolTip.timeout: 3000
                ToolTip.visible: hovered
                ToolTip.text:i18nd("lliurex-guard","Click to add the urls to list")
                Keys.onReturnPressed: applyUserBtn.clicked()
                Keys.onEnterPressed: applyUserBtn.clicked()
                onClicked:listStackBridge.addNewUrl(urlEntry.text)
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
                    entryRow.visible=false
                    urlEntry.text=""
                    searchRow.visible=true
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

                PC3.ScrollView{
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
                                url:model.url
                                
                            }
                        }
                        Kirigami.PlaceholderMessage { 
                            id: emptyHint
                            anchors.centerIn: parent
                            width: parent.width - (units.largeSpacing * 4)
                            visible: urlList.count==0?true:false
                            text: i18nd("lliurex-guard","No url is configured")
                        }
                    } 
                 }
            }
            Button{
                id:addUrlBtn
                visible:true
                focus:true
                display:AbstractButton.TextBesideIcon
                icon.name:"list-add.svg"
                text:i18nd("lliurex-guard","Añadir url")
                Layout.preferredHeight:40
                Layout.leftMargin:10
                enabled:true
                Keys.onReturnPressed: applyBtn.clicked()
                Keys.onEnterPressed: applyBtn.clicked()
                onClicked:{
                    entryRow.visible=true
                    searchRow.visible=false
                }

            }
        }
    }
}

