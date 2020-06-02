function isValidLoan(loan_inputs) {
    $('.error').removeClass('error');
    let isValid = true;

    for (let [key, value] of Object.entries(loan_inputs)) {
        if (value <= 0) {
            $(`input[name="${key}"`).addClass('error');
            isValid = false;
        }
    }
      
    // comment out the if condition below to test validation from back-end (surfacing to front-end)
    // handle term_years exclusively as per described in instructions (if term_years > 30, show modal)
    if (loan_inputs['term_years'] > 30) {
        $(`input[name="term_years"`).addClass('error');
        $('#errorText').text("Term (years) needs to be an integer that is less than 30.");
        $('.modal').modal('show');
        isValid = false;
    }
            
    return isValid
}

$('#loanForm').submit(function(e){
    e.preventDefault();     

    let loan_inputs = {};
    $.each($("#loanForm").serializeArray(), function(i, field) {
        loan_inputs[field.name] = field.value;
    });

    if (isValidLoan(loan_inputs)) {
        $.ajax({
            url:'/loan/',
            type:"POST",
            timeout: 8000,
            data: JSON.stringify(loan_inputs),
            contentType:"application/json; charset=utf-8",
            dataType:"json",
            success: function(payment_plan_data){
                $(document).trigger('payment_plan_loaded', [payment_plan_data]);
            },
            error: function(xhr, textStatus, errorThrown){      
                let error_msg = "";
                if (xhr.statusText == "timeout") {
                    error_msg = "Response took longer than expected and timed out.";
                }
                else {
                    // showing validation error from backend    
                    error_msg = xhr.responseJSON.detail[0].msg;           
                }
                $('#errorText').text(error_msg);
                $('.modal').modal('show');
            }
        })
    }
});

$(document).on('payment_plan_loaded', function(event, plan_data) {
    let plan_fields = [];
    for (let [key, value] of Object.entries(plan_data[0])) {
        if (key != "month") {
            plan_fields.push({
                "data": String(key),
                "render": $.fn.dataTable.render.number( ',', '.', 2, '' )
            });
        }
        else {
            plan_fields.push({"data": String(key)});
        }
    }

    $("#payment_plan_table").dataTable().fnDestroy(); // avoid reinitialization error on new data-entry
    $('#payment_plan_table').DataTable({
        data: plan_data,
        columns: plan_fields,
        fixedHeader: {
            header: true,
        },
        aLengthMenu: [
            [25, 50, 100, 200, -1],
            [25, 50, 100, 200, 'All']
        ],
        iDisplayLength: -1
    });

    $('.input-area').fadeOut('fast');
    $('.show-input').text("Show Input Area");
    $('.output-area').fadeIn('slow');
});

$('.show-input').on('click', function(){
    if ($('.show-input').text() == "Show Input Area"){
        $('.input-area').fadeIn('fast');
        $('.show-input').text("Hide Input Area");
    }
    else {
        $('.input-area').fadeOut('fast');
        $('.show-input').text("Show Input Area");
    }
});