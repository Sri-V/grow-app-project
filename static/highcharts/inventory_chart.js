/**
 * Get a list of the crops for each variety younger than 'days' days old
 * @param chart_series a list of objects representing data for each category in stacked bar chart
 */
function createInventoryChart(chart_series, variety_list) {
    Highcharts.chart('high-charts-container', {
      chart: {
        type: 'bar'
      },
      title: {
        text: 'Crop Inventory'
      },
      xAxis: {
        categories: variety_list
      },
      yAxis: {
        min: 0,
        title: {
          text: 'Number of Trays'
        }
      },
      legend: {
        reversed: true
      },
      plotOptions: {
        series: {
          stacking: 'normal'
        }
      },
      series: chart_series
});
}

function createChartSeries2(breakdown, varieties, crop_groups) {
    var series = []
    for (var b in breakdown) {
        var count = 0
        for (var v in varieties) {
            for (var c in crop_groups) {

            }
        }
    }
    series.push({name: "", data: []})
    return series
}