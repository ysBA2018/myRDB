(function(){
$(document).ready(function(){
    var svg = d3.select("#trashSVG"),
        margin = 20,
        diameter = +svg.attr("width"),
        g = svg.append("g").attr("transform", "translate(" + diameter / 2 + "," + diameter / 2 + ")");
    svg.select("g").style('transform','translate(50%, 50%)');
    function get_color(d) {
          if(d.depth===0){
              return "white";
          }
          else{
              if(d.depth===3){return d.data.color}
              else{return "white"}
          }
      }


    var pack = d3.pack()
        .size([diameter - margin, diameter - margin])
        .padding(2);

    var root = window.trashlistdata;
    console.log(root);

      root = d3.hierarchy(root)
          .sum(function(d) { return d.size; })
          .sort(function(a, b) { return b.value - a.value; });

      var focus = root,
          nodes = pack(root).descendants(),
          view;

      var div = d3.select("body").append("div")
          .attr("class","tooltip")
          .attr("id","trashTooltip")
          .style("opacity",0);

      function get_opacity(d) {
          if(d.depth ===0) return 0.5;
          if(d.depth ===1) return 0.7;
          if(d.depth ===2) return 0.8;
          if(d.depth ===3) return 0.9;
      }

    //TODO: bei erstellen von json color für leaves mitgeben!!!
      var circle = g.selectAll("circle")
        .data(nodes)
        .enter().append("circle")
          .attr("class", function(d) { return d.parent ? d.children ? "node" : "node node--leaf" : "node node--root"; })
          .style("stroke","grey")
          .style("opacity",function(d){return get_opacity(d)})
          .style("fill", function(d) { return get_color(d) })
          .on("click", function(d) { if(d3.event.defaultPrevented) return;
                console.log("clicked");
              if (focus !== d) zoom(d), d3.event.stopPropagation(); })
          .on("contextmenu",function(d,i){confirm_restore(d,i)})
          .on("mouseover",function (d) {
              d3.select(this).style("stroke","black");
              div.transition()
                  .duration(200)
                  .style("opacity",9);
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
              d3.select(this).style("stroke","grey");
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
    function updateTrash(updated_data){
          console.log(updated_data);
          root = updated_data;

          svg = d3.select("#trashSVG"),
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
          .attr("id","trashTooltip")
          .style("opacity",0);

    //TODO: bei erstellen von json color für leaves mitgeben!!!
      circle = g.selectAll("circle")
        .data(nodes)
        .enter().append("circle")
          .attr("class", function(d) { return d.parent ? d.children ? "node" : "node node--leaf" : "node node--root"; })
          .style("opacity",function(d){return get_opacity(d)})
          .style("stroke","grey")
          .style("fill", function(d) { return get_color(d)})
          .on("click", function(d) { if(d3.event.defaultPrevented) return;
                console.log("clicked");
              if (focus !== d) zoom(d), d3.event.stopPropagation(); })
          .on("contextmenu", function(d,i){confirm_restore(d,i)})
          .on("mouseover",function (d) {
              d3.select(this).style("stroke","black");
              div.transition()
                  .duration(200)
                  .style("opacity",9);
              var text;
              if(d.depth === 1){
                  text = "<b>AF:</b> "+d.data.name
              }else if(d.depth === 2){
                  text = "<b>GF:</b> "+d.data.name+"<br/>"+ "<b>AF:</b> "+d.parent.data.name+"<br/>"
              }else if(d.depth === 3){
                  text = "<b>TF:</b> "+d.data.name+"<br/>"+"<b>GF:</b> "+d.parent.data.name+"<br/>"+ "<b>AF:</b> "+d.parent.parent.data.name
              }
              div .html(text)
                  .style("left",(d3.event.pageX)+"px")
                  .style("top",(d3.event.pageY-28)+"px")
          })
          .on("mouseout",function (d) {
              d3.select(this).style("stroke","grey");
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
    window.updateTrash=function () {
        updateTrash(window.trashlistdata);
    };
      function confirm_restore(d,i) {
          d3.event.preventDefault();
          bootbox.confirm("Berechtigung:\n\n"+d.data.name+"\n\nvon Löschliste entfernen\n\nund wiederherstellen?\n\n", function (result) {
                console.log('This was logged in the callback: ' + result);
                if(result===true){
                    restorefunction(d,i)
                }
            });
      }
    function restorefunction(d,i){
        if(d.depth !== 1){
            bootbox.alert("Berechtigung:\n\n"+d.data.name+"\n\nkonnte nicht wiederhergestellt werden!\n\nBerechtigungsbündel können nur\nkomplett wiederhergestellt werden!",function(){
                    console.log("Berechtigungen können nur komplett wiederhergestellt werden");
            });
            return;
        }
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
            var data = {"X-CSRFToken":getCookie("csrftoken"),"X_METHODOVERRIDE":'PATCH',"user_pk":window.user,"action_type":"restore","right_name":d.data.name};
            var successful=false;
            $.ajax({type:'POST',
                    data:data,
                    url:'http://127.0.0.1:8000/users/'+window.user+'/',
                    async:false,
                    success: function(res){console.log(res);
                        successful=true},
                    error: function(res){console.log(res);}
                    });
            if(successful===true){
                var trash = window.trashlistdata['children'];
                var rights;
                if (window.current_site === 'analysis') {
                    rights = window['jsondata_unequal'+svgIndex];
                }else{
                    rights = window.jsondata['children'];
                }
                update_rights(trash,rights,d);

                d3.select("body").selectAll("#trashTooltip").remove();

                d3.select('#trashSVG').select("g").data(window.trashlistdata).exit().remove();
                updateTrash(window['trashlistdata']);

                if (window.current_site === 'analysis') {

                }else{
                d3.select('#circlePackingSVG').select('g').data(window.jsondata).exit().remove();
                    window.updateCP();
                }
                if(window.current_site==="compare"){
                    d3.select('#compareCirclePackingSVG').select('g').data(window.compare_jsondata).exit().remove();
                    window.updateCompareCP();
                }
                bootbox.alert("Berechtigung "+d.data.name+" erfolgreich wiederhergestellt!",function(){
                    console.log(d.data.name+'wiederhergestellt!');
                });
            }else{
                bootbox.alert("Beim Wiederherstellen der Berechtigung "+d.data.name+" ist ein Fehler aufgetreten!",function(){
                    console.log("Fehler beim wiederherstellen von "+d.data.name+'!');
                });
            }

      }
      function update_right_counters(right){
        //TODO: Counters in Profile-head anpassen!
        for (j in right['children']){
            window.trash_table_count-=right['children'][j]['children'].length;
        }
        document.getElementById('graph_trash_badge').innerHTML = window.trash_table_count;

      }

      function rechain_right_to_rights(right,rights){
        var af_found = false;
        for(i in rights){
            var curr_af = rights[i];
            if(curr_af['name']===right['name']){
                af_found = true;
                break
            }
        }
        if(af_found){
            var right_gfs = right['children'];
            for(rgf in right_gfs){
                var right_gf = right_gfs[rgf];
                var gf_found = false;
                for(j in curr_af['children']){
                    var curr_gf = curr_af['children'][j];
                    if(curr_gf['name']===right_gf['name']){
                        gf_found = true;
                        break
                    }
                }
                if(gf_found){
                    var right_tfs = right_gf['children'];
                    for(rtf in right_tfs){
                        var right_tf = right_tfs[rtf];
                        var tf_found = false;
                        for(k in curr_gf['children']){
                            var curr_tf = curr_gf['children'][k];
                            if(curr_tf['name']===right_tf['name']){
                                tf_found = true;
                                break
                            }
                        }
                        if(! tf_found){
                            curr_gf['children'].push(right_tf)
                        }
                    }
                }
                else{
                    curr_af['children'].push(right_gf)
                }
            }

        }
        else{
            rights.push(right)
        }


      }
      //-------> TODO: an ein level für Rollen denken sobald rollen eingefügt
      function update_rights(trash,rights,d){
        if (d.depth===1){
            for (trash_item in trash) {
                if (trash[trash_item]['name'] === d.data.name) {
                    console.log(trash_item + "," + d.data.name);
                    rechain_right_to_rights(trash[trash_item], rights);
                    update_right_counters(trash[trash_item]);
                    trash.splice(trash_item, 1);
                    //alert("Berechtigung von\n\nLöschliste entfernt\n\nund wiederhergestellt!\n");
                    break;
                }
            }
        }
        //else{
        //    alert("Berechtigung:\n\n"+d.data.name+"\n\nkonnte nicht wiederhergestellt werden!\n\nBerechtigungsbündel können nur\nkomplett wiederhergestellt werden!");
        //}
            /*for (trash_item in trash){
                if(trash[trash_item]['name']===d.data.name){
                    console.log(trash_item+","+d.data.name);
                    rechain_right_to_rights(trash[trash_item],rights,level);
                    trash.splice(trash_item,1);
                    alert("Berechtigung von\n\nLöschliste entfernt\n\nund wiederhergestellt!\n");
                    break;
                }
                else{
                    if(trash[trash_item].hasOwnProperty('children')){
                        var trash_lev_2 = trash[trash_item]['children'];
                        for (trash_item_lev_2 in trash_lev_2){
                            if(trash_lev_2[trash_item_lev_2]['name']===d.data.name){
                                console.log(trash_item_lev_2+","+d.data.name);
                                if (d.depth===1) {
                                    rechain_right_to_rights(trash_lev_2[trash_item_lev_2], rights, level);
                                    trash_lev_2.splice(trash_item_lev_2, 1);
                                    alert("Berechtigung von\n\nLöschliste entfernt\n\nund wiederhergestellt!\n");
                                }else {
                                    alert("Berechtigung:\n\n"+d.data.name+"\n\nkonnte nicht wiederhergestellt werden!\n\nBerechtigungsbündel können nur\nkomplett wiederhergestellt werden!");
                                }
                                break;
                            }
                            else{
                                if(trash_lev_2[trash_item_lev_2].hasOwnProperty('children')){
                                    var trash_lev_3 = trash_lev_2[trash_item_lev_2]['children'];
                                    for (trash_item_lev_3 in trash_lev_3){
                                        if(trash_lev_3[trash_item_lev_3]['name']===d.data.name){
                                            console.log(trash_item_lev_3+","+d.data.name);
                                            if(d.depth===1) {
                                                rechain_right_to_rights(trash_lev_3[trash_item_lev_3], rights, level);
                                                trash_lev_3.splice(trash_item_lev_3, 1);
                                                alert("Berechtigung von\n\nLöschliste entfernt\n\nund wiederhergestellt!\n");
                                            }
                                            else{
                                                alert("Berechtigung:\n\n"+d.data.name+"\n\nkonnte nicht wiederhergestellt werden!\n\nBerechtigungsbündel können nur\nkomplett wiederhergestellt werden!");
                                            }
                                            break;
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }*/
      }
    });
}());
