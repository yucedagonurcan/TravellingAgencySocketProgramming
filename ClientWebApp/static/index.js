$(document).ready(function () {

    $(function () {
        // Show alert function inputs strong and a regular message and success status
        // It will pıp up a alert.
        function ShowAlert(strong_msg, regular_msg, is_success) {
            if (is_success) {
                alert_type = "alert-success";
            } else {
                alert_type = "alert-warning";
            }
            $("#info-alert").addClass(alert_type);
            $("#info-alert").html(`<strong>${strong_msg}</strong> ${regular_msg}`);
            $("#info-alert").show()

            $("#info-alert").fadeTo(2000, 500).slideUp(500, function () {
                $(this).hide();
                $(this).removeClass(alert_type);
            });

        }
        // Post message object for sending to the back-end.
        post_msg = {
            "starting_date": null,
            "return_date": null,
            "preferred_hotel": null,
            "preferred_airline": null,
            "people_count": null
        };


        $("#starting_date_picker").datepicker({
            changeYear: true,
            changeMonth: true,
            minDate: 0,
            dateFormat: "dd/m/yy",
            yearRange: "-100:+20",
        });
        $("#return_date_picker").datepicker({
            changeYear: true,
            changeMonth: true,
            yearRange: "-100:+20",
            dateFormat: "dd/m/yy",
        });

        // If search_travel button is clicked:
        // -- Get the starting, return date, preferred hotel, airline and people count.
        // -- If dates are not specified show as invalid 
        $("#search_travel").click(function () {

            var send_msg = true;
            post_msg["starting_date"] = $('#starting_date_picker').val();
            post_msg["return_date"] = $('#return_date_picker').val();

            post_msg["preferred_hotel"] = $("#select-hotel-button").text();
            post_msg["preferred_airline"] = $("#select-airline-button").text()
            post_msg["people_count"] = $('#people_cnt').val();

            if (post_msg["starting_date"].length == 0) {
                $('#starting_date_picker').addClass("is-invalid");
                send_msg = false;
            }
            if (post_msg["return_date"].length == 0) {
                $('#return_date_picker').addClass("is-invalid");
                send_msg = false;
            }
            if (post_msg["preferred_hotel"] == "Preferred hotel" || post_msg["preferred_airline"] == "Preferred airline") {

                send_msg = false;
            }

            $("#select-hotel-button").removeClass("btn-secondary");
            $("#select-hotel-button").addClass("btn-success");

            $("#select-airline-button").removeClass("btn-secondary");
            $("#select-airline-button").addClass("btn-success");
            if (send_msg) {

                $('#starting_date_picker').removeClass("is-invalid");
                $('#return_date_picker').removeClass("is-invalid");

                // Trip Advisor Server check if dates are available for preferred hotel and airplane if it is
                // it will return Success and if not, it will return alternative airlplanes and hotels if it finds any.
                // If there is no alternative it will simply return Failure.
                $.post("/check_dates", post_msg, (msg) => {

                    splitted_msg = msg.split("||");

                    if (msg == "Success||Success") {
                        $('#accept_reject_modal_single').modal('toggle');
                    } else if (msg == "Failure||Failure" || splitted_msg[0] == "Failure" || splitted_msg[1] == "Failure") {
                        ShowAlert("No Luck!", "There is no place for you.", false);
                    } else {
                        var splitted_msg = msg.split("||");
                        if (splitted_msg[0] == "Success") {
                            splitted_msg[0] = post_msg["preferred_airline"]
                        }
                        if (splitted_msg[1] == "Success") {
                            splitted_msg[1] = post_msg["preferred_hotel"]
                        }

                        var airline_alternatives = splitted_msg[0].split(";");
                        var hotel_alternatives = splitted_msg[1].split(";");

                        $("#select-alternative-airline").empty();
                        $("#select-alternative-hotel").empty();
                        $("#select-alternative-airline-button").text("Select airline");
                        $("#select-alternative-hotel-button").text("Select hotel");

                        airline_alternatives.forEach(function (element) {
                            a_element = `<a class="dropdown-item" href="#">${element}</a>`;
                            $("#select-alternative-airline").append(a_element);
                        });
                        hotel_alternatives.forEach(function (element) {
                            a_element = `<a class="dropdown-item" href="#">${element}</a>`;
                            $("#select-alternative-hotel").append(a_element);

                            $("#select-alternative-hotel-button").removeClass("btn-success");
                            $("#select-alternative-hotel-button").addClass("btn-secondary");

                            $("#select-alternative-airline-button").removeClass("btn-success");
                            $("#select-alternative-airline-button").addClass("btn-secondary");

                            $('#accept_reject_modal_alternative').modal('toggle');
                            $("#select-alternative-airline > a").click(function (e) {
                                var text = $(this).text();
                                $("#select-alternative-airline-button").text(text);
                            });
                            $("#select-alternative-hotel > a").click(function (e) {
                                var text = $(this).text();
                                $("#select-alternative-hotel-button").text(text);
                            });
                        });
                    }


                });
            }
        });

        // Accept the original preferred hotel and airline offer.
        $('#accept_offer_single').click(() => {
            $.post("/accept_dates", post_msg, (msg) => {
                if (msg == "Success||Success") {
                    ShowAlert("All OK", "Successfully booked your place.", true);
                } else {
                    ShowAlert("ERROR", "There is something wrong. Internal Error.", false);
                }
            });
        });

        // Accept the alternative hotel and airline offer.
        $('#accept_offer_alternative').click(() => {

            var send_msg = true;
            if ($("#select-alternative-airline-button").text() != "Select airline") {

                post_msg["preferred_airline"] = $("#select-alternative-airline-button").text();
            } else {
                send_msg = false;
            }
            if ($("#select-alternative-hotel-button").text() != "Select hotel") {

                post_msg["preferred_hotel"] = $("#select-alternative-hotel-button").text();
            } else {
                send_msg = false;
            }
            $("#select-alternative-hotel-button").removeClass("btn-secondary");
            $("#select-alternative-hotel-button").addClass("btn-success");

            $("#select-alternative-airline-button").removeClass("btn-secondary");
            $("#select-alternative-airline-button").addClass("btn-success");

            if (send_msg) {

                $.post("/accept_dates", post_msg, (msg) => {

                    if (msg == "Success||Success") {
                        ShowAlert("Great Choice", "Successfully booked your alternative place.", true);
                    } else {
                        ShowAlert("ERROR", "There is something wrong. Internal Error.", false);
                    }
                });
            }
        });

        $("#inc_people").click(() => {
            var people_count = parseInt($('#people_cnt').val());
            if (Number.isNaN(people_count)) {
                people_count = 1;
            } else {
                people_count = people_count + 1;
            }
            $('#people_cnt').val(people_count);

        });
        $("#dec_people").click(function (e) {
            var people_count = parseInt($('#people_cnt').val());
            if (Number.isNaN(people_count) || people_count == 1) {
                people_count = 1;
            } else {
                people_count = people_count - 1;
            }
            $('#people_cnt').val(people_count);

        });
        $("#select-airline > a").click(function (e) {
            var text = $(this).text();
            $("#select-airline-button").text(text);
        });
        $("#select-hotel > a").click(function (e) {
            var text = $(this).text();
            $("#select-hotel-button").text(text);
        });


    });
});