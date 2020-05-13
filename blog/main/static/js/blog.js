let commentsArea = $('#comments-area')

let url = window.location.href
let blogID = url.split('/')[4]
let author
let blogContent
let token = getToken()
let commentID = ''
// 生成正文
$.ajax({
    type: 'GET',
    url: 'http://<your host/your domain>/api/blog/' + blogID,
    data: {
        token: getToken()
    },
    success: function (data) {
        blogContent = data.content
        let title = $('#title')
        let type = $('#type')
        author = $('#author')
        let publishTime = $('#publishTime')
        let dpt = data.publish_time.split('T')
        title.text(data.title)
        type.html('<span class="type">类型：</span><a href="/type/' + data.type + '/">' + types[data.type] + '</a>')
        author.html('<a href="/user/' + data.user_id + '/">' + data.username + '</a>')
        publishTime.html('<span>发布时间：' + dpt[0] + '&nbsp;' + dpt[1] + '</span>')
        const converter = new showdown.Converter();
        document.getElementById("show-area").innerHTML = converter.makeHtml(data.content);
    },
    error: function (jqXHR, textStatus, errorThrown) {
        let err = jqXHR.responseText
        let msg = JSON.parse(err)
        alert(msg.error || JSON.stringify(msg.message).replace('{', '').replace('}', ''))
        window.history.back()
    }
})

// 生成评论
let commentsObj = {}
let converter = new showdown.Converter();
$.ajax({
    type: 'GET',
    url: 'http://<your host/your domain>/api/comments' + '?blogID=' + url.split('/')[4],
    success: function (data) {
        let userAgent = navigator.userAgent;
        let allPages = generatePages(data, 10)
        let pages = allPages.pages
        let pageCount = allPages.pageCount
        $.ajax({
            type: 'GET',
            async: false,
            url: 'http://<your host/your domain>/api/comments' + '?blogID=' + url.split('/')[4] + "&pageSize=" + data.count,
            success: function (data) {
                $.each(data.comments, function (i, v) {
                    commentsObj[v.id] = {
                        author: v.author,
                        content: v.content,
                        publishTime: v.publish_time,
                        float: v.float
                    }
                })
            }
        })
        let commentsArea = $('#comments-area')
        let comments = ''
        let firstID = data.comments.length ? data.comments[0].id : null  // 因为数据库中的评论不是根据每个blog从1开始生成，所以需要标记一下文章的第一条评论的id，方便后面切换页码
        if (getToken()) {
            if (userAgent.indexOf("Firefox") > -1) {
                generateComments(data, commentsArea, comments)
            } else {
                waitForReady(generateComments, data, commentsArea, comments)
            }
        } else {
            $.each(data.comments, function (index, value) {
                let dpt = value.publish_time.split('T')
                let quote = addQuote(value, data)
                let comment = ''
                if (value.content !== '已删除') {
                    comment = '<div class="comment" id="comment-' + (index + 1) + '" data-id="' + value.id + '"><div class="pi">' + value.float + '<sup>F</sup></div><div class="clearfix">' + quote + converter.makeHtml(value.content) + '</div><div class="comment-info">' +
                        '<a href="/user/' + value.user_id + '/" class="author">' + value.author + '</a><span class="comment-publish-time">&nbsp;&nbsp;&nbsp;&nbsp;评论于&nbsp;' + dpt[0] + '&nbsp;' + dpt[1] + '&nbsp;&nbsp;&nbsp;&nbsp;</span><button>回复</button></div></div>'
                }
                comments += comment
                if (index === 0) {
                    firstID = value.id
                }
            })
            commentsArea.html(comments)
        }

        function addQuote(value, data) {
            let replyID = value.reply_id
            let quote = ''
            if (replyID) {
                console.log(value.id)
                console.log(replyID)
                console.log(commentsObj[replyID])
                let dpt = commentsObj[replyID].publishTime.split('T')
                let content = commentsObj[replyID].content
                let text = converter.makeHtml(content).replace(/<[^<>]+>/g, "").replace(/[\r\n]/g, " ").replace(/\s+/g, '。')
                quote = '>回复：' + commentsObj[replyID].float + '楼&nbsp;&nbsp;-->&nbsp;&nbsp;' + commentsObj[replyID].author + '&nbsp;&nbsp;&nbsp;&nbsp;评论于&nbsp;' + dpt[0] + '&nbsp;' + dpt[1] + '<br>' + text.substring(0, 100)
                quote = converter.makeHtml(quote)
            }
            return quote
        }


        function changePage(page) { // 页码切换
            let pagesHTML = generatePagesHTML(page, pageCount)
            pages.html(pagesHTML)
            $.ajax({
                type: 'GET',
                url: 'http://<your host/your domain>/api/comments' + '?blogID=' + url.split('/')[4] + '&page=' + page,
                success: function (data) {
                    let commentsArea = $('#comments-area')
                    let comments = ''

                    if (userAgent.indexOf("Firefox") > -1) {
                        generateComments(data, commentsArea, comments, page)
                    } else {
                        waitForReady(generateComments, data, commentsArea, comments, page)
                    }

                }
            })
        }

        function generateComments(data, commentsArea, comments, page = 1) {
            $.each(data.comments, function (index, value) {
                let dpt = value.publish_time.split('T')
                let quote = addQuote(value, data)
                let edit = ''
                if ($('#status .dropdown-toggle').text().trim() === value.author) {
                    edit = '<a href="javascript:" class="edit-comments">编辑</a>'
                }
                if (token.indexOf('admin') > -1) {
                    edit = '<div class="manage-comment">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' +
                        '<a href="javascript:" class="blocked-comment">封禁</a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href="javascript:" class="deleted-comment">删除</a></div>'
                }
                let comment = ''
                if (value.content !== '已删除') {
                    comment = '<div class="comment" id="comment-' + (index + 1 + (page - 1) * 10) + '" data-id="' + value.id + '"><div class="pi">' + value.float + '<sup>F</sup></div><div class="clearfix">' + quote + converter.makeHtml(value.content) + '</div><div class="comment-info">' +
                        edit + '<a href="/user/' + value.user_id + '/" class="author">' + value.author + '</a><span class="comment-publish-time">&nbsp;&nbsp;&nbsp;&nbsp;评论于&nbsp;' + dpt[0] + '&nbsp;' + dpt[1] + '&nbsp;&nbsp;&nbsp;&nbsp;</span><button class="reply">回复</button></div></div>'
                }
                comments += comment
            })
            commentsArea.html(comments)
        }

        pagesToggle(changePage, pages, pageCount)


        if (userAgent.indexOf("Firefox") > -1) {
            editBlog()
        } else {
            waitForReady(editBlog)
        }
    },
    error: function (jqXHR, textStatus, errorThrown) {
        let err = jqXHR.responseText
        let msg = JSON.parse(err)
        alert(msg.error || JSON.stringify(msg.message).replace('{', '').replace('}', ''))
    }
})

