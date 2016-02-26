$(document).foundation();

$(window).scroll(function() {
if ($(this).scrollTop() > 1){
    $('.header').addClass("tiny");
  }
  else{
    $('.header').removeClass("tiny");
  }
});

$(document).ready(function() {
  $('#select').selectize({
      valueField: 'id',
      labelField: 'name',
      searchField: 'name',
      create: false,
      render: {
          option: function(item, escape) {
              return '<div class="select_result">' +
                      '<img src="' + item.avatar_url + '"/>' +
                      '<span class="name">' + escape(item.name) + '</span>' +
              '</div>';
              return item;
          }
      },
      load: function(query, callback) {
          if (!query.length) return callback();
          $.ajax({
              url: 'http://localhost:5000/users/',
              type: 'GET',
              data: {
                q: query
              },
              error: function() {
                  callback();
              },
              success: function(res) {
                  callback(res.data);
              }
          });
      },
      onChange: function(value) {
        console.log("memes")
        $.ajax({
            url: 'http://localhost:5000/users/' + value ,
            type: 'GET',
            success: function(res) {
                console.log(res)
                if (res.users) {
                  $('.header').css('height', '20vh');
                  var image = $('.details img.thumbnail').attr('src', res.users[0].avatar_urls.xlarge);
                  $('.details_text textarea').val(res.users[0].first_name + ' is tops because...')
                  image.on('load', function() {
                    $('.details').css('height', 'auto').css('opacity', 100);
                  })
                }
                console.log(res);
                $('.tops_button').click(function(e) {
                  $.ajax({
                      url: 'http://localhost:5000/topsevents/',
                      type: 'POST',
                      dataType: 'json',
                      contentType: "application/json",
                      data: JSON.stringify({
                        to_user_email: res.users[0].email,
                        reason: $('#tops_text').val()
                      }),
                      success: function(res) {
                          console.log(res);
                          if (res.success) {
                            $('.meta').html("Thanks for submitting a tops!")
                          }
                      }
                  });
                });
            }
        });
      }
  });

});
