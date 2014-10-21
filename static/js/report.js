var report=null;
var model={
  filename: ko.observable(''),
  admin: ko.observable(false),
  logout: ko.observable('')
}

function drawChart()
{
//    drawLengthCounts();
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
    filekey=$.query.get('filekey');
    reports.getForPcap(filekey, function(result) {
      model.filename(result.filename);
      report=result;
      drawChart();
    });
  });
});
