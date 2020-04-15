from bs4 import BeautifulSoup
import requests
import datetime
import sys
import Config


class MovieModel:
    def __init__(self, title, url):
        self.Title = title
        self.Url = url


target_date = datetime.datetime.now() + datetime.timedelta(days=-1)
target_date = target_date.strftime("%Y-%#m-%#d")  # windows 使用#字號去除零，Linux使用-號 去零


# 取得伊莉論壇昨天發文的電影資訊 (標題 + 網址)
def get_the_newest_movie_post():
    eyny_domain_url = 'http://www.eyny.com/'
    eyny_movie_url = 'http://www.eyny.com/forum.php?mod=forumdisplay&fid=205&filter=author&orderby=dateline&page='
    page_code = {1: '3DN3CFFH', 2: '3W0P8JX0', 3: '42RLY2A3'}  # 每頁的page參數是使用加密的方式
    result = []

    page = 1  # 第幾頁
    keep_next_page = True  # 是否翻頁
    print('開始蒐集電影資訊...')
    while page < len(page_code) + 1 and keep_next_page:
        print('開始第 %s 頁' % page)
        movie_url = (eyny_movie_url + page_code[page])

        r = requests.get(movie_url)
        soup = BeautifulSoup(r.text, "html5lib")
        thread_list = soup.find_all(summary='forum_205')[0].find_all('tbody')

        for i in thread_list:
            item = i.find('th', class_='new')
            if item is not None:

                date_item = i.find('td', class_='by')
                if target_date == date_item.span.text:
                    # print(item.prettify())
                    # print("==============================")
                    # print(date_item.span.text)
                    # print(item.em.text)
                    # print(item.find_all('a')[1].text)
                    # print(eyny_domain_url + str(item.find_all('a')[1]['href'])[: str(item.find_all('a')[1][
                    # 'href']).find('&extra# ')])
                    post_url = str(item.find_all('a')[1]['href'])
                    result.append(MovieModel(item.em.text + item.find_all('a')[1].text,
                                             eyny_domain_url + post_url[: post_url.find('&extra')]))
                elif target_date > date_item.span.text:
                    keep_next_page = False

        page += 1
        if keep_next_page:
            print('翻頁繼續查找...')

    print('收集完成!')
    return result


notify_msg = ('\n%s 最新電影資訊\n\n' % target_date)
for post in get_the_newest_movie_post():
    try:
        print(post.Title.encode('ascii', 'ignore'))
        print(post.Url.encode('ascii', 'ignore'))
        print('======')
        notify_msg += post.Title + '\n'
        notify_msg += post.Url + '\n\n'
    except:
        print("Unexpected error:", sys.exc_info()[0])
        input("Press enter to exit ;)")


# 若有節目，則發送lINE訊息通知
if notify_msg:
    headers = {"Authorization": "Bearer " + Config.LINE_NOTIFY_TOKEN}
    params = {"message": notify_msg}
    requests.post(Config.LINE_NOTIFY_URL, headers=headers, params=params)

