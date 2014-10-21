var report=null;
var model={
  protocol: ko.observable(''),
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
    var protocol=$.query.get('protocol');
    model.protocol(protocol);
    reports.getForProtocol(protocol, function(result) {
      report=result;
      drawChart();
    });
  });
});
