#!/usr/bin/env python
# coding: utf-8
#

from wxbot import *
import re
import sys
import urllib2
import json
import urllib
import hmac
import hashlib
import base64

reload(sys)
sys.setdefaultencoding('utf-8')

coins = ['btc','eth','ltc','doge','ybc','etc']


class MyWXBot(WXBot):

    def search_coin(self,coin):
        response = urllib2.urlopen("http://api.btctrade.com/api/ticker?coin=" + coin,None,5)
        print '------------------------------------'
        result = json.loads(response.read())
        # print result.keys()

        # return """╔═══════════
        #           ║ 比特币交易网 
        #           ╟───────────
        #           ║ 最新成交价格 %s￥ 
        #           ╚═══════════
        #           """ % result["last"]
        return """最新成交价格 %s￥
------------
比特币交易网""" % result["last"]


    def handle_coin(self,msg):
        isCoin = False
        for coin in coins:
            if re.search(coin, msg['content']['data'], re.IGNORECASE):
                isCoin = True
                self.send_msg_by_uid(self.search_coin(coin), msg['user']['id'])
        return isCoin

    def handle_fanfan_case(self,msg):
        if msg['msg_type_id'] == 4 and msg['user']['name'] == '范范':
        # if msg['msg_type_id'] == 4 and msg['user']['name'] == 'Judy':
            if not self.handle_coin(msg):
                self.send_msg_by_uid(u'范范好', msg['user']['id'])


    def handle_msg_all(self, msg):
        self.handle_fanfan_case(msg)
        # if msg['msg_type_id'] == 4 and msg['content']['type'] == 0:
        #     print  msg['user']['id']
        #     print msg
            # self.send_msg_by_uid(u'hi', msg['user']['id'])
            #self.send_img_msg_by_uid("img/1.png", msg['user']['id'])
            #self.send_file_msg_by_uid("img/1.png", msg['user']['id'])




'''
    def schedule(self):
        self.send_msg(u'张三', u'测试')
        time.sleep(1)
'''



def main():
    bot = MyWXBot()
    bot.DEBUG = True
    bot.conf['qr'] = 'png'
    bot.run()


if __name__ == '__main__':
    main()
