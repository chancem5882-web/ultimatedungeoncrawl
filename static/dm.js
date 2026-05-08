const socket = io();

function sendAnnouncement(cid,msg,type){
socket.emit("message",{
cid,
msg,
type,
sender:"Dungeon AI"
});
}

function applyEffect(cid,name,duration,payload){
socket.emit("apply_effect",{
cid,
name,
duration,
payload
});
}

function rollAll(){
socket.emit("roll_all",{});
}
