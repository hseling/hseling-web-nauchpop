

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
            return data
        } else {
            $("i").show();
            setTimeout(get_status, 1000, task_id);
        }
      });
}

var template = `
{{#api_results}}
    <tr>
        <th><b>Имя файла</b></th>
        <th><b>Имена ученых</b></th>
        <th><b>Тематика</b></th>
        <th><b>Ридабилити</b></th>
        <th><b>Термины</b></td>
    </tr>
    <tr>
        <td>{{file}}</td>
        <td>{{ner}}</td>
        <td>{{topic}}</td>
        <td>{{rb}}</td>
        <td>{{term}}</td>
    </tr> 
{{/api_results}}
`;


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
        success: function(data) {
            var view = data;
            var output = Mustache.render(template, view);
            $(".api-result").append(output);
            console.log("POST JSONs status OK");
        }
      });
});