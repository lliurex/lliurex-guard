import org.kde.plasma.components 2.0 as Components
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQml.Models 2.8

Components.ListItem{

    id: listItem
    property int listOrder
    property string listId
    property string listName
    property int listEntries
    property string listDescription
    property bool listActivated
    property bool listDelete
    property string metaInfo

    enabled:true

    onContainsMouseChanged: {
        if (!optionsMenu.activeFocus){
            if (containsMouse) {
                guardLists.currentIndex = index
            }else {
                guardLists.currentIndex = -1
            }
        }

    }

    Rectangle {
        height:visible?60:0
        width:parent.width
        color:{
            if (listDelete){
                "#a9a9a9"
            }else{
                "transparent"
            }
        }
        border.color: "transparent"
        Item{
            id: menuItem
            height:visible?60:0
            width:listItem.width-manageListBtn.width
            
            Column{
                id:description
                anchors.verticalCenter:parent.verticalCenter
                anchors.leftMargin:5
                spacing:10
                width:{
                    if (listItem.ListView.isCurrentItem){
                        parent.width-(entriesText.width+listState.width+manageListBtn.width+15)
                    }else{
                        parent.width-(entriesText.width+listState.width+15)
                    }
                }
               
                Text{
                    id:nameText
                    text:listName
                    font.family: "Quattrocento Sans Bold"
                    font.pointSize: 14
                    horizontalAlignment:Text.AlignLeft
                    elide:Text.ElideMiddle
                    width:parent.width
                }

                Text{
                    id:descriptionText
                    text:listDescription
                    font.family:"Quattrocento Sans Bold"
                    font.pointSize: 11
                    horizontalAlignment:Text.AlignLeft
                    elide:Text.ElideMiddle
                    width:parent.width
                }

            }

            Text{
                id:entriesText
                text:listEntries+" "+i18nd("lliurex-guard","entries")
                font.family:"Quattrocento Sans Bold"
                font.pointSize: 14
                width:50
                anchors.left:description.right
                anchors.verticalCenter:parent.verticalCenter
                anchors.leftMargin:30
            }

            Image{
                id:listState
                source:listActivated?"/usr/share/icons/breeze/status/24/security-high.svg":"/usr/share/icons/breeze/status/24/security-low.svg"
                sourceSize.width:32
                sourceSize.height:32
                anchors.left:entriesText.right
                anchors.verticalCenter:parent.verticalCenter
                anchors.leftMargin:30
            }
            
            Button{
                id:manageListBtn
                display:AbstractButton.IconOnly
                icon.name:"configure.svg"
                anchors.leftMargin:15
                anchors.left:listState.right
                anchors.verticalCenter:parent.verticalCenter
                visible:listItem.ListView.isCurrentItem
                ToolTip.delay: 1000
                ToolTip.timeout: 3000
                ToolTip.visible: hovered
                ToolTip.text:i18nd("lliurex-guard","Click to manage this list")
                onClicked:optionsMenu.open();
                onVisibleChanged:{
                    optionsMenu.close()
                }

                Menu{
                    id:optionsMenu
                    y: manageListBtn.height
                    x:-(optionsMenu.width-manageListBtn.width/2)

                    MenuItem{
                        icon.name:listActivated?"security-low.svg":"security-high.svg"
                        text:listActivated?i18nd("lliurex-guard","Disable list"):i18nd("lliurex-guard","Enable list")
                        enabled:listDelete?false:true
                        onClicked:guardOptionsStackBridge.changeListStatus([false,!listActivated,listOrder])
                    }

                    MenuItem{
                        icon.name:"document-edit.svg"
                        text:i18nd("lliurex-guard","Edit list")
                        onClicked:listStackBridge.loadList(listOrder)
                    }
                    MenuItem{
                        icon.name:listDelete?"restoration.svg":"delete.svg"
                        text:listDelete?i18nd("lliurex-guard","Restore the list"):i18nd("lliurex-guard","Delete the list")
                        onClicked:listDelete?guardOptionsStackBridge.restoreList(listOrder):guardOptionsStackBridge.restoreList([false,listOrder])
                    }
                }
            }
        }
    }
}
