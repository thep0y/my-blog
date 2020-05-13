let typeID = window.location.href.split('/')[4]
let typeName = types[typeID]

$('#publishNewBlog').remove()
$('title').text('「' + typeName + '」下的公开Blog')
$('.pages.top').before('<span id="typeBlogTile">「' + typeName + '」下的公开Blog</span>')

$.ajax({
    type: 'GET',
    url: 'http://<your host/your domain>/api/blktype/' + typeID + '/',
    success: function (data) {
        if (data.count) {
            let allPages = generatePages(data, 20)
            let pages = allPages.pages
            let pageCount = allPages.pageCount
            let blogList = fillBlogList(data)

            function changePage(page) { // 页码切换
                let pagesHTML = generatePagesHTML(page, pageCount)
                pages.html(pagesHTML)
                $.ajax({
                    type: 'GET',
                    url: 'http://<your host/your domain>/api/blktype/' + typeID + '/' + '?page=' + page,
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
        } else {
            let noBlog = '<span id="noBlog">此类型下暂无文章</span>'
            $('.content').append(noBlog)
        }
    }
})