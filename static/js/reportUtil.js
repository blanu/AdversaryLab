function expand(lab, arr)
{
  var results=[lab];
  for(var x=0; x<arr.length; x++)
  {
    results.push([x, arr[x]]);
  }
  
  return results;
}

function label(lab, arr)
{
  var results=[lab];
  for(var x=0; x<arr.length; x++)
  {
    results.push([x, arr[x]]);
  }
  
  return results;
}

function normalize(lab, arr)
{
  var results=[lab];
  total=0;
  for(var x=0; x<arr.length; x++)
  {
    total=total+arr[x]
  }
  
  for(var x=0; x<arr.length; x++)
  {
    results.push([x, arr[x]/total]);
  }
  
  log('normalized');
  log(results);
  
  return results;  
}

function drawLengthCounts(report)
{
    var data = google.visualization.arrayToDataTable(expand(["Packet Length", "Count"], report['incoming']['lengths']));
    
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
    
    data = google.visualization.arrayToDataTable(expand(["Packet Length", "Count"], report['outgoing']['lengths']));
    
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

function drawLengthProbs(report)
{
    var data = google.visualization.arrayToDataTable(normalize(["Packet Length", "Probability"], report['incoming']['lengths']));
    
    var options = {
      'title':'Incoming Stream: Probability of Packets with a Given Length',
      'width':400, 'height':300,
      'orientation': 'horizontal',
      'legend': {
        'position': 'none'
      },
      'vAxis': {
        'maxValue': 1
      }
    };

    chart = new google.visualization.BarChart(document.getElementById('incomingLengthProbs'));
    chart.draw(data, options);

    /* ------------- */
    
    data = google.visualization.arrayToDataTable(normalize(["Packet Length", "Probability"], report['outgoing']['lengths']));
    
    options = {
      'title':'Outgoing Stream: Probability of Packets with a Given Length',
      'width':400, 'height':300,
      'orientation': 'horizontal',
      'legend': {
        'position': 'none'
      },
      'vAxis': {
        'maxValue': 1
      }
    };

    chart = new google.visualization.BarChart(document.getElementById('outgoingLengthProbs'));
    chart.draw(data, options);    
}

function drawEntropies(report)
{
    var data = google.visualization.arrayToDataTable(label(["Dataset", 'Entropy'], report.incoming.entropy));
    
    var options = {
      'title':'Incoming Stream: Entropies',
      'width':400, 'height':300,
      'orientation': 'horizontal',
      'legend': {
        'position': 'none'
      },
      'vAxis': {
        'maxValue': 8
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
      },
      'vAxis': {
        'maxValue': 8
      }
    };

    chart = new google.visualization.BarChart(document.getElementById('outgoingEntropy'));
    chart.draw(data, options);
}

function drawContentProbs(report)
{
    var data = google.visualization.arrayToDataTable(normalize(["Byte Value", "Probability"], report['incoming']['content']));
    
    var options = {
      'title':'Incoming Stream: Probability of Byte with a Given Value',
      'width':400, 'height':300,
      'orientation': 'horizontal',
      'legend': {
        'position': 'none'
      },
      'vAxis': {
        'maxValue': 0.05
      }
    };

    chart = new google.visualization.BarChart(document.getElementById('incomingContentProbs'));
    chart.draw(data, options);

    /* ------------- */
    
    data = google.visualization.arrayToDataTable(normalize(["Byte Value", "Probability"], report['outgoing']['content']));
    
    options = {
      'title':'Outgoing Stream: Probability of Byte with a Given Value',
      'width':400, 'height':300,
      'orientation': 'horizontal',
      'legend': {
        'position': 'none'
      },
      'vAxis': {
        'maxValue': 0.05
      }
    };

    chart = new google.visualization.BarChart(document.getElementById('outgoingContentProbs'));
    chart.draw(data, options);    
}
