$('#publishNewBlog').remove()
$('title').text('我的所有Blog')
$('.pages.top').before('<span id="userBlogTile">我的所有Blog</span>')

$.ajax({
    type: 'GET',
    url: 'http://<your host/your domain>/api/blogs/?token=' + getToken(),
    success: function (data) {
        let allPages = generatePages(data, 20)
        let pages = allPages.pages
        let pageCount = allPages.pageCount
        let blogList = fillBlogList(data)

        function changePage(page) { // 页码切换
            let pagesHTML = generatePagesHTML(page, pageCount)
            pages.html(pagesHTML)
            $.ajax({
                type: 'GET',
                url: 'http://<your host/your domain>/api/blogs/?token=' + getToken() + '&page=' + page,
                success: function (data) {
                    let html = ''
                    $.each(data.data, function (index, value) {
                        let temp = ''
                        html += generateBlogTitles(temp, value)
                    })
                    blogList.html(html)
                }
            })
        }

        pagesToggle(changePage, pages, pageCount)
    }
})