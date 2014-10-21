var report=null;
var model={
  dataset: ko.observable(''),
  protocol: ko.observable(''),
  reportName: ko.observable(''),
  admin: ko.observable(false),
  logout: ko.observable('')
}

function drawChart()
{
  drawLengthProbs(report);
  drawEntropies(report);
  drawContentProbs(report);
  drawDurations(report);
  drawFlow(report);
}

$(document).ready(function() {
  ko.applyBindings(model);

  login(model);

  google.setOnLoadCallback(function() {
    var dataset=$.query.get('dataset');
    var protocol=$.query.get('protocol');
    model.dataset(dataset);
    model.protocol(protocol);
    model.reportName(dataset+' / '+protocol)

    $('#generateModel').click(function() {
      reports.generateModel(dataset, protocol);
    });

    reports.getForDatasetAndProtocol(dataset, protocol, function(result) {
      report=result;
      drawChart();
    });
  });
});
