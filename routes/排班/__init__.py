# MySQL数据库配置
from sched import scheduler

# MySQL数据库配置
MYSQL_HOST = '127.0.0.1'
MYSQL_PORT = 3306
MYSQL_USER = 'root'
MYSQL_PWD = '12345678'
MYSQL_DB = 'schedule'
MYSQL_CHARSET = 'utf8mb4'

# 节假日接口配置
HOLIDAY_API_BASE = 'http://timor.tech/api/holiday/year/'

# 定时任务配置（cron表达式，示例：每月1号凌晨2点执行，同步下一年的节假日）
# 不懂cron表达式可参考：https://tool.lu/crontab/
CRON_YEAR = '*'
CRON_MONTH = '*'
CRON_DAY = '1'
CRON_HOUR = '2'
CRON_MINUTE = '0'
CRON_SECOND = '0'

# 默认同步年份（手动触发时若不指定，同步当前年+下一年）
DEFAULT_SYNC_YEARS = '2026,2027'
