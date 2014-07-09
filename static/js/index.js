$(document).ready(function () {
  log("init index");
    
  $(".runButton").click(function(button) {
    log("clicked run");
    var filekey=$(this).attr("filekey");
    log(filekey);
    $.post("/process", JSON.stringify({"filekey": filekey}));
  })
  
  $("#addProtocol").click(function(button) {
    log("clicked add protocol");
    $("#prots").append("<li><input type=\"text\"><button class=\"saveProtocol\">Save</button></li>");
    var li=$('#prots').find('li').last();
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

  $("#addDataset").click(function(button) {
    log("clicked add dataset");
    $("#datasets").append("<li><input type=\"text\"><button class=\"saveDataset\">Save</button></li>");
    var li=$('#datasets').find('li').last();
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
  
  $('.pcapProtocol').change(function () {
    var name=$(this).attr('filekey');
    var prot=$(this).find('option:selected').text();
    log(name+' selected '+prot);
    pcap.setProtocol(name, prot);
  });
  
  $('.pcapDataset').change(function () {
    var name=$(this).attr('filekey');
    var dataset=$(this).find('option:selected').text();
    log(name+' selected '+dataset);
    pcap.setDataset(name, dataset);
  });  
});