// 发表新评论
$('#publishAddComment').click(function () {
    let content = $('#addComment').val().replace(/>回复\S+\n\n/g, '')
    if (!content.trim()) {
        alert('评论不能为空')
    } else {
        $.ajax({
            type: 'POST',
            url: 'http://<your host/your domain>/api/comments',
            data: {
                token: getToken(),
                blogID: url.split('/')[4],
                content: content,
                replyID: commentID
            },
            success: function (data) {
                $('#addComment').val('')
                location.reload()
            },
            error: function (jqXHR, textStatus, errorThrown) {
                let err = jqXHR.responseText
                let msg = JSON.parse(err)
                alert(msg.error || JSON.stringify(msg.message).replace('{', '').replace('}', ''))
            }
        })
    }
})

commentsArea.on('click', 'button.reply', function () {
    let comment = $(this).parent().parent()
    commentID = comment.attr('data-id')
    let dataID = comment.attr('data-id')
    let addComment = $('#addComment')
    if ($(this).text() === '回复') {
        $.ajax({
            type: 'GET',
            url: 'http://<your host/your domain>/api/comment/' + dataID + '?token=' + getToken(),
            success: function (data) {
                let dpt = data.publish_time.split('T')
                let text = converter.makeHtml(data.content.replace(/^>回复\S+\n/g, '')).replace(/<[^<>]+>/g, "").replace(/[\r\n]/g, " ").replace(/\s+/g, '。')
                let quote = '>回复：' + data.float + '楼&nbsp;&nbsp;-->&nbsp;&nbsp;' + data.author + '&nbsp;&nbsp;&nbsp;&nbsp;评论于&nbsp;' + dpt[0] + '&nbsp;' + dpt[1] + '<br>' + text.substring(0, 100)
                addComment.val(quote + '\n\n')
            },
            error: function (jqXHR, textStatus, errorThrown) {
                let err = jqXHR.responseText
                let msg = JSON.parse(err)
                alert(msg.error || JSON.stringify(msg.message).replace('{', '').replace('}', ''))
            }
        })
        $('html, body').animate({scrollTop: addComment.offset().top - 400}, 1000)  // 平滑滚动到发布评论
        addComment.focus()
    } else if ($(this).text() === '确认') {
        let content = comment.children('textarea').val()
        $.ajax({
            type: 'PUT',
            url: 'http://<your host/your domain>/api/comment/' + dataID,
            data: {
                token: getToken(),
                content: content
            },
            success: function (data) {
                comment.children('textarea').remove()
                comment.children('.pi').after('<div class="clearfix">' + converter.makeHtml(data.content) + '</div>')
            }
        })
    }
})


