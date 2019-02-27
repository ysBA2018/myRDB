$(document).ready(function() {
    transfer_table = $('#transfer_table').DataTable({
        "pageLength":3,
        "aLengthMenu":[[3,10,25,50,100,-1],[3,10,25,50,100,"All"]],
        "createdRow":function (row, data, dataIndex) {
            $(row).addClass("darkgrey");
        },
        "order":[[2,'asc']]
    });

    $('#transfer_table tbody').on('contextmenu', 'td', function (e) {
        e.preventDefault();
        var cell_data = window.transfer_table.cell( this ).data();
        var colIndex = window.transfer_table.cell(this).index().column;
        var rowIndex = window.transfer_table.cell( this ).index().row;
        var row_data=window.transfer_table.row(rowIndex).data();
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
        var r = confirm("Berechtigung:\n\n"+cell_data+"\n\nwirklich von Transferliste entfernen?\n\n");
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
            var data = {"X-CSRFToken":getCookie("csrftoken"),"X_METHODOVERRIDE":'PATCH',"user_pk":window.user_pk,"action_type":"restore_transfer","right_type":right_type,"right_name":cell_data,"parent":right_parent,"grandparent":right_grandparent};
            var successful=false;
            $.ajax({type:'POST',
                    data:data,
                    url:'http://127.0.0.1:8000/users/'+window.user_pk+'/',
                    async:false,
                    success: function(res){console.log("Success!: "+res);
                        update_table_data(cell_data,right_type,row_data);
                        alert("Berechtigung von\n\nTransferliste entfernt!\n");
                        },
                    error: function(res){console.log(res);}
                    });
        }
    } ).on('mouseenter', 'td', function (e) {
        e.preventDefault();
        var colIndex = window.transfer_table.cell(this).index().column;
        $(window.transfer_table.cells().nodes()).removeClass('highlight');
        $(window.transfer_table.column(colIndex).nodes()).addClass('highlight');
    });
    function update_table_data(cell_data,right_type,row_data) {
        var rows_to_restore = [];
        var data_to_reset_color = [];
        if (right_type==="af"){
            window.transfer_table.rows().every(function(rowIdx,tableLoop,rowLoop){
               var data = this.data();
               if(data[2]===cell_data){
                   data_to_reset_color.push(data);
                   rows_to_restore.push(this.node());
                   window.transfer_table_count-=1;
                   document.getElementById('transfer_badge').innerHTML = window.transfer_table_count;
               }
            });
        }
        if (right_type==="gf"){
            window.transfer_table.rows().every(function(rowIdx,tableLoop,rowLoop){
               var data = this.data();
               if(data[1]===cell_data&&data[2]===row_data[2]){
                   data_to_reset_color.push(data);
                   rows_to_restore.push(this.node());
                   window.transfer_table_count-=1;
                   document.getElementById('transfer_badge').innerHTML = window.transfer_table_count;
               }
            });
        }
        //TODO: noch so ändern, dass row nicht ers gesucht werden muss sondern direkt geTransfert wird!
        if (right_type==="tf"){
            window.transfer_table.rows().every(function(rowIdx,tableLoop,rowLoop){
               var data = this.data();
               if(data[0]===cell_data&&data[1]===row_data[1]&&data[2]===row_data[2]){
                   data_to_reset_color.push(data);
                   rows_to_restore.push(this.node());
                   window.transfer_table_count-=1;
                   document.getElementById('transfer_badge').innerHTML = window.transfer_table_count;
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
        rows_to_restore.forEach(function(node){
           window.transfer_table.row(node).remove().draw();
        });
        window.transfer_table.draw();
        window.compare_data_table.draw();
    }
} );