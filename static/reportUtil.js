function expand(arr)
{
  var results=[["Packet Length", "Count"]];
  for(var x=0; x<arr.length; x++)
  {
    results.push([x, arr[x]]);
  }
  
  return results;
}

function label(lab, arr)
{
  log('label '+arr);
  var results=[lab];
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
    var data = google.visualization.arrayToDataTable(expand(report['incoming']['lengths']));
    
    var options = {
      'title':'Incoming Stream: Count of Packets with a Given Length',
      'width':400, 'height':300,
      'orientation': 'horizontal',
      'legend': {
        'position': 'none'
      }
    };

    chart = new google.visualization.BarChart(document.getElementById('incomingLengthCount'));
    chart.draw(data, options);

    /* ------------- */
    
    data = google.visualization.arrayToDataTable(expand(report['outgoing']['lengths']));
    
    options = {
      'title':'Outgoing Stream: Count of Packets with a Given Length',
      'width':400, 'height':300,
      'orientation': 'horizontal',
      'legend': {
        'position': 'none'
      }
    };

    chart = new google.visualization.BarChart(document.getElementById('outgoingLengthCount'));
    chart.draw(data, options);    
}

function drawEntropies()
{
    var data = google.visualization.arrayToDataTable(label(["Dataset", 'Entropy'], report.incoming.entropy));
    
    var options = {
      'title':'Incoming Stream: Entropies',
      'width':400, 'height':300,
      'orientation': 'horizontal',
      'legend': {
        'position': 'none'
      }
    };

    var chart = new google.visualization.BarChart(document.getElementById('incomingEntropy'));
    chart.draw(data, options);
    
    /* ------------- */

    data = google.visualization.arrayToDataTable(label(["Dataset", 'Entropy'], report.outgoing.entropy));
    
    options = {
      'title':'Outgoing Stream: Entropies',
      'width':400, 'height':300,
      'orientation': 'horizontal',
      'legend': {
        'position': 'none'
      }
    };

    chart = new google.visualization.BarChart(document.getElementById('outgoingEntropy'));
    chart.draw(data, options);
}

$(document).ready(function() {
  function drawChart()
  {
    drawLengthCounts();
    drawEntropies();
  }
    
  google.setOnLoadCallback(drawChart);  
  
  $('#streamEntropy').text(report.entropy);
  $('#firstEntropy').text(report['entropy-first']);
});
