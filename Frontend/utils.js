async function fetchSetup(url="http://localhost:8888/setup") {
    const response = await fetch(url);
    const json = await response.json();
    return json;
}

async function fetchSnapshot(url="http://localhost:8888/snapshot") {
    const response = await fetch(url);
    const json = await response.json();
    return json;
}

async function fetchNodeInfo(node_id, url = "http://localhost:8888/node") {
    const response = await fetch(`${url}?node_id=${node_id}`);
    const json = await response.json();
    return json;
}

async function fetchLinkInfo(link_id, url = "http://localhost:8888/link") {
    const response = await fetch(`${url}?link_id=${link_id}`);
    const json = await response.json();
    return json;
}


function interpolateColor(intensity, M=200) {
    // M should be the max resources going through one edge
    let rho = intensity / M;
    rho = Math.min(rho,1); //cap at rho=1
    rho = Math.floor(rho * 255) // map to range [0,255]
    let r = rho;
    let g = 255 - rho;
    let color = `rgb(${r}, ${g}, 0)`;
    return color;
}

class HtmlTable {
    constructor() {
        this.html = "<table><tr>";
        for (let col_name of arguments) { // supports arbitrary number of columns
            this.html += `<td>${col_name}</td>`;
        }
        this.html += "</tr>";
    }
    addRow() {
        this.html += "<tr>";
        for (let col_val of arguments) {
            this.html += `<td>${col_val}</td>`;
        }
        this.html += "</tr>";
    }
    toHtml() {
        return this.html + "</table>";
    }

}

