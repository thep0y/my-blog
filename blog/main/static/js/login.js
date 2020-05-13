$(function () {
    let $username = $('#username')
    let $password = $('#password')
    $username.change(function () {
        let username = $username.val().trim()
        if (username) {
            $('#username_status').html('')
        }
    })
    $password.change(function () {
        let password = $password.val().trim()
        if (password) {
            $('#password_status').html('')
        }
    })
})

$('#submit').click(function () {
    let currentUrl = window.location.href
    let username = $('#username').val().trim()
    let password = $('#password').val().trim()
    let $username_status = $('#username_status')
    let $password_status = $('#password_status')
    if (!username) {
        $username_status.html('用户名不能为空').css({
            'color': 'red',
            'font-size': '0.8rem'
        })
        return false
    }
    if (!password) {
        $password_status.html('密码不能为空').css({
            'color': 'red',
            'font-size': '0.8rem'
        })
        return false
    }
    let url
    let status = true
    if (currentUrl.indexOf('admin') === -1) {
        url = 'http://<your host/your domain>/api/user?action=login'
        status = false
    } else {
        url = 'http://<your host/your domain>/api/admin/login/'
        status = true
    }
    $.ajax({
        type: 'POST',
        url: url,
        data: {
            username: username,
            password: password
        },
        error: function (jqXHR, textStatus, errorThrown) {
            let err = jqXHR.responseText
            let msg = JSON.parse(err).error
            console.log(msg)
            alert(msg)
        },
        success: function (data) {
            setCookie('token', data.token, 30)
            if (!status) {
                window.location.href = document.referrer;  // 返回登录前的上一页并刷新
            } else {
                window.location.href = 'http://127.0.0.1:5000/admin/'
            }
        },
    })
})