$(document).foundation();
$(document).ready(function() {

});

$('.redeem-button').click(function(e) {
  console.log(e);
  console.log($(e.target).data('redeemable'));
  $.ajax({
    url: 'http://localhost:5000/redeemevents/',
    type: 'POST',
    dataType: 'json',
    contentType: "application/json",
    data: JSON.stringify({
      redeemable_id: $(e.target).data('redeemable'),
    }),
    success: function(res) {
        console.log(res);
    }
  });
});
