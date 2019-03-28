$(document).ready(function(){
    var svg = d3.select("#profileLegendSVG"),
        margin = 20,
        diameter = +svg.attr("width"),
        g = svg.append("g").attr("transform", "translate(" + diameter / 2 + "," + diameter / 2 + ")");

    svg.select("g").style('transform','translate(50%, 50%)');

    var data = window.legendData;
    console.log(data);
    var j = 0;

    svg.selectAll('mydots')
        .data(data)
        .enter()
        .append("circle")
            .attr("cx",function (d,i) {
                if(i>=3&&i<6){return 130}else if(i>=6&&i<9){return 245}else if(i>=9&&i<12){return 360}else{return 15}
            })
            .attr("cy",function (d,i) {return 15 + (i * 25)%75 })
            .attr("r", 7)
            .style("fill", function (d){return d.color});

    svg.selectAll("mylabels")
        .data(data)
        .enter()
        .append("text")
        .attr("x",function (d,i) { if(i>=3&&i<6){return 145}else if(i>=6&&i<9){return 260}else if(i>=9&&i<12){return 375}else{return 30} })
        .attr("y",function (d,i){return 15 + (i * 25)%75 } )
        .text(function (d) { return d.application_name })
        .attr("text-anchor","left")
        .attr("alignment-baseline","middle");

});