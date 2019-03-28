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
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT, 
  `ip` varchar(64) NOT NULL DEFAULT '' COMMENT 'ip and port',
  `user_agent` varchar(64) NOT NULL DEFAULT '' COMMENT 'client version',
  `services` varchar(128) NOT NULL DEFAULT '' COMMENT 'services',
  `height` INT NOT NULL DEFAULT '0' COMMENT 'block height',
  `location` varchar(128) NOT NULL DEFAULT '' COMMENT 'host location',
  `timezone` varchar(64) NOT NULL DEFAULT '' COMMENT 'timezone',
  `network` varchar(128) NOT NULL DEFAULT '' COMMENT 'network status',
  `asn` varchar(64) NOT NULL DEFAULT '' COMMENT 'asn',
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

CREATE TABLE IF NOT EXISTS `node_not_valid` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT, 
  `ip` varchar(64) NOT NULL DEFAULT '' COMMENT 'ip and port',
  `count` INT NOT NULL DEFAULT '0' COMMENT 'connection try times', 
  `create_time` datetime NOT NULL DEFAULT '1970-01-01 00:00:00',
  PRIMARY KEY (`id`),
  UNIQUE KEY `lbtcnode_node_ip` (`ip`)
) ENGINE=InnoDB AUTO_INCREMENT=1000 DEFAULT CHARSET=utf8;


CREATE TABLE IF NOT EXISTS `node_distribution` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `country` varchar(64) NOT NULL DEFAULT '' COMMENT '',
  `rank` INT NOT NULL DEFAULT '0' COMMENT '',
  `node_num` INT NOT NULL DEFAULT '0' COMMENT '',
  `node_persent` float NOT NULL DEFAULT '0' COMMENT '',
  `deleted` tinyint(4) NOT NULL DEFAULT '0' COMMENT '0: normal, 1: deleted',
  PRIMARY KEY (`id`),
  UNIQUE KEY `node_distribution_country` (`country`)
) ENGINE=InnoDB AUTO_INCREMENT=1000 DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `block_status` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `key` varchar(64) NOT NULL DEFAULT '' COMMENT '',
  `value` text NOT NULL COMMENT '',
  `create_time` datetime NOT NULL DEFAULT '1970-01-01 00:00:00',
  `update_time` datetime NOT NULL DEFAULT '1970-01-01 00:00:00',
  PRIMARY KEY (`id`),
  UNIQUE KEY `block_status_key` (`key`)
) ENGINE=InnoDB AUTO_INCREMENT=1000 DEFAULT CHARSET=utf8;
