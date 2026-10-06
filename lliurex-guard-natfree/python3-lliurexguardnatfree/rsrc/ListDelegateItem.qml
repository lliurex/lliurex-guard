import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQml.Models 2.8
import QtQuick.Layouts 1.15
import org.kde.kirigami 2.16 as Kirigami

ItemDelegate{

    id: listFilterItem
    property int listOrder
    property string listId
    property string listName
    property int listEntries
    property string listDescription
    property bool listActivated
    property bool listRemove
    property string metaInfo

    enabled:true
    height:80
    width: listFilterItem.ListView.view?listFilterItem.ListView.width-10:0
    hoverEnabled:true

    leftPadding:15
    rightPadding:10

    onHoveredChanged:{
        if (listFilterItem.ListView.view){
            if (hovered && !optionsMenu.opened){
                listFilterItem.ListView.currentIndex=index
            }
        }else if (!hovered && !optionsMenu.opened && listFilterItem.ListView.view.currentIndex===index){
            listFilterItem.ListView.view.currentIndex=-1
        }

    }

    background: Rectangle {
        x:5
        y:5
        width:parent.width-5
        height:parent.height-5

        color:{
            if (listRemove){
                Qt.hsla(Kirigami.Theme.disabledTextColor.hslHue, 
                    Kirigami.Theme.disabledTextColor.hslSaturation, 
                    Kirigami.Theme.disabledTextColor.hslLightness, 
                    0.45)
            }else{
                if (listFilterItem.hovered || optionsMenu.opened){
                    Qt.hsla(Kirigami.Theme.highlightColor.hslHue, 
                    Kirigami.Theme.highlightColor.hslSaturation, 
                    Kirigami.Theme.highlightColor.hslLightness, 
                    0.15)
                }else{
                    "transparent"
                }
            }
        }

        radius:6
        border.width:1
        border.color:{
            if (listFilterItem.hovered || optionsMenu.opened){
                if (listRemove){
                    Kirigami.Theme.disabledTextColor
                }else{
                    Kirigami.Theme.highlightColor
                }
            }else{            
                "transparent"
            }
        }
    }

    contentItem:RowLayout {
        id: filtertem
        spacing:20

        ColumnLayout{
            id:description
            spacing:10
            Layout.fillWidth:true
            Layout.alignment:Qt.AlignVCenter
            Layout.preferredWidth:300

            Text{
                id:nameText
                text:listName
                font.pointSize: 12
                horizontalAlignment:Text.AlignLeft
                elide:Text.ElideMiddle
                Layout.fillWidth:true
            }

            Text{
                id:descriptionText
                text:listDescription
                font.pointSize: 10
                horizontalAlignment:Text.AlignLeft
                elide:Text.ElideMiddle
                Layout.fillWidth:true
            }

        }

        Text{
            id:entriesText
            text:listEntries+" "+i18nd("lliurex-guard-natfree","entries")
            font.pointSize: 12
            Layout.alignment:Qt.AlignVCenter
            Layout.fillWidth:true
            Layout.preferredWidth:190
        }

        Kirigami.Icon{
            id:listState
            source:listActivated?"security-high":"security-low"
            Layout.preferredWidth: 32
            Layout.preferredHeight: 32
            Layout.alignment: Qt.AlignVCenter

        }

        Button{
            id:manageListBtn
            display:AbstractButton.IconOnly
            icon.name:"configure"
            Layout.alignment: Qt.AlignVCenter
            visible:listFilterItem.hovered || optionsMenu.opened
            ToolTip.delay: 1000
            ToolTip.timeout: 3000
            ToolTip.visible: hovered
            ToolTip.text:i18nd("lliurex-guard-natfree","Click to manage this list")
            onClicked:optionsMenu.open()

            Connections{
                target:guardLists
                function onCurrentIndexChanged(){
                    if (!listFilterItem.ListView.isCurrentItem && optionsMenu.opened){
                        optionsMenu.close()
                    }
                }
            }

            Menu{
                id:optionsMenu
                y: manageListBtn.height
                x:-(optionsMenu.width-manageListBtn.width/2)

                MenuItem{
                    icon.name:listActivated?"lliurex-guard-disable-mode":"security-high"
                    text:listActivated?i18nd("lliurex-guard-natfree","Disable list"):i18nd("lliurex-guard-natfree","Enable list")
                    enabled:listRemove?false:true
                    onClicked:guardOptionsStackBridge.changeListStatus({"allLists":false,"active":!listActivated,"listId":listOrder})
                }

                MenuItem{
                    icon.name:"document-edit.svg"
                    text:i18nd("lliurex-guard-natfree","Edit list")
                    enabled:listRemove?false:true
                    onClicked:listStackBridge.loadList(listOrder)
                }
                
                MenuItem{
                    icon.name:listRemove?"restoration":"delete"
                    text:listRemove?i18nd("lliurex-guard-natfree","Restore the list"):i18nd("lliurex-guard-natfree","Delete the list")
                    onClicked:listRemove?guardOptionsStackBridge.restoreLists({"allLists":false,"listId":listOrder}):guardOptionsStackBridge.removeLists({"allLists":false,"listId":listOrder})
                }
            }
        }
    }
}