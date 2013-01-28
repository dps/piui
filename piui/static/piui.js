/**
 * piui.js
 **/

!function() {

var dispatch = function (msg) {
    msg_json = JSON.parse(msg)
    if (msg_json.cmd === "timeout") {
      // Do nothing, will re-poll
      return null;
    } else if (msg_json.cmd === "newpage") {
      newpage = msg_json.page;
      console.log('newpage');
      // Reset the dynamic parts of the page back to initial state.
      $('#hdr').html('<h1 class="title" id="title"></h1>');
      $('#padded').html('<p id="end"></p>');
      $('#padded').removeClass('content-padded');
      $('#console').html('<p id="consoleend"></p>');

      if (newpage === "console") {
        $('#console').css('visibility', 'visible');
        $('.content').css('visibility', 'hidden');
      } else {
        $('#console').css('visibility', 'hidden');
        $('.content').css('visibility', 'visible');
      }

      return null;
    } else {
      return msg_json;
    }
}

var initPiUi = function() {
  console.log("PiUi init");
  $.get("/init", {}, function(r) {poll();});
}

var BEFORE = "#end";
function poll() {
  $.get("/poll", {}, function(xml) {
       msg = dispatch(xml);
       console.log("PiUi msg");
       console.log(msg);
       if (msg != null) {
         if (msg.cmd === "print") {
           // format and output result
           $('<p>' + msg.msg + '</p>').insertBefore('#consoleend');
           $('html, body').animate({scrollTop: $(document).height()}, 'fast');
         } else if (msg.cmd === "pagepost") {
           if (msg.previd) {
             $('#hdr').prepend('<a href="#" id="' + msg.previd + '" class="button-prev">' + msg.prevtxt + '</a>');
             $('#' + msg.previd).click(function(o) {
               $.get('/click?eid=' + $(this).attr('id'), {}, function (r) {});
             });
             $('#padded').toggleClass('content-padded');
           }
           $('#title').append(msg.title);
         } if (msg.cmd === "addelement") {
           $('<' + msg.e + ' id="' + msg.eid + '">' + msg.txt + '</' + msg.e + '>').insertBefore(BEFORE)
         } else if (msg.cmd === "updateinner") {
           $('#' + msg.eid).html(msg.txt);
         } else if (msg.cmd === "addbutton") {
           $('<a class="button" id="' + msg.eid + '">' + msg.txt + '</a>').insertBefore(BEFORE);
           $('#' + msg.eid).click(function(o) {
              $.get('/click?eid=' + $(this).attr('id'), {}, function (r) {});
           });
         } else if (msg.cmd === "addinput") {
           $('<input id="' + msg.eid + '" type="' + msg["type"] +'" placeholder = "' + msg.placeholder +'">').insertBefore(BEFORE);
         } else if (msg.cmd === "getinput") {
           $.get('/state?msg=' + $('#' + msg.eid).val(), {}, function (r) {});
         } else if (msg.cmd === "addimage") {
           $('<img id="' + msg.eid + '" src="/imgs/' + msg.src +'">').insertBefore(BEFORE);
         } else if (msg.cmd === "setimagesrc") {
           $('#' + msg.eid).attr('src', '/imgs/' + msg["src"]);
         } else if (msg.cmd === "addul") {
           $('<ul class="list" id="' + msg.eid + '" ></ul>').insertBefore(BEFORE);
         } else if (msg.cmd === "addli") {
           chevron = "";
           if (msg.chevron === '1') {
             chevron = "<span class='chevron'></span>";
           }
           toggle = "";
           if (msg.toggle === '1') {
             toggle = "<div class='toggle' id='" + msg.tid +
                 "'><div class='toggle-handle'></div></div>";
           }
           new_html = "<li id='" + msg.eid + "'><a>" + msg.txt + toggle + chevron + "</a></li>";
           $('#' + msg.pid).append(new_html);
           if (msg.toggle === '1') {
               document.querySelector('#' + msg.tid).addEventListener('toggle',
                  function(event) {
                    $.get('/toggle?eid=' + $(this).attr('id') +'&v=' + event["detail"]["isActive"]);
                  });
           }

           $('#' + msg.eid).click(function(o) {
              $.get('/click?eid=' + $(this).attr('id'), {}, function (r) {});
            });
         }
       }
       setTimeout(function() {poll()}, 0);
     });    
}

window.initPiUi = initPiUi;
}();