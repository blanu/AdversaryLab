var model={
  adversaries: ko.observableArray([]),
  admin: ko.observable(false),
  logout: ko.observable('')
}

$(document).ready(function () {
  ko.applyBindings(model);

  login(model);

  adversary.list(function(results) {
    log(results);
    for(var index in results)
    {
      log(results[index]);
      model.adversaries.push({"name": results[index]});
    }
    log(model.adversaries());

    $('.adversaryLink').each(function() {
      var adversary=$(this).attr('name');
      $(this).attr('href', '/adversary?adversary='+adversary);
    });
  });

  $("#addAdversary").click(function(button) {
    log("clicked add adversary");
    $("#adversaries").append("<tr><td><input type=\"text\"><button class=\"saveAdversary\">Save</button></td></tr>");
    var li=$('#adversaries').find('tr td').last();
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
      adversary.add(name);
    });
  })
});
