function check_for_row_in_user_and_transfer_table(row,data,dataIndex){
    var data_table = window.user_table_data;
    var data_table_stripped = data_table.replace(/(&#39;)|(\s)/g,"");
    var contains = data_table_stripped.includes(data);
    if(contains){
        $(row).addClass("darkgrey");
    }
    data_table = window.transfer_list_table_data;
    data_table_stripped = data_table.replace(/(&#39;)|(\s)/g,"");
    contains = data_table_stripped.includes(data);
    if(contains){
        $(row).addClass("darkgrey");
    }
}

$(document).ready(function() {

    compare_data_table = $('#compare_data_table').DataTable({
        "pageLength":10,
        "aLengthMenu":[[10,25,50,100,-1],[10,25,50,100,"All"]],
        "createdRow":function (row, data, dataIndex) {
            check_for_row_in_user_and_transfer_table(row,data,dataIndex);
        },
        "order":[[2,'asc']]
    });
    function check_for_parent_existance(type, parent, grandparent){
        var data_table = window.transfer_list_table_data;
        var data_table_stripped = data_table.replace(/(&#39;)|(\s)/g,"");
        if(type==="gf"){
            var contains = data_table_stripped.includes(parent);
            if(contains){
                return true;
            }
            else{
                data_table = window.user_table_data;
                data_table_stripped = data_table.replace(/(&#39;)|(\s)/g,"");
                contains = data_table_stripped.includes(parent);
                if(contains){
                    return true;
                }
                alert("GF kann nicht übertragen werden!\n\nUser besitzt nicht die nötige AF!");
                return false;
            }

        }
        if(type==="tf"){
            var contains = data_table_stripped.includes(grandparent);
            if(contains){
                contains = data_table_stripped.includes(parent);
                if(contains) {
                    return true;
                }
                else{
                    alert("TF kann nicht übertragen werden!\n\nUser besitzt benötigte AF\naber nicht die nötige GF!");
                    return false;
                }
            }
            else{
                data_table = window.user_table_data;
                data_table_stripped = data_table.replace(/(&#39;)|(\s)/g,"");
                contains = data_table_stripped.includes(grandparent);
                if(contains){
                    contains = data_table_stripped.includes(parent);
                    if(contains) {
                        return true;
                    }
                    else{
                        alert("TF kann nicht übertragen werden!\n\nUser besitzt benötigte AF\naber nicht die nötige GF!");
                        return false;
                    }
                }
                alert("TF kann nicht übertragen werden!\n\nUser besitzt nicht die nötige AF!");
                return false;
            }
        }
    }

    $('#compare_data_table tbody').on('contextmenu', 'td', function (e) {
        e.preventDefault();

        var cell_data = window.compare_data_table.cell( this ).data();
        var colIndex = window.compare_data_table.cell(this).index().column;
        var rowIndex = window.compare_data_table.cell( this ).index().row;
        var row_data=window.compare_data_table.row(rowIndex).data();

        var row_node = window.compare_data_table.row(rowIndex).node();
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
        if(right_type!=="af"&&!check_for_parent_existance(right_type,right_parent,right_grandparent)){
            return;
        }
        //console.log(this.parentElement.className);
        if(!(this.parentElement.className==="darkgrey even")&&!(this.parentElement.className==="darkgrey odd")){
            var r = confirm("Berechtigung:\n\n"+cell_data+"\n\nwirklich zu Transferliste hinzufügen?\n\n");
        }else{
            alert("Berechtigung existiert bereits!\n");
            return;
        }
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
            var data = {"X-CSRFToken":getCookie("csrftoken"),"X_METHODOVERRIDE":'PATCH',"user_pk":window.user_pk,"compare_user":window.compare_user,"action_type":"transfer","right_type":right_type,"right_name":cell_data,"parent":right_parent,"grandparent":right_grandparent};
            var successful=false;
            $.ajax({type:'POST',
                    data:data,
                    url:'http://127.0.0.1:8000/users/'+window.user_pk+'/',
                    async:false,
                    success: function(res){console.log(res);
                        alert("Berechtigung zur\n\nTransferliste hinzugefügt\n");
                        successful=true},
                    error: function(res){console.log(res);}
                    });
            if(successful===true){
                console.log("success!");
                update_table_data(cell_data,right_type,row_data);
            }
        }
    } ).on('mouseenter', 'td', function (e) {
        e.preventDefault();
        var colIndex = window.compare_data_table.cell(this).index().column;
        $(window.compare_data_table.cells().nodes()).removeClass('highlight');
        $(window.compare_data_table.column(colIndex).nodes()).addClass('highlight');
    });
    function update_table_data(cell_data,right_type,row_data) {
        if (right_type==="af"){
            window.compare_data_table.rows().every(function(rowIdx,tableLoop,rowLoop){
               var data = this.data();
               if(data[2]===cell_data){
                   this.nodes().to$().addClass("darkgrey");
                   window.transfer_table.row.add(data).draw();
                   window.transfer_table_count+=1;
                   document.getElementById('transfer_badge').innerHTML = window.transfer_table_count;
               }
            });
        }
        if (right_type==="gf"){
            window.compare_data_table.rows().every(function(rowIdx,tableLoop,rowLoop){
               var data = this.data();
               if(data[1]===cell_data&&data[2]===row_data[2]){
                   this.nodes().to$().addClass("darkgrey");
                   window.transfer_table.row.add(data).draw();
                   window.transfer_table_count+=1;
                   document.getElementById('transfer_badge').innerHTML = window.transfer_table_count;
               }
            });

        }
        //TODO: noch so ändern, dass row nicht ers gesucht werden muss sondern direkt getransfert wird!
        if (right_type==="tf"){
            window.compare_data_table.rows().every(function(rowIdx,tableLoop,rowLoop){
               var data = this.data();
               if(data[0]===cell_data&&data[1]===row_data[1]&&data[2]===row_data[2]){
                   this.nodes().to$().addClass("darkgrey");
                   window.transfer_table.row.add(data).draw();
                   window.transfer_table_count+=1;
                   document.getElementById('transfer_badge').innerHTML = window.transfer_table_count;
               }
            });
        }
    }
} );