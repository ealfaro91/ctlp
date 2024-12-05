$("select[name='area_id']").change(function(){
         let $select_type = $("select[name='type_id']");
         $select_type.find("option:not(:first)").hide();
         let nb = $select_type.find("option[data-area_id="+($(this).val() || 0)+"]").show().length;
         $select_type.val(0);

          // Clear the category_id field
          let $select_category = $("select[name='category_id']");
          $select_category.val(0);
          $select_category.find("option:not(:first)").hide();

          // Clear the location_id field
          let $select_location = $("select[name='location_id']");
          $select_location.val(0);
          $select_location.find("option:not(:first)").hide();
});


$("select[name='area_id']").change(function(){
         let $select_location = $("select[name='location_id']");
         $select_location.find("option:not(:first)").hide();
         let nb2 = $select_location.find("option[data-area_id="+($(this).val() || 0)+"]").show().length;
         $select_location.val(0);

});


$("select[name='type_id']").change(function(){
         let $select_category = $("select[name='category_id']");
         $select_category.find("option:not(:first)").hide();
         let nb = $select_category.find("option[data-type_id="+($(this).val() || 0)+"]").show().length;
         $select_category.val(0);
});

function showFileNames() {
    const fileInput = document.querySelector('input[name="attachments"]');
    const fileListDiv = document.getElementById('fileList');

    // Clear the previous file names
    fileListDiv.innerHTML = '';

    // Create a list to hold the file names
    const fileNames = Array.from(fileInput.files).map(file => file.name);

    // Check if there are any files selected
    if (fileNames.length > 0) {
        // Create a list element
        const ul = document.createElement('ul');

        // Add each file name to the list
        fileNames.forEach(name => {
            const li = document.createElement('li');
            li.textContent = name;
            ul.appendChild(li);
        });

        // Append the list to the fileList div
        fileListDiv.appendChild(ul);
    } else {
        // Optionally, you can show a message if no files are selected
        fileListDiv.textContent = 'No files selected.';
    }
}


