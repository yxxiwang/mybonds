var graph;
var xPadding = 30;
var yPadding = 30;

var data = { values:[
    { X: "1-Month", Y: 1.2 },
    { X: "3-Month", Y: 2.8 },
    { X: "6-Month", Y: 1.8 },
    { X: "1-Year", Y: 3.4 },
    { X: "2-Year", Y: 4.0 },
    { X: "3-Year", Y: 6.13},
    { X: "5-Year", Y: 6.3 },
    { X: "7-Year", Y: 6.45},
    { X: "10-Year", Y:6.54 },
    { X: "20-Year", Y:6.85 },
    { X: "30-Year", Y:6.75 },
]};


// Returns the max Y value in our data list
function getMaxY() {
    var max = 0;
    
    for(var i = 0; i < data.values.length; i ++) {
        if(data.values[i].Y > max) {
            max = data.values[i].Y;
        }
    }
    
    max += 10 - max % 10;
    return max;
}

// Return the x pixel for a graph point
function getXPixel(val) {
    return ((graph.width() - xPadding) / data.values.length) * val + (xPadding * 1.5);
}

// Return the y pixel for a graph point
function getYPixel(val) {
    return graph.height() - (((graph.height() - yPadding) / getMaxY()) * val) - yPadding;
}

$(document).ready(function() {
    graph = $('#graph');
    var c = graph[0].getContext('2d');            
    
    c.lineWidth = 2;
    c.strokeStyle = '#333';
    c.font = 'italic 8pt sans-serif';
    c.textAlign = "center";
    
    // Draw the axises
    c.beginPath();
    c.moveTo(xPadding, 0);
    c.lineTo(xPadding, graph.height() - yPadding);
    c.lineTo(graph.width(), graph.height() - yPadding);
    c.stroke();
    
    // Draw the X value texts
    for(var i = 0; i < data.values.length; i ++) {
        c.fillText(data.values[i].X, getXPixel(i), graph.height() - yPadding + 20);
    }
    
    // Draw the Y value texts
    c.textAlign = "right"
    c.textBaseline = "middle";
    
    for(var i = 0; i < getMaxY(); i += 10) {
        c.fillText(i, xPadding - 10, getYPixel(i));
    }
    
    c.strokeStyle = '#f00';
    
    // Draw the line graph
    c.beginPath();
    c.moveTo(getXPixel(0), getYPixel(data.values[0].Y));
    for(var i = 1; i < data.values.length; i ++) {
        c.lineTo(getXPixel(i), getYPixel(data.values[i].Y));
    }
    c.stroke();
    
    // Draw the dots
    c.fillStyle = '#333';
    
    for(var i = 0; i < data.values.length; i ++) {  
        c.beginPath();
        c.arc(getXPixel(i), getYPixel(data.values[i].Y), 4, 0, Math.PI * 2, true);
        c.fill();
    }
});