$('#publishNewBlog').remove()

let userID = window.location.href.split('/')[4]

$.ajax({
    type: 'GET',
    url: 'http://<your host/your domain>/api/getuser/' + userID + '/',
    data: {
        token: getToken()
    },
    success: function (data) {
        $('title').text(data.username + '的公开Blog')
        $('.pages.top').before('<span id="userBlogTile">' + data.username + '的公开Blog</span>')
    }
})

$.ajax({
    type: 'GET',
    url: 'http://<your host/your domain>/api/user/' + userID + '/',
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
                url: 'http://<your host/your domain>/api/user/' + window.location.href.split('/')[4] + '/' + '?page=' + page,
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