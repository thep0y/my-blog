console.log(types)
$.ajax({
    type: 'GET',
    url: 'http://<your host/your domain>/api/allarts',
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
                url: 'http://<your host/your domain>/api/allarts?page=' + page,
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

$('#publishNewBlog').click(function () {
    window.open('/publish/')
})