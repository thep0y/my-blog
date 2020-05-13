$('#publishNewBlog').remove()
$('title').text('我收藏的Blog')
$('.pages.top').before('<span id="userBlogTile">我收藏的Blog</span>')

$('.newCommentTimeBtn').text('是否取消收藏')

$.ajax({
    type: 'GET',
    url: 'http://<your host/your domain>/api/myfav/?token=' + getToken(),
    success: function (data) {
        let allPages = generatePages(data, 20)
        let pages = allPages.pages
        let pageCount = allPages.pageCount
        let blogList = fillBlogList(data)
        let newCommentTime = $('.blog .newCommentTime')
        let b = newCommentTime.parent()
        newCommentTime.remove()
        b.html('<button class="delete-favorite">取消收藏</button>')

        function changePage(page) { // 页码切换
            let pagesHTML = generatePagesHTML(page, pageCount)
            pages.html(pagesHTML)
            $.ajax({
                type: 'GET',
                url: 'http://<your host/your domain>/api/myfav/?token=' + getToken() + '&page=' + page,
                success: function (data) {
                    let html = ''
                    $.each(data.data, function (index, value) {
                        let temp = ''
                        html += generateBlogTitles(temp, value)
                    })
                    blogList.html(html)
                    let newCommentTime = $('.blog .newCommentTime')
                    let b = newCommentTime.parent()
                    newCommentTime.remove()
                    b.html('<button class="delete-favorite">取消收藏</button>')
                }
            })
        }

        pagesToggle(changePage, pages, pageCount)

    }
})

// 监听取消收藏按钮
$('.blogList').on('click', '.delete-favorite', function (event) {
    let p = $(this).parent().parent()
    let blogID = p.find('.title').attr('href').split('/')[2]
    $.ajax({
        type: 'DELETE',
        url: 'http://<your host/your domain>/api/favorite/',
        data: {
            token: getToken(),
            blog_id: blogID,
        },
        success: function (data) {
            p.remove()
        },
        error: function (jqXHR, textStatus, errorThrown) {
            let err = jqXHR.responseText
            let msg = JSON.parse(err)
            alert(msg.error || JSON.stringify(msg.message).replace('{', '').replace('}', ''))
        }
    })
})