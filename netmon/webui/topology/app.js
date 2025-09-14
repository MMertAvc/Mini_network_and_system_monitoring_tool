async function loadTopo(){
  const r = await fetch("/topology");
  const topo = await r.json();
  const width=960, height=600;
  const svg = d3.select("#graph").append("svg")
      .attr("width", width).attr("height", height);

  const sim = d3.forceSimulation(topo.nodes)
    .force("link", d3.forceLink(topo.links).id(d=>d.id).distance(120))
    .force("charge", d3.forceManyBody().strength(-400))
    .force("center", d3.forceCenter(width/2, height/2));

  const link = svg.append("g").selectAll("line")
    .data(topo.links).enter().append("line").attr("stroke","#999");

  const color = (d)=> ({router:"#2b8cbe",switch:"#31a354",server:"#756bb1",firewall:"#e34a33"}[d.dtype] || "#636363");

  const node = svg.append("g").selectAll("circle")
    .data(topo.nodes).enter().append("circle")
    .attr("r", 12).attr("fill", d=>color(d))
    .call(d3.drag()
      .on("start", (event,d)=>{ if (!event.active) sim.alphaTarget(0.3).restart(); d.fx=d.x; d.fy=d.y; })
      .on("drag", (event,d)=>{ d.fx=event.x; d.fy=event.y; })
      .on("end", (event,d)=>{ if (!event.active) sim.alphaTarget(0); d.fx=null; d.fy=null; }));

  const label = svg.append("g").selectAll("text")
    .data(topo.nodes).enter().append("text")
    .text(d=>d.name).attr("font-size","10px").attr("dx",14).attr("dy",4);

  sim.on("tick", ()=>{
    link.attr("x1",d=>d.source.x).attr("y1",d=>d.source.y)
        .attr("x2",d=>d.target.x).attr("y2",d=>d.target.y);
    node.attr("cx",d=>d.x).attr("cy",d=>d.y);
    label.attr("x",d=>d.x).attr("y",d=>d.y);
  });
}
loadTopo();