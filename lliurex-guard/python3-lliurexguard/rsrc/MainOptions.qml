import QtQuick
import QtQuick.Controls
import QtQuick.Layouts


RowLayout{
    id: mainGrid
    spacing:10

    Rectangle{
        width:130
        Layout.fillHeight:true
        border.color: "#d3d3d3"

        ColumnLayout{
            id: menuGrid
            Layout.fillWidth:true
            Layout.fillHeight:true
            spacing:0

            MenuOptionBtn {
                id:listItem
                Layout.fillWidth:true
                optionText:i18nd("lliurex-guard","Configuration")
                optionIcon:"security-high"
                onMenuOptionClicked:mainStackBridge.moveToMainOptions(0)
            }

            MenuOptionBtn {
                id:helpItem
                Layout.fillWidth:true
                optionText:i18nd("lliurex-guard","Help")
                optionIcon:"help-contents"
                onMenuOptionClicked:mainStackBridge.openHelp();
            }
        }
    }

    StackView {
        id: optionsView
        Layout.fillWidth:true
        Layout.fillHeight:true

        property int currentIndex:mainStackBridge.mainCurrentOption
      
        initialItem:guardView

        onCurrentIndexChanged:{
            switch(currentIndex){
                case 0:
                    optionsView.replace(guardView)
                    break;
            }
         }
        replaceEnter: Transition {
            NumberAnimation {
                property: "opacity"
                from: 0
                to: 1
                duration: 60
            }
        }
        replaceExit: Transition {
            NumberAnimation {
                property: "opacity"
                from: 1
                to: 0
                duration: 60
            }
        }

        Component{
            id:guardView
            GuardManager{
                id:guardManager
            }
        }
     
    }
}

