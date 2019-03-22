#!/usr/bin/env python
# encoding: utf-8

#curl --user luyao:123456  --data-binary '{"jsonrpc":"1.0","id":"curltest","method": "getinfo","params":[]}' -H 'content-type:text/plain;' http://127.0.0.1:8332/

import cPickle
'''
f = open('all_balance.txt', 'r+')
all_balance = cPickle.load(f)
f.close()
print all_balance
'''

'''
f = open('/home/luyao/git/blockparser/allBalances.txt', 'rU')
all_balance = {}
for line in f.readlines():
    line = line.strip('\n')
    try:
        all_balance[line[26:]] = float(line[0:26])
    except:
        print 'convert to float error:', line, '|'
f.close()
print all_balance
f = open('all_balance.txt', 'wb')
cPickle.dump(all_balance, f)
f.close
'''

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:9332" % ('luyao', 'r5ysVC3MdNl2S8ZBKoqLNoNSQoRQFAK9jFu1W0ePySo='))
try:
    print(rpc_connection.help())
    print('\n\n')
    #print(rpc_connection.getinfo())
    print(rpc_connection.getblockchaininfo())
    #print(rpc_connection.getnewaddress("account1"))
    print(rpc_connection.getaddressesbylabel("account1"))  # 1BcNXePEwhJHDrvmC6xBszrzDsrcJ6wope
    print(rpc_connection.getbalance())
    getbalance('16ftSEQ4ctQFDtVZiUBusQUjRrGhM3JYwe')
    #print(rpc_connection.setgenerate(True))
except Exception as e:
    print unicode(e)
#print(rpc_connection.getaccount('1ZJaSNGw37MPYejr9uWzx9ZLyhvFt9b2C'))
#print(rpc_connection.getaccountaddress("account1"))  # 1JVjemAg9FrNhesrJmEq1HVnEh7WxMtZHy
#print(rpc_connection.getaddressesbyaccount("account1")) #[u'1ZJaSNGw37MPYejr9uWzx9ZLyhvFt9b2C', u'1JVjemAg9FrNhesrJmEq1HVnEh7WxMtZHy']
#print(rpc_connection.getblockcount())
#print(rpc_connection.getblocknumber())
#print(rpc_connection.getgenerate())
#print(rpc_connection.gethashespersec())
#print(rpc_connection.getreceivedbyaccount('account1'))
#print(rpc_connection.getreceivedbyaddress('1ZJaSNGw37MPYejr9uWzx9ZLyhvFt9b2C'))
#print(rpc_connection.validateaddress('1ZJaSNGw37MPYejr9uWzx9ZLyhvFt9b2C'))
#print(rpc_connection.getwork())
#print(rpc_connection.getbalance('*'))
#print(rpc_connection.listtransactions("account1"))
#print(rpc_connection.listaccounts())
#print rpc_connection.listreceivedbyaddress(6)
#print rpc_connection.sendtoaddress("11yEmxiMso2RsFVfBcCa616npBvGgxiBX", 10)
