async function fetchSetup() {
    let url="http://localhost:8888/setup";
    const response = await fetch(url);
    const json = await response.json();
    return json;
}

async function fetchSnapshot(getNext, layerVisibility) {
    let url=`http://localhost:8888/snapshot`;
    url = addParameter(url, "next_snapshot", getNext);
    url = addParameter(url, "visible_vehicles", filterVisibleLayers(layerVisibility));
    const response = await fetch(url);
    const json = await response.json();
    return json;
}

async function fetchNodeInfo(node_id, layerVisibility) 
{
    let url = "http://localhost:8888/node";
    url = addParameter(url, "node_id", node_id);
    url = addParameter(url, "visible_vehicles", filterVisibleLayers(layerVisibility));
    const response = await fetch(url);
    const json = await response.json();
    return json;
}

async function fetchLinkInfo(link_id, layerVisibility) {
    let url = "http://localhost:8888/link";
    url = addParameter(url, "link_id", link_id);
    url = addParameter(url, "visible_vehicles", filterVisibleLayers(layerVisibility));
    const response = await fetch(url);
    const json = await response.json();
    return json;
}

function filterVisibleLayers(layerVisibility) {
    return Object.keys(layerVisibility).filter(key => layerVisibility[key]); // convert a map from layer name to visibility flag to a list of all visible layers
}

function addParameter(url, name, value) {
    
    const params = new URLSearchParams();
    params.append(name, JSON.stringify(value));
    const separator = url.includes("?") ? "&" : "?";
    return `${url}${separator}${params.toString()}`;
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

