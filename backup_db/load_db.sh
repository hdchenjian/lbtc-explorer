back_dir='2019-05-04'

mysql -ulbtc -psxfMd4_f12508ccsdfdf   < $back_dir/lbtcnode.sql

mongorestore -d lbtc $back_dir/mongodump/lbtc/
