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
        'maxValue': 0.5
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
        'maxValue': 0.5
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

function drawDurations(report)
{
    log('drawDurations');
    log(report.incoming.durations);
    if(report.incoming.durations.length==0)
    {
      $('#incomingDurations').append('Insufficient incoming stream duration data available.');
    }
    else
    {
      var data = google.visualization.arrayToDataTable(label(["Dataset", 'Duration'], report.incoming.durations));

      var options = {
        'title':'Incoming Stream: Durations',
        'width':400, 'height':300,
        'orientation': 'horizontal',
        'legend': {
          'position': 'none'
        },
        'vAxis': {
          'maxValue': 8
        }
      };

      var chart = new google.visualization.BarChart(document.getElementById('incomingDurations'));
      chart.draw(data, options);
    }

    /* ------------- */

    if(report.outgoing.durations.length==0)
    {
      $('#outgoingDurations').append('Insufficient outgoing stream duration data available.');
    }
    else
    {
      data = google.visualization.arrayToDataTable(label(["Dataset", 'Duration'], report.outgoing.durations));

      options = {
        'title':'Outgoing Stream: Durations',
        'width':400, 'height':300,
        'orientation': 'horizontal',
        'legend': {
          'position': 'none'
        },
        'vAxis': {
          'maxValue': 8
        }
      };

      chart = new google.visualization.BarChart(document.getElementById('outgoingDurations'));
      chart.draw(data, options);
    }
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
        'maxValue': 0.1
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
        'maxValue': 0.1
      }
    };

    chart = new google.visualization.BarChart(document.getElementById('outgoingContentProbs'));
    chart.draw(data, options);
}

function drawFlow(report)
{
  if(report.incoming.flow.length==0)
  {
    $('#incomingFlow').append('Insufficient incoming flow data available.');
  }
  else
  {
    var data = google.visualization.arrayToDataTable(label(["Dataset", 'Packets Per Second'], report.incoming.flow));

    var options = {
      'title':'Incoming Stream: Packets Per Second',
      'width':400, 'height':300,
      'orientation': 'horizontal',
      'legend': {
        'position': 'none'
      },
      'vAxis': {
      }
    };

    var chart = new google.visualization.BarChart(document.getElementById('incomingFlow'));
    chart.draw(data, options);
  }

    /* ------------- */

  if(report.outgoing.flow.length==0)
  {
    $('#outgoingFlow').append('Insufficient outgoing flow data available.');
  }
  else
  {
    data = google.visualization.arrayToDataTable(label(["Dataset", 'Packets Per Second'], report.outgoing.flow));

    options = {
      'title':'Outgoing Stream: Packets Per Second',
      'width':400, 'height':300,
      'orientation': 'horizontal',
      'legend': {
        'position': 'none'
      },
      'vAxis': {
      }
    };

    chart = new google.visualization.BarChart(document.getElementById('outgoingFlow'));
    chart.draw(data, options);
  }
}
