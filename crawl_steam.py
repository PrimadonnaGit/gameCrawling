from bs4 import BeautifulSoup
from datetime import datetime
import requests
import json
import re

STEAM = "https://store.steampowered.com/search/results/"

HEADER = {
    'referer': 'https://store.steampowered.com/search/?specials=1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36',
}

COOKIES = {
    'Steam_Language' : 'koreana',
    'lastagecheckage' : '15-2-1992'
}

HEADER_DETAIL = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36',
}

COOKIES_DETAIL = {
    'Steam_Language' : 'koreana',
    'lastagecheckage' : '15-2-1992',
    'birthtime' : '692722801',
    'wants_mature_content':'1'
}

count = 100
total = 1000
for i in range(int(total/count)):
    start = count * i

    data = {
        'query': '',
        'start': start,
        'count': count, # 25 - 100
        'dynamic_data': '',
        'sort_by':'_ASC',
        'snr': '1_7_7_2300_7',
        'specials':1,
        'infinite':1,
    }

    game_json = {}

    res = requests.get(STEAM, params=data, headers=HEADER, cookies=COOKIES)
    res.encoding = 'utf-8'

    pageSoup = BeautifulSoup(res.json()['results_html'], 'html.parser')

    gameList = pageSoup.select('a')

    for game in gameList:
        title = game.select_one('div.col.search_name > span').text
        print(title, end='')
        detail_url = game['href']
        thumbnail = re.sub('\s\dx', '',game.select_one('div.col.search_capsule > img')['srcset']).split(', ')

        released_date = '' if game.select_one('div.col.search_released.responsive_secondrow') is None else game.select_one('div.col.search_released.responsive_secondrow').text
        review = '' if game.select_one('div.col.search_reviewscore.responsive_secondrow > span') is None else game.select_one('div.col.search_reviewscore.responsive_secondrow > span')['data-tooltip-html'].split('<br>')
        discount = 1 if game.select_one('div.col.search_discount.responsive_secondrow > span') is None else int(game.select_one('div.col.search_discount.responsive_secondrow > span').text.replace('-', '').replace('%', '')) / 100
        try:
            price = (int(re.findall('[\\\s\d+,\d+]+',game.select_one('div.col.search_price.discounted.responsive_secondrow').text.replace('\n', ''))[0].replace(',', '')), int(re.findall('[\\\s\d+,\d+]+', game.select_one('div.col.search_price.discounted.responsive_secondrow').text.replace('\n', ''))[1].replace(',', '')))
        except:
            continue

        detail_res = requests.get(detail_url, headers=HEADER_DETAIL, cookies=COOKIES_DETAIL)
        detail_res.encoding = 'utf-8'

        detail_pageSoup = BeautifulSoup(detail_res.text, 'html.parser')

        game_tag = '' if detail_pageSoup.select_one('div.blockbg > a:nth-child(2)') is None else detail_pageSoup.select_one('div.blockbg > a:nth-child(2)').text
        app_tags = [] if detail_pageSoup.select('.popular_tags > .app_tag') is None else [x.text.replace('\n', '').replace('\r', '').replace('\t','') for x in detail_pageSoup.select('.popular_tags > .app_tag')][:-1]
        #details_block = [] if detail_pageSoup.select('.details_block > b') is None else [x.text.replace(':', '') for x in detail_pageSoup.select('.details_block > b')][1:-1]
        #details_block_content = [] if detail_pageSoup.select('.details_block > a') is None else [x.text for x in detail_pageSoup.select('.details_block > a')]

        try:
            video = detail_pageSoup.select('div.highlight_player_item.highlight_movie')
            thumbnail_video_hd = [] if video[0]['data-mp4-hd-source'] is None else [x['data-mp4-hd-source'] for x in video]
            thumbnail_video_mp4 = [] if video[0]['data-mp4-source'] is None else [x['data-mp4-source'] for x in video]
            thumbnail_video_poster = [] if video[0]['data-poster'] is None else [x['data-poster'] for x in video]
            thumbnail_video_webm_hd = [] if video[0]['data-webm-hd-source'] is None else [x['data-webm-hd-source'] for x in video]
            thumbnail_video_webm_sd = [] if video[0]['data-webm-source'] is None else [x['data-webm-source'] for x in video]

            thumbnail_video = {
                'hd': thumbnail_video_hd,
                'mp4': thumbnail_video_mp4,
                'poster': thumbnail_video_poster,
                'webm_hd': thumbnail_video_webm_hd,
                'webm_sd': thumbnail_video_webm_sd
            }
        except:
            thumbnail_video = {}
            pass

        thumbnail_screenshot = [x['href'] for x in detail_pageSoup.select('div.highlight_player_item.highlight_screenshot > div.screenshot_holder > a')]

        print(' [DONE]')

        game_json[title] = {
            'detail_url' : detail_url,
            'thumbnail' : thumbnail,
            'released_date' : released_date,
            'review' : review,
            'discount' : discount,
            'price' : price,
            'game_tag' : game_tag,
            'app_tags' : app_tags,
            'thumbnail_video': thumbnail_video,
            'thumbnail_screenshot': thumbnail_screenshot
        }

    with open('data/steam/{}_{}.json'.format(datetime.now().strftime("%Y%m%d"), i+1), 'w', encoding='utf-8') as f:
        json.dump(game_json, f, ensure_ascii=False)


