$(document).foundation();
$(document).ready(function() {
  tops();
});

function tops() {
  $.ajax({
      url: 'http://localhost:5000/topsevents/',
      type: 'GET',
      error: function(msg) {
          alert(msg.responseText);
      },
      success: function(res) {
        var table = document.getElementById('events');
        table.innerHTML = '';
        $('<tr>').append(
          $('<th>').text('Event'),
          $('<th>').text('Reciever'),
          $('<th>').text('Sender'),
          $('<th>').text('Reason'),
          $('<th>').text('Disapprove')
        ).appendTo('#events');
        $.each(res.data, function (i, item) {
          var row = $('<tr>');
          row.append(
            $('<td>').text('Tops'),
            $('<td>').text(item.to_user_email),
            $('<td>').text(item.from_user_email),
            $('<td>').text(item.reason)
          );
          var approve_row = $('<td>');
          var box = `
            <div class="switch round large">
              <input event_type="tops" id="`+item.id+`" type="checkbox"`;
          if (item.approved) {
            box += ` checked`;
          }
          box += `>
              <label for="`+item.id+`"></label>
            </div>
          `;
          approve_row.append(box);
          row.append(approve_row);
          row.appendTo('#events');
        });
      }
  });
}

function redeem() {
  $.ajax({
      url: 'http://localhost:5000/redeemevents/',
      type: 'GET',
      error: function(msg) {
          alert(msg.responseText);
      },
      success: function(res) {
        var table = document.getElementById('events');
        table.innerHTML = '';
        $('<tr>').append(
          $('<th>').text('Event'),
          $('<th>').text('User'),
          $('<th>').text('Redeemable'),
          $('<th>').text(''),
          $('<th>').text('Approve')
        ).appendTo('#events');
        $.each(res.data, function (i, item) {
          var row = $('<tr>');
          row.append(
            $('<td>').text('Redeem'),
            $('<td>').text(item.user.email),
            $('<td>').text(item.redeemable.name),
            $('<td>').text(item.redeemable.image)
          );
          var approve_row = $('<td>');
          var box = `
            <div class="switch round large">
              <input event_type="redeem" id="`+item.id+`" type="checkbox"`;
          if (item.approved) {
            box += ` checked`;
          }
          box += `>
              <label for="`+item.id+`"></label>
            </div>
          `;
          approve_row.append(box);
          row.append(approve_row);
          row.appendTo('#events');
        });
      }
  });
}

$('#filter').on('click', 'dd', function() {
  $('#filter dd.active').removeClass('active');
  $(this).addClass('active');
  var name = $(this).attr('name');
  if (name == 'tops') {
    tops();
  } else if (name == 'redeem') {
    redeem();
  }
});

$('#events').on('click', 'input', function() {
  var id = $(this).attr.id;
  var type = $(this).attr.event_type;
  // Do memes here.
});
