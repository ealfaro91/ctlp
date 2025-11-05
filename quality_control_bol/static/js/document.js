$("select[name='area_id']").change(function(){
         let $select_document = $("select[name='document_directory_id']");
         $select_document.find("option:not(:first)").hide();
         let nb = $select_type.find("option[data-area_id="+($(this).val() || 0)+"]").show().length;
         $select_document.val(0);


