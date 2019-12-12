$(document).ready(function () {

    $(function () {
        post_msg = {
            "starting_date": null,
            "return_date": null,
            "preferred_hotel": null,
            "preferred_airline": null,
            "people_count": null
        };


        $("#starting_date_picker").datepicker();
        $("#return_date_picker").datepicker();
        $("#search_travel").click(function () {

            send_msg = true;
            post_msg["starting_date"] = $('#starting_date_picker').val();
            post_msg["return_date"] = $('#return_date_picker').val();

            post_msg["preferred_hotel"] = $("#select-hotel-button").text();
            post_msg["preferred_airline"] = $("#select-airline-button").text()
            post_msg["people_count"] = $('#people_cnt').val();

            if (post_msg["starting_date"].length == 0) {
                $('#starting_date_picker').addClass("is-invalid");
                var send_msg = false;
            }
            if (post_msg["return_date"].length == 0) {
                $('#return_date_picker').addClass("is-invalid");
                var send_msg = false;
            }
            if (send_msg) {

                $('#starting_date_picker').removeClass("is-invalid");
                $('#return_date_picker').removeClass("is-invalid");
                $.post("/check_dates", post_msg, (msg) => {
                    if (msg == "Success") {
                        $('#accept_reject_modal').modal('toggle');
                    } else {
                        alert("There is no place for you.");
                    }
                });
            }

        });
        $('#accept_offer').click(() => {
            $.post("/accept_dates", post_msg, (msg) => {
                if (msg == "Success") {
                    alert("Successfully booked place.");
                } else {
                    alert("There is something wrong.");
                }
            });
        })

        $("#inc_people").click(() => {
            var people_count = parseInt($('#people_cnt').val());
            if (Number.isNaN(people_count)) {
                people_count = 1;
            } else {
                people_count = people_count + 1;
            }
            $('#people_cnt').val(people_count);

        })
        $("#dec_people").click(function (e) {
            var people_count = parseInt($('#people_cnt').val());
            if (Number.isNaN(people_count) || people_count == 1) {
                people_count = 1;
            } else {
                people_count = people_count - 1;
            }
            $('#people_cnt').val(people_count);

        })
        $("#select-airline > a").click(function (e) {
            var text = $(this).text();
            $("#select-airline-button").text(text);
        });
        $("#select-hotel > a").click(function (e) {
            var text = $(this).text();
            $("#select-hotel-button").text(text);
        });
    });
})