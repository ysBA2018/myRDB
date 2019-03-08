(function(){
$(document).ready(function(){
    var svgDeletionIndex = window.iAcceptedDelete;
    var svg, margin, diameter, g;

    svg = d3.select("#acceptedDeletionSVG"+svgDeletionIndex),
    margin = 20,
    diameter = +svg.attr("width"),
    g = svg.append("g").attr("transform", "translate(" + diameter / 2 + "," + diameter / 2 + ")");


    var div = d3.select("body").append("div")
          .attr("class","tooltip")
          .attr("id","CPtooltip")
          .style("opacity",0);


    var pack = d3.pack()
        .size([diameter - margin, diameter - margin])
        .padding(2);

    var root = window['jsondata_accepted_delete'+svgDeletionIndex];
    if(root == null){
        root = {'name':'doesnt exist','size' : 2000}
    }
    console.log(root);
        window.iAcceptedDelete=window.iAcceptedDelete+1;
      root = d3.hierarchy(root)
          .sum(function(d) { return d.size; })
          .sort(function(a, b) { return b.value - a.value; });

      var focus = root,
          nodes = pack(root).descendants(),
          view;


      function get_color(d) {
           if(d.data.name === "doesnt exist" && d.depth ===0){return d3.hsl(141,0.71,0.48)}
          if(!d.hasOwnProperty('children')){return d.data.color}
          else{return "white"}
      }

      var circle = g.selectAll("circle")
        .data(nodes)
        .enter().append("circle")
          .attr("class", function(d) { return d.parent ? d.children ? "node" : "node node--leaf" : "node node--root"; })
          .style("stroke","grey")
          .style("fill", function(d) { return get_color(d) })
          .on("click", function(d) { if (focus !== d) zoom(d), d3.event.stopPropagation(); })
          .on("mouseover",function (d) {
              d3.select(this).style("stroke","black");
              div.transition()
                  .duration(200)
                  .style("opacity",9);
              div .html(d.data.name+"<br/>")
                  .style("left",(d3.event.pageX)+"px")
                  .style("top",(d3.event.pageY-28)+"px")
          })
          .on("mouseout",function (d) {
              d3.select(this).style("stroke","grey");
              div.transition()
                  .duration(500)
                  .style("opacity",0)
          });

      var leaves = d3.selectAll("circle").filter(function(d){
        return d.children === null;
      });

      var text = g.selectAll("text")
        .data(nodes)
        .enter().append("text")
          .attr("class", "label")
          .style("fill-opacity", function(d) {return d ;})
          .style("display", function(d) {  return d ;})
          .text(function(d) { if(d.data.name==="doesnt exist" && d.depth ===0) return "Berechtigung wurde erfolgreich gelöscht!"; });
      var node = g.selectAll("circle,text");

      svg
          .style("background", "white")
          .on("click", function() { zoom(root); });

      zoomTo([root.x, root.y, root.r * 2 + margin]);

      function zoom(d) {
          if(!d.hasOwnProperty('children')){return;}
        var focus0 = focus; focus = d;

        var transition = d3.transition()
            .duration(d3.event.altKey ? 7500 : 750)
            .tween("zoom", function(d) {
              var i = d3.interpolateZoom(view, [focus.x, focus.y, focus.r * 2 + margin]);
              return function(t) { zoomTo(i(t)); };
            });

      }

      function zoomTo(v) {
        var k = diameter / v[2]; view = v;
        node.attr("transform", function(d) { return "translate(" + (d.x - v[0]) * k + "," + (d.y - v[1]) * k + ")"; });
        circle.attr("r", function(d) { return d.r * k; });
      }

    });
}());
