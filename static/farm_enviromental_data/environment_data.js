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

/**
 * Create a highcharts chart to add to the webpage.
 * @param chart_name the name of the chart
 * @param channel the channel to create chart for
 * @param weather_channel the outside weather channel to add to the chart
 */
function createChart(chart_name, channel, weather_channel) {
    $.getJSON('https://www.thingspeak.com/channels/' + channel.channel_no + '/feed.json?callback=?&amp;offset=0&amp;results=2500;key=' + channel.read_key, function (data) {
        if (data == '-1') {
            $('#chart-container-' + channel.channel_no).append('This channel is not public.  To embed charts, the channel must be public or a read key must be specified.');
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
                {
                    name: data.channel.field2,
                    data: field2_series,
                    tooltip: {
                        valueDecimals: 2
                    }
                }]
        }

         // Make promise to get weather data & add it to chart series
         var add_weather_promise = addCurrentWeatherData(chartOptions, weather_channel);

        // When weather data fetched...
        add_weather_promise.then(function (chart_options) {
            // Create the chart
            Highcharts.stockChart('chart-container-' + channel.channel_no, chart_options);
        });

    });
}
/**
 * Add the current outside weather data from thingspeak into chart options.
 * @param chart_options the Highcharts chart options
 * @param channel the outside weather thingspeak channel
 * @return javascript Promise
 */
function addCurrentWeatherData(chart_options, channel) {
    return $.getJSON('https://www.thingspeak.com/channels/'+channel.channel_no+'/feed.json?callback=?&amp;offset=0&amp;results=2500;key='+channel.read_key).then(function(data) {
        var field1_series = [];
        var field2_series = [];
        prepFieldData(1, field1_series, data);
        prepFieldData(2, field2_series, data);
        chart_options.series.push({name: 'Outside Temperature',
                data: field1_series,
                tooltip: {
                valueDecimals: 2 }}
        );
        chart_options.series.push({name: 'Outside Humidity',
                data: field2_series,
                tooltip: {
                valueDecimals: 2 }}
        );
        return chart_options;
    });
}