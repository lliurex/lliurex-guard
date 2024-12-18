import org.kde.plasma.components as PC
import org.kde.kirigami as Kirigami
import QtQuick
import QtQuick.Controls
import QtQml.Models
import QtQuick.Layouts


Rectangle {
    property alias listsModel:filterModel.model
    property alias listsCount:guardLists.count
    color:"transparent"

    GridLayout{
        id:mainGrid
        rows:2
        flow: GridLayout.TopToBottom
        rowSpacing:10
        anchors.left:parent.left
        anchors.fill:parent

        RowLayout{
            Layout.alignment:Qt.AlignRight
            spacing:10
            Button{
                id:statusFilterBtn
                display:AbstractButton.IconOnly
                icon.name:"view-filter.svg"
                enabled:guardOptionsStackBridge.enableListsStatusOptions[2]
                ToolTip.delay: 1000
                ToolTip.timeout: 3000
                ToolTip.visible: hovered
                ToolTip.text:i18nd("lliurex-guard","Click to filter list by status")
                onClicked:optionsMenu.open();
               
                Menu{
                    id:optionsMenu
                    y: statusFilterBtn.height
                    x:-(optionsMenu.width-statusFilterBtn.width/2)

                    MenuItem{
                        icon.name:"security-high.svg"
                        text:i18nd("lliurex-guard","Show activated lists ")
                        enabled:{
                            if (guardOptionsStackBridge.filterStatusValue!="active"){
                                true
                            }else{
                                false
                            }
                        }
                        onClicked:guardOptionsStackBridge.manageStatusFilter("active")
                    }

                    MenuItem{
                        icon.name:"lliurex-guard-disable-mode.svg"
                        text:i18nd("lliurex-guard","Show disabled lists")
                        enabled:{
                            if (guardOptionsStackBridge.filterStatusValue!="disable"){
                                true
                            }else{
                                false
                            }
                        }
                        onClicked:guardOptionsStackBridge.manageStatusFilter("disable")
                    }
                    MenuItem{
                        icon.name:"kt-remove-filters.svg"
                        text:i18nd("lliurex-guard","Remove filter")
                        enabled:{
                            if (guardOptionsStackBridge.filterStatusValue!="all"){
                                true
                            }else{
                                false
                            }
                        }
                        onClicked:guardOptionsStackBridge.manageStatusFilter("all")
                    }
                }
                
            }
            PC.TextField{
                id:listSearchEntry
                font.pointSize:10
                horizontalAlignment:TextInput.AlignLeft
                Layout.alignment:Qt.AlignRight
                focus:true
                width:100
                visible:true
                enabled:true
                placeholderText:i18nd("lliurex-guard","Search...")
                onTextChanged:{
                    filterModel.update()
                }
                
            }
        }

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
                    id: guardLists
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
                    model:FilterDelegateModel{
                        id:filterModel
                        model:listsModel
                        role:"metaInfo"
                        search:listSearchEntry.text.trim()
                        statusFilter:guardOptionsStackBridge.filterStatusValue

                        delegate: ListDelegateItem{
                            width:listsTable.width
                            listOrder:model.order
                            listId:model.id
                            listName:model.name
                            listEntries:model.entries
                            listDescription:model.description
                            listActivated:model.activated
                            listRemove:model.remove
                            metaInfo:model.metaInfo
                           
                        }
                    }
                    Kirigami.PlaceholderMessage { 
                        id: emptyHint
                        anchors.centerIn: parent
                        width: parent.width - (Kirigami.Units.largeSpacing * 4)
                        visible: guardLists.count==0?true:false
                        text: i18nd("lliurex-guard","No list is configured")
                    }
                } 
             }
        }
    }
}

