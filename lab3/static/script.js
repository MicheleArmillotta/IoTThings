let relationId = 0;

function addRelation() {
    const container = document.getElementById("relations");

    const div = document.createElement("div");
    div.id = `relation-${relationId}`;
    div.innerHTML = `
        Service A: <input name="service_a" required> 
        Relation: 
        <select name="relation">
            <option value="after">after</option>
            <option value="on_value">on_value</option>
        </select> 
        Service B: <input name="service_b" required> 
        Expected Value (only for "on_value"): <input name="expected_value">
        <button type="button" onclick="removeRelation(${relationId})">Remove</button>
        <br><br>
    `;
    container.appendChild(div);
    relationId++;
}

function removeRelation(id) {
    const div = document.getElementById(`relation-${id}`);
    div.remove();
}

document.getElementById("composition-form").addEventListener("submit", function (e) {
    e.preventDefault();
    const relations = [];

    const relationDivs = document.querySelectorAll("[id^=relation-]");
    relationDivs.forEach(div => {
        const inputs = div.querySelectorAll("input, select");
        const obj = {
            service_a: inputs[0].value,
            relation: inputs[1].value,
            service_b: inputs[2].value,
        };
        if (inputs[1].value === "on_value") {
            obj.expected_value = inputs[3].value;
        }
        relations.push(obj);
    });

    const interval = parseInt(document.getElementById("interval").value);

    fetch("/save_composition", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ compositions: relations, interval: interval || null })
    }).then(resp => resp.json())
      .then(data => {
          alert(data.status);
      });
});
