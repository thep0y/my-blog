$(function () {
    let $username = $('#username')
    let $password = $('#password')
    let $email = $('#email')
    let $phone = $('#phone')
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
    $email.change(function () {
        let email = $email.val().trim()
        if (email) {
            $('#email_status').html('')
        }
    })
    $phone.change(function () {
        let phone = $phone.val().trim()
        if (phone) {
            $('#phone_status').html('')
        }
    })
})

function check() {
    let username = $('#username').val().trim()
    let email = $('#email').val().trim()
    let password = $('#password').val().trim()
    let phone = $('#phone').val().trim()
    let $username_status = $('#username_status')
    let $password_status = $('#password_status')
    let $email_status = $('#email_status')
    let $phone_status = $('#phone_status')
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
    if (!email) {
        $email_status.html('邮箱不能为空').css({
            'color': 'red',
            'font-size': '0.8rem'
        })
        return false
    }
    if (!phone) {
        $phone_status.html('手机号不能为空').css({
            'color': 'red',
            'font-size': '0.8rem'
        })
        return false
    }

    let username_color = $username_status.css('color')
    let password_color = $password_status.css('color')
    let email_color = $email_status.css('color')
    let phone_color = $phone_status.css('color')
    let red = "rgb(255, 0, 0)"
    // 任何一个提示文字为红色(rgb(255,0,0))，都不能提交，返回false
    if (username_color == red) {  // 因为username_color本身是个字符串，所以"rgb(255, 0, 0)"里的空格一个也不能少
        return false
    } else if (email_color == red) {
        return false
    } else if (password_color == red) {
        return false
    } else if (phone_color == red) {
        return false
    }

    $.ajax({
        type: 'POST',
        // async: false,  // ajax执行完再向下执行(关闭异步, 异步默认打开)
        url: 'http://<your host/your domain>/api/user?action=register',
        dateType: 'json',
        data: {
            username: username,
            password: password,
            email: email,
            phone: phone
        },
        error: function (jqXHR, textStatus, errorThrown) {
            // alert(jqXHR.responseText)
            // alert(jqXHR.status)
            // alert(jqXHR.readyState)
            // alert(jqXHR.statusText)
            // alert(textStatus)
            // alert(errorThrown)

            let err = jqXHR.responseText
            let msg = JSON.parse(err).error
            alert(msg)
            console.log('注册失败')
        },
        success: function (data) {
            console.log('注册成功')
            // window.open('http://127.0.0.1:5000/')  // 在新窗口中打开页面
            window.location.href='http://127.0.0.1:5000/'
        }
    })

    return false
}