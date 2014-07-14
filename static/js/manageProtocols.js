var model={
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
  });

  $("#addProtocol").click(function(button) {
    log("clicked add dataset");
    $("#protocols").append("<tr><td><input type=\"text\"><button class=\"saveProtocol\">Save</button></td></tr>");
    var li=$('#protocols').find('tr td').last();
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
      protocol.add(name);
    });
  })  
});
