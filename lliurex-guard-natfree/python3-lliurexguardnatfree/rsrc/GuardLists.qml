import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQml.Models 2.8
import QtQuick.Layouts 1.15
import org.kde.plasma.components 3.0 as PC3
import org.kde.kirigami 2.16 as Kirigami


Rectangle {
    property alias listsModel:filterModel.model
    property alias listsCount:guardLists.count
    color:"transparent"

    ColumnLayout{
        anchors.fill:parent
        spacing:10

        RowLayout{
            id:filterRow
            Layout.fillWidth:true
            Layout.alignment:Qt.AlignRight
            spacing:10
            enabled:true

            Button{
                id:statusFilterBtn
                display:AbstractButton.IconOnly
                icon.name:"view-filter"
                enabled:guardOptionsStackBridge.enableListsStatusOptions.enableStatusFilter
                ToolTip.delay: 1000
                ToolTip.timeout: 3000
                ToolTip.visible: hovered
                ToolTip.text:i18nd("lliurex-guard-natfree","Click to filter list by status")
                onClicked:optionsMenu.open();
               
                Menu{
                    id:optionsMenu
                    y: statusFilterBtn.height
                    x:-(optionsMenu.width-statusFilterBtn.width/2)

                    MenuItem{
                        icon.name:"security-high"
                        text:i18nd("lliurex-guard-natfree","Show activated lists ")
                        enabled:guardOptionsStackBridge.filterStatusValue!="active"?true:false
                        onClicked:guardOptionsStackBridge.manageStatusFilter("active")
                    }

                    MenuItem{
                        icon.name:"lliurex-guard-natfree-disable-mode"
                        text:i18nd("lliurex-guard-natfree","Show disabled lists")
                        enabled:guardOptionsStackBridge.filterStatusValue!="disable"?true:false
                        onClicked:guardOptionsStackBridge.manageStatusFilter("disable")
                    }

                    MenuItem{
                        icon.name:"kt-remove-filters"
                        text:i18nd("lliurex-guard-natfree","Remove filter")
                        enabled:guardOptionsStackBridge.filterStatusValue!="all"?true:false
                        onClicked:guardOptionsStackBridge.manageStatusFilter("all")
                    }
                }
                
            }

            PC3.TextField{
                id:listSearchEntry
                font.pointSize:10
                horizontalAlignment:TextInput.AlignLeft
                Layout.alignment:Qt.AlignRight
                focus:true
                width:100
                visible:true
                enabled:true
                placeholderText:i18nd("lliurex-guard-natfree","Search...")
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


            PC3.ScrollView{
                anchors.fill:parent

                ListView{
                    id: guardLists

                    Timer {
                        id: searchTimer
                        interval: 150
                        repeat: false
                        onTriggered: filterModel.update()
                    }

                    model:FilterDelegateModel{
                        id:filterModel
                        model:listsModel
                        role:"metaInfo"
                        search:listSearchEntry.text.trim()
                        statusFilter:guardOptionsStackBridge.filterStatusValue 
                        externalTimer: searchTimer

                        delegate: ListDelegateItem{
                            width:listsTable.width-18
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
                        visible: guardLists.count==0?true:false
                        text: listSearchEntry.text.length==0
                              ?i18nd("lliurex-guard-natfree","No list is configured")
                              :i18nd("lliurex-guard-natfree","No list found")
                        icon.name:"lliurex-guard-natfree"
                    }
                } 
             }
        }
    }
}

