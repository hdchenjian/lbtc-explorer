create database lbtcnode;
use lbtcnode;
ALTER database `lbtcnode` CHARACTER SET utf8;

SET character_set_client = utf8;
SET character_set_connection = utf8;
SET character_set_results = utf8;
SET character_set_server = utf8;

SET collation_connection = utf8_general_ci;
SET collation_server = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `weixin` (
  `id` INT NOT NULL AUTO_INCREMENT, 
  `ip` varchar(64) NOT NULL DEFAULT '',
  `user_agent` varchar(32) NOT NULL DEFAULT '',
  `country` varchar(32) NOT NULL DEFAULT '',
  `location` varchar(64) NOT NULL DEFAULT '',
  `height` INT NOT NULL DEFAULT '0',
  `network` varchar(64) NOT NULL DEFAULT '',
  `pix` float NOT NULL DEFAULT '0' COMMENT 'calculated properties and network metrics every 24 hours',
  `status` tinyint(4) NOT NULL DEFAULT '0' COMMENT '0: offline, 1: online',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `lbtcnode_weixin_open_id` (`open_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1000 DEFAULT CHARSET=utf8;
