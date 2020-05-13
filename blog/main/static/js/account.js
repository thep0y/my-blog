let token = getToken()
let content = $('.content')
if (token) {
    let html = '    <div id="changeEmail" class="change">\n' +
        '        <h3>修改邮箱</h3>\n' +
        '        <br>\n' +
        '        <label for="newEmail">邮箱地址：</label><input type="text" placeholder="请输入新邮箱" id="newEmail">\n' +
        '        <button id="sendVerifyEmail">获取验证码</button>\n' +
        '        <br>\n' +
        '        <label for="verifyEmail">验&nbsp;&nbsp;证&nbsp;&nbsp;码：</label><input type="text" placeholder="请输入验证码"\n' +
        '                                                                            id="verifyEmail">\n' +
        '        <br>\n' +
        '        <button class="confirm">确认</button>\n' +
        '    </div>\n' +
        '    <div id="changePhone" class="change">\n' +
        '        <h3>修改手机</h3>\n' +
        '        <br>\n' +
        '        <label for="newPhone">手机号码：</label><input type="text" placeholder="请输入新邮箱" id="newPhone">\n' +
        '        <button id="sendVerifyPhone">获取验证码</button>\n' +
        '        <br>\n' +
        '        <label for="verifyPhone">验&nbsp;&nbsp;证&nbsp;&nbsp;码：</label><input type="text" placeholder="请输入验证码"\n' +
        '                                                                            id="verifyPhone">\n' +
        '        <br>\n' +
        '        <button class="confirm">确认</button>\n' +
        '    </div>\n' +
        '    <div id="changePwd" class="change">\n' +
        '        <h3>修改密码</h3>\n' +
        '        <br>\n' +
        '        <label for="oldPwd">旧&nbsp;&nbsp;密&nbsp;&nbsp;码：</label><input type="password" placeholder="请输入旧密码" id="oldPwd">\n' +
        '        <br>\n' +
        '        <label for="newPwd">新&nbsp;&nbsp;密&nbsp;&nbsp;码：</label><input type="password" placeholder="请输入新密码" id="newPwd">\n' +
        '        <br>\n' +
        '        <label for="confirmNewPwd">确认密码：</label><input type="password" placeholder="请再次输入新密码" id="confirmNewPwd">\n' +
        '        <br>\n' +
        '        <button class="confirm">确认</button>\n' +
        '    </div>'
    content.html(html)
    let flag = true
    let time = 60
    $('#sendVerifyEmail').click(function () {
        let emailReg = /^([a-zA-Z0-9]+[_|\_|\.]?)*[a-zA-Z0-9]+@([a-zA-Z0-9]+[_|\_|\.]?)*[a-zA-Z0-9]+\.[a-zA-Z]{2,3}$/
        let email = $('#newEmail').val().trim()
        if (email && flag) {
            let timer = setInterval(function () {
                if (time === 60 && flag) {
                    flag = false

                    if (emailReg.test(email)) {
                        $('#sendVerifyEmail').attr('disabled', true)
                        $.ajax({
                            type: 'POST',
                            url: 'http://<your host/your domain>/api/verify/' + email + '?action=email',
                            success: function (data) {
                                $('#sendVerifyEmail').text('已发送')
                            },
                            error: function (jqXHR, textStatus, errorThrown) {
                                let err = jqXHR.responseText
                                let msg = JSON.parse(err)
                                alert(msg.error || JSON.stringify(msg.message).replace('{', '').replace('}', ''))
                                location.reload()
                            }
                        })
                    } else {
                        alert('邮箱格式不正确')
                    }
                } else if (time === 0) {
                    $('#sendVerifyEmail').removeAttr('disabled')
                    $('#sendVerifyEmail').text('获取验证码')
                    clearInterval(timer)
                    time = 60
                    flag = true
                } else {
                    $("#sendVerifyEmail").html(time + " s 后可重新发送");
                    time--;
                }
            }, 1000)
        } else {
            alert('邮箱不能为空')
        }
    })
    $('#changeEmail .confirm').click(function () {
        let email = $('#newEmail').val().trim()
        let verifyCode = $('#verifyEmail').val().trim()
        if (verifyCode && email) {
            $.ajax({
                type: "PATCH",
                url: 'http://<your host/your domain>/api/user',
                data: {
                    token: getToken(),
                    email_verify_code: verifyCode,
                    email: email
                },
                success: function (data) {
                    alert('您的邮箱已修改为：「' + email + '」')
                    location.reload()
                },
                error: function (jqXHR, textStatus, errorThrown) {
                    let err = jqXHR.responseText
                    let msg = JSON.parse(err)
                    alert(msg.error || JSON.stringify(msg.message).replace('{', '').replace('}', ''))
                    location.reload()
                }
            })
        } else {
            if (!email) {
                alert('邮箱为空')
            } else if (!verifyCode) {
                alert('验证码为空')
            }
        }
    })
    $('#sendVerifyPhone').click(function () {
        alert('暂不支持修改手机号')
    })
    $('#changePhone .confirm').click(function () {
        alert('暂不支持修改手机号')
    })

    let oldPwd = $('#oldPwd')
    let newPwd = $('#newPwd')
    let confirmNewPwd = $('#confirmNewPwd')
    newPwd.change(function () {
        let pwd = $(this).val()
        if (pwd === oldPwd.val()) {
            oldPwd.after('<span class="pwd-status same" style="color: red">新旧密码不可相同。</span>')
            $(this).after('<span class="pwd-status same" style="color: red">新旧密码不可相同。</span>')
        } else {
            $('span.same').remove()
        }
    })

    let warning = true
    $('#changePwd .confirm').click(function () {
        let pwd = confirmNewPwd.val()
        if (pwd !== newPwd.val() && warning) {
            warning = false
            newPwd.after('<span class="pwd-status not-same" style="color: red">两次密码不一致。</span>')
            confirmNewPwd.after('<span class="pwd-status not-same" style="color: red">两次密码不一致。</span>')
        }
        if (!$('.pwd-status').length) {
            $.ajax({
                type: 'POST',
                url: 'http://<your host/your domain>/api/user/chpwd/',
                data: {
                    token: token,
                    old: oldPwd.val().trim(),
                    new: newPwd.val().trim()
                },
                success: function (data) {
                    setCookie('token', '', -1)
                    alert('密码已修改')
                    window.location.reload()
                },
                error: function (jqXHR, textStatus, errorThrown) {
                    let err = jqXHR.responseText
                    let msg = JSON.parse(err)
                    alert(msg.error || JSON.stringify(msg.message).replace('{', '').replace('}', ''))
                }
            })
        } else {
            alert('三个密码项有误，请修改')
        }
    })
} else {
    content.html('<span class="notLogin">未登录</span>')
}


