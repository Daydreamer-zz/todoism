$(document).ready(function () {
    var ENTER_KEY = 13;
    var ESC_KEY = 27;


    // 默认错误信息处理
    $(document).ajaxError(function (event, request) {
        var message = null;

        if (request.responseJSON && request.responseJSON.hasOwnProperty('message')) {
            message = request.responseJSON.message;
        } else if (request.responseText) {
            var IS_JSON = true;
            try {
                var data = JSON.parse(request.responseText);
            }
            catch (err) {
                IS_JSON = false;
            }
            if (IS_JSON && data !== undefined && data.hasOwnProperty('message')) {
                message = JSON.parse(request.responseText).message
            } else {
                message = default_error_message;
            }
        } else {
            message = default_error_message;
        }
        M.toast({html: message});
    });


    // ajax post请求csrf处理
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!/^(GET|HEAD|TRACE|OPTIONS)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader('X-CSRFToken', csrf_token);
            }
        }
    })

    function display_dashboard() {
        var all_count = $('.item').length;
        if (all_count === 0) {
            $('#dashboard').hide();
        } else {
            $('#dashboard').show();
            $('ul.tabs').tabs();
        }
    }

    // 激活新插入的页面中的materialize组件
    function activeM() {
        $('.sidenav').sidenav();
        $('ul.tabs').tabs();
        $('.modal').modal();
        $('.tooltipped').tooltip();
        $('.dropdown-trigger').dropdown({
                constrainWidth: false,
                coverTrigger: false
            }
        );
        display_dashboard();
    }

    // 监听页面路由变化
    $(window).bind('hashchange', function () {
        var hash = window.location.hash.replace('#', '');
        var url = null;
        console.log(hash);
        if (hash == 'login') {
            url = login_page_url;
        } else if (hash == 'app') {
            url = app_page_url;
        } else {
            url = intro_page_url;
        }

        // 向对应的页面发送get请求，服务器端返回对应的局部模板
        $.ajax({
            type: 'GET',
            url: url,
            success: function (data) {
                $('#main').hide().html(data).fadeIn(800);
                activeM();
            }
        })
    })

    // 设置默认location
    if (window.location.hash === '') {
        window.location.hash = '#intro';
    } else {
        $(window).trigger('hashchange');  // 触发hashchange事件，重新加载页面
    }
    
    // 登录
    function login_user() {
        var username = $('#username-input').val();
        var password = $('#password-input').val();
        if (!username || !password) {
            M.toast({html: login_error_message});
            return ;
        }
        var data = {
            'username': username,
            'password': password,
        };
        $.ajax({
            type: 'POST',
            url: login_page_url,
            data: JSON.stringify(data),
            contentType: 'application/json;charset=UTF-8',
            success: function (data) {
                window.location.hash = '#app';
                M.toast({html: data.message});
            }
        });
        
    }
    $(document).on('click', '#login-btn', login_user);



    // 获取测试账户
    function register() {
        $.ajax({
            url: register_url,
            type: 'GET',
            success: function (data) {
                $('#username-input').val(data.username);
                $('#password-input').val(data.password);
            }
        })
    }
    $(document).on('click', '#register-btn', register);
});