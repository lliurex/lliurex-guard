import org.kde.plasma.components as Components
import QtQuick
import QtQuick.Controls
import QtQml.Models

Components.ItemDelegate{

    id: listUrlItem
    property int urlId
    property string url

    enabled:true
    height:40

    Rectangle {
        height:visible?35:0
        width:parent.width
        color:"transparent"
        border.color: "transparent"
        Item{
            id: menuItem
            height:visible?35:0
            width:listUrlItem.width-manageUrlBtn.width

            MouseArea {
                id: mouseAreaOption
                anchors.fill: parent
                hoverEnabled:true
                propagateComposedEvents:true

                onEntered: {
                    if (!optionsUrlMenu.activeFocus){
                        urlList.currentIndex=filterModel.visibleElements.indexOf(index)
                    }
                }
            }

            Text{
                id:urlText
                text:url
                font.pointSize: 10
                width:{
                    if (listUrlItem.ListView.isCurrentItem){
                        parent.width-(manageUrlBtn.width+20)
                    }else{
                        parent.width-20
                    }
                }
                anchors.verticalCenter:parent.verticalCenter
                leftPadding:10

                elide:Text.ElideMiddle

            }
            
            Button{
                id:manageUrlBtn
                display:AbstractButton.IconOnly
                icon.name:"configure.svg"
                anchors.leftMargin:15
                anchors.left:urlText.right
                anchors.verticalCenter:parent.verticalCenter
                visible:listUrlItem.ListView.isCurrentItem
                ToolTip.delay: 1000
                ToolTip.timeout: 3000
                ToolTip.visible: hovered
                ToolTip.text:i18nd("lliurex-guard","Click to manage this url")
                onClicked:{
                    optionsUrlMenu.open();
                    listStackBridge.cancelUrlEdition()
                    manageEntryRow(false)
                }
                onVisibleChanged:{
                    optionsUrlMenu.close()
                }

                Menu{
                    id:optionsUrlMenu
                    y: manageUrlBtn.height
                    x:-(optionsUrlMenu.width-manageUrlBtn.width/2)

                   MenuItem{
                        icon.name:"document-edit.svg"
                        text:i18nd("lliurex-guard","Edit url")
                        onClicked:{
                            listStackBridge.manageEditUrlBtn([index,urlText.text])
                            manageEntryRow(true)
                            urlEntry.forceActiveFocus()
                            urlEntry.text=urlText.text
                        }
                    }
                    MenuItem{
                        icon.name:"delete.svg"
                        text:i18nd("lliurex-guard","Delete the url")
                        onClicked:listStackBridge.removeUrl(index)
          
                    }
                }
          
            }
        }
    }
}
