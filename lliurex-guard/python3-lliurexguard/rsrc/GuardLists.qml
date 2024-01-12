import org.kde.plasma.components 3.0 as PC3
import org.kde.kirigami 2.16 as Kirigami
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQml.Models 2.8
import QtQuick.Layouts 1.15


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

        PC3.TextField{
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

        Rectangle {

            id:listsTable
            visible: true
            Layout.fillHeight:true
            Layout.fillWidth:true
            color:"white"
            border.color: "#d3d3d3"


            PC3.ScrollView{
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
                        width: parent.width - (units.largeSpacing * 4)
                        visible: guardLists.count==0?true:false
                        text: i18nd("lliurex-guard","No list is configured")
                    }
                } 
             }
        }
    }
}

