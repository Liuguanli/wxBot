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
import ssl

reload(sys)
sys.setdefaultencoding('utf-8')

coins = ['btc','rep','dash','exc','nmc','shell','xcp','xtc','ltc','etp','bts','bat','eth','ftc','nxt','tips','xmr','xem','zec','xrp','qtum','btrx','cnc','snt','btm','ico','eos','doge','etc','ifc','ppc','tix','xpm','ans','dgd','zmc','1st','gxs','gnt','obs','omg']


class MyWXBot(WXBot):

    def __init__(self):
        WXBot.__init__(self)

        self.tuling_key = "8c7a289ea3054c088b069b899a38c184"
        self.robot_switch = True
            

    def get_access_token(self):
        try:
            host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=hswHkMv8NbAxwPUFwIBLmO5a&client_secret=XqLpUb4zS70ESojBFUEPtiHGyGgGCIzm'
            request = urllib2.Request(host)
            request.add_header('Content-Type', 'application/json; charset=UTF-8')
            response = urllib2.urlopen(request)
            access_token = json.loads(response.read())['access_token']
            print 'access_token', access_token
            return access_token
        except Exception as e:
            print e  

    def baidu_robot_api(self,msg):
        access_token = self.get_access_token()
        url = 'https://aip.baidubce.com/rpc/2.0/solution/v1/unit_utterance?access_token=' + access_token
        post_data = "{\"scene_id\":7129,\"query\":\"%s \",\"session_id\":\" \"}" % msg
        request = urllib2.Request(url, post_data)
        request.add_header('Content-Type', 'application/json')
        response = urllib2.urlopen(request)
        result = json.loads(response.read())
        print result
        self.baidu_robot_sesson_id = result['result']['session_id']
        return result['result']['action_list'][0]['say']

    def tuling_auto_reply(self, uid, msg):
        try:
            if self.tuling_key:
                url = "http://openapi.tuling123.com/openapi/api/v2"
                user_id = uid.replace('@', '')[:30]
                body = {'key': self.tuling_key, 'info': msg.encode('utf8'), 'userid': user_id}
                r = requests.post(url, data=body)
                respond = json.loads(r.text)
                result = ''
                print respond
                if respond['code'] == 100000:
                    result = respond['text'].replace('<br>', '  ')
                    result = result.replace(u'\xa0', u' ')
                elif respond['code'] == 200000:
                    result = respond['url']
                elif respond['code'] == 302000:
                    for k in respond['list']:
                        result = result + u"【" + k['source'] + u"】 " +\
                            k['article'] + "\t" + k['detailurl'] + "\n"
                else:
                    result = respond['text'].replace('<br>', '  ')
                    result = result.replace(u'\xa0', u' ')

                print '    ROBOT:', result
                return result
            else:
                return u"知道啦"
        except Exception as e:
            print e
        
    def search_coin_from_b8wang(self,coin):
        try:
            response = urllib2.urlopen("https://www.b8wang.com/api/ticker?symbol=%scny" % coin)
            result = json.loads(response.read())
            print result
            price = result['ticker']['last']
            if price == 0:
                return -1
            else:
                return price
        except Exception as e:
            return -1

    def search_coin_from_yunbi(self,coin):
        # url = "https://yunbi.com/api/v2/tickers/%scny.json?" % coin
        try:
            resp = urllib2.urlopen("https://yunbi.com/api/v2/tickers/%scny.json?" % coin)
            data = resp.readlines()
            if len(data):
                result = json.loads(data[0])
                return result['ticker']['last']
        except Exception as e:
            print "search_coin_from_yunbi error"
            return -1

    def search_coin_from_btjy(self,coin):
        try:
            resp = urllib2.urlopen("https://szzc.com/api/public/ticker/%sCNY" % coin.upper())
            data = resp.readlines()
            if len(data):
                result = json.loads(data[0])
                return long(result['result']['last'])/1e8
        except Exception as e:
            print "search_coin_from_btjy error"
            return -1

    def search_coin_from_szzc(self,coin):
        try:
            resp = urllib2.urlopen("https://szzc.com/api/public/ticker/%sCNY" % coin.upper())
            data = resp.readlines()
            if len(data):
                result = json.loads(data[0])
                return long(result['result']['last'])/1e8
        except Exception as e:
            print "search_coin_from_szzc error"
            return -1
        
    def search_coin_from_bter(sefl,coin):
        url = "http://data.bter.com/api2/1/ticker/%s_cny" % coin

        hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'en-US,en;q=0.8',
           'Connection': 'keep-alive'}

        req = urllib2.Request(url, headers=hdr)
        try:
            data = urllib2.urlopen(req).read()
            if len(data):
                result = json.loads(data)
                return result['last']
        except Exception as e:
            print "search_coin_from_bter error"
            return -1
    
    def search_coin(self,coin):
        print "search_coin"
        # print result.keys()

        # return """╔═══════════
        #           ║ 比特币交易网 
        #           ╟───────────
        #           ║ 最新成交价格 %s￥ 
        #           ╚═══════════
        #           """ % result["last"]
        btjy = self.search_coin_from_btjy(coin)
        yunbi = self.search_coin_from_yunbi(coin)
        szzc = self.search_coin_from_szzc(coin)
        bter = self.search_coin_from_bter(coin)
        b8wang = self.search_coin_from_b8wang(coin)
        hasResult = False
        result = "--%s--\n" % coin
        if btjy != -1:
            hasResult = True
            result += "------------\n"
            result += "比特币交易网 ￥%s" % (btjy) +"\n"
        if yunbi != -1:
            hasResult = True
            result += "------------\n"
            result += "云币网 ￥%s" % (yunbi) +"\n"
        if szzc != -1:
            hasResult = True
            result += "------------\n"
            result += "海风藤 ￥%s" % (szzc) +"\n"
        if bter != -1:
            hasResult = True
            result += "------------\n"
            result += "比特儿 ￥%s" % (bter) +"\n"
        if b8wang != -1:
            hasResult = True
            result += "------------\n"
            result += "币八 ￥%s" % (b8wang)
        if hasResult:
            return result
        else:
            return "系统开小差了~"
