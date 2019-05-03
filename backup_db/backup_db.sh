back_dir=`date --date today +%Y-%m-%d`
mkdir $back_dir


#mongodump -d lbtc -o $back_dir/mongodump
mysqldump -ulbtc -psxfMd4_f12508ccsdfdf  --databases lbtcnode > $back_dir/lbtcnode.sql
