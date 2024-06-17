import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15


GridLayout{
    id: listGrid
    columns: 2
    flow: GridLayout.LeftToRight
    columnSpacing:10

    GridLayout{
        rows:2
        flow: GridLayout.TopToBottom

        MenuOptionBtn {
            id:goBackBtn
            optionText:i18nd("lliurex-guard","Home")
            optionFontSize:14
            optionIcon:"/usr/share/icons/breeze/actions/24/arrow-left.svg"
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
            Layout.minimumHeight:475
            Layout.fillHeight:true
            border.color: "#d3d3d3"
            GridLayout{
                id: menuGrid
                rows:1 
                flow: GridLayout.TopToBottom
                rowSpacing:0

                MenuOptionBtn {
                    id:infoItem
                    optionText:i18nd("lliurex-guard","List")
                    optionIcon:"/usr/share/icons/breeze/actions/22/view-list-details.svg"
                 }

            }
        }
    }

    StackView {
        id: manageView
        property int currentOption:listStackBridge.listCurrentOption
        Layout.fillWidth:true
        Layout.fillHeight: true
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
                duration: 600
            }
        }
        replaceExit: Transition {
            PropertyAnimation {
                property: "opacity"
                from: 1
                to:0
                duration: 600
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

