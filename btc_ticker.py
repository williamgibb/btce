import time

import btce

timestring = '%Y-%m-%dT%H:%M:%SZ'
wait_time = 15
field_count = 10
tickers = [['btc','usd'],['ltc','usd'], ['trc','btc'], ['nmc','btc'], ['ppc','btc']]
fields = ['server_time', 'high', 'low', 'buy', 'sell' ]
#tickers = [['btc','usd'], ['trc','btc']]

def portfolio_worth(ticker_data, info = None):
    if info is None:
        info = btce.getinfo()
    funds = info['funds']
    btc_usd = ticker_data[('btc','usd')]['sell']
    ltc_usd = ticker_data[('ltc','usd')]['sell']
    trc_btc = ticker_data[('trc','btc')]['sell']
    nmc_btc = ticker_data[('btc','usd')]['sell']
    ppc_btc = ticker_data[('ppc','btc')]['sell']
    total = funds['usd']
    total = total + funds['btc'] * btc_usd
    total = total + funds['ltc'] * ltc_usd
    total = total + funds['trc'] * trc_btc * btc_usd
    total = total + funds['nmc'] * nmc_btc * btc_usd
    total = total + funds['ppc'] * ppc_btc * btc_usd
    return total

def print_portfolio(ticker_data):
    info = btce.getinfo()
    funds = info['funds']
    btc_usd = ticker_data[('btc','usd')]['sell']
    ltc_usd = ticker_data[('ltc','usd')]['sell']
    trc_btc = ticker_data[('trc','btc')]['sell']
    nmc_btc = ticker_data[('btc','usd')]['sell']
    ppc_btc = ticker_data[('ppc','btc')]['sell']
    print 'USD: ' + str(funds['usd'])
    print 'BTC: ' + str(funds['btc']) + '\t\tIN USD: ' + str(funds['btc'] * btc_usd)
    print 'LTC: ' + str(funds['ltc']) + '\t\tIN USD: ' + str(funds['ltc'] * ltc_usd)
    print 'TRC: ' + str(funds['trc']) + '\tIN USD: ' + str(funds['trc'] * trc_btc * btc_usd)
    print 'NMC: ' + str(funds['nmc']) + '\t\tIN USD: ' + str(funds['nmc'] * nmc_btc * btc_usd)
    print 'PPC: ' + str(funds['ppc']) + '\t\tIN USD: ' + str(funds['ppc'] * ppc_btc * btc_usd)
    worth = portfolio_worth(ticker_data, info)
    print 'Portfolio networth: %s USD' % str(worth)
count = 0


while True:
    ticker_data = {}
    if count % field_count == 0:
        print fields
    for ticker in tickers:
        try:
            data = btce.ticker(ticker)
        except:
            print 'error with ticker [%s]' % str(ticker)
            continue
        if data:
            ticker_string = ''
            servertime = data['server_time']
            gmt = time.gmtime(servertime)
            gmt = time.strftime(timestring, gmt)
            ticker_string = gmt
            for field in fields:
                if field != 'server_time':
                    ticker_string = ticker_string + '\t' + str(data[field])
            print ticker
            print ticker_string
            ticker_data[tuple(ticker)] = data
    print_portfolio(ticker_data)
    print '======================================================================='
    count = count + 1
    time.sleep(wait_time)


