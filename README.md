# 部分开发文档

# Allarticlesresource

## GET(获取全部全部已验证、未封禁且未删除文章的标题)

#### url
- /allarts

#### doc
```
        默认按时间排序。
        已注销的用户用户名统一显示为已注销。
        已封禁的用户文章被过滤(管理员在封禁用户时，文章就已经blocked)。
```


#### args
|参数|是否必需|数据类型|默认值|描述|
|---|---|---|---|---|
|page|否|整型|1|要查询的页码数|

#### returns
- #### json
```json
{
      "msg": "Got all articles successful.",
      "count": 42,
      "data": [
        {
          "id": 89,
          "type": "44",
          "title": "许多年前用过，不知道现在微机课还教不教打字。最喜欢的还是后面那个打字游戏。打地鼠",
          "user_id": 19,
          "username": "tom",
          "publish_time": "2020-05-05T23:01:18",
          "url": "http://127.0.0.1:5000/blog/89",
          "comments": 0,
          "latest_comment": null
        },
        {
          "id": 100,
          "type": "44",
          "title": "许多年前用过，不知道现在微机课还教不教打字。最喜欢的还是后面那个打字游戏。打地鼠",
          "user_id": 19,
          "username": "tom",
          "publish_time": "2020-05-05T23:01:18",
          "url": "http://127.0.0.1:5000/blog/100",
          "comments": 0,
          "latest_comment": null
        },
        {
          "id": 10,
          "type": "44",
          "title": "测试2",
          "user_id": 19,
          "username": "tom",
          "publish_time": "2020-05-05T08:58:27",
          "url": "http://127.0.0.1:5000/blog/10",
          "comments": 3,
          "latest_comment": {
            "username": "jack",
            "user_id": 16,
            "publish_time": "2020-05-05 10:12:31"
          }
        }]
}
```


# Blogtypemanage

## GET(获取全部文章类型)

#### url
- /types

#### doc
```
        无需权限和认证，任何人都可以查询文章类型
```


## GET(获取全部文章类型)

#### url
- /types/

#### doc
```
        无需权限和认证，任何人都可以查询文章类型
```



# Commentsresource

## GET(获取当前文章下全部已验证、未删除且未封禁的评论)

#### url
- /comments

#### doc
```
        按时间排序。
```


#### args
|参数|是否必需|数据类型|默认值|描述|
|---|---|---|---|---|
|blogID|是|整型|无|要查询的blogID|
|page|否|整型|1|要查询的页码数|
|pageSize|否|整型|10|每页的评论数量|
#### returns
```json
{
  "msg": "ok",
  "comments": [
    {
      "id": 1,
      "content": "11111",
      "user_id": 16,
      "reply_id": 0,
      "blog_id": 10,
      "publish_time": "2020-05-05T10:12:31",
      "update_time": null,
      "author": "jack",
      "float": 1
    },
    {
      "id": 28,
      "content": "11111",
      "user_id": 16,
      "reply_id": 0,
      "blog_id": 10,
      "publish_time": "2020-05-05T10:12:31",
      "update_time": null,
      "author": "jack",
      "float": 2
    },
    {
      "id": 55,
      "content": "11111",
      "user_id": 16,
      "reply_id": 0,
      "blog_id": 10,
      "publish_time": "2020-05-05T10:12:31",
      "update_time": null,
      "author": "jack",
      "float": 3
    }
  ],
  "count": 3
}
```

## POST(增加评论)

#### url
- /comments

#### doc
```
        只有已登录的用户才能增加评论。
```


#### args
|参数|是否必需|数据类型|默认值|描述|
|---|---|---|---|---|
|blogID|是|整型|无|要评论的blogID|
|replyID|否|整型|无|要回复的评论ID|
|content|是|字符串|无|评论内容|
#### returns

```json
{
  "id": 55,
  "content": "11111",
  "user_id": 16,
  "reply_id": 0,
  "blog_id": 10,
  "publish_time": "2020-05-05T10:12:31",
  "update_time": null,
  "author": "jack",
  "float": 3
}
```



# Typeblogsresource

## GET(获取某类型下全部文章的标题)

#### url
- /blktype/id

#### doc
```
        通过类型筛选blog
```

#### args

| 参数 | 是否必需 | 数据类型 | 默认值 | 描述           |
| ---- | -------- | -------- | ------ | -------------- |
| id   | 是       | 整型     | 无     | 要查询的类型ID |

#### returns

```json
{
  "msg": "ok",
  "count": 42,
  "data": [
    {
      "id": 89,
      "type": "44",
      "title": "许多年前用过，不知道现在微机课还教不教打字。最喜欢的还是后面那个打字游戏。打地鼠",
      "user_id": 19,
      "username": "tom",
      "publish_time": "2020-05-05T23:01:18",
      "url": "http://127.0.0.1:5000/blog/89",
      "comments": 0,
      "latest_comment": null
    },
    {
      "id": 100,
      "type": "44",
      "title": "许多年前用过，不知道现在微机课还教不教打字。最喜欢的还是后面那个打字游戏。打地鼠",
      "user_id": 19,
      "username": "tom",
      "publish_time": "2020-05-05T23:01:18",
      "url": "http://127.0.0.1:5000/blog/100",
      "comments": 0,
      "latest_comment": null
    },
    {
      "id": 111,
      "type": "44",
      "title": "许多年前用过，不知道现在微机课还教不教打字。最喜欢的还是后面那个打字游戏。打地鼠",
      "user_id": 19,
      "username": "tom",
      "publish_time": "2020-05-05T23:01:18",
      "url": "http://127.0.0.1:5000/blog/111",
      "comments": 0,
      "latest_comment": null
    }]
}
```






