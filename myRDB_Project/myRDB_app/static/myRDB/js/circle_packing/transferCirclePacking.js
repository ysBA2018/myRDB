(function(){
$(document).ready(function(){
    var svg = d3.select("#transferSVG"),
        margin = 20,
        diameter = +svg.attr("width"),
        g = svg.append("g").attr("transform", "translate(" + diameter / 2 + "," + diameter / 2 + ")");

    svg.select("g").style('transform','translate(50%, 50%)');
    var color = d3.scaleLinear()
        .domain([-1, 5])
        .range(["hsl(360,100%,100%)", "hsl(0,0%,0%)"])
        .interpolate(d3.interpolateHcl);


    var pack = d3.pack()
        .size([diameter - margin, diameter - margin])
        .padding(2);

    var root = window.transferlistdata;
    console.log(root);

      root = d3.hierarchy(root)
          .sum(function(d) { return d.size; })
          .sort(function(a, b) { return b.value - a.value; });

      var focus = root,
          nodes = pack(root).descendants(),
          view;

      var div = d3.select("body").append("div")
          .attr("class","tooltip")
          .attr("id","transferTooltip")
          .style("opacity",0);

      function get_opacity(d) {
          if(d.depth ===0) return 0.5;
          if(d.depth ===1) return 0.7;
          if(d.depth ===2) return 0.8;
          if(d.depth ===3) return 0.9;
      }
      function get_color(d) {
          if(d.depth===0){
              return "white";
          }
          else{
              if(d.depth===3){return d.data.color}
              else{return "white"}
          }
      }

    //TODO: bei erstellen von json color für leaves mitgeben!!!
      var circle = g.selectAll("circle")
        .data(nodes)
        .enter().append("circle")
          .attr("class", function(d) { return d.parent ? d.children ? "node" : "node node--leaf" : "node node--root"; })
          .style("fill", function(d) { if(window.current_site === "compare" ){ return d.children ? color(d.depth) : null;}
                                        else{ return get_color(d) }})
          .style("stroke",function (d){if(window.current_site !== "compare" ){return "grey"}return null;})
          .style("opacity",function(d){return get_opacity(d)})
          .on("click", function(d) { if(d3.event.defaultPrevented) return;
                console.log("clicked");
              if (focus !== d) zoom(d), d3.event.stopPropagation(); })
          .on("contextmenu",function(d,i){confirm_restore(d,i)})
          .on("mouseover",function (d) {
              div.transition()
                  .duration(200)
                  .style("opacity",9)
              var text;
              if(d.depth === 1){
                  text = "<b>AF:</b> "+d.data.name
              }else if(d.depth === 2){
                  text = "<b>GF:</b> "+d.data.name+"<br/>"+ "<b>AF:</b> "+d.parent.data.name
              }else if(d.depth === 3){
                  text = "<b>TF:</b> "+d.data.name+"<br/>"+"<b>GF:</b> "+d.parent.data.name+"<br/>"+ "<b>AF:</b> "+d.parent.parent.data.name
              }
              div .html(text)
                  .style("left",(d3.event.pageX)+"px")
                  .style("top",(d3.event.pageY-28)+"px")
          })
          .on("mouseout",function (d) {
              div.transition()
                  .duration(500)
                  .style("opacity",0)
          });

      var leaves = d3.selectAll("circle").filter(function(d){
        return d.children === null;
      });

      //var text = g.selectAll("text")
      //  .data(nodes)
      //  .enter().append("text")
      //    .attr("class", "label")
      //    .style("fill-opacity", function(d) { return d.parent === root ? 1 : 0; })
      //    .style("display", function(d) { return d.parent === root ? "inline" : "none"; })
      //    .text(function(d) { return d.data.name; });

        var node = g.selectAll("circle");
      //var node = g.selectAll("circle,text");
      //.call(d3.drag()
        //                   .on("start",dragstarted)
        //                   .on("drag",dragged)
        //                   .on("end",dragended))

      svg.on("click", function() { zoom(root); });

      zoomTo([root.x, root.y, root.r * 2 + margin]);

      function zoom(d) {
          if (!d.hasOwnProperty('children')) return;
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

      //function dragstarted(d){
      //    d3.event.sourceEvent.stopPropagation()
      //    console.log("dragstarted");
      //    d3.select(this).raise().classed("active",true);
      //}
      //function dragged(d) {
      //    console.log("dragged");
      //    d.x += d3.event.dx;
      //    d.y += d3.event.dy;
      //    draw();
      //}
      //function dragended(d) {
      //    console.log("dragended");
      //    d3.select(this).classed("active",false);
      //}
      //function draw() {
      //    var k = diameter / (root.r * 2 + margin);
      //    node.attr("transform", function(d){
      //        return "translate("+(d.x -root.x)*k+","+(d.y-root.y)*k+")";
      //    });
      //    circle.attr("r", function(d){
      //        return d.r*k;
      //    });
      //}
    function updateTransfer(updated_data){
          console.log(updated_data);
          root = updated_data;

          svg = d3.select("#transferSVG"),
        margin = 20,
        diameter = +svg.attr("width"),
        g = svg.append("g").attr("transform", "translate(" + diameter / 2 + "," + diameter / 2 + ")");

        svg.select("g").style('transform','translate(50%, 50%)');

        color = d3.scaleLinear()
            .domain([-1, 5])
            .range(["hsl(360,100%,100%)", "hsl(0,0%,0%)"])
            .interpolate(d3.interpolateHcl);


        pack = d3.pack()
            .size([diameter - margin, diameter - margin])
            .padding(2);
      root = d3.hierarchy(root)
          .sum(function(d) { return d.size; })
          .sort(function(a, b) { return b.value - a.value; });

      focus = root,
          nodes = pack(root).descendants(),
          view;

      var div = d3.select("body").append("div")
          .attr("class","tooltip")
          .attr("id","transferTooltip")
          .style("opacity",0);

    //TODO: bei erstellen von json color für leaves mitgeben!!!
      circle = g.selectAll("circle")
        .data(nodes)
        .enter().append("circle")
          .attr("class", function(d) { return d.parent ? d.children ? "node" : "node node--leaf" : "node node--root"; })
          .style("fill", function(d) {  if(window.current_site === "compare" ){return d.children ? color(d.depth) : null;}
                                        else{return get_color(d)}})
          .style("stroke",function (d){if(window.current_site !== "compare" ){return "grey"}return null;})
          .style("opacity",function(d){return get_opacity(d)})
          .on("click", function(d) { if(d3.event.defaultPrevented) return;
                console.log("clicked");
              if (focus !== d) zoom(d), d3.event.stopPropagation(); })
          .on("contextmenu", function(d,i){confirm_restore(d,i)})
          .on("mouseover",function (d) {
              div.transition()
                  .duration(200)
                  .style("opacity",9)
              var text;
              if(d.depth === 1){
                  text = "<b>AF:</b> "+d.data.name
              }else if(d.depth === 2){
                  text = "<b>GF:</b> "+d.data.name+"<br/>"+ "<b>AF:</b> "+d.parent.data.name
              }else if(d.depth === 3){
                  text = "<b>TF:</b> "+d.data.name+"<br/>"+"<b>GF:</b> "+d.parent.data.name+"<br/>"+ "<b>AF:</b> "+d.parent.parent.data.name
              }
              div .html(text)
                  .style("left",(d3.event.pageX)+"px")
                  .style("top",(d3.event.pageY-28)+"px")
          })
          .on("mouseout",function (d) {
              div.transition()
                  .duration(500)
                  .style("opacity",0)
          });

      leaves = d3.selectAll("circle").filter(function(d){
        return d.children === null;
      });

      //var text = g.selectAll("text")
      //  .data(nodes)
      //  .enter().append("text")
      //    .attr("class", "label")
      //    .style("fill-opacity", function(d) { return d.parent === root ? 1 : 0; })
      //    .style("display", function(d) { return d.parent === root ? "inline" : "none"; })
      //    .text(function(d) { return d.data.name; });

        node = g.selectAll("circle");
      //var node = g.selectAll("circle,text");
      //.call(d3.drag()
        //                   .on("start",dragstarted)
        //                   .on("drag",dragged)
        //                   .on("end",dragended))

      svg.on("click", function() { zoom(root); });

      zoomTo([root.x, root.y, root.r * 2 + margin]);
    }
    window.updateTransfer=function () {
        updateTransfer(window.transferlistdata);
    };
    function find_svgIndex(d) {
        var svgIndex = 0;
        var data;
        var found =false;
        while(found===false){
            data = window['jsonModeldata_unequal'+svgIndex];

                if(window.level==='AF'){
                    if(d.depth===1) {
                        if (d.data.name === data.name) {
                            return svgIndex;
                        }
                    }else if(d.depth===2) {
                        if (d.parent.data.name === data.name) {
                            return svgIndex;
                        }
                    }else if(d.depth===3) {
                        if (d.parent.parent.data.name === data.name) {
                            return svgIndex;
                        }
                    }
                }else if(window.level==='GF'){
                    if(d.depth===1) {
                        for (i in d.children) {
                            if (d.children[i].data.name === data.name) {
                                return svgIndex;
                            }
                        }
                    }else if(d.depth===2) {
                        if (d.data.name === data.name) {
                            return svgIndex;
                        }
                    }else if(d.depth===3) {
                        if (d.parent.data.name === data.name) {
                            return svgIndex;
                        }
                    }
                }

            console.log(data);
            svgIndex+=1;
        }
        return svgIndex
    }
    function confirm_restore(d,i) {
          d3.event.preventDefault();
          bootbox.confirm("Berechtigung:\n\n"+d.data.name+"\n\nvon Transferliste entfernen?\n\n", function (result) {
                console.log('This was logged in the callback: ' + result);
                if(result===true){
                    restorefunction(d,i)
                }
            });
      }

    function restorefunction(d,i){
            function getCookie(name) {
                var cookieValue = null;
                if (document.cookie && document.cookie !== '') {
                    var cookies = document.cookie.split(';');
                    for (var i = 0; i < cookies.length; i++) {
                        var cookie = jQuery.trim(cookies[i]);
                        // Does this cookie string begin with the name we want?
                        if (cookie.substring(0, name.length + 1) === (name + '=')) {
                            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                            break;
                        }
                    }
                }
                return cookieValue;
            }
            function csrfSafeMethod(method) {
                // these HTTP methods do not require CSRF protection
                return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
            }
            $.ajaxSetup({
                beforeSend: function(xhr, settings) {
                    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
                    }
                }
            });
            var right_type="",right_parent = "",right_grandparent = "";
            if(d.depth===1){
                right_type="af";
            }
            else if(d.depth===2){
                right_type="gf";
                right_parent = d.parent.data.name;
            }
            else if(d.depth === 3){
                right_type="tf";
                right_grandparent = d.parent.parent.data.name;
                right_parent = d.parent.data.name;
            }

            var data = {"X-CSRFToken":getCookie("csrftoken"),"X_METHODOVERRIDE":'PATCH',"user":window.user,"action_type":"restore_transfer","right_type":right_type,"right_name":d.data.name,"parent":right_parent,"grandparent":right_grandparent};
            var successful=false;
            $.ajax({type:'POST',
                    data:data,
                    url:'http://127.0.0.1:8000/users/'+window.user+'/',
                    async:false,
                    success: function(res){console.log(res);
                        successful=true},
                    error: function(res){console.log(res);}
                    });
            if(successful===true) {
                var transfer = window.transferlistdata['children'];
                //var rights = window.jsondata['children'];
                update_rights(transfer, data['right_type'], d);

                d3.select("body").selectAll("#transferTooltip").remove();

                d3.select('#transferSVG').select("g").data(window.transferlistdata).exit().remove();
                updateTransfer(window.transferlistdata);

                if (window.current_site === 'compare') {
                    d3.select('#compareCirclePackingSVG').select("g").data(window.compare_jsondata).exit().remove();
                    window.updateCompareCP();
                }
                if (window.current_site === 'analysis') {
                    var svgIndex = find_svgIndex(d);
                    d3.select("#analysisModelCirclePackingSVG_unequal"+svgIndex).select("g").data(window['jsonModeldata_unequal'+svgIndex]).exit().remove();
                    window.updateUnequalModelCP(svgIndex);
                }
                bootbox.alert("Berechtigung "+d.data.name+" von\n\nTransferliste entfernt!\n");
            }
            else{
                bootbox.alert("Beim entfernen der Berechtigung "+d.data.name+" von der Transferliste\nist ein Fehler aufgetreten!")
            }

      }
      function update_right_counters(right,type){
        if (type === "af"){
            for (j in right['children']){
                window.transfer_table_count-=right['children'][j]['children'].length;
            }
            document.getElementById('graph_transfer_badge').innerHTML = window.transfer_table_count;
        }
        else if (type === "gf"){
            window.transfer_table_count-=right['children'].length;
            document.getElementById('graph_transfer_badge').innerHTML = window.transfer_table_count;
        }
        else if (type === "tf"){
            window.transfer_table_count-=1;
            document.getElementById('graph_transfer_badge').innerHTML = window.transfer_table_count;
        }
      }

      //-------> TODO: an ein level für Rollen denken sobald rollen eingefügt
      function update_rights(transfer,level,d){
        if (d.depth===1){
            for (transfer_item in transfer) {
                if (transfer[transfer_item]['name'] === d.data.name) {
                    console.log(transfer_item + "," + d.data.name);
                    update_right_counters(transfer[transfer_item],level);
                    transfer.splice(transfer_item, 1);
                    console.log("transfer");
                    console.log(transfer);
                    return;
                }
            }
        }
        if (d.depth===2){
            for (transfer_item in transfer) {
                if (transfer[transfer_item]['name'] === d.parent.data.name) {
                    var lev_2 = transfer[transfer_item]['children'];
                    for(j in lev_2){
                        if (lev_2[j]['name']===d.data.name){
                            console.log(j + "," + d.data.name);
                            update_right_counters(lev_2[j],level);
                            lev_2.splice(j, 1);
                            return;
                        }
                    }
                }
            }
        }
        if (d.depth===3){
            for (transfer_item in transfer) {
                if (transfer[transfer_item]['name'] === d.parent.parent.data.name) {
                    var lev_2 = transfer[transfer_item]['children'];
                    for(j in lev_2){
                        if (lev_2[j]['name']===d.parent.data.name){
                            var lev_3 = lev_2[j]['children'];
                            for(k in lev_3) {
                                if (lev_3[k]['name'] === d.data.name) {
                                    console.log(k + "," + d.data.name);
                                    update_right_counters(lev_3[k], level);
                                    lev_3.splice(k, 1);
                                    return;
                                }
                            }
                        }
                    }
                }
            }
        }
      }
    });
}());
