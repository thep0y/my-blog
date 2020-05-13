$(function () {

    let token = getToken()

    if (token) {
        // setCookie('token', '', -1)
        let url
        if (token.indexOf('user') !== -1) {
            url = 'http://<your host/your domain>/api/user?action=get'
        } else if (token.indexOf('admin') !== -1) {
            url = 'http://<your host/your domain>/api/admin/get/'
        } else {
            return false
        }
        $.ajax({
            type: 'POST',
            url: url,
            data: {
                token: token
            },
            success: function (data) {
                $('#username').text(data.username)
                $('#login').remove()
                $('#register').remove()
                let logined = '<li class="dropdown" id="status">' +
                    '<a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true"' +
                    'aria-expanded="false">' + data.username + '&nbsp;&nbsp;<span class="caret"></span></a>' +
                    '<ul class="dropdown-menu">\n' +
                    '<li><a href="/myblog/">我的文章</a></li>\n' +
                    '<li><a href="/comments/' + data.id + '">我的评论</a></li>\n' +
                    '<li><a href="/myfavorite/">我的收藏</a></li>\n' +
                    '<li><a href="/account/">个人中心</a></li>\n' +
                    '<li role="separator" class="divider"></li>\n' +
                    '<li><a href="javascript:;" id="logout">退出</a></li>\n' +
                    '</ul></li>'
                $('#topbar-right').append(logined)
                $('#logout').click(function () {
                    // alert('退出')
                    setCookie('token', '', -1)
                    location.reload()
                })
            },
            error: function (jqXHR, textStatus, errorThrown) {
                setCookie('token', '', -1)  // token失效的话清除cookie
                let err = JSON.parse(jqXHR.responseText)
                alert(err.error)
            }
        })

    }
})

let types = {}
$.ajax({
    type: 'GET',
    async: false,
    url: 'http://<your host/your domain>/api/types/',
    success: function (data) {
        $.each(data.data, function (index, value) {
            types[value.id] = value.type
            $('#types .dropdown-menu').append('<li><a href="/type/' + value.id + '/">' + value.type + '</a></li>')
        })
    }
})

function setCookie(cname, cvalue, exdays) {
    let d = new Date();
    d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
    let expires = "expires=" + d.toString();
    document.cookie = cname + "=" + cvalue + ";path=/;" + expires;
}

function clearCookie(name) {
    setCookie(name, "", -1);
}

function getToken() {
    let cookie = document.cookie;
    let token = ''
    let cookies = cookie.split(';')
    $.each(cookies, function (index, value) {
        b = value.split('=')
        if (b[0] === 'token') {
            token = b[1]
        }
    })
    return token
}

function ajaxError(jqXHR, textStatus, errorThrown) {
    let err = jqXHR.responseText
    let msg = JSON.parse(err)
    alert(msg.error || JSON.stringify(msg.message).replace('{', '').replace('}', ''))
}

//参数n为休眠时间，单位为毫秒:
function sleep(n) {
    const start = new Date().getTime();
    while (true) {
        if (new Date().getTime() - start > n) {
            break;
        }
    }
}

// 生成页码
function generatePages(data, pageSize) {
    let pageCount = Math.ceil(data.count / pageSize)
    let pagesHTML = '<strong>1</strong>'
    for (let i = 2; i <= pageCount; i++) {
        pagesHTML += '<a href="javascript:" id="page-' + i + '">' + i + '</a>'
    }
    if (pageCount > 1) {
        pagesHTML += '<a href="javascript:" id="next">下一页</a>'
    }
    let pages = $('.pages')
    pages.html(pagesHTML)
    return {
        pages: pages,
        pageCount: pageCount
    }
}

