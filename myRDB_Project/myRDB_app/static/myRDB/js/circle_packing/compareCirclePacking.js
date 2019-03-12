(function(){
$(document).ready(function(){
    var svg = d3.select("#compareCirclePackingSVG"),
        margin = 20,
        diameter = +svg.attr("width"),
        g = svg.append("g").attr("transform", "translate(" + diameter / 2 + "," + diameter / 2 + ")");
/*
    var color = d3.scaleLinear()
        .domain([-1, 5])
        .range(["hsl(360,100%,100%)", "hsl(0,0%,0%)"])
        .interpolate(d3.interpolateHcl);
*/


    var pack = d3.pack()
        .size([diameter - margin, diameter - margin])
        .padding(2);

    var root = window.compare_jsondata;
    console.log(root);

      root = d3.hierarchy(root)
          .sum(function(d) { return d.size; })
          .sort(function(a, b) { return b.value - a.value; });

      var focus = root,
          nodes = pack(root).descendants(),
          view;

      var div = d3.select("body").append("div")
          .attr("class","tooltip")
          .attr("id","compareCPtooltip")
          .style("opacity",0);

      //TODO: compare auch auf my_requests!
      function compare_graphs(d, compare_data){
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
              if(compare_graphs(d,window.jsondata['children'])||compare_graphs(d,window.transferlistdata['children'])){
                  if(d.depth===1)return "darkgrey";
                  if(d.depth===2)return "grey";
                  if(d.depth===3)return "lightgrey";
              }else{
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
          .style("fill", function(d) {return get_color(d)})
          .on("click", function(d) { if(d3.event.defaultPrevented) return;
                console.log("clicked");
              if (focus !== d) zoom(d), d3.event.stopPropagation(); })
          .on("contextmenu",function(d,i){transferfunction(d,i)})
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

          svg = d3.select("#compareCirclePackingSVG"),
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
          .attr("id","compareCPtooltip")
          .style("opacity",0);

    //TODO: bei erstellen von json color für leaves mitgeben!!!
      circle = g.selectAll("circle")
        .data(nodes)
        .enter().append("circle")
          .attr("class", function(d) { return d.parent ? d.children ? "node" : "node node--leaf" : "node node--root"; })
          .style("stroke","grey")
          .style("fill", function(d) {return get_color(d)})
          .on("click", function(d) { if(d3.event.defaultPrevented) return;
                console.log("clicked");
              if (focus !== d) zoom(d), d3.event.stopPropagation(); })
          .on("contextmenu", function(d,i){transferfunction(d,i)})
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
    window.updateCompareCP=function () {
        update(window.compare_jsondata)
    };

    function check_user_rights_for_existance(d,right_type, parent, grandparent, user_rights, transfer_rights) {
        var exists_in_user_rights = false;
        var exists_in_transfer_rights = false;
        if(right_type==="af"){
            for(i in user_rights){
                if(user_rights[i]['name']===d.data.name){
                    exists_in_user_rights = true
                }
            }
            for(i in transfer_rights){
                if(transfer_rights[i]['name']===d.data.name){
                    exists_in_transfer_rights = true;
                }
            }
            if (!exists_in_user_rights && !exists_in_transfer_rights){
                return false;
            }else{
                alert("AF existiert bereits\nund kann nicht übertragen werden!");
                return true;
            }

        }
        if(right_type==="gf"){
            var parent_exists_in_user_rights=false;
            var parent_exists_in_transfer_rights=false;
            var transferable = true;
            for(i in user_rights){
                if(user_rights[i]['name']===parent){
                    parent_exists_in_user_rights = true;
                    var rights_lev_2 = user_rights[i]['children'];
                    for(j in rights_lev_2){
                        if(rights_lev_2[j]['name']===d.data.name){
                            exists_in_user_rights = true;
                        }
                    }
                }
            }
            for(i in transfer_rights){
                if(transfer_rights[i]['name']===parent){
                    parent_exists_in_transfer_rights = true;
                    var rights_lev_2 = transfer_rights[i]['children'];
                    for(j in rights_lev_2){
                        if(rights_lev_2[j]['name']===d.data.name){
                            exists_in_transfer_rights = true;
                        }
                    }
                }
            }
            if(!exists_in_user_rights && !exists_in_transfer_rights){
                if(parent_exists_in_user_rights || parent_exists_in_transfer_rights){
                    return false
                }
                else{
                    alert("GF kann nicht übertragen werden!\n\nUser besitzt nicht die nötige AF!");
                    return true;
                }
            }else{
                alert("GF existiert bereits\nund kann nicht übertragen werden!");
                return true;
            }
        }
        if(right_type==="tf") {
            var grandparent_exists_in_user_rights = false;
            var parent_exists_in_user_rights = false;
            var grandparent_exists_in_transfer_rights = false;
            var parent_exists_in_transfer_rights = false;
            for (i in user_rights) {
                if (user_rights[i]['name'] === grandparent) {
                    grandparent_exists_in_user_rights = true;
                    var rights_lev_2 = user_rights[i]['children'];
                    for (j in rights_lev_2) {
                        if (rights_lev_2[j]['name'] === parent) {
                            parent_exists_in_user_rights = true;
                            var rights_lev_3 = rights_lev_2[j]['children'];
                            for (k in rights_lev_3) {
                                if (rights_lev_3[k]['name'] === d.data.name) {
                                    exists_in_user_rights = true
                                }
                            }
                        }
                    }
                }
            }
            for (i in transfer_rights) {
                if (transfer_rights[i]['name'] === grandparent) {
                    grandparent_exists_in_transfer_rights = true;
                    var rights_lev_2 = transfer_rights[i]['children'];
                    for (j in rights_lev_2) {
                        if (rights_lev_2[j]['name'] === parent) {
                            parent_exists_in_transfer_rights = true;
                            var rights_lev_3 = rights_lev_2[j]['children'];
                            for (k in rights_lev_3) {
                                if (rights_lev_3[k]['name'] === d.data.name) {
                                    exists_in_transfer_rights = true
                                }
                            }
                        }
                    }
                }
            }
            if (!exists_in_user_rights && !exists_in_transfer_rights) {
                if ((grandparent_exists_in_user_rights && parent_exists_in_user_rights)||(grandparent_exists_in_transfer_rights && parent_exists_in_transfer_rights)) {
                    return false;
                } else if (!grandparent_exists_in_user_rights && !grandparent_exists_in_transfer_rights) {
                    alert("TF kann nicht übertragen werden!\n\nUser besitzt nicht die nötige AF!");
                    return true;
                } else if ((grandparent_exists_in_user_rights && !parent_exists_in_user_rights)||(grandparent_exists_in_transfer_rights && !parent_exists_in_transfer_rights)) {
                    alert("TF kann nicht übertragen werden!\n\nUser besitzt benötigte AF\naber nicht die nötige GF!");
                    return true;
                }
            }else{
                alert("TF existiert bereits\nund kann nicht übertragen werden!");
                return true;
            }
        }
    }
    function transferfunction(d,i){
        d3.event.preventDefault();
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
        if(check_user_rights_for_existance(d,right_type,right_parent,right_grandparent, window.jsondata['children'],window.transferlistdata['children'])){
            return;
        }
        var r = confirm("Berechtigung:\n\n"+d.data.name+"\n\nwirklich zu Transferliste hinzufügen?\n\n");
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

            var data = {"X-CSRFToken":getCookie("csrftoken"),"X_METHODOVERRIDE":'PATCH',"user_pk":window.user_pk,"compare_user":window.compare_user,"action_type":"transfer","right_type":right_type,"right_name":d.data.name,"parent":right_parent,"grandparent":right_grandparent};
            var successful=false;
            $.ajax({type:'POST',
                    data:data,
                    url:'http://127.0.0.1:8000/users/'+window.user_pk+'/',
                    async:false,
                    success: function(res){console.log(res);
                        successful=true},
                    error: function(res){console.log(res);}
                    });
            if(successful===true){
                var compare_rights = window.compare_jsondata['children'];
                var user_rights = window.jsondata['children'];
                var transfer = window.transferlistdata['children'];
                update_rights(user_rights,compare_rights, transfer, d);

                d3.select("body").selectAll("#compareCPtooltip").remove();

                d3.select('#compareCirclePackingSVG').select("g").data(window.compare_jsondata).exit().remove();
                update(window['compare_jsondata']);

                d3.select('#transferSVG').select('g').data(window.transferlistdata).exit().remove();
                window.updateTransfer();
                //d3.select('#circlePackingSVG').select('g').data(window.jsondata).exit().remove();
                //window.updateCP();
                alert("Berechtigung zur\n\nTransferliste hinzugefügt\n");
                //update_session();
            }
        }
      }
      function update_right_counters(right,type){
        if (type === "af"){
            for (j in right['children']){
                window.transfer_table_count+=right['children'][j]['children'].length;
            }
            document.getElementById('graph_transfer_badge').innerHTML = window.transfer_table_count;
        }
        else if (type === "gf"){
            window.transfer_table_count+=right['children'].length;
            document.getElementById('graph_transfer_badge').innerHTML = window.transfer_table_count;
        }
        else if (type === "tf"){
            window.transfer_table_count+=1;
            document.getElementById('graph_transfer_badge').innerHTML = window.transfer_table_count;
        }
      }
      function add_to_transfer_list(transfer, right, parent_right, grandparent_right, level){
        if(level === "gf"){
            for(i in transfer){
                var curr_af = transfer[i];
                if(curr_af['name']===parent_right['name']){
                    curr_af['children'].push(right);
                    return;
                }
            }
            var parent_cpy = jQuery.extend({},parent_right);
            parent_cpy['children']=[right];
            transfer.push(parent_cpy);
        }
        if(level === "tf"){
            for(i in transfer){
                var curr_af = transfer[i];
                if(curr_af['name']===grandparent_right['name']){
                    var curr_af_gfs = curr_af['children'];
                    for(j in curr_af_gfs){
                        var curr_gf = curr_af_gfs[j];
                        if(curr_gf['name']===parent_right['name']){
                            curr_gf['children'].push(right);
                            return;
                        }
                    }

                }
            }
            var grandparent_cpy = jQuery.extend({},grandparent_right);
                var parent_cpy = jQuery.extend({},parent_right);
                parent_cpy['children']=[right];
                grandparent_cpy['children']=[parent_cpy];
                transfer.push(grandparent_cpy);
        }
      }

      //-------> TODO: an ein level für Rollen denken sobald rollen eingefügt
      function update_rights(user_rights,compare_rights, transfer, d){
        if (d.depth ===1){
            for (i in compare_rights) {
                if (compare_rights[i]['name'] === d.data.name) {
                    console.log(i + "," + d.data.name);
                    update_right_counters(compare_rights[i],"af");
                    transfer.push(compare_rights[i]);
                    //user_rights.push(compare_rights[i]);
                    return;
                }
            }
        }
        else if(d.depth===2){
            for (i in compare_rights) {
                var right = compare_rights[i];
                if (right['name'] === d.parent.data.name) {
                    for (j in right['children']) {
                        var right_lev_2 = right['children'][j];
                        if (right_lev_2['name'] === d.data.name) {
                            console.log(j + "," + d.data.name);
                            right_lev_2["parent"]=d.parent.data.name;
                            update_right_counters(right_lev_2,"gf");
                            //user_rights.push(right_lev_2);
                            add_to_transfer_list(transfer,right_lev_2,right,null,'gf');
                            return;
                        }
                    }
                }
            }
        }
        else if(d.depth===3){
            for (i in compare_rights) {
                var right = compare_rights[i];
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
                                    //user_rights.push(right_lev_3);
                                    add_to_transfer_list(transfer,right_lev_3,right_lev_2,right,'tf');
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
