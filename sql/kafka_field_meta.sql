-- Kafka Generator 字段元数据配置表
-- 用途：配置「推送告警消息字段」<->「字段中文解释/匹配数据库中文」<->「对应ES字段」
-- 前端页面：templates（弃用）/kafka_generator.html 会通过后端接口 /kafka-generator/field-meta 读取

CREATE TABLE IF NOT EXISTS kafka_field_meta (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  kafka_field VARCHAR(64) NOT NULL COMMENT '推送告警消息字段（建议存大写，例如 NETWORK_TYPE_TOP）',
  es_field VARCHAR(128) NULL COMMENT '对应ES字段（例如 NETWORK_TYPE_ID）',
  db_cn VARCHAR(255) NULL COMMENT '匹配数据库中文（优先展示）',
  label_cn VARCHAR(255) NULL COMMENT '字段中文解释（兜底展示）',
  remark VARCHAR(255) NULL COMMENT '备注',
  is_enabled TINYINT NOT NULL DEFAULT 1 COMMENT '1启用 0禁用',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_kafka_field (kafka_field),
  KEY idx_enabled (is_enabled)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

