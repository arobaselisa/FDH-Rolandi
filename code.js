var svg = d3.select("svg"),
    width = 1000,
    height = 200;

// svg objects
var link, node, text;
// the data - an object with nodes and links
var graph;
var data = "network_2.json"

// load the data
d3.json(myFunction(), function(error, _graph) {
  if (error) throw error;
  graph = _graph;
  initializeDisplay();
  initializeSimulation();
});

//////////// FORCE SIMULATION ////////////

// force simulator
var simulation = d3.forceSimulation();

// set up the simulation and event to update locations after each tick
function initializeSimulation() {
  simulation.nodes(graph.nodes);
  initializeForces();
  simulation.on("tick", ticked);
}

function loaddata(){
  svg.selectAll("*").remove();  // load the data
  d3.json(myFunction(), function(error, _graph) {
    if (error) throw error;
    graph = _graph;
    initializeDisplay();
    initializeSimulation();
  });
}

// values for all forces
forceProperties = {
    center: {
        x: 0.5,
        y: 2
    },
    charge: {
        strength: -30,
        distanceMin: 1,
        distanceMax: 2000
    },
    collide: {
        strength: .7,
        radius: 5
    },
    forceX: {
        strength: .1,
        x: .5
    },
    forceY: {
        strength: .1,
        y: .5
    },
    link: {
        enabled1: true,
        enabled2: true,
        enabled3: true,
        distance: 300
    }
}

function myFunction() {
  data = document.getElementById("mySelect").value;
  return data;
}

// add forces to the simulation
function initializeForces() {
    // add forces and associate each with a name
    simulation
        .force("link", d3.forceLink())
        .force("charge", d3.forceManyBody())
        .force("collide", d3.forceCollide())
        .force("center", d3.forceCenter())
        .force("forceX", d3.forceX())
        .force("forceY", d3.forceY());
    // apply properties to each of the forces
    updateForces();
}

// apply new force properties
function updateForces() {
    // get each force by name and update the properties
    simulation.force("center")
        .x(width * forceProperties.center.x)
        .y(height * forceProperties.center.y);
    simulation.force("charge")
        .strength(forceProperties.charge.strength)
        .distanceMin(forceProperties.charge.distanceMin)
        .distanceMax(forceProperties.charge.distanceMax);
    simulation.force("collide")
        .strength(forceProperties.collide.strength)
        .radius(forceProperties.collide.radius);
    simulation.force("forceX")
        .strength(forceProperties.forceX.strength)
        .x(width * forceProperties.forceX.x);
    simulation.force("forceY")
        .strength(forceProperties.forceY.strength)
        .y(height * forceProperties.forceY.y);
    simulation.force("link")
        .id(function(d) {return d.id;})
        .distance(forceProperties.link.distance)
        .links(graph.links);

    // updates ignored until this is run
    // restarts the simulation (important if simulation has already slowed down)
    simulation.alpha(1).restart();
}

function linkOpacity(d){
  if(forceProperties.link.enabled1 & d.act1 != 0){
    return 1;
  } else if(forceProperties.link.enabled2 & d.act2 != 0){
		return 1;
	} else if(forceProperties.link.enabled3 & d.act3 != 0){
		return 1;
	} else {
    return 0;
  }
}

function circleRadius(d){
  val = 0
  if(forceProperties.link.enabled1){
    val += d.act1;
  }
  if(forceProperties.link.enabled2){
		val += d.act2;
  }
	if(forceProperties.link.enabled3){
		val += d.act3;
  }
	return val;
}

function linkWidth(d){
  val = 0
  if(forceProperties.link.enabled1){
    val += d.act1;
  }
  if(forceProperties.link.enabled2){
		val += d.act2;
  }
	if(forceProperties.link.enabled3){
		val += d.act3;
  }
  return val/3;
}

//////////// DISPLAY ////////////

// generate the svg objects and force simulation
function initializeDisplay() {
  // set the data and properties of link lines
  link = svg.append("g")
        .attr("class", "links")
    .selectAll("line")
    .data(graph.links)
    .enter().append("line")
    .attr("opacity", linkOpacity)
    .attr("stroke-width", linkWidth);

  // set the data and properties of node circles
  node = svg.append("g")
        .attr("class", "nodes")
    .selectAll("circle")
    .data(graph.nodes)
    .enter().append("circle")
        .attr("r", circleRadius)
        .attr("fill", "blue")
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended));

  text = svg.selectAll(".texts")
        .data(graph.nodes)
        .enter()
        .append("text")
        .text(function(d){ return d.id; })
        .attr("stroke", "black")
        .attr("font-size", "15");
  // node tooltip

  node.append("title")
      .text(function(d) { return d.id; });

  // visualize the graph
  updateDisplay();
}

// update the display based on the forces (but not positions)
function updateDisplay() {
    node
        .attr("r", circleRadius)
        .attr("stroke", "blue")
        .attr("stroke-width", Math.abs(forceProperties.charge.strength)/15);

    link
        .attr("stroke-width", 1)
        .attr("opacity", linkOpacity)
        .attr("stroke-width", linkWidth);
}

// update the display positions after each simulation tick
function ticked() {
    link
        .attr("x1", function(d) { return d.source.x; })
        .attr("y1", function(d) { return d.source.y; })
        .attr("x2", function(d) { return d.target.x; })
        .attr("y2", function(d) { return d.target.y; });

    node
        .attr("cx", function(d) { return d.x; })
        .attr("cy", function(d) { return d.y; });

    text
        .attr("dx", function(d) { return d.x - 4.5; })
        .attr("dy", function(d) { return d.y + 3.5; });

    d3.select('#alpha_value').style('flex-basis', (simulation.alpha()*100) + '%');
}

//////////// UI EVENTS ////////////

// from where node strats to get dragged
function dragstarted(d) {
  if (!d3.event.active) simulation.alphaTarget(0.3).restart();
  d.fx = d.x;
  d.fy = d.y;
}

// dragging node event
function dragged(d) {
  d.fx = d3.event.x;
  d.fy = d3.event.y;
}

// where dragged node stops
function dragended(d) {
  if (!d3.event.active) simulation.alphaTarget(0.0001);
  d.fx = d.x;
  d.fy = d.y;
}

// update size-related forces
d3.select(window).on("resize", function(){
    width = 1000;
    height = 200;
    updateForces();
});

// convenience function to update everything (run after UI input)
function updateAll() {
    updateForces();
    updateDisplay();
    loaddata();
}
