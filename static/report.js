function expand(arr)
{
  var results=[["Packet Length", "Count"]];
  for(var x=0; x<arr.length; x++)
  {
    results.push([x, arr[x]]);
  }
  
  return results;
}

function normalize(arr)
{
  var results=[["Packet Length", "Count"]];
  total=0;
  for(var x=0; x<arr.length; x++)
  {
    total=total+arr[x]
  }
  
  for(var x=0; x<arr.length; x++)
  {
    results.push([x, arr[x]/total]);
  }
  
  return results;  
}

function drawLengthCounts()
{
    var data = google.visualization.arrayToDataTable(expand(report['lengths']));
    
    var options = {
      'title':'Count of Packets with a Given Length',
      'width':400, 'height':300,
      'orientation': 'horizontal',
      'legend': {
        'position': 'none'
      }
    };

    var chart = new google.visualization.BarChart(document.getElementById('lengthCount'));
    chart.draw(data, options);
}

function drawLengthProbs()
{
    var data = google.visualization.arrayToDataTable(normalize(report['lengths']));
    
    var options = {
      'title':'Probability of Packets with a Given Length',
      'width':400, 'height':300,
      'orientation': 'horizontal',
      'legend': {
        'position': 'none'
      }
    };

    var chart = new google.visualization.BarChart(document.getElementById('lengthProbability'));
    chart.draw(data, options);
}

$(document).ready(function() {
  function drawChart()
  {
    drawLengthCounts();
//    drawLengthProbs();
  }
    
  google.setOnLoadCallback(drawChart);  
  
  $('#streamEntropy').text(report.entropy);
  $('#firstEntropy').text(report['entropy-first']);
});
