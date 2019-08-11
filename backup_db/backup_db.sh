sed -i 's/0/1/g' /home/ubuntu/.bin/lbtc/lbtcnode/src/exit_parse
sleep 30
tail -n 3 /home/ubuntu/.bin/lbtc/lbtcnode/src/logs/parse_lbtc_block.log

back_dir=`date --date today +%Y-%m-%d`
mkdir $back_dir


mongodump -d lbtc -o $back_dir/mongodump
mysqldump -ulbtc -psxfMd4_f12508ccsdfdf  --databases lbtcnode > $back_dir/lbtcnode.sql

sync
sleep 3
sed -i 's/1/0/g' /home/ubuntu/.bin/lbtc/lbtcnode/src/exit_parse
