/**
 * Get a list of the crops for each variety younger than 'days' days old
 * @param chart_series a list of objects representing data for each category in stacked bar chart
 */
function createInventoryChart(chart_series, variety_list, colors) {
    Highcharts.chart('high-charts-container', {
      chart: {
        type: 'bar'
      },
      title: {
        text: 'Crop Inventory'
      },
      colors: colors,

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
    console.log(colors)
}