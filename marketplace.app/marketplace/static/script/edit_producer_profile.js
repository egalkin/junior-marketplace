$(document).ready(function () {
    $('#save_producer_profile').click(function(){
        var addr = window.location + '';
        addr = addr.split('/');
        var producer_id = addr[addr.length - 2];
        var producerObject = {
            name: $('#producer_name').val(),
            person_to_contact: $('#producer_contact_person').val(),
            email: $('#producer_email').val(),
            // fileHelp: $('#producer_logo').val(),
            phone: $('#producer_phone').val(),
            address: $('#producer_adress').val(),
            description: $('#producer_description').val()
        };
        $.ajax({
            url: '/api/v1/producers/' + producer_id,
            type: 'PUT',
            contentType: 'application/json',
            data: JSON.stringify(producerObject),
            success: function(data, status) {
                
            }
        });
    });
});
