$(function () {
//        var numberOfMonths;
//        if (window.matchMedia && window.matchMedia('(max-device-width: 640px)').matches) {
//            // smartphone
//            numberOfMonths = 1;
//        } else {
//            // pc
//            numberOfMonths = 2;
//        }
    var numberOfMonths = 1;

    $("#eventDateTimeCalendar").datepicker({
        dateFormat: "m/d(DD)",
        firstDay: 0,
        yearSuffix: '年',
        showMonthAfterYear: true,
        monthNames: ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'],
        dayNames: ['日', '月', '火', '水', '木', '金', '土'],
        dayNamesMin: ['日', '月', '火', '水', '木', '金', '土'],
        minDate: new Date(),
        maxDate: '+12m',
        hideIfNoPrevNext: true,
        todayHighlight: true,
        multidate: true,
        numberOfMonths: numberOfMonths,

        onSelect: function (dateText, inst) {
            var nowText = $("#event_datetime_kouho").val();

            if (nowText === "") {
                $("#event_datetime_kouho").val(dateText + " 19:00〜");
            }
            else {
                $("#event_datetime_kouho").val(nowText + "\n" + dateText + " 19:00〜");
            }
        }
    });

    $('.rightBottomFixed').click(function(){
        $('html,body').animate({'scrollTop':0},500);
    });

});
