var model={
  pcaps: ko.observableArray([]),
  datasets: ko.observableArray([]),
  protocols: ko.observableArray([])
}

$(document).ready(function () {
  ko.applyBindings(model);
  
  protocol.list(function(results) {
    log(results);
    for(var index in results)
    {
      log(results[index]);
      model.protocols.push({"name": results[index]});
    }
    
    dataset.list(function(results) {
      log(results);
      for(var index in results)
      {
        log(results[index]);
        model.datasets.push({"name": results[index]});
      }
      
      pcap.list(function(results) {
        log(results);
        for(var index in results)
        {
          log(results[index]);
          var result=results[index];
          result.datasets=model.datasets().map(function(item) {return {'name': item.name, 'selected': item==pcap.dataset}});
          result.protocols=model.protocols().map(function(item) {return {'name': item.name, 'selected': item==pcap.protocol}});
          log(result);
    
          model.pcaps.push(result);
        }
      });
    });    
  });
});
