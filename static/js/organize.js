var model={
  pcaps: ko.observableArray([]),
  datasets: ko.observableArray([]),
  protocols: ko.observableArray([])
}

function fixLinks()
{
  log('fixLinks');
  $('.reportLink').each(function() {
    var filekey=$(this).attr('filekey');    
    $(this).attr('href', '/report?filekey='+filekey);
  });
}

$(document).ready(function () {
  ko.applyBindings(model);
  
  protocol.list(function(results) {
    for(var index in results)
    {
      model.protocols.push({"name": results[index]});
    }
    
    dataset.list(function(results) {
      for(var index in results)
      {
        model.datasets.push({"name": results[index]});
      }
      
      pcap.list(function(results) {
        for(var index in results)
        {
          var result=results[index];
          result.datasets=model.datasets().map(function(item) {return {'name': item.name, 'selected': item.name==result.dataset}});
          result.datasets.unshift({'name': '', 'selected': false});
          result.protocols=model.protocols().map(function(item) {return {'name': item.name, 'selected': item.name==result.protocol}});
          result.protocols.unshift({'name': '', 'selected': false});
    
          model.pcaps.push(result);
        }
        
        $('.pcapProtocol').change(function () {
          var name=$(this).attr('filekey');
          var prot=$(this).find('option:selected').text();
          pcap.setProtocol(name, prot);
        });
        
        $('.pcapDataset').change(function () {
          var name=$(this).attr('filekey');
          var dataset=$(this).find('option:selected').text();
          pcap.setDataset(name, dataset);
        });  
        
        log('calling fixLinks');
        fixLinks();
      });
    });    
  });  
});
