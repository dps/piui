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
      window.location.href = newpage;
      return null;
    } else {
      return msg_json;
    }
}

var consolePoll = function () {
  $.get("/poll", {}, function(xml) {
       setTimeout(function() {consolePoll()}, 0);
       msg_json = dispatch(xml);
       if (msg_json != null && msg_json.cmd === "print") {
           // format and output result
           $('<p>' + msg_json.msg + '</p>').insertBefore('#console');
           $('html, body').animate({scrollTop: $(document).height()}, 'fast');
       }
     });    
}

var BEFORE = "#end";
function poll() {
  $.get("/poll", {}, function(xml) {
       setTimeout(function() {poll()}, 0);
       msg = dispatch(xml);
       if (msg != null) {
         if (msg.cmd === "postpage") {
           $('#hdr').append('<a href="#"" class="button-prev">' + msg.prevtxt + '</a>');
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
           $('#' + msg.eid).click(function(o) {
              $.get('/click?eid=' + $(this).attr('id'), {}, function (r) {});
            });
           document.querySelector('#' + tid).addEventListener('toggle',
              function(event) {
                $.get('/toggle?eid=' + $(this).attr('id') +'&v=' + event["detail"]["isActive"]);
              });
         }
       }
     });    
}

window.consolePoll = consolePoll;
window.poll = poll;
}();