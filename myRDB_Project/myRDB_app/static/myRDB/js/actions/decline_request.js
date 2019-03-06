function change_request_state_to_declined(formElement) {
    var inputs = formElement.serializeArray();
    console.log("in decline-request");
    console.log(inputs);
}

$('.decline-form').submit(function () {
    change_request_state_to_declined($(this));
   return false;
});