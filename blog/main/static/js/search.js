let keyword = decodeURI(getQueryVariable('keyword'))

$.ajax({
    type: 'POST',
    url: 'http://<your host/your domain>/api/search/',
    data: {
        word: keyword
    },
    success: function (data) {
        let allPages = generatePages(data, 20)
        let pages = allPages.pages
        let pageCount = allPages.pageCount
        console.log(pages, pageCount)
        $('#searchCount').text('（找到 “ ' + keyword + ' ” 相关内容 ' + data.count + ' 个）')
        let resultList = fillResultList(data)

        function changePage(page) { // 页码切换
            let pagesHTML = generatePagesHTML(page, pageCount)
            pages.html(pagesHTML)
            $.ajax({
                type: 'POST',
                url: 'http://<your host/your domain>/api/search/',
                data: {
                    page: page,
                    word: keyword
                },
                success: function (data) {
                    fillResultList(data)
                }
            })
        }

        pagesToggle(changePage, pages, pageCount)
    }
})

function generateSearchResults(html, v) {
    html += '<li class="result" id="' + v.id + '">' +
        '<a href="/blog/' + v.id + '/" target="_blank" class="blog-title">' + v.title + '</a>' +
        '<p class="blog-content">' + v.content + '<p>' +
        '<span class="publish-time">' + v.publish_time + '</span> - <span>' +
        '<a href="/user/' + v.user_id + '/" target="_blank">' + v.username + '</a>' +
        '</span> - <span><a href="/type/' + v.type + '/" target="_blank" class="xi1">『' + types[v.type] + '』</a></span>' +
        '</p></li>'
    return html
}

function fillResultList(data) {
    let resultList = $('#result-list ul')
    let html = ''
    $.each(data.data, function (index, value) {
        let temp = ''
        html += generateSearchResults(temp, value)
    })
    resultList.html(html)
    return resultList
}