let blogID = window.location.href.split('/')[4]
let token = getToken()
// 生成正文
$.ajax({
    type: 'GET',
    url: 'http://<your host/your domain>/api/audit/' + blogID,
    data: {
        token: token
    },
    success: function (data) {
        blogContent = data.data.content
        let title = $('#title')
        let type = $('#type')
        author = $('#author')
        let publishTime = $('#publishTime')
        let dpt = data.data.publish_time.split('T')
        title.text(data.data.title)
        type.html('<span class="type">类型：</span><a href="/type/' + data.data.type + '/">' + types[data.data.type] + '</a>')
        author.html('<a href="/user/' + data.data.user_id + '/">' + data.data.username + '</a>')
        publishTime.html('<span>发布时间：' + dpt[0] + '&nbsp;' + dpt[1] + '</span>')
        const converter = new showdown.Converter();
        document.getElementById("show-area").innerHTML = converter.makeHtml(data.data.content);
        publishTime.before('<div id="manage-blog">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href="javascript:" id="verified">审核通过</a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' +
            '<a href="javascript:" id="deleted">删除</a></div>')
    },
    error: function (jqXHR, textStatus, errorThrown) {
        let err = jqXHR.responseText
        let msg = JSON.parse(err)
        console.log('测试')
        alert(msg.error || JSON.stringify(msg.message).replace('{', '').replace('}', ''))
        window.history.back()
    }
})

// 审核文章
let content = $('.content')
content.on('click', '#deleted', function () {
    $('#deleted').after('<label for="reason">删除原因：</label><input type="text" id="reason" placeholder="请输入删除此文的原因"><button id="confirm-reason">确认</button>')
    $('#confirm-reason').click(function () {
        let reason = $('#reason').val().trim()
        if (!reason) {
            alert('请输入删除理由')
        } else {
            $.ajax({
                type: 'POST',
                url: 'http://<your host/your domain>/api/audit/' + blogID,
                data: {
                    token: token,
                    deleted: true,
                    reason: reason
                },
                success: function (data) {
                    console.log(data)
                    self.location = document.referrer
                }
            })
        }
    })
})
content.on('click', '#verified', function () {
    let result = confirm('通过此 blog？')
    if (result) {
        $.ajax({
            type: 'POST',
            url: 'http://<your host/your domain>/api/audit/' + blogID,
            data: {
                token: token,
                verified: true,
            },
            success: function (data) {
                console.log(data)
                self.location = document.referrer
            }
        })
    }
})