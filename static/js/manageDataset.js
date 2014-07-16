var model={
  datasets: ko.observableArray([])
}

$(document).ready(function () {
  ko.applyBindings(model);
  
  dataset.list(function(results) {
    log(results);
    for(var index in results)
    {
      log(results[index]);
      model.datasets.push({"name": results[index]});
    }
    log(model.datasets());
    
    $('.reportLink').each(function() {
      var dataset=$(this).attr('filekey');    
      $(this).attr('href', '/datasetReport?dataset='+dataset);
    });
  });

  $("#addDataset").click(function(button) {
    log("clicked add dataset");
    $("#datasets").append("<tr><td><input type=\"text\"><button class=\"saveDataset\">Save</button></td></tr>");
    var li=$('#datasets').find('tr td').last();
    var text=li.find('input');
    var save=li.find('button');
    $(text).focus();
    $(text).keyup(function(e) {
      if(e.keyCode == 13)
      {
        $(save).click();
      }
    });    
    $(save).click(function() {
      log('clicked save');
      var name=text.val();
      li.empty().append(name);
      dataset.add(name);
    });
  })    
});
