from bs4 import BeautifulSoup
import requests
import json
from datetime import datetime

NINTENDO = "https://www.nintendo.co.kr/lib/software_xml.php"

HEADER = {
    'referer': 'https://www.nintendo.co.kr/software/software_all.php',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36'
}

data = {
    'gubun': 'allsoftware',
    'page': 30,
    'searchWord': '',
    'sort':'',
    'lang[]': ['kor']
}

game_json = {}

res = requests.post(NINTENDO, data=data, headers=HEADER)
res.encoding = 'utf-8'
pageSoup = BeautifulSoup(res.json()['software'], 'html.parser')

divList = pageSoup.select('div')
gameList = [divList[i*2:(i+1)*2] for i in range((len(divList)+2-1)//2)] # 2개씩 분할하기

for idx in range(len(gameList)):
    game_title = gameList[idx][0].select_one('p').text
    print('{}'.format(game_title), end='')
    game_detail_url = gameList[idx][0].select_one('.thumb')['href']
    try:
        game_device = gameList[idx][0].select_one('.cate').text
    except:
        continue
    game_methods = [x.text for x in gameList[idx][0].select('.ico_rel')]
    releaseDate = gameList[idx][0].select_one('.releaseInfo').text

    try:
        language = gameList[idx][0].select_one('.ico_lang').text
    except:
        language = ''

    thumbnail_url = "https://www.nintendo.co.kr" + gameList[idx][0].select_one('img')['src']

    if not 'store.nintendo.co.kr' in game_detail_url:
        continue

    req = requests.get(game_detail_url, headers=HEADER)
    pageDetailSoup = BeautifulSoup(req.text, 'html.parser')

    try:
        game_pusblisher = pageDetailSoup.select_one('.product-page-pusblisher-attr').text
    except:
        game_pusblisher = ''

    try:
        game_description = [x.text for x in pageDetailSoup.select_one('.description > .value').select('p')]
    except:
        game_description = ''

    product_attribute_title = pageDetailSoup.select('.product-attribute-title')
    product_attribute_val = pageDetailSoup.select('.product-attribute-val')

    product_attribute = []
    for title, val in zip(product_attribute_title, product_attribute_val):
        product_attribute.append([title.text, val.text])

    for script in pageDetailSoup.find_all('script', type='text/x-magento-init'):
        try:
            gallery = json.loads(script.text)['[data-gallery-role=gallery-placeholder]']['mage/gallery/gallery']
            game_image_thumb = [data['thumb'] for data in gallery['data']]
            game_image_raw = [data['img'] for data in gallery['data']]
            game_image_full = [data['full'] for data in gallery['data']]
        except:
            continue
    game_json[game_title] = {
        'game_detail_url': game_detail_url,
        'game_device': game_device,
        'game_methods': game_methods,
        'releaseDate': releaseDate,
        'language': language,
        'thumbnail_url': thumbnail_url,
        'game_pusblisher': game_pusblisher,
        'game_description': game_description,
        'product_attribute': product_attribute,
        'game_image_thumb': game_image_thumb,
        'game_image_raw': game_image_raw,
        'game_image_full': game_image_full
    }

    print(' [DONE]')

with open('data/nintendo/{}.json'.format(datetime.now().strftime("%Y%m%d")), 'w', encoding='utf-8') as f:
    json.dump(game_json, f, ensure_ascii=False)