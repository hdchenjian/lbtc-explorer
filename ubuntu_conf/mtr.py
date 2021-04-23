#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import time
import traceback

host = 'https://data-cache.gj.com/data/kline/price.json?lang=zh_cn&t=26208406&token=7b93120460fc6d71c7ab18409118db90a1a12b5e163a42f29f5b71bcddcf50f0&appId=web&device=pc&version=1.0.0&timeZone=480'

def test_get():
    price_init = 0.00001
    first = True
    while True:
        try:
            ret = requests.get(host)
            ret = ret.json()['messages']
            d = ret['data']
            price = d['mtrusdt']['price']
            if abs(price - price_init) / price_init > 0.8:
                t = time.localtime()
                if (6 > t.tm_hour or t.tm_hour > 22) and abs(price - price_init) / price_init < 0.85: continue
                price_init = price
                print(ret['serverTime'], 'mtr', price)
                if first:
                    first = False
                else:
                    data = {'apikey': 'dc4768d332a1aa9f78e1c76b6fd64f6f',
                            'text': u'【中新智擎】您的验证码是' + str(price).replace('.', 'l') + u'。如非本人操作，请忽略本短信', 'mobile': '+8615919460519'}
                    try:
                        ret = requests.post('https://sms.yunpian.com/v2/sms/single_send.json', data=data)
                    except Exception as e:
                        traceback.print_exc()
            time.sleep(30)
        except Exception as e:
            traceback.print_exc()
        '''
    print(k, 'price', 'high', 'change', 'low')
    for k in ['bchusdt', 'bsvusdt', 'mtrusdt', 'ethusdt', 'btcusdt']:
        print(k, d[k]['vol'], d[k]['price'], d[k]['high'], d[k]['amount'], d[k]['lastClose'], d[k]['change'], d[k]['low'])
    '''

def test_post():
    ret = requests.post(host + "/navigation/pose/current")
    print(ret.content)


if __name__ == '__main__':
    #test_post()
    test_get()
