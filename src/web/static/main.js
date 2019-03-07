

function getTaskIds()
{
    var rtn = [],
        params = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
    for(var i = 0; i < params.length; i++)
    {
        var param = params[i].split('='),
            key = param[0],
            value = param[1].split(',');

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
          $(".lead").append('<p>' + data.result + '</p>');
          $(".raw").append('<p>' + data.raw + '</p>');
        } else {
          setTimeout(get_status, 2000);
        }
      });
};


$(function () {
  var taskIds = getTaskIds();
  console.log(taskIds);
    for (var i = 0; i < taskIds.length; i++) {
        get_status(taskIds[i]);
    }
});