// 页码切换
function generatePagesHTML(page, pageCount) {
    if (page === 1) {
        pagesHTML = ''
    } else {
        pagesHTML = '<a href="javascript:" id="prev">&nbsp;上一页</a>'
    }
    for (let j = 1; j < page; j++) {
        pagesHTML += '<a href="javascript:" id="page-' + j + '">' + j + '</a>'
    }
    pagesHTML += '<strong>' + page + "</strong>"
    for (let j = page + 1; j <= pageCount; j++) {
        pagesHTML += '<a href="javascript:" id="page-' + j + '">' + j + '</a>'
    }
    if (page !== pageCount) {
        pagesHTML += '<a href="javascript:" id="next">下一页</a>'
    }
    return pagesHTML
}

function generateBlogTitles(html, value) {
    let pt = value.publish_time.split('T')
    let latestComment = value.latest_comment
    let commentsCount = value.comments
    let cc
    if (!commentsCount) {
        cc = "<div class=\"blog\"><a href=\"javascript:\" class=\"commentsCount\" style='pointer-events: none'>" + value.comments + "</a></div>\n"
    } else {
        cc = "<div class=\"blog\"><a href=\"javascript:\" class=\"commentsCount\">" + value.comments + "</a></div>\n"
    }
    let lc
    if (!latestComment) {
        lc = "<div class=\"blog\"><a href=\"javascript:\" class=\"newCommentTime\" style='pointer-events: none'>暂无评论</a></div>\n"
    } else {
        lc = "<div class=\"blog\"><a href='/blog/" + value.id + "/#comment-" + commentsCount + "' class=\"newCommentTime\" style='font-size: 12px;margin-top: 3px'><span style='color: #007CD5'>" + latestComment.username + "</span></br>" + latestComment.publish_time + "</a></div>\n"
    }
    html += "        <div class=\"blogOverview\">\n" +
        "            <div class=\"blog\"><a href=\"/type/" + value.type + "/\" class=\"type\" style='color: #007CD5'>" + types[value.type] + "</a></div>\n" +
        "            <div class=\"blog\"><a href=\"/blog/" + value.id + "/\" class=\"title\">" + value.title + "</a></div>\n" +
        "            <div class=\"blog\"><a href=\"/user/" + value.user_id + "\" class=\"author\">" + value.username + "</a></div>\n" +
        "            <div class=\"blog\"><a href='javascript;' class=\"publishTime\" style='font-size: 12px;margin-top: 11px'>" + pt[0] + '&nbsp;' + pt[1] + "</a></div>\n" +
        cc + lc +
        "        </div>"
    return html
}

function fillBlogList(data) {
    let blogList = $('.blogList')
    let html = ''
    $.each(data.data, function (index, value) {
        let temp = ''
        html += generateBlogTitles(temp, value)
    })
    blogList.html(html)
    return blogList
}

function pagesToggle(changePage, pages, pageCount) {
    // 页码点击事件
    for (let i = 1; i <= pageCount; i++) {
        pages.on('click', '#page-' + i, function () {
            changePage(i)
        })
    }
    // 上一页点击事件
    pages.on('click', '#prev', function () {
        let page = Number($('.pages strong')[0].innerText) - 1
        changePage(page)
    })
    // 下一页点击事件
    pages.on('click', '#next', function () {
        let page = Number($('.pages strong')[0].innerText) + 1
        changePage(page)
    })
}

$('#search-input').bind('keypress', function (event) {
    if (event.keyCode === 13) {
        let searchWord = $('#search input').val().trim()
        if (!searchWord) {
            alert('搜索关键词不能为空')
        } else {
            window.open('/search/?keyword=' + searchWord)
        }
    }

});

$('#search button').click(function () {
    let searchWord = $('#search input').val().trim()
    if (!searchWord) {
        alert('搜索关键词不能为空')
    } else {
        window.open('/search/?keyword=' + searchWord)
    }
})

function getQueryVariable(variable) {
    const query = window.location.search.substring(1);
    const vars = query.split("&");
    for (let i = 0; i < vars.length; i++) {
        const pair = vars[i].split("=");
        if (pair[0] === variable) {
            return pair[1];
        }
    }
    return false;
}
