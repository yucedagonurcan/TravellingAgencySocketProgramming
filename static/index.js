$(document).ready(function () {

    $(function () {
        $("#starting_date_picker").datepicker();
        $("#return_date_picker").datepicker();
        $("#search_travel").click(function () {

            var send_msg = true;
            var start_date = $('#starting_date_picker').val();
            var return_date = $('#return_date_picker').val();
            if (start_date.length == 0) {
                $('#starting_date_picker').addClass("is-invalid");
                var send_msg = false;
            }
            if (return_date.length == 0) {
                $('#return_date_picker').addClass("is-invalid");
                var send_msg = false;
            }
            if (send_msg) {

                $('#starting_date_picker').removeClass("is-invalid");
                $('#return_date_picker').removeClass("is-invalid");
                $.post("/send_data", {
                    'starting_date': start_date,
                    'return_date': return_date
                }, (msg) => {
                    alert("Data sent. " + msg);
                });
            }

        });

        $("#inc_people").click(() => {
            var people_count = parseInt($('#people_cnt').val());
            if (Number.isNaN(people_count)) {
                people_count = 0;
            } else {
                people_count = people_count + 1;
            }
            $('#people_cnt').val(people_count);

        })
        $("#dec_people").click(() => {
            var people_count = parseInt($('#people_cnt').val());
            if (Number.isNaN(people_count) || people_count == 0) {
                people_count = 0;
            } else {
                people_count = people_count - 1;
            }
            $('#people_cnt').val(people_count);

        })

    });
})