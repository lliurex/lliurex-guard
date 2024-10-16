import QtQuick
import Edupals.N4D.Agent 1.0 as N4DAgent


Rectangle {
    width:  childrenRect.width+5
    height:  childrenRect.height+5
    anchors.centerIn: parent
    color: "#e9e9e9"

    N4DAgent.Login
    {
        showAddress:!tunnel.standAlone
        address:!showAddress?'localhost':'server'
        showCancel: false
        inGroups:["sudo","admins","teachers"]
        
        /*anchors.centerIn: parent*/
        
        onLogged:(ticket)=> {
            tunnel.on_ticket(ticket);
        }
        onAuthenticated: (passwd)=>{
            tunnel.on_authenticated(passwd);
        }
    }
}
