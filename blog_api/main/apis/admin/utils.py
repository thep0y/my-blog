import os

from main.settings import BASE_DIR


def verify_article(title: str = '', content: str = ''):
    # 如果标题和内容有敏感字，is_verified改为False，管理员审核后根据事实修改文章的is_blocked和is_deleted
    with open(os.path.join(BASE_DIR, 'utils/sensitive_words.txt')) as f:
        for word in f.readlines():
            if word.strip() in title or word.strip() in content:
                print(word)
                return False
    return True
