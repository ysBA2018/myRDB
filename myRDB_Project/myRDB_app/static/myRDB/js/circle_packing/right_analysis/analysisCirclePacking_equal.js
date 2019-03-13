(function(){
$(document).ready(function(){
    var svg = d3.select("#circlePackingSVG"),
        margin = 20,
        diameter = +svg.attr("width"),
        g = svg.append("g").attr("transform", "translate(" + diameter / 2 + "," + diameter / 2 + ")");
    /*
    var color = d3.scaleLinear()
        .domain([-1, 5])
        .range(["hsl(360,0%,100%)", "hsl(0,100%,100%)"])
        .interpolate(d3.interpolateHcl);
    */

    var pack = d3.pack()
        .size([diameter - margin, diameter - margin])
        .padding(2);

    var root = window.jsondata;
    console.log(root);

      root = d3.hierarchy(root)
          .sum(function(d) { return d.size; })
          .sort(function(a, b) { return b.value - a.value; });

      var focus = root,
          nodes = pack(root).descendants(),
          view;

      var div = d3.select("body").append("div")
          .attr("class","tooltip")
          .attr("id","CPtooltip")
          .style("opacity",0);

      function compare_graphs(d){
          var compare_data = window.compare_jsondata['children'];
          if(d.depth===1){
              for(i in compare_data){
                  if(compare_data[i].name===d.data.name) return true;
              }
          }
          else if (d.depth === 2){
              for(i in compare_data){
                  if(compare_data[i].name===d.parent.data.name){
                      var level_2 = compare_data[i]['children'];
                      for(j in level_2){
                          if(level_2[j].name===d.data.name) return true;
                      }
                  }
              }
          }
          else if (d.depth === 3){
              for(i in compare_data){
                  if(compare_data[i].name===d.parent.parent.data.name){
                      var level_2 = compare_data[i]['children'];
                      for(j in level_2){
                          if(level_2[j].name===d.parent.data.name){
                              var level_3 = level_2[j]['children'];
                              for(k in level_3){
                                  if(level_3[k].name===d.data.name) return true;
                              }
                          }
                      }
                  }
              }
          }
          return false;
      }
      function get_color(d) {
          if(d.depth===0){
              return "white";
          }
          else{
              console.log(window.current_site);
              if(window.current_site==="compare"){
                  if(compare_graphs(d)){
                      if(d.depth===1)return "darkgrey";
                      if(d.depth===2)return "grey";
                      if(d.depth===3)return "lightgrey";
                  }else{
                      if(d.depth===3){return d.data.color}
                      else{return "white"}
                  }
              }
              else{
                  if(d.depth===3){return d.data.color}
                  else{return "white"}
              }
          }
      }

    //TODO: bei erstellen von json color für leaves mitgeben!!!
      var circle = g.selectAll("circle")
        .data(nodes)
        .enter().append("circle")
          .attr("class", function(d) { return d.parent ? d.children ? "node" : "node node--leaf" : "node node--root"; })
          .style("stroke","grey")
          .style("fill", function(d) {return get_color(d)}) //else{return d.children ? color(d.depth) : null; }
          .on("click", function(d) { if(d3.event.defaultPrevented) return;
                console.log("clicked");
              if (focus !== d) zoom(d), d3.event.stopPropagation(); })
          .on("contextmenu",function(d,i){deletefunction(d,i)})
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

      svg
          .style("background", "white")
          .on("click", function() { zoom(root); });

      zoomTo([root.x, root.y, root.r * 2 + margin]);

      function zoom(d) {
          if (d.depth===3) return;
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
    function update(updated_data){
          console.log(updated_data);
          root = updated_data;

          svg = d3.select("#circlePackingSVG"),
        margin = 20,
        diameter = +svg.attr("width"),
        g = svg.append("g").attr("transform", "translate(" + diameter / 2 + "," + diameter / 2 + ")");
/*
        color = d3.scaleLinear()
            .domain([-1, 5])
            .range(["hsl(360,100%,100%)", "hsl(0,0%,0%)"])
            .interpolate(d3.interpolateHcl);
*/

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
          .attr("id","CPtooltip")
          .style("opacity",0);

    //TODO: bei erstellen von json color für leaves mitgeben!!!
      circle = g.selectAll("circle")
        .data(nodes)
        .enter().append("circle")
          .attr("class", function(d) { return d.parent ? d.children ? "node" : "node node--leaf" : "node node--root"; })
          .style("stroke","grey")
          .style("fill", function(d) { return get_color(d)}) //else{return d.children ? color(d.depth) : null; }
          .on("click", function(d) { if(d3.event.defaultPrevented) return;
                console.log("clicked");
              if (focus !== d) zoom(d), d3.event.stopPropagation(); })
          .on("contextmenu", function(d,i){deletefunction(d,i)})
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

      svg
          .style("background", "white")
          .on("click", function() { zoom(root); });

      zoomTo([root.x, root.y, root.r * 2 + margin]);
    }
    window.updateCP=function () {
        update(window.jsondata)
    };
    function deletefunction(d,i){
        d3.event.preventDefault();
        var r = confirm("Berechtigung:\n\n"+d.data.name+"\n\nwirklich zu Löschliste hinzufügen?\n\n");
        if (r === true){
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
            if(d.depth===1) right_type="af";
            else if(d.depth===2) {
                right_type="gf";
                right_parent = d.parent.data.name;
            }
            else if(d.depth===3){
                right_type="tf";
                right_grandparent = d.parent.parent.data.name;
                right_parent = d.parent.data.name;
            }
            var data = {"X-CSRFToken":getCookie("csrftoken"),"X_METHODOVERRIDE":'PATCH',"user":window.user,"action_type":"trash","right_type":right_type,"right_name":d.data.name,"parent":right_parent,"grandparent":right_grandparent};
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
                var rights = window.jsondata['children'];
                var trash = window.trashlistdata['children'];
                update_rights(rights, trash, d);

                d3.select("body").selectAll("#CPtooltip").remove();

                d3.select('#circlePackingSVG').select("g").data(window.jsondata).exit().remove();
                update(window['jsondata']);

                d3.select('#trashSVG').select('g').data(window.trashlistdata).exit().remove();
                window.updateTrash();

                if(window.current_site==="compare"){
                    d3.select('#compareCirclePackingSVG').select('g').data(window.compare_jsondata).exit().remove();
                    window.updateCompareCP();
                }
                alert("Berechtigung zur\n\nLöschliste hinzugefügt\n");
                //update_session();
            }
            else{
                alert("Beim Löschen der Berechtigung\nist ein Fehler aufgetreten!")
            }
        }
      }
      /**
      function update_session() {
        var trash_table_update_data = {"action_type":"update_session","trash_table_data":{"data":window.trash_table_data}};
        $.ajax({type:'POST',
            data:trash_table_update_data,
            success: function(res){console.log(res);
                alert("session-update-success");},
            error: function(res){console.log(res);}
            });
        var trash_graph_update_data = {"action_type":"update_session","trash_graph_data":window.trashlistdata};
        $.ajax({type:'POST',
            data:trash_graph_update_data,
            success: function(res){console.log(res);
                alert("session-update-success");},
            error: function(res){console.log(res);}
            });
        var user_graph_update_data = {"action_type":"update_session","user_graph_data":window.jsondata};
        $.ajax({type:'POST',
            data:user_graph_update_data,
            success: function(res){console.log(res);
                alert("session-update-success");},
            error: function(res){console.log(res);}
            });
        var user_table_update_data = {"action_type":"update_session","user_table_data":{"data":window.user_table_data}};
        $.ajax({type:'POST',
            data:user_table_update_data,
            success: function(res){console.log(res);
                alert("session-update-success");},
            error: function(res){console.log(res);}
            });

      }
       **/

      function update_right_counters(right,type){
        if (type === "af"){
            for (j in right['children']){
                window.trash_table_count+=right['children'][j]['children'].length;
            }
            document.getElementById('graph_trash_badge').innerHTML = window.trash_table_count;
        }
        else if (type === "gf"){
            window.trash_table_count+=right['children'].length;
            document.getElementById('graph_trash_badge').innerHTML = window.trash_table_count;
        }
        else if (type === "tf"){
            window.trash_table_count+=1;
            document.getElementById('graph_trash_badge').innerHTML = window.trash_table_count;
        }
      }
      function add_to_delete_list(delete_list, right, parent_right, grandparent_right, level){
        if(level === "gf"){
            var af_found = false;
            for(i in delete_list){
                var curr_af = delete_list[i];
                if(curr_af['name']===parent_right['name']){
                    af_found = true;
                    var gf_found =false;
                    var gfs = curr_af['children'];
                    for(gf in gfs){
                        var curr_gf = gfs[gf];
                        if(curr_gf['name']===right['name']){
                            gf_found = true;
                            break
                        }
                    }
                    if(gf_found){
                        for(child in right['children']){
                            curr_gf['children'].push(right['children'][child]);

                            return;
                        }
                    }
                    break
                }
            }
            if(af_found){
                curr_af['children'].push(right);
                return;
            }
            var parent_cpy = jQuery.extend({},parent_right);
            parent_cpy['children']=[right];
            delete_list.push(parent_cpy);
        }
        if(level === "tf"){
            for(i in delete_list){
                var curr_af = delete_list[i];
                if(curr_af['name']===grandparent_right['name']){
                    var curr_af_gfs = curr_af['children'];
                    var gf_found = false;
                    for(j in curr_af_gfs){
                        var curr_gf = curr_af_gfs[j];
                        if(curr_gf['name']===parent_right['name']){
                            gf_found = true;
                            break
                        }
                    }
                    if (gf_found){
                        curr_gf['children'].push(right);
                        return;
                    }
                    else{
                        var parent_cpy = jQuery.extend({},parent_right);
                        parent_cpy['children']=[right];
                        curr_af_gfs.push(parent_cpy);
                        return
                    }

                }
            }
            var grandparent_cpy = jQuery.extend({},grandparent_right);
                var parent_cpy = jQuery.extend({},parent_right);
                parent_cpy['children']=[right];
                grandparent_cpy['children']=[parent_cpy];
                delete_list.push(grandparent_cpy);
        }
      }


      //-------> TODO: an ein level für Rollen denken sobald rollen eingefügt
      function update_rights(rights, trash, d){
        if (d.depth ===1){
            for (i in rights) {
                if (rights[i]['name'] === d.data.name) {
                    console.log(i + "," + d.data.name);
                    update_right_counters(rights[i],"af");
                    trash.push(rights[i]);
                    rights.splice(i, 1);
                    return;
                }
            }
        }
        else if(d.depth===2){
            for (i in rights) {
                var right = rights[i];
                if (right['name'] === d.parent.data.name) {
                    for (j in right['children']) {
                        var right_lev_2 = right['children'][j];
                        if (right_lev_2['name'] === d.data.name) {
                            console.log(j + "," + d.data.name);
                            right_lev_2["parent"]=d.parent.data.name;
                            update_right_counters(right_lev_2,"gf");
                            add_to_delete_list(trash,right_lev_2,right,null,'gf');
                            right['children'].splice(j, 1);
                            if(right['children'].length===0){
                                rights.splice(i,1)
                            }
                            return;
                        }
                    }
                }
            }
        }
        else if(d.depth===3){
            for (i in rights) {
                var right = rights[i];
                if (right['name'] === d.parent.parent.data.name) {
                    for (j in right['children']) {
                        var right_lev_2 = right['children'][j];
                        if (right_lev_2['name'] === d.parent.data.name) {
                            for (k in right_lev_2['children']) {
                                var right_lev_3 = right_lev_2['children'][k];
                                if (right_lev_3['name'] === d.data.name) {
                                    console.log(k + "," + d.data.name);
                                    right_lev_3["grandparent"]= d.parent.parent.data.name;
                                    right_lev_3["parent"]=d.parent.data.name;
                                    update_right_counters(right_lev_3,"tf");
                                    add_to_delete_list(trash,right_lev_3,right_lev_2,right,'tf');
                                    right_lev_2['children'].splice(k, 1);
                                    if(right_lev_2['children'].length===0){
                                        right['children'].splice(j,1)
                                    }
                                    if(right['children'].length===0){
                                        rights.splice(i,1)
                                    }

                                    return;
                                }
                            }
                        }
                    }
                }
            }
        }
            /*for (right in rights){
                if(rights[right]['name']===d.data.name){
                    console.log(right+","+d.data.name);
                    trash.push(rights[right]);
                    rights.splice(right,1);
                    return;
                }
                else{
                    if(rights[right].hasOwnProperty('children')){
                        var rights_lev_2 = rights[right]['children']
                        for (right_lev_2 in rights_lev_2){
                            if(rights_lev_2[right_lev_2]['name']===d.data.name){
                                console.log(right_lev_2+","+d.data.name);
                                trash.push(rights_lev_2[right_lev_2]);
                                rights_lev_2.splice(right_lev_2,1);
                                return;
                            }
                            else{
                                if(rights_lev_2[right_lev_2].hasOwnProperty('children')){
                                    var rights_lev_3 = rights_lev_2[right_lev_2]['children']
                                    for (right_lev_3 in rights_lev_3){
                                        if(rights_lev_3[right_lev_3]['name']===d.data.name){
                                            console.log(right_lev_3+","+d.data.name);
                                            trash.push(rights_lev_3[right_lev_3]);
                                            rights_lev_3.splice(right_lev_3,1);
                                            return;
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
