var model={
  adversary: ko.observable(''),

  emptyPositive: ko.observable(true),
  positive: ko.observableArray([]),
  emptyNegative: ko.observable(true),
  negative: ko.observableArray([]),
  emptyPositiveTraining: ko.observable(true),
  positiveTraining: ko.observableArray([]),
  emptyNegativeTraining: ko.observable(true),
  negativeTraining: ko.observableArray([]),

  emptyUnsorted: ko.observable(true),
  unsorted: ko.observableArray([]),

  admin: ko.observable(false),
  logout: ko.observable('')
}

function findPcap(button)
{
  return $(button).first().parents('tr').children('td').first().attr('name');
}

function fixButtons()
{
  $('.positiveButton').click(function(button) {
    log('positive clicked');
    var name=model.adversary();
    var pcap=findPcap(this);
    adversary.sort(name, pcap, false, true, displayPcaps);
    loadPcaps();
  });
  $('.negativeButton').click(function(buttpn) {
    log('negative clicked');
    var name=model.adversary();
    var pcap=findPcap(this);
    adversary.sort(name, pcap, false, false, displayPcaps);
    model.negative.push({"name": pcap});
    loadPcaps();
  });
  $('.positiveTrainingButton').click(function(button) {
    log('positive training clicked');
    var name=model.adversary();
    var pcap=findPcap(this);
    adversary.sort(name, pcap, true, true, displayPcaps);
    loadPcaps();
  });
  $('.negativeTrainingButton').click(function(button) {
    log('negative training clicked');
    var name=model.adversary();
    var pcap=findPcap(this);
    adversary.sort(name, pcap, true, false, displayPcaps);
    loadPcaps();
  });
  $('.removeButton').click(function() {
    log('remove button clicked');
    var name=model.adversary();
    var pcap=findPcap(this);
    adversary.unsort(name, pcap, displayPcaps);
    loadPcaps();
  });
  $('#trainButton').click(function() {
    log('train button clicked');
    var name=model.adversary();
    adversary.train(name);
  });
  $('#testButton').click(function() {
    log('test button clicked');
    var name=model.adversary();
    adversary.test(name);
  });
}

function emptyPcaps()
{
  model.emptyPositive(true);
  model.positive([]);

  model.emptyNegative(true);
  model.negative([]);

  model.emptyPositiveTraining(true);
  model.positiveTraining([]);

  model.emptyNegativeTraining(true);
  model.negativeTraining([]);

  model.emptyUnsorted(true);
  model.unsorted([]);
}

function loadPcaps(adv)
{
  adversary.pcaps(adv, displayPcaps);
}

function displayPcaps(results)
{
  emptyPcaps();
  log(results);
  if(results['positive'].length>0)
  {
    model.emptyPositive(false);
    for(var index in results['positive'])
    {
      log(results['positive'][index]);
      model.positive.push({"name": results['positive'][index]});
    }
    log(model.positive());
  }

  if(results['negative'].length>0)
  {
    model.emptyNegative(false);
    for(var index in results['negative'])
    {
      log(results['negative'][index]);
      model.negative.push({"name": results['negative'][index]});
    }
  }
  log(model.negative());

  if(results['positiveTraining'].length>0)
  {
    model.emptyPositiveTraining(false);
    for(var index in results['positiveTraining'])
    {
      log(results['positiveTraining'][index]);
      model.positiveTraining.push({"name": results['positiveTraining'][index]});
    }
    log(model.positiveTraining());
  }

  if(results['negativeTraining'].length>0)
  {
    model.emptyNegativeTraining(false);
    for(var index in results['negativeTraining'])
    {
      log(results['negativeTraining'][index]);
      model.negativeTraining.push({"name": results['negativeTraining'][index]});
    }
  }
  log(model.negativeTraining());

  if(results['unsorted'].length>0)
  {
    model.emptyUnsorted(false);
    for(var index in results['unsorted'])
    {
      log(results['unsorted'][index]);
      model.unsorted.push({"name": results['unsorted'][index]});
    }
    log(model.unsorted());
  }

  fixButtons();
}

$(document).ready(function () {
  ko.applyBindings(model);

  login(model);

  var adv=$.query.get('adversary');
  model.adversary(adv);
  log('name:');
  log(adv);
  log(model.adversary());

  loadPcaps(adv);
});
