function change_request_state_to_accepted_and_perform_action(formElement) {
    var inputs = formElement.serializeArray();
    console.log("in accept-request");
    console.log(inputs);
}

$('.decline-form').submit(function () {
    change_request_state_to_accepted_and_perform_action($(this));
   return false;
});