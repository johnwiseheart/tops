$(document).foundation();

$(window).scroll(function() {
if ($(this).scrollTop() > 1){
    $('.header').addClass("tiny");
  }
  else{
    $('.header').removeClass("tiny");
  }
});


$('.redeem-button').click(function(e) {
  if (e.target !== this)
    e.target = this;
  console.log(e);
   e.preventDefault();
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
        if (res.success) {
          window.location.reload();
        }
    }
  });
});
