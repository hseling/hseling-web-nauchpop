

function getTaskIds()
{
    var rtn = [],
        params = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
    for(var i = 0; i < params.length; i++)
    {
        var param = params[i].split('=');
        var key = param[0];
        var value = param[1].split(',');

        if (key == 'task_id') {

            for (var j = 0; j < value.length; j++) {
                rtn[j] = value[j];
            }
        }
    }
    return rtn;
}


function get_status(task_id)
{
    $.get("/web/status?task_id=" + task_id, function(data) {
        if (data.ready) {
            $("i").hide();
            if(prettifyModuleNames(data.result)=='Ридабилити'){
                $(".api-result").append('<tr><td class="lead"><p><b>' + prettifyModuleNames(data.result) + '</b></p></td>' + '<td class="raw">' + prettifyRbResult(data.raw) + '</td></tr>')

            } else {$(".api-result").append('<tr><td class="lead"><p><b>' + prettifyModuleNames(data.result) + '</b></p></td>' + '<td class="raw"><p>' + data.raw + '</p></td></tr>')}
        } else {
            $("i").show();
            setTimeout(get_status, 1000, task_id);
        }
      });
}


$(function () {
  var taskIds = getTaskIds();
  console.log(taskIds);
  var jsonsToParse = [];
    for (var i = 0; i < taskIds.length; i++) {
        jsonsToParse.push(get_status(taskIds[i]));
    }
    var url = window.location.href.slice(window.location.href.indexOf('?') + 1);
    url = url.split('/').pop(-1).join('/') + 'result';

    $.ajax({
        type: "POST",
        url: url,
        data: JSON.stringify(jsonsToParse),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        error: function() {
          console.log("POST JSONs status Error");
        },
        success: function() {
          console.log("POST JSONs status OK");
        }
      });
});

function prettifyModuleNames(processedFileName){
    var moduleNames = {topic: "Тематика", ner: "Имена ученых", rb: "Ридабилити", term:"Термины"} ;
    var pattern = /processed\/([a-z]+)_/g ;
    var match = pattern.exec(processedFileName);
    return moduleNames[match[1]];
}

function prettifyRbResult(rbResult){
    var pattern = /(\d+\.\d+|\d+)(\s)/gm ;
    var numbers = rbResult.match(pattern);
    for(i=0; i < numbers.length; i++){
        rbResult = rbResult.replace(numbers[i], numbers[i]+ '<br>');
    };
    return rbResult;
}