var model={
  dataset: ko.observable(''),
  protocols: ko.observableArray([]),
  admin: ko.observable(false),
  logout: ko.observable('')
}

$(document).ready(function () {
  var datasetName=$.query.get('dataset');
  model.dataset(datasetName);
  
  ko.applyBindings(model);
  
  login(model);
  
  protocol.list(function(results) {
    log(results);
    for(var index in results)
    {
      log(results[index]);
      model.protocols.push({"name": results[index]});
    }
    
    $('.reportLink').each(function() {
      var protocol=$(this).attr('filekey');    
      $(this).attr('href', '/datasetReport?dataset='+datasetName+'&protocol='+protocol);
    });    
  });
});
