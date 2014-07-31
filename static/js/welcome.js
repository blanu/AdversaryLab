var model={
  login: ko.observable('')
}

$(document).ready(function() {
  ko.applyBindings(model);
    
  user.login(function(result) {
    model.login(result)
  });
});
