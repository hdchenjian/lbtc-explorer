
sql = '''
CREATE TABLE IF NOT EXISTS `zz_address_tx_%03d` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `hash` varchar(64) NOT NULL DEFAULT '' COMMENT '',
  `address` varchar(64) NOT NULL DEFAULT '' COMMENT '',
  PRIMARY KEY (`id`),
  KEY (`address`)
) ENGINE=InnoDB AUTO_INCREMENT=1000 DEFAULT CHARSET=utf8;
'''

for i in range(0, 256):
    cmd = sql % i
    print(cmd)
