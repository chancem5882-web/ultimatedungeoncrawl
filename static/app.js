async function updateCharacter(id){

const data = {

level: document.getElementById("level").value,

hp: document.getElementById("hp").value,
max_hp: document.getElementById("max_hp").value,

mana: document.getElementById("mana").value,
max_mana: document.getElementById("max_mana").value,

gold: document.getElementById("gold").value,

strength: document.getElementById("strength").value,
dexterity: document.getElementById("dexterity").value,
intelligence: document.getElementById("intelligence").value,
constitution: document.getElementById("constitution").value,
charisma: document.getElementById("charisma").value,

equipment: document.getElementById("equipment").value,
inventory: document.getElementById("inventory").value,
spells: document.getElementById("spells").value,
skills: document.getElementById("skills").value,

}

await fetch(`/update/${id}`,
{
method:"POST",
headers:{
"Content-Type":"application/json"
},
body:JSON.stringify(data)
})
}