let clearfix
commentsArea.on('click', '.edit-comments', function () {
    let comment = $(this).parent().parent()
    let temp = clearfix
    let pi = comment.children('.pi')
    if ($(this).text() === '编辑') {
        let dataID = comment.attr('data-id')
        $.ajax({
            type: 'GET',
            url: 'http://<your host/your domain>/api/comment/' + dataID + '?token=' + getToken(),
            success: function (data) {
                clearfix = comment.children('.clearfix')[0]
                let content = data.content
                let textarea = '<textarea class="edit-comment-area" style="width: 1120px"></textarea>'
                clearfix.remove()
                pi.after(textarea)
                comment.children('textarea').val(content)
                comment.find('button').text('确认')
                comment.find('.edit-comments').text('取消')
            }
        })
    } else if ($(this).text() === '取消') {
        comment.children('textarea').remove()
        pi.after(temp.outerHTML)
        comment.find('button').text('回复')
        comment.find('.edit-comments').text('编辑')
    }
})

// 收藏功能
if (token) {
    $.ajax({
        type: 'GET',
        url: 'http://<your host/your domain>/api/favorite/',
        data: {
            token: getToken(),
            blog_id: blogID,
        },
        success: function (data) {
            if (data.favorite) {
                $('#addComment').before('<button id="delete-favorite">取消收藏</button>')
                $('#delete-favorite').click(function () {
                    $.ajax({
                        type: 'DELETE',
                        url: 'http://<your host/your domain>/api/favorite/',
                        data: {
                            token: getToken(),
                            blog_id: blogID,
                        },
                        success: function (data) {
                            $('#delete-favorite').remove()
                            $('#addComment').before('<button id="favorite">收藏</button>')
                            location.reload() // 最简单的是直接刷新更改网页的收藏状态

                        },
                        error: function (jqXHR, textStatus, errorThrown) {
                            let err = jqXHR.responseText
                            let msg = JSON.parse(err)
                            alert(msg.error || JSON.stringify(msg.message).replace('{', '').replace('}', ''))
                        }
                    })
                })
            } else {
                $('#addComment').before('<button id="favorite">收藏</button>')
                $('#favorite').click(function () {
                    $.ajax({
                        type: 'POST',
                        url: 'http://<your host/your domain>/api/favorite/',
                        data: {
                            token: getToken(),
                            blog_id: blogID,
                        },
                        success: function (data) {
                            $('#favorite').remove()
                            $('#addComment').before('<button id="delete-favorite">取消收藏</button>')
                            location.reload()
                        },
                        error: function (jqXHR, textStatus, errorThrown) {
                            let err = jqXHR.responseText
                            let msg = JSON.parse(err)
                            alert(msg.error || JSON.stringify(msg.message).replace('{', '').replace('}', ''))
                        }
                    })
                })
            }
        }
    })
}


function check() {
    return $('#status .dropdown-toggle').text().trim();
}

function waitForReady(f, ...args) {
    if (!check()) {
        return setTimeout(waitForReady, 50, f, ...args); // 每50毫秒检查一下
    } else {
        f(...args)
    }
}


