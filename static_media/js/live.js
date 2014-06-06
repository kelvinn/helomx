$(function () {
   get_data();
  });

function getUrlVars()
{
    var vars = [], hash;
    var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
    for(var i = 0; i < hashes.length; i++)
    {
        hash = hashes[i].split('=');
        vars.push(hash[0]);
        vars[hash[0]] = hash[1];
    }
    return vars;
}

function get_data() {
    var hash = getUrlVars();
    var portField=document.getElementById("portField");
    var blkField=document.getElementById("blkField");
    $.getJSON("/ajax/?mx="slug,
	function(json) {

        /* Parse JSON objects */
        /* json[0].fields.ping_rtt */
        response = {
            AUvalues: [[],[]],
            count: 0
        };
        $.each(json,function(i,item) {
            if (item.fields.probe == "au") {
                response.count++;
                response.AUvalues[i] = [item.pk, item.fields.check_type, item.check_time];
            }
        });
    $.plot($("#placeholder"), [{ label: "Australia",  data: response.AUvalues}], { points: { show: true }});
    });
	window.setTimeout( get_data, 4000 );
};
