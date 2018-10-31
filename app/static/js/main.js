/* site-base.html */
(function() {
  "use strict";

  $("label[for]").each(function(idx, ele) {
    var label = $(ele);
    if ($("input[id=" + label.attr("for") + "]").attr('required') !== undefined) {
      label.prepend('<span class="text-danger">* </span>')
    }
  });

  var pathname = window.location.pathname;
  var path = pathname.substring(pathname.lastIndexOf("/") + 1);
  $("header ul li.nav-item a.nav-link").each(function(idx, ele) {
    var a = $(ele);
    var href = a.attr("href");
    if (href.substring(href.lastIndexOf("/") + 1) == path) {
      a.addClass('active');
    }
  });

})();


/* queue.html */
(function() {
  "use strict";

  $("select.select-status").change(function() {
    var select = $(this);
    var statusVal = parseInt(select.val());

    var statusColor = ["text-danger", "text-warning", "text-success"];
    for (var i = 0; i < statusColor.length; i++) {
      select.removeClass(statusColor[i]);
    };
    select.addClass(statusColor[statusVal]);

    var urlParams = new URLSearchParams(window.location.search);
    $.ajax({
        url: select.attr('action') + "?token=" + urlParams.get("token"),
        type: select.attr('method'),
        data: {
          queueID: select.parent("td").prev("th").html(),
          status: statusVal,
        },
      })
      .done(function(res) {
        switch (res.errcode) {
          case 0:
            break;
          default:
            console.error(res);
            alert("设置失败！");
            throw new Error(res.errmsg);
            break;
        }
      })
      .fail(function(res) {
        throw new Error(res);
      });
    return false;
  });

})();


/* check.html */
(function() {
  "use strict";

  $("form#form-check").submit(function() {
    var form = $(this);
    $.ajax({
        url: form.attr("action"),
        type: form.attr("method"),
        data: form.serialize(),
      })
      .done(function(res) {
        switch (res.errcode) {
          case 0:
            window.location.href = res.redirect;
            break;
          case 302: // 订单未找到
            var emailInput = form.find('input#form-email');
            emailInput.addClass("is-invalid").next("div.invalid-feedback").removeAttr('hidden');
            emailInput[0].oninput = function() {
              $(this).removeClass("is-invalid").next("div.invalid-feedback").attr('hidden', 'hidden');
            };
            break;
          default:
            console.error(res);
            throw new Error(res.errmsg);
            break;
        }
      })
      .fail(function(res) {
        throw new Error(res);
      });
    return false;
  });

})();


/* new.html */
(function() {
  "use strict";

  $("form#form-order").submit(function() {
    var form = $(this);
    $.ajax({
        url: form.attr('action'),
        type: form.attr('method'),
        data: form.serialize(),
      })
      .done(function(res) {
        switch (res.errcode) {
          case 0:
            window.location.href = res.redirect;
            break;
          case 301: // 表单重复创建
            var emailInput = form.find('input#form-email');
            emailInput.addClass("is-invalid").next("div.invalid-feedback").removeAttr('hidden');
            emailInput[0].oninput = function() {
              $(this).removeClass("is-invalid").next("div.invalid-feedback").attr('hidden', 'hidden');
            };
            break;
          default:
            console.error(res);
            throw new Error(res.errmsg);
            break;
        };
      })
      .fail(function(res) {
        throw new Error(res);
      });
    return false;
  });

})();


/* order.html */
(function() {
  "use strict";

  $("button#btn-register").click(function() {
    var btn = $(this);
    var urlParams = new URLSearchParams(window.location.search);
    $.ajax({
        url: btn.attr("action") + "?token=" + urlParams.get('token'),
        type: btn.attr("method"),
        data: {
          order: urlParams.get('order'),
        },
      })
      .done(function(res) {
        switch (res.errcode) {
          case 0:
            window.location.href = res.redirect;
            break;
          default:
            console.error(res);
            throw new Error(res.errmsg);
            break;
        }
      })
      .fail(function(res) {
        throw new Error(res);
      });
    return false;
  });

  $("form#form-withdraw").submit(function() {
    var form = $(this);
    $.ajax({
        url: form.attr('action'),
        type: form.attr('method'),
        data: form.serialize(),
      })
      .done(function(res) {
        console.log(res);
        switch (res.errcode) {
          case 0:
            console.log('ok');
            window.location.href = res.redirect;
            break;
          case 302: // 订单未找到
            var emailInput = form.find('input#form-email');
            emailInput.addClass("is-invalid").next("div.invalid-feedback").removeAttr('hidden');
            emailInput[0].oninput = function() {
              $(this).removeClass("is-invalid").next("div.invalid-feedback").attr('hidden', 'hidden');
            };
            break;
          case 201: // 校验码错误
            var chksnInput = form.find('input#form-chksn');
            chksnInput.addClass("is-invalid").next("small.form-text").attr('hidden', 'hidden').next("div.invalid-feedback").removeAttr('hidden');
            chksnInput[0].oninput = function() {
              $(this).removeClass("is-invalid").next("small.form-text").removeAttr('hidden').next("div.invalid-feedback").attr('hidden', 'hidden');
            };
            break;
          default:
            console.error(res);
            throw new Error(res.errmsg);
            break;
        }
      })
      .fail(function(res) {
        throw new Error(res);
      });
    return false;
  });

})();


/* register.html */
(function() {
  "use strict";

  $("form#form-register").submit(function() {
    var urlParams = new URLSearchParams(window.location.search);
    var form = $(this);
    $.ajax({
        url: form.attr('action') + "&token=" + urlParams.get("token"),
        type: form.attr('method'),
        data: form.serialize(),
      })
      .done(function(res) {
        switch (res.errcode) {
          case 0:
            window.location.href = res.redirect;
            break;
          case 302: // 订单未找到
            var emailInput = form.find('input#form-email');
            emailInput.addClass("is-invalid").next("div.invalid-feedback").removeAttr('hidden');
            emailInput[0].oninput = function() {
              $(this).removeClass("is-invalid").next("div.invalid-feedback").attr('hidden', 'hidden');
            };
            break;
          default:
            console.error(res);
            throw new Error(res.errmsg);
            break;
        }
      })
      .fail(function(res) {
        throw new Error(res);
      });
    return false;
  });

})();