function editBlog() {
    if (author.text() === $('#status .dropdown-toggle').text().trim()) {
        let showArea = $('#show-area')
        showArea.before('<div id="edit-blog"><a href="javascript:">编辑本文</a></div>')
        $('#edit-blog').click(function () {
            let title = $('#title')
            title.remove()
            $('#type').after('<input type="text" id="title" value="' + title.text() + '">')
            $('#show-area').remove()
            $('#edit-blog').after('<textarea id="show-area"></textarea>')
            $(this).html('')
            $('#area #show-area').val(blogContent)
            $('#show-area').after('<button id="cancel">取消</button><button id="confirm">确认</button>')
            $('#confirm').click(function () {
                let newTitle = $('#title').val().trim()
                if (newTitle) {
                    if (newTitle.length > 40) {
                        alert('标题不能超过40个字符')
                    } else {
                        let content = $('#show-area').val()
                        if (content < 5) {
                            alert('内容最少包含5个字符')
                        } else {
                            if (title.text() === newTitle && content === blogContent) {
                                alert('未修改')
                                location.reload()
                            } else {
                                $.ajax({
                                    type: 'PUT',
                                    url: 'http://<your host/your domain>/api/blog/' + blogID,
                                    data: {
                                        token: getToken(),
                                        type: $('#type a').attr('href').split('/')[2],
                                        title: newTitle,
                                        content: content,
                                    },
                                    success: function (data) {
                                        location.reload()
                                    },
                                    error: function (jqXHR, textStatus, errorThrown) {
                                        let err = jqXHR.responseText
                                        let msg = JSON.parse(err)
                                        alert(msg.error || JSON.stringify(msg.message).replace('{', '').replace('}', ''))
                                    }
                                })
                            }
                        }
                    }
                }
            })
            $('#cancel').click(function () {
                location.reload()
            })
        })
    }
    if (token.indexOf('admin') > -1) {
        let publishTime = $('#publishTime')
        publishTime.before('<div id="manage-blog">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' +
            '<a href="javascript:" id="blocked">封禁</a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href="javascript:" id="deleted">删除</a></div>')
    }
}

// 管理文章
let content = $('.content')
content.on('click', '#deleted', function () {
    $('#deleted').after('<label for="delete-reason">删除原因：</label><input type="text" id="delete-reason" placeholder="请输入删除此文的原因"><button id="confirm-delete-reason">确认</button>')
    $('#confirm-delete-reason').click(function () {
        let reason = $('#delete-reason').val().trim()
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
                    self.location = document.referrer
                },
                error: function (jqXHR, textStatus, errorThrown) {
                    let err = jqXHR.responseText
                    let msg = JSON.parse(err)
                    alert(msg.error || JSON.stringify(msg.message).replace('{', '').replace('}', ''))
                }
            })
        }
    })
})
content.on('click', '#blocked', function () {
    $('#blocked').after('<label for="block-reason">封禁原因：</label><input type="text" id="block-reason" placeholder="请输入删除此文的原因"><button id="confirm-block-reason">确认</button>')
    $('#confirm-block-reason').click(function () {
        let reason = $('#block-reason').val().trim()
        if (!reason) {
            alert('请输入封禁理由')
        } else {
            $.ajax({
                type: 'POST',
                url: 'http://<your host/your domain>/api/block/',
                data: {
                    token: token,
                    action: 'blog',
                    id: blogID,
                    reason: reason
                },
                success: function (data) {
                    self.location = document.referrer
                },
                error: function (jqXHR, textStatus, errorThrown) {
                    let err = jqXHR.responseText
                    let msg = JSON.parse(err)
                    alert(msg.error || JSON.stringify(msg.message).replace('{', '').replace('}', ''))
                }
            })
        }
    })
})

// 管理评论
commentsArea.on('click', '.blocked-comment', function () {
    $(this).after('<label for="block-reason">封禁原因：</label><input type="text" id="block-reason" placeholder="请输入删除此文的原因"><button id="confirm-block-reason">确认</button>')
    $(this).parent().children('#confirm-block-reason').click(function () {
        let reason = $('#block-reason').val().trim()
        if (!reason) {
            alert('请输入封禁理由')
        } else {
            let currentCommentID = $(this).parent().parent().parent().attr('data-id')
            $.ajax({
                type: 'POST',
                url: 'http://<your host/your domain>/api/manac/' + currentCommentID,
                data: {
                    token: token
                },
                success: function (data) {
                    alert('已封禁 id 为 ' + currentCommentID + ' 的评论')
                    location.reload()
                }
            })
        }
    })
})
commentsArea.on('click', '.deleted-comment', function () {
    $(this).after('<label for="delete-reason">删除原因：</label><input type="text" id="delete-reason" placeholder="请输入删除此文的原因"><button id="confirm-delete-reason">确认</button>')
    $(this).parent().children('#confirm-delete-reason').click(function () {
        let reason = $('#delete-reason').val().trim()
        if (!reason) {
            alert('请输入删除理由')
        } else {
            let currentCommentID = $(this).parent().parent().parent().attr('data-id')
            $.ajax({
                type: 'DELETE',
                url: 'http://<your host/your domain>/api/manac/' + currentCommentID,
                data: {
                    token: token
                },
                success: function (data) {
                    alert('已删除 id 为 ' + currentCommentID + ' 的评论')
                    location.reload()
                }
            })
        }
    })
})