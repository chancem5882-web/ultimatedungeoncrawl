const socket = io();

socket.on("character_updated", ()=>{
location.reload();
});

socket.on("new_message", ()=>{
location.reload();
});

socket.on("effect_added", ()=>{
location.reload();
})
