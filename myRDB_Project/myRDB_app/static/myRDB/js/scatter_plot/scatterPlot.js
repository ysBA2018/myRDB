(function scatterPlot(){
$(document).ready(function(){
    var scatterMargin = {top: 20, right: 20, bottom: 30, left: 40},
        scatterWidth = 960 -scatterMargin.left - scatterMargin.right,
        scatterHeight = 500 -scatterMargin.top - scatterMargin.bottom;

    var scatterXvalue = function(d) { return d.Calories;}, //data -> value
        scatterXscale = d3.scaleLinear().range([0, scatterWidth]),
        scatterXmap = function(d) { return scatterXscale(scatterXvalue(d));},
        scatterXaxis = d3.axisBottom(scatterXscale);

    var scatterYvalue = function(d) { return d["Protein (g)"];}, //data -> value
        scatterYscale = d3.scaleLinear().range([scatterHeight, 0]),
        scatterYmap = function(d) { return scatterYscale(scatterYvalue(d));},
        scatterYaxis = d3.axisLeft(scatterYscale);

    var scatterCvalue = function(d){ return d.Manufacturer;}, //data -> value
        scatterColor = d3.scaleOrdinal(d3.schemeCategory10);

    var scatterSVG = d3.select("#scatterPlotSVG").append("svg") // in orig. +: .append("svg")
        .attr("width", scatterWidth + scatterMargin.left +scatterMargin.right)
        .attr("height", scatterHeight + scatterMargin.top + scatterMargin.bottom)
      .append("g")
        .attr("transform", "translate("+scatterMargin.left+","+scatterMargin.top+")");

    var scatterTooltip = d3.select("#scatterPlotSVG").append("div") // in orig.: select("body")
        .attr("class", "scatterTooltip")
        .style("opacity",0)

    d3.csv("/../../static/myRDB/data/cereal.csv", function(error, data){
        data.forEach(function(d){
            d.Calories =+d.Calories;
            d["Protein (g)"]=+d["Protein (g)"];
            console.log(d);
        });

        scatterXscale.domain([d3.min(data, scatterXvalue)-1,d3.max(data,scatterXvalue)+1]);
        scatterYscale.domain([d3.min(data, scatterYvalue)-1,d3.max(data,scatterYvalue)+1]);

        scatterSVG.append("g")
            .attr("class","x axis")
            .attr("transform","translate(0,"+scatterHeight+")")
            .call(scatterXaxis)
           .append("text")
            .attr("class", "label")
            .attr("x",scatterWidth)
            .attr("y",-6)
            .style("text-anchor","end")
            .text("Calories");

        scatterSVG.append("g")
            .attr("class","y axis")
            .call(scatterYaxis)
           .append("text")
            .attr("class", "label")
            .attr("transform","rotate(-90)")
            .attr("y",6)
            .attr("dy",".71em")
            .style("text-anchor","end")
            .text("Protein (g)");

        scatterSVG.selectAll(".dot")
            .data(data)
           .enter().append("circle")
           .attr("class", "dot")
           .attr("r",3.5)
           .attr("cx",scatterXmap)
           .attr("cy",scatterYmap)
           .style("fill", function(d) {return scatterColor(scatterCvalue(d));})
           .on("mouseover",function(d){
                scatterTooltip.transition()
                    .duration(200)
                    .style("opacity", .9);
                scatterTooltip.html(d["Cereal Name"]+"</br> ("+scatterXvalue(d)+", "+scatterYvalue(d)+")")
                    .style("left",(d3.event.pageX + 5) +"px")
                    .style("top",(d3.event.pageY - 28) +"px");
           })
           .on("mouseout", function(d){
                scatterTooltip.transition()
                    .duration(500)
                    .style("opacity",0);
           });

      var scatterLegend = scatterSVG.selectAll(".legend")
          .data(scatterColor.domain())
        .enter().append("g")
          .attr("class", "legend")
          .attr("transform", function(d, i) { return "translate(0," + i * 20 + ")"; });

      // draw legend colored rectangles
      scatterLegend.append("rect")
          .attr("x", scatterWidth - 18)
          .attr("width", 18)
          .attr("height", 18)
          .style("fill", scatterColor);

      // draw legend text
      scatterLegend.append("text")
          .attr("x", scatterWidth - 24)
          .attr("y", 9)
          .attr("dy", ".35em")
          .style("text-anchor", "end")
          .text(function(d) { return d;})

    });
});
}());