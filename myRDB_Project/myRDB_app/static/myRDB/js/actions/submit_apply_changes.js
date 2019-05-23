function insert_change_request_to_database(formElement){
    var inputs = formElement.serializeArray();
    console.log(inputs);
    var csrf_middleware_token = inputs[0];
    var requesting_user = inputs[1];
    var compare_user = inputs[2];
    var repacked_objects = [];
    for(var i=3;i<inputs.length;i+=4){
        repacked_objects.push([inputs[i],inputs[i+1],inputs[i+2],inputs[i+3]]);
    }
    console.log(repacked_objects);
    var r = confirm("Änderungen beantragen?\n\n");
    if (r === true) {
        var res =make_changerequest(repacked_objects,requesting_user,csrf_middleware_token,compare_user);
        if (res === true){
            return true;
        }
        else{
            return false;
        }
    }
}
function make_changerequest(repacked_objects,requesting_user,csrf_middleware_token,compare_user){
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
        var objects_to_change = JSON.stringify(repacked_objects);
        var data = {"X-CSRFToken":getCookie("csrftoken"),"requesting_user":requesting_user,"compare_user":compare_user,"objects_to_change":objects_to_change};
        var successful=false;
        var response_data;
        $.ajax({type:'POST',
                data:data,
                url:'http://127.0.0.1:8000/changerequests/',
                async:false,
                success: function(res){console.log(res);
                    response_data = res;
                    successful=true},
                error: function(res){console.log(res);}
                });
        if (successful){
            data = {"X-CSRFToken":getCookie("csrftoken"),"X_METHODOVERRIDE":'PATCH',"action_type":"add_to_requests","requesting_user":requesting_user,"request_pks":response_data};
            successful=false;
            $.ajax({type:'POST',
                    data:data,
                    url:'http://127.0.0.1:8000/users/'+requesting_user['value']+'/',
                    async:false,
                    success: function(res){console.log(res);
                        successful=true},
                    error: function(res){console.log(res);}
                });
            if(successful){
                data = {"X-CSRFToken":getCookie("csrftoken"),"X_METHODOVERRIDE":'PATCH',"action_type":"set_rights_as_requested","requesting_user":requesting_user, "objects_to_change": objects_to_change};
                successful=false;
                $.ajax({type:'POST',
                        data:data,
                        url:'http://127.0.0.1:8000/users/'+requesting_user['value']+'/',
                        async:false,
                        success: function(res){console.log(res);
                            successful=true},
                        error: function(res){console.log(res);}
                    });
                if(successful){
                    bootbox.alert("Antrag erfolgreich gestellt!",function(){
                        console.log("Antrag erfolgreich gestellt!");
                    });
                    return true;
                }else{
                    bootbox.alert("Beim leeren der Transfer- und Deleteliste \n ist ein Fehler aufgetreten!",function(){
                        console.log("Beim leeren der Transfer- und Deleteliste \n ist ein Fehler aufgetreten!");
                    });
                }
            }else{
                bootbox.alert("Beim hinzufügen zu MyRequests \n ist ein Fehler aufgetreten!",function(){
                    console.log("Beim hinzufügen zu MyRequests \n ist ein Fehler aufgetreten!");
                });
            }
        }
        else {
            bootbox.alert("Beim erstellen der Requests \n ist ein Fehler aufgetreten!", function () {
                console.log("Beim erstellen der Requests \n ist ein Fehler aufgetreten!");
            });
        }
    return false;
}

$('.apply-changes-form').submit(function () {
   var success = insert_change_request_to_database($(this));
   if(success){
       return true;
   }else{
       return false;
   }

});