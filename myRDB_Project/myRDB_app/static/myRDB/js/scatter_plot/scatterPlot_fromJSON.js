(function scatterPlot(){
    $(document).ready(function(){
        var scatterMargin = {top:10,right:20,bottom:30,left:30};
        var scatterWidth = 400-scatterMargin.left-scatterMargin.right;
        var scatterHeight = 200-scatterMargin.top-scatterMargin.bottom;

        var scatterSVG = d3.select('#scatterPlotSVG')
            .append('svg')
                .attr('width',scatterWidth+scatterMargin.left+scatterMargin.right)
                .attr('height',scatterHeight+scatterMargin.top+scatterMargin.bottom)
                .call(responsivefy)
            .append('g')
                .attr('transform','translate('+scatterMargin.left+', '+scatterMargin.top+')');

        var data = window.scatterData;

        var div = d3.select('#scatterPlotSVG').append("div")
          .attr("class","tooltip")
          .attr("id","scattertooltip")
          .style("opacity",0);

            var scatterYscale=d3.scaleLinear()
                .domain(d3.extent(data, d => d.index))
                .range([scatterHeight,0])
                .nice();
            var scatterYaxis=d3.axisLeft(scatterYscale);
            scatterSVG.call(scatterYaxis);

            var scatterXscale=d3.scaleTime()
                .domain(d3.extent(data, d => new Date(d.af_applied)))
                .range([0,scatterWidth])
                .nice();
            var scatterXaxis = d3.axisBottom(scatterXscale)
                .tickPadding(15);

            scatterSVG.append('g')
                .attr('transform',`translate(0, ${scatterHeight})`)
                .call(scatterXaxis)
                .selectAll("text")
                .style("text-anchor", "end")
                .attr("dx", "8px")
                .attr("dy", "-8px")
                .attr("transform", "rotate(-25)");

            var scatterRscale= d3.scaleSqrt()
                .domain([0,d3.max(data, d => new Date(d.af_applied))])
                .range([0,40]);

            var scatterCircles = scatterSVG
                .selectAll('.ball')
                .data(data)
                .enter()
                .append('g')
                .attr('class','ball')
                .attr('transform', d => {
                    return `translate(${scatterXscale(new Date(d.af_applied))}, ${scatterYscale(d.index)})`;
                });

            scatterCircles
                .append('circle')
                .attr('cx',0)
                .attr('cy',0)
                .attr('r',d => 10)
                .style('fill-opacity',0.5)
                .style('fill',d => d.color)
                .on("mouseover",function (d) {
                      d3.select(this).style("stroke","black");
                      div.transition()
                          .duration(200)
                          .style("opacity",9);
                      div .html("<b>TF:</b> "+d.name+"<br/>"+"<b>GF:</b> "+d.gf_name+"<br/>"+"<b>AF:</b> "+d.af_name+"<br/>"+"<b>AF aktiv seit:</b> "+d.af_applied+"<br/>")
                          .style("right","px")
                          .style("top","py"+(d3.event.pageY))
                  })
                  .on("mouseout",function (d) {
                      d3.select(this).style("stroke",null);
                      div.transition()
                          .duration(500)
                          .style("opacity",0)
                  });
/*
            scatterCircles
                .append('text')
                .style('text-anchor','middle')
                .style('fill','black')
                .attr('y',4)
                .text(d => d.name);
*/

        function responsivefy(scatterSVG){
            var scatterContainer = d3.select(scatterSVG.node().parentNode),
                scatterWidth = parseInt(scatterSVG.style("width")),
                scatterHeight = parseInt(scatterSVG.style("height")),
                scatterAspect = scatterWidth/scatterHeight;

            scatterSVG.attr("viewBox","0 0 "+scatterWidth+" "+scatterHeight)
                .attr("preserveAspectRatio","xMinYMid")
                .call(resize);

            d3.select(window).on("resize."+scatterContainer.attr("id"), resize);

            function resize(){
                var scatterTargetWidth = parseInt(scatterContainer.style("width"));
                scatterSVG.attr("width", scatterTargetWidth);
                scatterSVG.attr("height", Math.round(scatterTargetWidth/scatterAspect));
            }
        }

    });
}());