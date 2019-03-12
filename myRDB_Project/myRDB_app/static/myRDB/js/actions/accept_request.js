function change_request_state_to_accepted_and_perform_action(formElement, current_card) {
    var inputs = formElement.serializeArray();
    console.log("in accept-request");
    console.log(inputs);
        var r = confirm("Antrag wirklich gestatten?\n\n");
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
        var data = {"X-CSRFToken":getCookie("csrftoken"),"X_METHODOVERRIDE":'PATCH',"action_type":"accept_request"};
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
            data = {"X-CSRFToken":getCookie("csrftoken"),"X_METHODOVERRIDE":'PATCH',"action_type":"perform_action", "request_data":JSON.stringify(response_data)};
            successful=false;
            $.ajax({type:'POST',
                    data:data,
                    url:'http://127.0.0.1:8000/users/'+response_data['requesting_user_pk']+"/",
                    async:false,
                    success: function(res){console.log(res);
                        response_data = res;
                        successful=true},
                    error: function(res){console.log(res);}
                    });
            if (successful){
                //var collapsible = current_card.parentElement;
                //collapsible.pop(current_card);
                var id = current_card[0].id;
                console.log(id);
                $('#'+id).remove();
                alert("Antrag stattgegeben!");

            }
            else{
                alert("Beim durchführen der Änderungen \n ist ein Fehler aufgetreten!")
            }
        }else{
            alert("Beim ändern des Antragsstatus \n ist ein Fehler aufgetreten!")
        }
    }
}

function accept_clicked(d) {
    var form = $(d);
    var current_card = $(d.parentElement.parentElement.parentElement.parentElement.parentElement.parentElement.parentElement.parentElement);
    change_request_state_to_accepted_and_perform_action(form,current_card);
   return false;
}