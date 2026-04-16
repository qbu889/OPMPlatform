#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Swagger API 文档配置 - 完整版本
包含所有模块的 API 接口定义
"""
from flask import Blueprint, render_template_string, jsonify

swagger_bp = Blueprint('swagger', __name__, url_prefix='/swagger')

SWAGGER_HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>OPM 综合业务系统 API</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5.10.0/swagger-ui.css">
    <style>
        html { box-sizing: border-box; overflow: -moz-scrollbars-vertical; overflow-y: scroll; }
        *, *:before, *:after { box-sizing: inherit; }
        body { margin:0; background: #fafafa; }
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5.10.0/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@5.10.0/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {
            const ui = SwaggerUIBundle({
                url: "/swagger/spec",
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout"
            });
            window.ui = ui;
        };
    </script>
</body>
</html>
"""


@swagger_bp.route('/')
def swagger_ui():
    """Swagger UI 页面"""
    return render_template_string(SWAGGER_HTML)


@swagger_bp.route('/spec')
def swagger_spec():
    """返回 Swagger JSON 规范"""
    spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "OPM 综合业务系统 API",
            "description": "诺基亚 OPM 综合业务系统的 RESTful API 文档，包含 Kafka 消息生成、FPA 功能点估算、文档转换、智能客服、排班管理等功能模块",
            "version": "1.0.0"
        },
        "servers": [
            {
                "url": "http://localhost:5001",
                "description": "本地开发环境"
            }
        ],
        "tags": [
            {"name": "Kafka消息生成器", "description": "Kafka 消息生成相关接口"},
            {"name": "FPA功能点估算", "description": "FPA 功能点估算、规则管理、异步任务"},
            {"name": "文档转换", "description": "Word/Excel/Markdown 文档转换工具"},
            {"name": "事件清洗", "description": "ES 事件数据清洗与推送消息生成"},
            {"name": "智能客服", "description": "AI 智能客服、知识库管理"},
            {"name": "排班管理", "description": "人员排班配置与生成"},
            {"name": "SQL工具", "description": "SQL ID 格式化工具"},
            {"name": "认证", "description": "用户登录、注册、密码管理"},
            {"name": "在线表格", "description": "在线协作表格功能"}
        ],
        "paths": generate_paths()
    }
    return jsonify(spec)


