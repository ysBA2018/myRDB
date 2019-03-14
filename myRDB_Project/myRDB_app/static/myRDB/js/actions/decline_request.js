function change_request_state_to_declined(formElement, current_card_id, current_user_collapse_id, current_user_id, content_div) {
    var inputs = formElement.serializeArray();
    console.log("in decline-request");
    console.log(inputs);
    var r = confirm("Antrag wirklich abweisen?\n\n");
    if (r === true) {
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
            beforeSend: function (xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
                }
            }
        });
        var data = {"X-CSRFToken":getCookie("csrftoken"),"X_METHODOVERRIDE":'PATCH',"action_type":"decline_request","reason_for_decline":inputs[1]['value']};
        var successful=false;
        var response_data;
        $.ajax({type:'POST',
                data:data,
                url:'http://127.0.0.1:8000/changerequests/'+inputs[2]['value']+"/",
                async:false,
                success: function(res){console.log(res);
                    response_data = res;
                    successful=true},
                error: function(res){console.log(res);}
                });
        if (successful){
            data = {"X-CSRFToken":getCookie("csrftoken"),"X_METHODOVERRIDE":'PATCH',"action_type":"decline_action", "request_data":JSON.stringify(response_data)};
            successful=false;
            $.ajax({type:'POST',
                    data:data,
                    url:'http://127.0.0.1:8000/users/'+response_data['requesting_user']+"/",
                    async:false,
                    success: function(res){console.log(res);
                        response_data = res;
                        successful=true},
                    error: function(res){console.log(res);}
                    });
            if (successful){
                $('#'+current_card_id).remove();
                var list,partner_list, toggle_button_id;
                if(current_card_id.includes('delete')){
                    list = window["user_delete_requests"+current_user_id];
                    partner_list = window["user_apply_requests"+current_user_id];
                    toggle_button_id = "#deleteButton"+current_user_id;
                }
                else if(current_card_id.includes('apply')){
                    list = window["user_apply_requests"+current_user_id];
                    partner_list = window["user_delete_requests"+current_user_id];
                    toggle_button_id = "#applyButton"+current_user_id;
                }
                for(i in list){
                    var curr_pk = list[i]['request_pk'];
                    console.log(curr_pk);
                    if (curr_pk===parseInt(inputs[2]['value'])){
                        list.splice(i,1);
                        break;
                    }
                }
                if(list.length === 0 && partner_list.length === 0){
                    $('#'+current_user_collapse_id).remove();
                }
                else if(list.length === 0 ){
                    $(toggle_button_id).remove()
                }
                if(content_div[0]['children'].length===0){
                    var empty_my_requests_div = $("<div class='container-fluid top-buffer'>" +
                        "<div class='card top-buffer'>" +
                        "<div class='card-header'>" +
                        "<h4 class='text-center'>Keine Anfragen im Pool vorhanden!</h4>" +
                        "</div></div></div>");
                    $("#content_container").append(empty_my_requests_div);
                }

                alert("Antrag abgewiesen!");

            }
            else{
                alert("Beim durchführen der Abweisung \n ist ein Fehler aufgetreten!")
            }
        }else{
            alert("Beim ändern des Antragsstatus \n ist ein Fehler aufgetreten!")
        }
    }
}
function decline_clicked(d) {
    var form = $(d);
    var current_card = $(d.parentElement.parentElement.parentElement.parentElement.parentElement.parentElement.parentElement.parentElement);
    var current_card_id = current_card[0].id;
    console.log(current_card_id);
    var current_user_collapse = $(d.parentElement.parentElement.parentElement.parentElement.parentElement.parentElement.parentElement.parentElement.parentElement.parentElement.parentElement.parentElement);
    var current_user_collapse_id = current_user_collapse[0].id;
    console.log(current_user_collapse);
    var current_user_id =current_card_id.charAt(current_card_id.length-2);
    console.log(window['user_apply_requests'+current_user_id]);
    console.log(window['user_delete_requests'+current_user_id]);

    var content_div = $(d.parentElement.parentElement.parentElement.parentElement.parentElement.parentElement.parentElement.parentElement.parentElement.parentElement.parentElement.parentElement.parentElement);

    change_request_state_to_declined(form,current_card_id, current_user_collapse_id, current_user_id, content_div);
   return false;
}
