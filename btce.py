#!/usr/bin/python
import sys
import httplib
import urllib
import json
import hashlib
import hmac

import config

def nonce_generator():
    fd = open("nonce_state", "r")
    nonce = int(fd.read())
    fd.close()
    while (True):
        nonce = nonce+1
        fd = open("nonce_state", "w")
        fd.write(str(nonce))
        fd.close()
        yield nonce

nonce = nonce_generator()

# TODO: support btc_eur, ltc_btc, ltc_usd, nmc_btc, eur_usd
correct_pairs = [['btc', 'usd'], 
                ['btc', 'rur'], 
                ['usd','rur'],
                ['ltc','usd'],
                ['btc','eur'],
                ['ltc','eur'],
                ['eur','usd'],
                ['trc','btc'],
                ['nmc','btc'], 
                ['ppc','btc'],]

class BTCEError(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return repr(self.msg)

def api_request(method, misc_params = {}):
	params = {
		"method": method,
		"nonce": nonce.next()
	}
	params.update(misc_params)
	params = urllib.urlencode(params)

	H = hmac.new(config.BTC_api_secret, digestmod=hashlib.sha512)
	H.update(params)
	sign = H.hexdigest()
	
	headers = {
		"Content-type": "application/x-www-form-urlencoded",
		"Key":config.BTC_api_key,
		"Sign":sign
	}
	
	conn = httplib.HTTPSConnection("btc-e.com")
	try:
		conn.request("POST", "/tapi", params, headers)
	except httplib.HTTPException:
		raise BTCEError("HTTP error: " + response.reason)
	
	try:
		reply = json.load(conn.getresponse())
		if reply['success'] == 1:
			return reply['return']
		else:
			raise BTCEError("API returned error: " + reply['error'])

		print "API returned error: " + reply['error']
		print response.status, response.reason
	except BTCEError:
		raise
	except:
		raise BTCEError("Unexpected error: " + str(sys.exc_info()[0]))

def pubapi_request(pair, type):
    if pair in correct_pairs:
        combo = pair[0]+'_'+pair[1]
    else:
        print 'can not find pair'
        return False
    url = "https://btc-e.com/api/2/" + combo + "/" + type
    try:
        f = urllib.urlopen(url)
        return json.load(f)
    except IOError:
        print f.code()


def ticker(pair):
    req =  pubapi_request(pair, "ticker")
    if req:
        return req['ticker']
    else:
        return None

def trades(pair):
    req =  pubapi_request(pair, "trades")
    if req:
        return req['trades']
    else:
        return None

def depth(pair):
    req =  pubapi_request(pair, "depth")
    if req:
        return req['depth']
    else:
        return None

def getinfo():
    return api_request('getInfo')

def order_list(filter = {}):
    return api_request('OrderList', filter)

def trans_history(filter = {}):
    return api_request('TransHistory', filter)

def trade_history(filter = {}):
    return api_request('TradeHistory', filter)

def prepare_trade(from_currency, to_currency, rate, amount):
    pair = [from_currency, to_currency]
    for p in correct_pairs:
        if pair == p:
            type = 'sell'
        elif pair == [p[1], p[0]]:
            type = 'buy'
            pair = p
            amount = float(amount) / float(rate)
    pair = '_'.join(pair)
    if not type:
        raise BTCEError("Unsupported currency pair: " + pair[0] + "_" + pair[1])
    return pair, type, rate, amount

def trade(pair, type, rate, amount):
#	print pair, type, amount, rate
    return api_request('Trade', { 'pair': pair, 'type': type, 'rate': rate, 'amount': amount })

def cancel_order(id):
    return api_request('CancelOrder', {'order_id': id})