#         return """ --%s--
# ------------
# 比特币交易网 ￥%s
# ------------
# 云币网 ￥%s
# ------------
# 海风藤 ￥%s
# ------------
# 比特儿 ￥%s""" % (coin,self.search_coin_from_btjy(coin), self.search_coin_from_yunbi(coin),self.search_coin_from_szzc(coin),self.search_coin_from_bter(coin))

    def is_at_me(self,msg):
        if 'detail' in msg['content']:
                my_names = self.get_group_member_name(msg['user']['id'], self.my_account['UserName'])
                if my_names is None:
                    my_names = {}
                if 'NickName' in self.my_account and self.my_account['NickName']:
                    my_names['nickname2'] = self.my_account['NickName']
                if 'RemarkName' in self.my_account and self.my_account['RemarkName']:
                    my_names['remark_name2'] = self.my_account['RemarkName']

                is_at_me = False
                for detail in msg['content']['detail']:
                    if detail['type'] == 'at':
                        for k in my_names:
                            if my_names[k] and my_names[k] == detail['value']:
                                is_at_me = True
                                break
                return is_at_me

    def handle_at_me(self,msg):
        print "图灵机器人的结果 ", self.tuling_auto_reply(msg['user']['id'], msg['content']['desc'])
        return self.baidu_robot_api(msg)

    def handle_coin(self,msg):
        isCoin = False
        for coin in coins:
            if re.search(coin, msg['content']['data'], re.IGNORECASE):
                isCoin = True
                self.send_msg_by_uid(self.search_coin(coin), msg['user']['id'])
        return isCoin

    def handle_fanfan_case(self,msg):
        if msg['user']['name'] == '范范':
            if not self.handle_coin(msg):
                self.send_msg_by_uid(u'范范好', msg['user']['id'])


    def handle_group_case(self,msg):
        print "handle_group_case", msg
        if msg['content']['user']['name'] == '范范':# or msg['content']['user']['name'] == '刘冠利':
            if self.is_at_me(msg):
                self.send_msg_by_uid(u"范范好 "+u"\U0001F339" + self.handle_at_me(msg), msg['user']['id'])
            else:
                self.send_msg_by_uid(u"范范好 "+u"\U0001F339", msg['user']['id'])
        else:
            if self.is_at_me(msg):
                self.send_msg_by_uid(unicode(self.handle_at_me(msg)), msg['user']['id'])
        self.handle_coin(msg)

    def handle_msg_all(self, msg):
        if msg['msg_type_id'] == 4:
            print msg
            self.handle_fanfan_case(msg)    
        elif msg['msg_type_id'] == 3:
            if msg['content']['type'] == 0:
                self.handle_group_case(msg)
            else:
                print msg
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
