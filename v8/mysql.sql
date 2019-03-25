create database lbtcnode;
use lbtcnode;
ALTER database `lbtcnode` CHARACTER SET utf8;

SET character_set_client = utf8;
SET character_set_connection = utf8;
SET character_set_results = utf8;
SET character_set_server = utf8;

SET collation_connection = utf8_general_ci;
SET collation_server = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `node` (
  `id` INT NOT NULL AUTO_INCREMENT, 
  `ip` varchar(64) NOT NULL DEFAULT '' COMMENT 'ip and port',
  `user_agent` varchar(255) NOT NULL DEFAULT '' COMMENT 'client version',
  `height` INT NOT NULL DEFAULT '0' COMMENT 'block height',
  `location` varchar(255) NOT NULL DEFAULT '' COMMENT 'host location',
  `network` varchar(255) NOT NULL DEFAULT '' COMMENT 'network status',
  `pix` float NOT NULL DEFAULT '0' COMMENT 'calculated properties and network metrics every 24 hours',
  `latitude` float NOT NULL DEFAULT '0' COMMENT '',
  `longitude` float NOT NULL DEFAULT '0' COMMENT '',
  `status` tinyint(4) NOT NULL DEFAULT '0' COMMENT '0: offline, 1: online',
  `deleted` tinyint(4) NOT NULL DEFAULT '0' COMMENT '0: normal, 1: deleted',
  `create_time` datetime NOT NULL DEFAULT '1970-01-01 00:00:00',
  `update_time` datetime NOT NULL DEFAULT '1970-01-01 00:00:00',
  PRIMARY KEY (`id`),
  UNIQUE KEY `lbtcnode_node_ip` (`ip`)
) ENGINE=InnoDB AUTO_INCREMENT=1000 DEFAULT CHARSET=utf8;
