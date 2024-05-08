let temp_registers = [];
$(".custom-control-input").on("change", function () {
  $("#service_text").val('');
  $("#service").val('');
});

function get_services(){
  let term = $("#service_text").val();
  if (term.length > 0) {
    $("#service").val('');
    $.ajax({
      type: "GET",
      url: "/service_desk/get_services",
      data: {
        term: term,
      },
      success: function (response) {
        let html = '';
        temp_registers = response.data;
        for(let i=0; i < response.data.length; i++){
          html += '<div><a class="suggest-element" data="'+response.data[i].name+'" id="'+response.data[i].id+'">'+response.data[i].name+'</a></div>';
        }
        $("#service_suggestions").fadeIn(1000).html(html);
        $(".suggest-element").on("click", function () {
          let id = $(this).attr("id");
          let value = $(this).attr("data");
          $("#service_text").val(value);
          $("#service").val(id);
          $("#service_suggestions").fadeOut(100);
          return false;
        });
      },
      error: function (error) {
        alert("No se ha podido obtener los servicios");
      }
    });
  }
}
$('#service_text').change(function(){
  if (!$('#service').val().length) {
    $('#service_text').val('');
  }
})

$("#service_text").on('keyup', function() {
  get_services();
});

$("#service_text").on('click', function(e) {
  get_services();
});
