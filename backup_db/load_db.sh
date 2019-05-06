back_dir='20190429'

mysql -ulbtc -psxfMd4_f12508ccsdfdf   < $back_dir/lbtcnode.sql

mongorestore -d lbtc $back_dir/mongodump/lbtc/
