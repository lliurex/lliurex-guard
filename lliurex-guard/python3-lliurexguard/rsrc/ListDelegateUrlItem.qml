import org.kde.plasma.components 2.0 as Components
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQml.Models 2.8

Components.ListItem{

    id: listItem
    property int urlId
    property string url

    enabled:true

    onContainsMouseChanged: {
        if (!manageUrlBtn.activeFocus){
            if (containsMouse) {
                urlList.currentIndex = index
            }else {
                urlList.currentIndex = -1
            }
        }

    }

    Rectangle {
        height:visible?35:0
        width:parent.width
        color:"transparent"
        border.color: "transparent"
        Item{
            id: menuItem
            height:visible?30:0
            width:listItem.width-manageUrlBtn.width
            
            Text{
                id:urlText
                text:url
                font.pointSize: 10
                width:{
                    if (listItem.ListView.isCurrentItem){
                        parent.width-(manageUrlBtn.width+20)
                    }else{
                        parent.width-20
                    }
                }
                anchors.verticalCenter:parent.verticalCenter
                anchors.leftMargin:30
                elide:Text.ElideMiddle

            }
            
            Button{
                id:manageUrlBtn
                display:AbstractButton.IconOnly
                icon.name:"delete.svg"
                anchors.leftMargin:15
                anchors.left:urlText.right
                anchors.verticalCenter:parent.verticalCenter
                visible:listItem.ListView.isCurrentItem
                ToolTip.delay: 1000
                ToolTip.timeout: 3000
                ToolTip.visible: hovered
                ToolTip.text:i18nd("lliurex-guard","Click to delete this url")
          
            }
        }
    }
}
