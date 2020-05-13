let token = getToken()

$.ajax({
    type: 'GET',
    url: 'http://<your host/your domain>/api/ganvas',
    data: {
        token: token
    },
    success: function (data) {
        console.log(data)
        let allPages = generatePages(data, 20)
        let pages = allPages.pages
        let pageCount = allPages.pageCount
        let blogList = $('.blogList')
        let html = ''
        $.each(data.data, function (index, value) {
            let temp = ''
            html += generateBlogTitles(temp, value)
        })
        blogList.html(html)

        function changePage(page) { // 页码切换
            let pagesHTML = generatePagesHTML(page, pageCount)
            pages.html(pagesHTML)
            $.ajax({
                type: 'GET',
                url: 'http://<your host/your domain>/api/ganvas?page=' + page,
                data: {
                    token: token
                },
                success: function (data) {
                    let html = ''
                    $.each(data.data, function (index, value) {
                        let temp = ''
                        html += generateBlogTitles(temp, value)
                    })
                    blogList.html(html)
                },
                error: function (jqXHR, textStatus, errorThrown) {
                    setCookie('token', '', -1)  // token失效的话清除cookie
                    let err = JSON.parse(jqXHR.responseText)
                    alert(err.error)
                }
            })
        }

        pagesToggle(changePage, pages, pageCount)
    }
})

function generateBlogTitles(html, value) {
    let pt = value.publish_time.split('T')
    html += "        <div class=\"blogOverview\">\n" +
        "            <div class=\"blog\"><a href=\"/type/" + value.type + "/\" class=\"type\" style='color: #007CD5'>" + types[value.type] + "</a></div>\n" +
        "            <div class=\"blog\"><a href=\"/audit/" + value.id + "/\" class=\"title\">" + value.title + "</a></div>\n" +
        "            <div class=\"blog\"><a href='javascript;' class=\"publishTime\" style='font-size: 14px;margin-top: 11px'>" + pt[0] + '&nbsp;' + pt[1] + "</a></div>\n" +
        "        </div>"
    return html
}