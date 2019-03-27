

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
    console.log('Got taskIds', rtn);
    return rtn;
}


async function getStatusNew(taskId){
    console.log('getting task ID',  taskId);
    var complete = new Promise(function(resolve, reject){

        async function retry(){
            console.log('ENTER RETRY')
            data = await $.get("/web/status?task_id="+taskId);
            console.log('GOT DATA', data);
            if (data.ready){
                console.log(`task ID ${taskId} ready`)
                resolve(data)
            } else {
                console.log(`Waiting task ID ${taskId}`);
                setTimeout(retry, 2000);
            }
        }
        console.log('BEFORE RETRY')
        retry()
    })
    return complete;
}

async function getAllStatuses(taskIds){
    statuses = [];
    for (const taskId of taskIds){
        statuses.push(getStatusNew(taskId));
    }
    return await Promise.all(statuses);
}

/*
function get_status(task_id)
{
    $.get("/web/status?task_id=" + task_id, function(data) {
        if (data.ready) {
            $("i").hide();
            console.log(data)
            
        } else {
            $("i").show();
            setTimeout(get_status, 1000, task_id);
        }
      });
}
*/

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


$(async function () {
    var taskIds = getTaskIds();
    console.log('Got before await', taskIds);
    results = await getAllStatuses(taskIds);
    var jsonsToParse = [];

    for (const result of results){
        jsonsToParse.push(result);
    }    
    var url = 'http://localhost:8000/web/result';
       
    $.ajax({
        type: "POST",
        url: url,
        data: jsonsToParse,
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