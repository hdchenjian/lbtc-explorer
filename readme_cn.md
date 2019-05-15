#### 开发工具

#### python + flask + mysql + mongo

#### 部署工具

#### nginx + supervisor + gevent + crontab

#### [Unspent transaction output (UTXO)](https://en.wikipedia.org/wiki/Unspent_transaction_output)

下面为一个交易信息，可调用 gettransactionnew RPC 接口获取，详情见[这里](https://lbtc.me/lbtc/rpc?run=1&cmd=gettransactionnew&param1=163d33738e9f2fc4b3cdb860fe8fe3d16fcae6a9d3a8c805e8c8b6607fe14c53):

```
{'blockhash': '59eda24d67bb61ead55bef8b3a9015437ba818d33208f3d6e5cd8273813071d3',
 'blocktime': 1545203200,
 'confirmations': 4167248,
 'hash': '163d33738e9f2fc4b3cdb860fe8fe3d16fcae6a9d3a8c805e8c8b6607fe14c53',
 'height': 1911040,
 'locktime': 1911037,
 'size': 779,
 'time': 1545203200,
 'txid': '163d33738e9f2fc4b3cdb860fe8fe3d16fcae6a9d3a8c805e8c8b6607fe14c53',
 'version': 65282,
 'vin': [{'scriptSig': {'asm': '30440220233560f5484da6ad56f723f41d54da6e',
                        'hex': '4730440220233560f5484da6ad508f11ed2681b9'},
          'sequence': 4294967294,
          'txid': 'e014da9430f0a721695c69cf71f7eb3c333a82f16e627021116faa49346485fa',
          'vout': 0}],
 'vout': [{'n': 0,
           'scriptPubKey': {'asm': 'OP_RETURN '
                                   '00000000c11b145c0a6d4a0b4ab',
                            'hex': '6a4d3d0200000000c11b145c0ad8048b',
                            'type': 'nulldata'},
           'value': Decimal('0E-8')},
          {'n': 1,
           'scriptPubKey': {'addresses': ['1LAMDkarMYfZXcRQX5ZKhSafQBJqcRf91v'],
                            'asm': 'OP_DUP OP_HASH160 '
                                   'd22f03218d0ea3860a7aabebc49ac10c9ce35c36 '
                                   'OP_EQUALVERIFY OP_CHECKSIG',
                            'hex': '76a914d22f03218d0ea3860a7aabebc49ac10c9ce35c3688ac',
                            'reqSigs': 1,
                            'type': 'pubkeyhash'},
           'value': Decimal('0.18624737')}],
 'vsize': 779}
```

```
解析区块数据需拿到每个交易的输入输出，即上面的 vin 和 vout 字段
vin: 是一个json array，每一个json object 是该交易引用的 utxo，
     可以是别人转账给自己的输出或者 coinbase， 在上面这个交易中，
     vin引用了 e014da9430f0a721695c69cf71f7eb3c333a82f16e627021116faa49346485fa(txid 字段) 交易
     的第一个输出('vout': 0)

vout: 也是一个json array，每一个json object 是该交易的输出，也就是给指定地址转账， 在上面这个交易中，
      vout 给地址 1LAMDkarMYfZXcRQX5ZKhSafQBJqcRf91v(addresses 字段) 转账 0.18624737 LBTC (value 字段)
```

解析每个交易数据存储在mongo数据库中，交易可能会引用之前的交易信息，上面交易信息在mongo中存取格式:
```
> db.lbtc_tx.findOne({'_id': '163d33738e9f2fc4b3cdb860fe8fe3d16fcae6a9d3a8c805e8c8b6607fe14c53'})
{
        "_id" : "163d33738e9f2fc4b3cdb860fe8fe3d16fcae6a9d3a8c805e8c8b6607fe14c53",
        "time" : ISODate("2018-12-19T15:06:40Z"),
        "size" : 779,
        "height" : 1911040,
        "input" : [
                "1LAMDkarMYfZXcRQX5ZKhSafQBJqcRf91v",
                "0.19624737"
        ],
        "output" : [
                0,
                "nulldata",
                "0E-8",
                1,
                "1LAMDkarMYfZXcRQX5ZKhSafQBJqcRf91v",
                "0.18624737"
        ]
}

```
使用交易hash作为主键( _id 字段)


#### Dpos规则
1. 每轮选出获取票数最多的 101 个节点为出块节点，由这101个节点轮流出块
2. 每轮的第一个区块有该轮出块的节点地址和顺序

下面为 5907122 高度的第一个交易信息，可调用 gettransactionnew RPC 接口获取，详情见[这里](https://lbtc.me/lbtc/rpc?run=1&cmd=gettransactionnew&param1=d8d3cfe8ef87080d6100496007165a8f8a5e96e74661b44672a5753fadc1a009):

```
{'blockhash': '201c33486b835be820fb2e3b4e97489fdfaac62bf8a60374499c6b10ca418d28',
 'blocktime': 1557377248,
 'confirmations': 170956,
 'hash': 'd8d3cfe8ef87080d6100496007165a8f8a5e96e74661b44672a5753fadc1a009',
 'height': 5907122,
 'locktime': 0,
 'size': 2233,
 'time': 1557377248,
 'txid': 'd8d3cfe8ef87080d6100496007165a8f8a5e96e74661b44672a5753fadc1a009',
 'version': 65282,
 'vin': [{'coinbase': '03b2225a0101', 'sequence': 4294967295}],
 'vout': [{'n': 0,
           'scriptPubKey': {'addresses': ['1GvB4GGjBEczBeYaAoPtN9u1pgQvfsYWKt'],
                            'asm': 'OP_DUP OP_HASH160 '
                                   'ae9853c878b9fd8d3ad35a8fda17bee2c99c6de5 '
                                   'OP_EQUALVERIFY OP_CHECKSIG',
                            'hex': '76a914ae9853c878b9fd8d3ad35a8fda17bee2c99c6de588ac',
                            'reqSigs': 1,
                            'type': 'pubkeyhash'},
           'value': Decimal('0.06250000')},
          {'delegates': ['1GvB4GGjBEczBeYaAoPtN9u1pgQvfsYWKt',
                         '1Hm5bfPC9pxkW4sKyz4tDHBdfmT6g6pBbi',
                         '1NDwzLkWG3TS6rAWn5Q7YzTymXLswcFd7h',
                         '1BN5BEZ3xyG9XqdxrGCv8DVpqnCAS3Fz7c',
                         ...
                         '1EMCC9jMQsXYftiriffiNKrRLw3n3UWD44'],
           'n': 1,
           'scriptPubKey': {'asm': 'OP_RETURN '
                                   '0304ef00ba12d14e978bd764697b366bc6bf7b835c44155cb8027cbae067b4c31d '
                                   '3045022100ac51e46d6c6ff0ff9a7f0865c1a '
                                   '07ae9853c878b9fd8d3ad35a8fda17bee2c99c6de5b7d8271b09e6409a1b5ceb7a4f3b',
                            'hex': '6a210304ef
                            'type': 'nulldata'},
           'type': 'CoinbaseDelegateInfo',
           'value': Decimal('0E-8')}],
 'vsize': 2233}
```
在该交易第一个 vout  json中(delegates 字段)记录了该轮出块的101个代理节点及出块顺序
