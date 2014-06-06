function loadUpdate() {
  $.getJSON("/status_json/", { id:"{{ mx.slug }}" },
    function(json){
    $.each(json,function(i,item) {
        if (item.fields.check_type == "blacklist") {
            $("#blk_update").html(item.fields.check_time);
        }
        if (item.fields.check_type == "port") {
            $("#port_update").html(item.fields.check_time);
        }
        if (item.fields.check_type == "misc") {
            $("#misc_update").html(item.fields.check_time);
        }
    });
  });
  window.setTimeout(loadUpdate, 10000);
}
$(document).ready(loadUpdate);
$(document).ready(function()
{
   // Notice the use of the each() method to acquire access to each elements attributes
   $('#bd li[tooltip]').each(function()
   {
      $(this).qtip({
         content: $(this).attr('tooltip'), // Use the tooltip attribute of the element for the content
           style: {
              tip: 'rightMiddle' // Notice the corner value is identical to the previously mentioned positioning corners
           },
           position: {
              corner: {
                 target: 'leftMiddle',
                 tooltip: 'rightMiddle'
              }
           }

      });
   });
});
