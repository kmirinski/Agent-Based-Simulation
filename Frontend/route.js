cities = {
    "Amsterdam" : [4.9041, 52.3676],
    "Brussel": [4.3572, 50.8477],
    "Eindhoven": [5.4623, 51.4231]
}

async function fetchRoute(origin, destination) {
    const url = `http://router.project-osrm.org/route/v1/driving/${origin[0]},${origin[1]};${destination[0]},${destination[1]}?geometries=geojson&overview=full`;
    const response = await fetch(url);
    const json = await response.json();
    return json['routes'][0]['geometry'];
}

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

function interpolateColor(intensity, M=2) {
    // M should be the max resources going through one edge
    let rho = intensity / M;
    rho = Math.min(rho,1); //cap at rho=1
    rho = Math.floor(rho * 255) // map to range [0,255]
    let r = rho;
    let g = 255 - rho;
    let color = `rgb(${r}, ${g}, 0)`;
    return color;
}

function edgeToPaths(paths) {
    //convert the paths to the a table from edges to paths they are on
   console.log(paths);
    edgeMap = new Map()
    for (let i = 0; i < paths.length; i++) {
        for (j = 0; j < paths[i].length; j++) {
            for (let k = 0; k < paths[i][j].length - 1; k++) {
                let key = JSON.stringify([paths[i][j][k], paths[i][j][k+1]]);
                let ods = edgeMap.get(key) || []; // origin/destinations as index pairs
                ods.push([i,j]);
                //console.log(ods.length);
                edgeMap.set(key, ods)
            }
        }
    }
    
    return edgeMap
}

class HtmlTable {
    constructor() {
        this.html = "<table><tr>";
        for (let arg of arguments) {
            this.html += `<td>${arg}</td>`;
        }
        this.html += "</tr>";
    }
    addRow() {
        this.html += "<tr>";
        for (let arg of arguments) {
            this.html += `<td>${arg}</td>`;
        }
        this.html += "</tr>";
    }
    toHtml() {
        return this.html + "</table>";
    }

}
class Node {
    constructor(coordinates = [0, 0], resources = new Map()) {
        if (coordinates.length !== 2) {
            throw new Error("Coordinates must be an array of size 2");
        }

        this.coordinates = coordinates;
        this.resources = resources; 
    }

    // Method to add a resource with integer validation
    addResource(resourceName, amount) {
        if (!Number.isInteger(amount)) {
            throw new Error("Amount must be an integer");
        }
        this.resources.set(resourceName, amount);
    }

    // Method to get a resource amount
    getResource(resourceName) {
        return this.resources.get(resourceName) || 0;
    }
}

class Link {
    constructor(origin=[0,0], destination=[1,1], intensity=0) {
        if (origin.length !== 2 || destination.length !== 2) {
            throw new Error("Coordinates must be an array of size 2");
        }

        this.intensity = intensity; 
        this.polyline = [origin, destination];
    }

    intensityColor(s=0.5, l=0.5, intensity_max = 100) {
        const h = -(this.intensity/intensity_max * 180) + 180 //max is red min is cyan
        const a = s * Math.min(l, 1 - l);
        const f = n => {
          const k = (n + h / 30) % 12;
          const color = l - a * Math.max(Math.min(k - 3, 9 - k, 1), -1);
          return Math.round(255 * color).toString(16).padStart(2, '0');   // convert to Hex and prefix "0" if needed
        };
        return `#${f(0)}${f(8)}${f(4)}`;
    }

   
}

function routeToPath(route) {
    //route json to array of links
    links = []
    for (let i = 0; i < route['coordinates'].length; i++) {
        // lon, lat format
        route['coordinates'][i].reverse()
    }

    for (let i = 0; i < route['coordinates'].length - 1; i++) {
        let start = route['coordinates'][i];
        let end = route['coordinates'][i+1];
        intensity = Math.floor(Math.random() * 100); //rand int less than 100
        links.push(new Link(start, end, intensity));
    }
    return links;
}

function combinePaths(paths) {
    // Takes an array of paths and combines their intensities
    let intensityMax = 0;
    let combinedIntensity = new Map();

    for (const path of paths) { // Use for..of for better readability
        for (const link of path) { // Iterate through each link in the path
            const key = link.polyline; // Get a string representation of the link (if applicable)
            
            // Update the intensity in the map
            const currentIntensity = combinedIntensity.get(key) || 0;
            
            combinedIntensity.set(key, currentIntensity + link.intensity);

            // Update the maximum intensity
            intensityMax = Math.max(intensityMax, combinedIntensity.get(key));
        }
    }

    let resultArray = [];
    for (let [key, value] of combinedIntensity) {
 
        resultArray.push(new Link(origin=key[0], destination=key[1], intensity=value));
    }
    
    return {links: resultArray, intensity_max: intensityMax }; // Return the array of Link objects and the maximum intensity
}

