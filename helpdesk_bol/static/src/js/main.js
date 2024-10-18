$("select[name='area_id']").change(function(){
         let $select_type = $("select[name='type_id']");
         $select_type.find("option:not(:first)").hide();
         let nb = $select_type.find("option[data-area_id="+($(this).val() || 0)+"]").show().length;
         $select_type.val(0);
});

$("select[name='type_id']").change(function(){
         let $select_category = $("select[name='category_id']");
         $select_category.find("option:not(:first)").hide();
         let nb = $select_category.find("option[data-type_id="+($(this).val() || 0)+"]").show().length;
         $select_category.val(0);
});


$("select[name='category_id']").change(function(){
         let $select_location = $("select[name='location_id']");
         $select_location.find("option:not(:first)").hide();
         let nb = $select_location.find("option[data-category_id="+($(this).val() || 0)+"]").show().length;
         $select_location.val(0);
});


