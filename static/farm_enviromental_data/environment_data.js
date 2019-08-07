

/**
 * Put the data into the proper format for Highcharts.
 * @param field_no The field number of the channel
 * @param series The series to be added to the chart
 * @param data The JSON data from the channel
 */
function prepFieldData(field_no, series, data) {
    var time = new Date();
    var milliseconds_since_epoch = 0;
    // iterate through each data point
    for (var h = 0; h < data.feeds.length; h++) {
        time = new Date(data.feeds[h].created_at);
        milliseconds_since_epoch = time.getTime();
        series.push([milliseconds_since_epoch, parseFloat(eval("data.feeds[h].field"+field_no))]);
    }
}

function createChart(chart_name, channel) {
    $.getJSON('https://www.thingspeak.com/channels/'+channel.channel_no+'/feed.json?callback=?&amp;offset=0&amp;results=2500;key='+channel.read_key, function(data) {
            if (data == '-1') {
                $('#chart-container-'+channel.channel_no).append('This channel is not public.  To embed charts, the channel must be public or a read key must be specified.');
                window.console && console.log('Thingspeak Data Loading Error');
                }

            var field1_series = [];
            var field2_series = [];
            prepFieldData(1, field1_series, data);
            prepFieldData(2, field2_series, data);

            var chartOptions = {
                rangeSelector: {
                    selected: 1
                },

                title: {
                    text: chart_name
                },

                series: [{
                    name: data.channel.field1,
                    data: field1_series,
                    tooltip: {
                        valueDecimals: 2
                    }
                },
                    {name: data.channel.field2,
                    data: field2_series,
                    tooltip: {
                        valueDecimals: 2
                    }}]
            }

            // Create the chart
            Highcharts.stockChart('chart-container-'+channel.channel_no, chartOptions);
            });
}

// TODO: create new Thingspeak channels & fill in info
/*
var inlet_channel = {
    channel_no: xxxxx,
    channel_name: 'xxxxxx',
    read_key: 'xxxxxxxxxxxxxxx'
}

var other_channel = {
    channel_no: xxxxxxxxxx,
    channel_name: 'xxxxxxxxxx',
    read_key: 'xxxxxxxxxxxxxx'
}
*/
