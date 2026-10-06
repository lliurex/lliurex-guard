import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQml.Models 2.8
import QtQuick.Layouts 1.15
import org.kde.kirigami 2.16 as Kirigami


ItemDelegate{
    id: listUrlItem
    property int urlId
    property string url

    enabled:true
    height:45
    width: listUrlItem.ListView.view?listUrlItem.ListView.width-10:0
    hoverEnabled:true

    leftPadding:10
    rightPadding:10

    onHoveredChanged:{
        if (listUrlItem.ListView.view){
            if (hovered && !optionsUrlMenu.opened){
                listUrlItem.ListView.currentIndex=index
            }
        }else if (!hovered && !optionsUrlMenu.opened && listUrlItem.ListView.view.currentIndex===index){
            listUrlItem.ListView.view.currentIndex=-1
        }

    }

    background: Rectangle {
        x:5
        y:5
        width:parent.width-5
        height:parent.height-5
        color:{
           if (listUrlItem.hovered || optionsUrlMenu.opened){
                Qt.hsla(Kirigami.Theme.highlightColor.hslHue, 
                Kirigami.Theme.highlightColor.hslSaturation, 
                Kirigami.Theme.highlightColor.hslLightness, 
                0.15)
            }else{
                "transparent"
            }
        }

        radius:6
        border.width:1
        border.color:{
            if (listUrlItem.hovered || optionsUrlMenu.opened){
                Kirigami.Theme.highlightColor
            }else{            
                "transparent"
            }
        }
    }

    contentItem:RowLayout {
        id: menuItem
        spacing:20
            
        Text{
            id:urlText
            text:url
            font.pointSize: 10
            Layout.fillWidth:true
            Layout.alignment:Qt.AlignVCenter
            elide:Text.ElideMiddle

        }
            
        Button{
            id:manageUrlBtn
            display:AbstractButton.IconOnly
            icon.name:"configure"
            Layout.alignment: Qt.AlignVCenter
            visible:listUrlItem.hovered || optionsUrlMenu.opened
            ToolTip.delay: 1000
            ToolTip.timeout: 3000
            ToolTip.visible: hovered
            ToolTip.text:i18nd("lliurex-guard-natfree","Click to manage this url")
            
            onClicked:{
                optionsUrlMenu.open();
                listStackBridge.cancelUrlEdition()
                manageEntryRow(false)
            }

            Connections{
                target:urlList
                function onCurrentIndexChanged(){
                    if (!listUrlItem.ListView.isCurrentItem && optionsUrlMenu.opened){
                        optionsUrlMenu.close()
                    }
                }
            }

            Menu{
                id:optionsUrlMenu
                y: manageUrlBtn.height
                x:-(optionsUrlMenu.width-manageUrlBtn.width/2)

               MenuItem{
                    icon.name:"document-edit"
                    text:i18nd("lliurex-guard-natfree","Edit url")
                    onClicked:{
                        listStackBridge.manageEditUrlBtn({"urlIndex":index,"urlValue":urlText.text})
                        manageEntryRow(true)
                        urlEntry.forceActiveFocus()
                        urlEntry.text=urlText.text
                    }
                }

                MenuItem{
                    icon.name:"delete"
                    text:i18nd("lliurex-guard-natfree","Delete the url")
                    onClicked:listStackBridge.removeUrl(index)
                }
          
            }
        }
    }
}
