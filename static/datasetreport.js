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

function expand(arr)
{
  return label(["Packet Length", "Count"], arr);
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
    log('drawLengthCounts');
    var data = google.visualization.arrayToDataTable(expand(report.lengths));
    
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

function drawStreamEntropies()
{
    log('stream');
    var data = google.visualization.arrayToDataTable(label(["Dataset", 'Entropy'], report.entropy));
    log('stream entropy data: '+data);
    
    var options = {
      'title':'Stream Entropies',
      'width':400, 'height':300,
      'orientation': 'horizontal',
      'legend': {
        'position': 'none'
      },
      'vAxis.maxValue': Math.max(report.entropy[report.entropy.length-1], report['entropy-first'][report['entropy-first'].length-1])
    };

    var chart = new google.visualization.BarChart(document.getElementById('entropy'));
    chart.draw(data, options);
}

function drawFirstEntropies()
{
    log('first');
    var data = google.visualization.arrayToDataTable(label(["Dataset", 'Entropy'], report['entropy-first']));
    
    var options = {
      'title':'First Packet Entropies',
      'width':400, 'height':300,
      'orientation': 'horizontal',
      'legend': {
        'position': 'none'
      },
      'vAxis.maxValue': Math.max(report.entropy[report.entropy.length-1], report['entropy-first'][report['entropy-first'].length-1])
    };

    var chart = new google.visualization.BarChart(document.getElementById('firstEntropy'));
    chart.draw(data, options);
}

$(document).ready(function() {
  function drawChart()
  {
    log('draw chart');
    log(report);
    drawLengthCounts();
    drawStreamEntropies();
    drawFirstEntropies();
  }
    
  google.setOnLoadCallback(drawChart);  
});
