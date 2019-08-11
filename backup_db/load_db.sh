back_dir='2019-08-07'

mongo 127.0.0.1:27017/lbtc --eval "printjson(db.dropDatabase())"
mysql -ulbtc -psxfMd4_f12508ccsdfdf -e "drop database lbtcnode"

mysql -ulbtc -psxfMd4_f12508ccsdfdf   < $back_dir/lbtcnode.sql

mongorestore -d lbtc $back_dir/mongodump/lbtc/
