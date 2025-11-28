$("select[name='area_id']").change(function(){
         let $select_directory = $("select[name='directory_id']");
         $select_directory.find("option:not(:first)").hide();
         let nb = $select_directory.find("option[data-area_id="+($(this).val() || 0)+"]").show().length;
         $select_directory.val(0);
 });