def generate_paths():
    """生成所有 API 路径定义"""
    paths = {}
    
    # ========== Kafka 消息生成器 ==========
    paths.update({
        "/kafka-generator/field-meta": {
            "get": {
                "summary": "获取字段元数据",
                "tags": ["Kafka消息生成器"],
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/kafka-generator/field-order": {
            "get": {
                "summary": "获取字段顺序",
                "tags": ["Kafka消息生成器"],
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/kafka-generator/field-options": {
            "get": {
                "summary": "获取字段选项",
                "tags": ["Kafka消息生成器"],
                "parameters": [
                    {"name": "kafka_field", "in": "query", "required": True, "schema": {"type": "string"}, "example": "BUSINESS_LAYER"}
                ],
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/kafka-generator/generate": {
            "post": {
                "summary": "生成 Kafka 消息",
                "tags": ["Kafka消息生成器"],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["es_source_raw"],
                                "properties": {
                                    "es_source_raw": {"type": "string"},
                                    "custom_fields": {"type": "object"},
                                    "delay_time": {"type": "integer"}
                                }
                            }
                        }
                    }
                },
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/kafka-generator/history": {
            "get": {
                "summary": "获取生成历史",
                "tags": ["Kafka消息生成器"],
                "parameters": [
                    {"name": "page", "in": "query", "schema": {"type": "integer", "default": 1}},
                    {"name": "per_page", "in": "query", "schema": {"type": "integer", "default": 20}},
                    {"name": "keyword", "in": "query", "schema": {"type": "string"}},
                    {"name": "field_name", "in": "query", "schema": {"type": "string"}}
                ],
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/kafka-generator/generate-push-message": {
            "post": {
                "summary": "生成推送消息",
                "tags": ["Kafka消息生成器"],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["fp_value"],
                                "properties": {
                                    "fp_value": {"type": "string"},
                                    "event_time": {"type": "string"},
                                    "active_status": {"type": "string"}
                                }
                            }
                        }
                    }
                },
                "responses": {"200": {"description": "成功"}}
            }
        }
    })
    
    # ========== FPA 功能点估算 ==========
    paths.update({
        "/fpa-generator/api/generate-async": {
            "post": {
                "summary": "异步生成 FPA 预估表",
                "tags": ["FPA功能点估算"],
                "requestBody": {
                    "content": {
                        "multipart/form-data": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "requirement_file": {"type": "string", "format": "binary"}
                                }
                            }
                        }
                    }
                },
                "responses": {"200": {"description": "任务已创建"}}
            }
        },
        "/fpa-generator/api/task-status/{task_id}": {
            "get": {
                "summary": "查询任务状态",
                "tags": ["FPA功能点估算"],
                "parameters": [
                    {"name": "task_id", "in": "path", "required": True, "schema": {"type": "string"}}
                ],
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/fpa-generator/api/task-cancel/{task_id}": {
            "post": {
                "summary": "取消任务",
                "tags": ["FPA功能点估算"],
                "parameters": [
                    {"name": "task_id", "in": "path", "required": True, "schema": {"type": "string"}}
                ],
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/fpa-generator/api/export-history": {
            "get": {
                "summary": "获取导出历史",
                "tags": ["FPA功能点估算"],
                "parameters": [
                    {"name": "page", "in": "query", "schema": {"type": "integer", "default": 1}},
                    {"name": "page_size", "in": "query", "schema": {"type": "integer", "default": 20}}
                ],
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/fpa-generator/api/export-history/{task_id}": {
            "delete": {
                "summary": "删除导出历史",
                "tags": ["FPA功能点估算"],
                "parameters": [
                    {"name": "task_id", "in": "path", "required": True, "schema": {"type": "string"}}
                ],
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/fpa-rules/api/rules": {
            "get": {
                "summary": "获取 FPA 规则列表",
                "tags": ["FPA功能点估算"],
                "parameters": [
                    {"name": "page", "in": "query", "schema": {"type": "integer", "default": 1}},
                    {"name": "per_page", "in": "query", "schema": {"type": "integer", "default": 20}},
                    {"name": "category", "in": "query", "schema": {"type": "string"}},
                    {"name": "keyword", "in": "query", "schema": {"type": "string"}},
                    {"name": "is_active", "in": "query", "schema": {"type": "boolean"}},
                    {"name": "priority", "in": "query", "schema": {"type": "integer"}}
                ],
                "responses": {"200": {"description": "成功"}}
            },
            "post": {
                "summary": "创建新规则",
                "tags": ["FPA功能点估算"],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["category", "priority", "rule_type", "keyword", "ufp_value"],
                                "properties": {
                                    "category": {"type": "string", "enum": ["EI", "EO", "EQ", "ILF", "EIF"]},
                                    "priority": {"type": "integer"},
                                    "rule_type": {"type": "string", "enum": ["endswith", "contains", "startswith", "special"]},
                                    "keyword": {"type": "string"},
                                    "ufp_value": {"type": "integer"},
                                    "description": {"type": "string"},
                                    "is_active": {"type": "boolean"}
                                }
                            }
                        }
                    }
                },
                "responses": {"201": {"description": "创建成功"}}
            }
        },
        "/fpa-rules/api/rules/{rule_id}": {
            "get": {
                "summary": "获取单个规则",
                "tags": ["FPA功能点估算"],
                "parameters": [
                    {"name": "rule_id", "in": "path", "required": True, "schema": {"type": "integer"}}
                ],
                "responses": {"200": {"description": "成功"}}
            },
            "put": {
                "summary": "更新规则",
                "tags": ["FPA功能点估算"],
                "parameters": [
                    {"name": "rule_id", "in": "path", "required": True, "schema": {"type": "integer"}}
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "category": {"type": "string"},
                                    "priority": {"type": "integer"},
                                    "rule_type": {"type": "string"},
                                    "keyword": {"type": "string"},
                                    "ufp_value": {"type": "integer"},
                                    "is_active": {"type": "boolean"}
                                }
                            }
                        }
                    }
                },
                "responses": {"200": {"description": "更新成功"}}
            },
            "delete": {
                "summary": "删除规则",
                "tags": ["FPA功能点估算"],
                "parameters": [
                    {"name": "rule_id", "in": "path", "required": True, "schema": {"type": "integer"}}
                ],
                "responses": {"200": {"description": "删除成功"}}
            }
        },
        "/fpa-rules/api/rules/batch": {
            "post": {
                "summary": "批量更新规则",
                "tags": ["FPA功能点估算"],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "updates": {
                                        "type": "array",
                                        "items": {"type": "object"}
                                    }
                                }
                            }
                        }
                    }
                },
                "responses": {"200": {"description": "批量更新成功"}}
            }
        },
        "/api/category/list": {
            "get": {
                "summary": "获取分类列表",
                "tags": ["FPA功能点估算"],
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/api/category/add": {
            "post": {
                "summary": "新增分类",
                "tags": ["FPA功能点估算"],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {"type": "object"}
                        }
                    }
                },
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/api/category/update": {
            "post": {
                "summary": "更新分类",
                "tags": ["FPA功能点估算"],
                "requestBody": {
                    "content": {
                        "application/json": {"schema": {"type": "object"}}
                    }
                },
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/api/category/delete": {
            "post": {
                "summary": "删除分类",
                "tags": ["FPA功能点估算"],
                "requestBody": {
                    "content": {
                        "application/json": {"schema": {"type": "object"}}
                    }
                },
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/adjustment/api/factors": {
            "get": {
                "summary": "获取调整因子列表",
                "tags": ["FPA功能点估算"],
                "responses": {"200": {"description": "成功"}}
            },
            "post": {
                "summary": "新增调整因子",
                "tags": ["FPA功能点估算"],
                "requestBody": {
                    "content": {
                        "application/json": {"schema": {"type": "object"}}
                    }
                },
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/adjustment/api/factor/{factor_id}": {
            "put": {
                "summary": "更新调整因子",
                "tags": ["FPA功能点估算"],
                "parameters": [
                    {"name": "factor_id", "in": "path", "required": True, "schema": {"type": "integer"}}
                ],
                "responses": {"200": {"description": "成功"}}
            },
            "delete": {
                "summary": "删除调整因子",
                "tags": ["FPA功能点估算"],
                "parameters": [
                    {"name": "factor_id", "in": "path", "required": True, "schema": {"type": "integer"}}
                ],
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/adjustment/api/import-excel": {
            "post": {
                "summary": "从 Excel 导入调整因子",
                "tags": ["FPA功能点估算"],
                "requestBody": {
                    "content": {
                        "multipart/form-data": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "file": {"type": "string", "format": "binary"}
                                }
                            }
                        }
                    }
                },
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/adjustment-calc/api/calculate-score": {
            "post": {
                "summary": "计算 FPA 分数",
                "tags": ["FPA功能点估算"],
                "requestBody": {
                    "content": {
                        "application/json": {"schema": {"type": "object"}}
                    }
                },
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/adjustment-calc/api/scale-timing-config": {
            "get": {
                "summary": "获取规模计数时机配置",
                "tags": ["FPA功能点估算"],
                "responses": {"200": {"description": "成功"}}
            },
            "post": {
                "summary": "更新规模计数时机配置",
                "tags": ["FPA功能点估算"],
                "requestBody": {
                    "content": {
                        "application/json": {"schema": {"type": "object"}}
                    }
                },
                "responses": {"200": {"description": "成功"}}
            }
        }
    })
    
    # ========== 文档转换 ==========
    paths.update({
        "/api/upload-and-convert": {
            "post": {
                "summary": "上传并转换文档",
                "tags": ["文档转换"],
                "requestBody": {
                    "content": {
                        "multipart/form-data": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "file": {"type": "string", "format": "binary"}
                                }
                            }
                        }
                    }
                },
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/api/format-check": {
            "post": {
                "summary": "格式检查",
                "tags": ["文档转换"],
                "requestBody": {
                    "content": {
                        "application/json": {"schema": {"type": "object"}}
                    }
                },
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/api/format-document": {
            "post": {
                "summary": "格式化文档",
                "tags": ["文档转换"],
                "requestBody": {
                    "content": {
                        "application/json": {"schema": {"type": "object"}}
                    }
                },
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/cosmic/upload": {
            "post": {
                "summary": "上传表格转 COSMIC",
                "tags": ["文档转换"],
                "requestBody": {
                    "content": {
                        "multipart/form-data": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "file": {"type": "string", "format": "binary"}
                                }
                            }
                        }
                    }
                },
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/cosmic/convert": {
            "post": {
                "summary": "执行 COSMIC 转换",
                "tags": ["文档转换"],
                "requestBody": {
                    "content": {
                        "application/json": {"schema": {"type": "object"}}
                    }
                },
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/cosmic/download/{filename}": {
            "get": {
                "summary": "下载 COSMIC 文档",
                "tags": ["文档转换"],
                "parameters": [
                    {"name": "filename", "in": "path", "required": True, "schema": {"type": "string"}}
                ],
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/cosmic/stats": {
            "post": {
                "summary": "获取 COSMIC 统计",
                "tags": ["文档转换"],
                "requestBody": {
                    "content": {
                        "application/json": {"schema": {"type": "object"}}
                    }
                },
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/es-to-excel/upload": {
            "post": {
                "summary": "上传 ES 查询结果",
                "tags": ["文档转换"],
                "requestBody": {
                    "content": {
                        "multipart/form-data": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "file": {"type": "string", "format": "binary"}
                                }
                            }
                        }
                    }
                },
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/es-to-excel/convert": {
            "post": {
                "summary": "转换为 Excel",
                "tags": ["文档转换"],
                "requestBody": {
                    "content": {
                        "application/json": {"schema": {"type": "object"}}
                    }
                },
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/es-to-excel/download/{filename}": {
            "get": {
                "summary": "下载 Excel 文件",
                "tags": ["文档转换"],
                "parameters": [
                    {"name": "filename", "in": "path", "required": True, "schema": {"type": "string"}}
                ],
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/word-to-excel/upload": {
            "post": {
                "summary": "上传 Word 转 Excel",
                "tags": ["文档转换"],
                "requestBody": {
                    "content": {
                        "multipart/form-data": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "file": {"type": "string", "format": "binary"}
                                }
                            }
                        }
                    }
                },
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/word-to-excel/download/{download_id}": {
            "get": {
                "summary": "下载转换后的 Excel",
                "tags": ["文档转换"],
                "parameters": [
                    {"name": "download_id", "in": "path", "required": True, "schema": {"type": "string"}}
                ],
                "responses": {"200": {"description": "成功"}}
            }
        }
    })
    
    # ========== 事件清洗 ==========
    paths.update({
        "/api/clean-event/process": {
            "post": {
                "summary": "处理 ES 数据生成推送消息",
                "tags": ["事件清洗"],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "hits": {
                                        "type": "object",
                                        "properties": {
                                            "hits": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "_source": {
                                                            "type": "object",
                                                            "properties": {
                                                                "EVENT_FP": {"type": "string"},
                                                                "EVENT_TIME": {"type": "string"}
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/api/clean-event/upload": {
            "post": {
                "summary": "上传 JSON 文件处理",
                "tags": ["事件清洗"],
                "requestBody": {
                    "content": {
                        "multipart/form-data": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "file": {"type": "string", "format": "binary", "description": "JSON 文件"}
                                }
                            }
                        }
                    }
                },
                "responses": {"200": {"description": "成功"}}
            }
        }
    })
    
    # ========== 智能客服 ==========
    paths.update({
        "/chatbot/chat": {
            "post": {
                "summary": "聊天接口",
                "tags": ["智能客服"],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["message"],
                                "properties": {
                                    "message": {"type": "string", "description": "用户问题"},
                                    "session_id": {"type": "string", "description": "会话 ID（可选）"}
                                }
                            }
                        }
                    }
                },
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/chatbot/upload_document/preview": {
            "post": {
                "summary": "上传文档预览 FAQ",
                "tags": ["智能客服"],
                "requestBody": {
                    "content": {
                        "multipart/form-data": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "file": {"type": "string", "format": "binary"},
                                    "domain_id": {"type": "string"}
                                }
                            }
                        }
                    }
                },
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/chatbot/upload_document/confirm": {
            "post": {
                "summary": "确认导入 FAQ",
                "tags": ["智能客服"],
                "requestBody": {
                    "content": {
                        "application/json": {"schema": {"type": "object"}}
                    }
                },
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/chatbot/documents": {
            "get": {
                "summary": "获取文档列表",
                "tags": ["智能客服"],
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/chatbot/faqs": {
            "get": {
                "summary": "获取 FAQ 列表",
                "tags": ["智能客服"],
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/chatbot/search": {
            "get": {
                "summary": "搜索 FAQ",
                "tags": ["智能客服"],
                "parameters": [
                    {"name": "q", "in": "query", "schema": {"type": "string"}}
                ],
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/chatbot/conversation/clear": {
            "post": {
                "summary": "清空会话",
                "tags": ["智能客服"],
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/chatbot/ollama/status": {
            "get": {
                "summary": "检查 Ollama 服务状态",
                "tags": ["智能客服"],
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/chatbot/upload_progress/{preview_id}": {
            "get": {
                "summary": "查询上传进度",
                "tags": ["智能客服"],
                "parameters": [
                    {"name": "preview_id", "in": "path", "required": True, "schema": {"type": "string"}}
                ],
                "responses": {"200": {"description": "成功"}}
            }
        }
    })
    
    # ========== 排班管理 ==========
    paths.update({
        "/schedule-config/api/staff-config": {
            "get": {
                "summary": "获取人员配置",
                "tags": ["排班管理"],
                "responses": {"200": {"description": "成功"}}
            },
            "post": {
                "summary": "更新人员配置",
                "tags": ["排班管理"],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "core_staff": {"type": "string"},
                                    "test_staffs": {"type": "array", "items": {"type": "string"}}
                                }
                            }
                        }
                    }
                },
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/schedule-config/api/leave-records": {
            "get": {
                "summary": "获取请假记录",
                "tags": ["排班管理"],
                "parameters": [
                    {"name": "start_date", "in": "query", "schema": {"type": "string", "format": "date"}},
                    {"name": "end_date", "in": "query", "schema": {"type": "string", "format": "date"}}
                ],
                "responses": {"200": {"description": "成功"}}
            },
            "post": {
                "summary": "添加请假记录",
                "tags": ["排班管理"],
                "requestBody": {
                    "content": {
                        "application/json": {"schema": {"type": "object"}}
                    }
                },
                "responses": {"200": {"description": "成功"}}
            },
            "delete": {
                "summary": "删除请假记录",
                "tags": ["排班管理"],
                "requestBody": {
                    "content": {
                        "application/json": {"schema": {"type": "object"}}
                    }
                },
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/schedule-config/api/generate-schedule": {
            "post": {
                "summary": "生成排班",
                "tags": ["排班管理"],
                "requestBody": {
                    "content": {
                        "application/json": {"schema": {"type": "object"}}
                    }
                },
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/schedule-config/api/schedule-records": {
            "get": {
                "summary": "获取排班记录",
                "tags": ["排班管理"],
                "parameters": [
                    {"name": "month", "in": "query", "schema": {"type": "string"}}
                ],
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/schedule-config/api/list": {
            "get": {
                "summary": "获取排班列表",
                "tags": ["排班管理"],
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/schedule-config/api/create": {
            "post": {
                "summary": "创建排班",
                "tags": ["排班管理"],
                "requestBody": {
                    "content": {
                        "application/json": {"schema": {"type": "object"}}
                    }
                },
                "responses": {"200": {"description": "成功"}}
            }
        }
    })
    
    # ========== SQL 工具 ==========
    paths.update({
        "/sql/format_ids": {
            "post": {
                "summary": "格式化 SQL ID",
                "tags": ["SQL工具"],
                "requestBody": {
                    "content": {
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "ids": {"type": "string", "description": "ID 列表，每行一个"}
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "成功",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean"},
                                        "formatted_ids": {"type": "string"},
                                        "sql_query": {"type": "string"},
                                        "count": {"type": "integer"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    })
    
    # ========== 认证 ==========
    paths.update({
        "/auth/api/login": {
            "post": {
                "summary": "用户登录",
                "tags": ["认证"],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["username", "password"],
                                "properties": {
                                    "username": {"type": "string", "example": "admin"},
                                    "password": {"type": "string", "example": "123456"}
                                }
                            }
                        }
                    }
                },
                "responses": {"200": {"description": "登录成功"}}
            }
        },
        "/auth/api/register": {
            "post": {
                "summary": "用户注册",
                "tags": ["认证"],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"type": "object"}
                        }
                    }
                },
                "responses": {"200": {"description": "注册成功"}}
            }
        },
        "/auth/api/logout": {
            "post": {
                "summary": "用户登出",
                "tags": ["认证"],
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/auth/api/current-user": {
            "get": {
                "summary": "获取当前用户信息",
                "tags": ["认证"],
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/auth/api/change-password": {
            "post": {
                "summary": "修改密码",
                "tags": ["认证"],
                "requestBody": {
                    "content": {
                        "application/json": {"schema": {"type": "object"}}
                    }
                },
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/auth/api/get-security-question": {
            "post": {
                "summary": "获取密保问题",
                "tags": ["认证"],
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/auth/api/reset-password": {
            "post": {
                "summary": "重置密码",
                "tags": ["认证"],
                "requestBody": {
                    "content": {
                        "application/json": {"schema": {"type": "object"}}
                    }
                },
                "responses": {"200": {"description": "成功"}}
            }
        }
    })
    
    # ========== 在线表格 ==========
    paths.update({
        "/spreadsheet/api/create": {
            "post": {
                "summary": "创建表格",
                "tags": ["在线表格"],
                "requestBody": {
                    "content": {
                        "application/json": {"schema": {"type": "object"}}
                    }
                },
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/spreadsheet/api/list": {
            "get": {
                "summary": "获取表格列表",
                "tags": ["在线表格"],
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/spreadsheet/api/{spreadsheet_id}": {
            "get": {
                "summary": "获取表格详情",
                "tags": ["在线表格"],
                "parameters": [
                    {"name": "spreadsheet_id", "in": "path", "required": True, "schema": {"type": "integer"}}
                ],
                "responses": {"200": {"description": "成功"}}
            },
            "delete": {
                "summary": "删除表格",
                "tags": ["在线表格"],
                "parameters": [
                    {"name": "spreadsheet_id", "in": "path", "required": True, "schema": {"type": "integer"}}
                ],
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/spreadsheet/api/{spreadsheet_id}/columns": {
            "get": {
                "summary": "获取列定义",
                "tags": ["在线表格"],
                "parameters": [
                    {"name": "spreadsheet_id", "in": "path", "required": True, "schema": {"type": "integer"}}
                ],
                "responses": {"200": {"description": "成功"}}
            },
            "post": {
                "summary": "添加列",
                "tags": ["在线表格"],
                "parameters": [
                    {"name": "spreadsheet_id", "in": "path", "required": True, "schema": {"type": "integer"}}
                ],
                "requestBody": {
                    "content": {
                        "application/json": {"schema": {"type": "object"}}
                    }
                },
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/spreadsheet/api/columns/{column_id}": {
            "put": {
                "summary": "更新列",
                "tags": ["在线表格"],
                "parameters": [
                    {"name": "column_id", "in": "path", "required": True, "schema": {"type": "integer"}}
                ],
                "responses": {"200": {"description": "成功"}}
            },
            "delete": {
                "summary": "删除列",
                "tags": ["在线表格"],
                "parameters": [
                    {"name": "column_id", "in": "path", "required": True, "schema": {"type": "integer"}}
                ],
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/spreadsheet/api/{spreadsheet_id}/rows": {
            "get": {
                "summary": "获取行数据",
                "tags": ["在线表格"],
                "parameters": [
                    {"name": "spreadsheet_id", "in": "path", "required": True, "schema": {"type": "integer"}}
                ],
                "responses": {"200": {"description": "成功"}}
            },
            "post": {
                "summary": "添加行",
                "tags": ["在线表格"],
                "parameters": [
                    {"name": "spreadsheet_id", "in": "path", "required": True, "schema": {"type": "integer"}}
                ],
                "requestBody": {
                    "content": {
                        "application/json": {"schema": {"type": "object"}}
                    }
                },
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/spreadsheet/api/rows/{row_id}": {
            "delete": {
                "summary": "删除行",
                "tags": ["在线表格"],
                "parameters": [
                    {"name": "row_id", "in": "path", "required": True, "schema": {"type": "integer"}}
                ],
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/spreadsheet/api/cells/{cell_id}": {
            "get": {
                "summary": "获取单元格",
                "tags": ["在线表格"],
                "parameters": [
                    {"name": "cell_id", "in": "path", "required": True, "schema": {"type": "integer"}}
                ],
                "responses": {"200": {"description": "成功"}}
            },
            "put": {
                "summary": "更新单元格",
                "tags": ["在线表格"],
                "parameters": [
                    {"name": "cell_id", "in": "path", "required": True, "schema": {"type": "integer"}}
                ],
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/spreadsheet/api/batch-update": {
            "post": {
                "summary": "批量更新",
                "tags": ["在线表格"],
                "requestBody": {
                    "content": {
                        "application/json": {"schema": {"type": "object"}}
                    }
                },
                "responses": {"200": {"description": "成功"}}
            }
        },
        "/spreadsheet/api/upload": {
            "post": {
                "summary": "上传 Excel 导入",
                "tags": ["在线表格"],
                "requestBody": {
                    "content": {
                        "multipart/form-data": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "file": {"type": "string", "format": "binary"}
                                }
                            }
                        }
                    }
                },
                "responses": {"200": {"description": "成功"}}
            }
        }
    })
    
    return paths
