function remove_current_card(form, card_id, collapse_id){

    var inputs = form.serializeArray();
    console.log(inputs);

    var remove_confirm;
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
    var data = {"X-CSRFToken":getCookie("csrftoken"),"X_METHODOVERRIDE":'PATCH',"action_type":"remove_from_requests","requesting_user":inputs[1]['value'],"request_pk":inputs[0]['value']};
    var successful=false;

    remove_confirm = confirm("Anfrage aus Listung entfernen?");
    var user_res;
    if(remove_confirm){
        $.ajax({type:'POST',
                data:data,
                url:'http://127.0.0.1:8000/users/'+inputs[1]['value']+'/',
                async:false,
                success: function(res){console.log(res);
                    user_res = res;
                    successful=true},
                error: function(res){console.log(res);}
            });
        if (successful) {
            $.ajax({type:'DELETE',
                data:data,
                url:'http://127.0.0.1:8000/changerequests/'+inputs[0]['value']+'/',
                async:false,
                success: function(res){console.log(res);
                    successful=true},
                error: function(res){console.log(res);}
            });
            if (successful) {
                $('#'+card_id).remove();
                var list, partnerList, controll_id;
                if(card_id.includes('accepted_apply')){
                    list = window.accepted_apply;
                    partnerList = window.accepted_delete;
                    controll_id="#collapseAcceptedApplyButton"
                }
                else if(card_id.includes('accepted_delete')){
                    list = window.accepted_delete;
                    partnerList = window.accepted_apply;
                    controll_id="#collapseAcceptedDeleteButton"
                }
                else if(card_id.includes('declined_apply')){
                    list = window.declined_apply;
                    partnerList = window.declined_delete;
                    controll_id="#collapseDeclinedApplyButton"
                }
                else if(card_id.includes('declined_delete')){
                    list = window.declined_delete;
                    partnerList = window.declined_apply;
                    controll_id="#collapseDeclinedDeleteButton"
                }
                for(i in list){
                    var curr_pk = list[i]['request']['pk'];
                    console.log(curr_pk);
                    if (curr_pk===parseInt(inputs[0]['value'])){
                        list.splice(i,1);
                        break;
                    }
                }
                if(list.length === 0 && partnerList.length === 0){
                    $('#'+collapse_id).remove();
                }
                else if(list.length === 0 ){
                    $(controll_id).remove()
                }
                if(window.accepted_delete.length===0&&window.accepted_apply.length===0
                    &&window.declined_delete.length===0&&window.declined_apply.length===0
                    &&window.unanswered_delete.length===0&&window.unanswered_apply.length===0){
                    var empty_my_requests_div = $("<div class='container-fluid top-buffer'>" +
                            "<div class='card top-buffer'>" +
                            "<div class='card-header'>" +
                            "<h4 class='text-center'>Keine Anfragen vorhanden!</h4>" +
                            "</div></div></div>");
                    $("#content_container").append(empty_my_requests_div);
                }
                bootbox.alert("Request erfolgreich aus Listung\nund Requestpool entfernt!", function () {
                    console.log("Request erfolgreich aus Listung\nund Requestpool entfernt!");
                });
            }
            else{
                bootbox.alert("Beim Entfernen aus Requestpool\nist ein Fehler aufgetreten!", function () {
                    console.log("Beim Entfernen aus Requestpool\nist ein Fehler aufgetreten!");
                });
            }
        }
        else{
            bootbox.alert("Beim Entfernen aus Listung\nist ein Fehler aufgetreten!", function () {
                console.log("Beim Entfernen aus Listung\nist ein Fehler aufgetreten!");
            });
        }
    }


}


function remove_card_clicked(d) {
    var form = $(d);
    var current_card = $(d.parentElement.parentElement.parentElement.parentElement);
    var card_id = current_card[0].id;
    var current_collapse = $(d.parentElement.parentElement.parentElement.parentElement.parentElement.parentElement.parentElement.parentElement);
    var collapse_id = current_collapse[0].id;
    remove_current_card(form,card_id, collapse_id);
   return false;
}