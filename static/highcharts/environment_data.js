/**
 * Put the data into the proper format for Highcharts.
 * @param field_no The field number of the channel
 * @param series The series to be added to the chart
 * @param data The JSON data from the channel
 */
function prepFieldData(field_no, series, data, start_date, end_date) {
    var time = new Date();
    var milliseconds_since_epoch = 0;
    var milliseconds_per_day = 86400000;
    // Iterate through each data point
    for (var h = 0; h < data.feeds.length; h++) {
        time = new Date(data.feeds[h].created_at);
        milliseconds_since_epoch = time.getTime();
        // If feed's timestamp is between start and end date...
        if (milliseconds_since_epoch >= start_date && milliseconds_since_epoch <= end_date+milliseconds_per_day) {
            // Add it to the series to plot.
            series.push([milliseconds_since_epoch, parseFloat(eval("data.feeds[h].field"+field_no))]);
        }
    }
}

/**
 * Create a highcharts chart to add to the webpage.
 * @param chart_name the name of the chart
 * @param channel the channel to create chart for
 * @param weather_channel the outside weather channel to add to the chart
 */
function createChart(chart_name, channel, weather_channel, start_date=0, end_date=new Date().getTime()) {
    $.getJSON('https://www.thingspeak.com/channels/' + channel.channel_no + '/feed.json?callback=?&amp;offset=0&amp;results=2500;key=' + channel.read_key, function (data) {
        if (data == '-1') {
            $('#chart-container-' + channel.channel_no).append('This channel is not public.  To embed charts, the channel must be public or a read key must be specified.');
            window.console && console.log('Thingspeak Data Loading Error');
        }

        var field1_series = [];
        var field2_series = [];
        prepFieldData(1, field1_series, data, start_date, end_date);
        prepFieldData(2, field2_series, data, start_date, end_date);

        // Make sure series exist before creating charts...
        if(field1_series.length != 0 && field2_series.length != 0) {
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
             var add_weather_promise = addCurrentWeatherData(chartOptions, weather_channel, start_date, end_date);

            // When weather data fetched...
            add_weather_promise.then(function (chart_options) {
                // Create the chart
                Highcharts.stockChart('chart-container-' + channel.channel_no, chart_options);
            });
        }
    });
}

/**
 * Add the current outside weather data from thingspeak into chart options constrained by date.
 * @param chart_options the Highcharts chart options
 * @param channel the outside weather thingspeak channel
 * @param start_date
 * @param end_date
 * @return javascript Promise
 */
function addCurrentWeatherData(chart_options, channel, start_date, end_date) {
    return $.getJSON('https://www.thingspeak.com/channels/'+channel.channel_no+'/feed.json?callback=?&amp;offset=0&amp;results=2500;key='+channel.read_key).then(function(data) {
        var field1_series = [];
        var field2_series = [];
        prepFieldData(1, field1_series, data, start_date, end_date);
        prepFieldData(2, field2_series, data, start_date, end_date);
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