function check_for_row_in_user_table(row,data,dataIndex){
    var tbl_dta = window.compare_user_table_data;
    var data_table_stripped = tbl_dta.replace(/(&#39;)|(\s)/g,"");
    var contains = data_table_stripped.includes(data);
    if(contains){
        $(row).addClass("darkgrey");
    }
}

$(document).ready(function() {
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
    $('#data_table tbody tr').each( function() {
        var sTitle;
        console.log(this);
        var user_data = window.jsondata;

        for (i in user_data['children']){
            if(user_data['children'][i]['name']===this.lastElementChild.textContent){
                var right = user_data['children'][i];
                break;
            }
        }
        var text = "AF-Beschreibung: "+ right['description']+"\nAF gültig seit: "+right['af_applied'];

        this.setAttribute( 'title', text );
    } );

    data_table = $('#data_table').DataTable({
        "processing": true,
        "serverSide": false,
        "pageLength":10,
        "aLengthMenu":[[10,25,50,100,-1],[10,25,50,100,"All"]],
        "createdRow":function (row, data, dataIndex) {
            if (window.current_site === 'compare') {
                check_for_row_in_user_table(row, data, dataIndex);
            }
        },
        "order":[[2,'asc']]
    });
    data_table.$('tr').tooltip();


    $('#data_table tbody').on('contextmenu', 'td', function (e) {
        e.preventDefault();

        var cell_data = window.data_table.cell( this ).data();
        var colIndex = window.data_table.cell(this).index().column;
        var rowIndex = window.data_table.cell( this ).index().row;
        var row_data=window.data_table.row(rowIndex).data();
        var right_type="",right_parent = "",right_grandparent = "";
        if(colIndex===0){
            right_type="tf";
            right_grandparent = row_data[2];
            right_parent = row_data[1];
        }else if (colIndex===1){
            right_type="gf";
            right_parent = row_data[2];
        }else if (colIndex===2){
            right_type="af";
        }

        var r = confirm("Berechtigung:\n\n"+cell_data+"\n\nwirklich zu Löschliste hinzufügen?\n\n");
        if (r === true){

            var data = {"X-CSRFToken":getCookie("csrftoken"),"X_METHODOVERRIDE":'PATCH',"user":window.user,"action_type":"trash","right_type":right_type,"right_name":cell_data,"parent":right_parent,"grandparent":right_grandparent};
            var successful=false;
            $.ajax({type:'POST',
                    data:data,
                    url:'http://127.0.0.1:8000/users/'+window.user+'/',
                    async:false,
                    success: function(res){console.log(res);
                        alert("Berechtigung zur\n\nLöschliste hinzugefügt\n");
                        successful=true},
                    error: function(res){console.log(res);}
                    });
            if(successful===true){
                console.log("success!");
                update_table_data(cell_data,right_type,row_data);
                if(window.current_site==="compare"){
                    window.compare_data_table.draw();
                }
            }
        }
    } ).on('mouseenter', 'td', function (e) {
        e.preventDefault();
        var colIndex = window.data_table.cell(this).index().column;
        $(window.data_table.cells().nodes()).removeClass('highlight');
        $(window.data_table.column(colIndex).nodes()).addClass('highlight');
    });
    function update_table_data(cell_data,right_type,row_data) {
        var rows_to_delete = [];
        var data_to_reset_color = [];
        if (right_type==="af"){
            var old_gfs=[];
            window.data_table.rows().every(function(rowIdx,tableLoop,rowLoop){
               var data = this.data();
               if(data[2]===cell_data){
                   rows_to_delete.push(this.node());
                   data_to_reset_color.push(data);
                   window.trash_table.row.add(data).draw();
                   window.trash_table_count+=1;
                   document.getElementById('trash_badge').innerHTML = window.trash_table_count;
               }
            });
        }
        if (right_type==="gf"){
            window.data_table.rows().every(function(rowIdx,tableLoop,rowLoop){
               var data = this.data();
               if(data[1]===cell_data&&data[2]===row_data[2]){
                   data_to_reset_color.push(data);
                   rows_to_delete.push(this.node());
                   window.trash_table.row.add(data).draw();
                   window.trash_table_count+=1;
                   document.getElementById('trash_badge').innerHTML = window.trash_table_count;
               }
            });
        }
        //TODO: noch so ändern, dass row nicht ers gesucht werden muss sondern direkt gelöscht wird!
        if (right_type==="tf"){
            window.data_table.rows().every(function(rowIdx,tableLoop,rowLoop){
               var data = this.data();
               if(data[0]===cell_data&&data[1]===row_data[1]&&data[2]===row_data[2]){
                   data_to_reset_color.push(data);
                   rows_to_delete.push(this.node());
                   window.trash_table.row.add(data).draw();
                   window.trash_table_count+=1;
                   document.getElementById('trash_badge').innerHTML = window.trash_table_count;
               }
            });
        }
        window.compare_data_table.rows().every(function (rowIdx, tableLoop, rowLoop) {
           var data = this.data();
           if(data_to_reset_color.length===1){
               if (data_to_reset_color[0] ===data){
                   this.nodes().to$().removeClass("darkgrey");
               }
           }
           else{
               if(data_to_reset_color.includes(data)){
                   this.nodes().to$().removeClass("darkgrey");
               }
           }
        });
        rows_to_delete.forEach(function(node){
           window.data_table.row(node).remove().draw();
        });
        window.data_table.draw();
        window.compare_data_table.draw();
    }
} );