$(document).ready(function () {

    $(function () {
        $("#starting_date_picker").datepicker();
        $("#return_date_picker").datepicker();
        $("#search_travel").click(function () {
            var start_date = $('#starting_date_picker').val();
            var return_date = $('#return_date_picker').val();
            if (start_date.length == 0) {
                $('#starting_date_picker').addClass("is-invalid");
            }
            if (return_date.length == 0) {
                $('#return_date_picker').addClass("is-invalid");
            }
            $('#starting_date_picker').addClass("is-valid");
            $('#return_date_picker').addClass("is-valid");

            $.post("/send_data", {
                'starting_date': start_date,
                'return_date': return_date
            }, (msg) => {
                alert("Data sent. " + msg);
            })

        });
    });
})