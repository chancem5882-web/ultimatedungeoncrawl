let cid = window.location.pathname.split("/").pop();
let socket = io();

socket.emit("join",{cid});

function save(){
fetch("/save/"+cid,{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({
equipment:document.getElementById("equipment").innerText
})
});
}

function roll(){
socket.emit("roll",{cid});
}

socket.on("roll_result",(d)=>{
alert("Rolled: " + d.value);
});
