import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15


RowLayout{
    id: listGrid
    spacing:10

    ColumnLayout{
        Layout.fillHeight:true
        spacing:5

        MenuOptionBtn {
            id:goBackBtn
            optionText:i18nd("lliurex-guard-natfree","Home")
            optionPointSize:14
            optionIcon:"actions/24/arrow-left.svg"
            enabled:listStackBridge.enableForm
            Connections{
                function onMenuOptionClicked(){
                    listStackBridge.goHome();
                    closeTimer.stop()
                }
            }
        }  
        Rectangle{
            width:130
            Layout.fillHeight:true
            border.color: palette.mid
            ColumnLayout{
               anchors.fill:parent
               spacing:0

                MenuOptionBtn {
                    id:infoItem
                    optionText:i18nd("lliurex-guard-natfree","List")
                    optionIcon:"actions/22/view-list-details.svg"
                 }

                 Item{
                    Layout.fillHeight:true
                 }

            }
        }
    }

    StackView {
        id: manageView
        Layout.fillWidth:true
        Layout.fillHeight: true
        
        property int currentOption:listStackBridge.listCurrentOption

        initialItem:listView

        onCurrentOptionChanged:{
            switch(currentOption){
                case 0:
                    manageView.replace(emptyView)
                case 1:
                    manageView.replace(listView)
            }

        }

        replaceEnter: Transition {
            PropertyAnimation {
                property: "opacity"
                from: 0
                to:1
                duration: 60
            }
        }
        replaceExit: Transition {
            PropertyAnimation {
                property: "opacity"
                from: 1
                to:0
                duration: 60
            }
        }
        
        Component{
            id:emptyView
            Item{
                id:emptyPanel
            }
        }
        
        Component{
            id:listView
            ListForm{
                id:listForm
            }
        }
        
    }
}

