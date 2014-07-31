var report=null;
var model={
  dataset: ko.observable(''),
  protocol: ko.observable(''),
  admin: ko.observable(false),
  logout: ko.observable('')
}

function drawChart()
{
  drawLengthProbs(report);
  drawEntropies(report);
}


$(document).ready(function() {
  ko.applyBindings(model);
  
  login(model);

  google.setOnLoadCallback(function() {
    var dataset=$.query.get('dataset');
    var protocol=$.query.get('protocol');
    model.dataset(dataset);
    model.protocol(protocol);
    
    reports.getForDatasetAndProtocol(dataset, protocol, function(result) {
      report=result;
      drawChart();
    });
  });    
});
