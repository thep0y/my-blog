let content = $('.content')
$('title').text('我的所有评论')
content.append('<span id="userCommentsTile">我的所有评论</span>')
content.append('<div class="pages top"></div>')
content.append('<div class="pages bottom"></div>')

let converter = new showdown.Converter();
$.ajax({
    type: 'GET',
    url: 'http://<your host/your domain>/api/my-comments/?token=' + getToken(),
    success: function (data) {
        let allPages = generatePages(data, 10)
        let pages = allPages.pages
        let pageCount = allPages.pageCount
        let commentsArea = $('#comments-area')
        let comments = ''
        console.log(data.comments)
        $.each(data.comments, function (index, value) {
            let dpt = value.publish_time.split('T')
            comments += '<div class="comment"><div class="clearfix">' + converter.makeHtml(value.content) + '</div><div class="fromBlog"><span class="float">' + value.float + '楼</span><a href="javascript:" class="blogTitle">' + value.blog_title + '</a><div class="publishTime"><span>回复于&nbsp;&nbsp;</span><span class="publishTime">' + dpt[0] + '&nbsp;' + dpt[1] + '</span></div></div></div>'
        })
        commentsArea.html(comments)

        pagesToggle(changePage, pages, pageCount)

        function changePage(page) { // 页码切换
            let pagesHTML = generatePagesHTML(page, pageCount)
            pages.html(pagesHTML)
            $.ajax({
                type: 'GET',
                url: 'http://<your host/your domain>/api/my-comments/?token=' + getToken() + '&page=' + page,
                success: function (data) {
                    let commentsArea = $('#comments-area')
                    let comments = ''
                    console.log(data.comments)
                    $.each(data.comments, function (index, value) {
                        let dpt = value.publish_time.split('T')
                        comments += '<div class="comment"><div class="clearfix">' + converter.makeHtml(value.content) + '</div><div class="fromBlog"><span class="float">' + value.float + '楼</span><a href="javascript:" class="blogTitle">' + value.blog_title + '</a><div class="publishTime"><span>回复于&nbsp;&nbsp;</span><span class="publishTime">' + dpt[0] + '&nbsp;' + dpt[1] + '</span></div></div></div>'
                    })
                    commentsArea.html(comments)
                }
            })
        }
    },
    error: function (jqXHR, textStatus, errorThrown) {
        let err = jqXHR.responseText
        let msg = JSON.parse(err)
        alert(msg.error || JSON.stringify(msg.message).replace('{', '').replace('}', ''))
    }
})

