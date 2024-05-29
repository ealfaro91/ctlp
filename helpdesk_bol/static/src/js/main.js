
$("select[name='type_id']").change(function(){
         let $select_category = $("select[name='category_id']");
         $select_category.find("option:not(:first)").hide();
         let nb = $select_category.find("option[data-type_id="+($(this).val() || 0)+"]").show().length;
         $select_category.val(0);
});
