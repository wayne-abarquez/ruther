// Load the Visualization API and the piechart package.
google.load('visualization', '1.0', {'packages':['corechart']});

function drawVisualization(raw_data){
  // Create and populate the data table.
  var data = google.visualization.arrayToDataTable(raw_data);

  // Clear existing visualization.
  $('#chart_div').empty();

  // Create and draw the visualization.
  var ac = new google.visualization.ComboChart(document.getElementById('chart_div'));
  ac.draw(data, {
    title : 'Chart View',
    width: 1000,
    height: 400,
    vAxis: {title: "Value"},
    hAxis: {title: "Last 7 Time Intervals"},
    seriesType: "bars",
    series: {2: {type: "line"}, 3: {type: "line"}},
  });
}

