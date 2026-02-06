import os
import sys
import logging
import requests
import pymysql
from datetime import datetime
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
# 解决Python3.8的时区警告
import warnings
warnings.filterwarnings('ignore')

# 加载.env配置文件
load_dotenv()
# 配置日志（打印时间、级别、信息，方便排查问题）
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# -------------------------- 配置项从.env加载 --------------------------
# MySQL配置
MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
    "port": int(os.getenv("MYSQL_PORT", 3306)),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PWD", "12345678"),
    "database": os.getenv("MYSQL_DB", "schedule"),
    "charset": os.getenv("MYSQL_CHARSET", "utf8mb4")
}
# 接口配置
HOLIDAY_API_BASE = os.getenv("HOLIDAY_API_BASE", "http://timor.tech/api/holiday/year/")
# 定时任务cron配置
CRON_CONFIG = {
    "year": os.getenv("CRON_YEAR", "*"),
    "month": os.getenv("CRON_MONTH", "*"),
    "day": os.getenv("CRON_DAY", "1"),
    "hour": os.getenv("CRON_HOUR", "2"),
    "minute": os.getenv("CRON_MINUTE", "0"),
    "second": os.getenv("CRON_SECOND", "0")
}
# 默认同步年份
DEFAULT_SYNC_YEARS = [int(y) for y in os.getenv("DEFAULT_SYNC_YEARS", "2026,2027").split(",")]


# -------------------------- 数据库工具函数 --------------------------
def get_mysql_conn():
    """获取MySQL数据库连接"""
    try:
        conn = pymysql.connect(**MYSQL_CONFIG)
        logger.info("MySQL数据库连接成功")
        return conn
    except pymysql.MySQLError as e:
        logger.error(f"MySQL数据库连接失败：{e}")
        sys.exit(1)  # 连接失败直接退出程序

def close_mysql_conn(conn, cursor):
    """关闭数据库连接和游标"""
    if cursor:
        cursor.close()
    if conn:
        conn.close()
    logger.info("MySQL数据库连接已关闭")

# -------------------------- 接口请求函数 --------------------------
def fetch_holiday_data(year):
    api_url = f"https://timor.tech/api/holiday/year/{year}"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        ),
        "Accept": "application/json"
    }
    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get("code") != 0:
            logger.error(f"接口返回异常：{data}")
            return None
        return data.get("holiday", {})
    except requests.RequestException as e:
        logger.error(f"拉取{year}年节假日数据请求异常：{e}")
        return None


# -------------------------- 数据清洗与同步核心函数 --------------------------
def sync_holiday_to_mysql(year):
    """
    核心同步函数：拉取数据→清洗转换→同步到MySQL（先删后插，避免重复数据）
    :param year: 要同步的年份（int）
    :return: 布尔值，同步成功返回True，失败返回False
    """
    # 1. 拉取接口数据
    holiday_data = fetch_holiday_data(year)
    if not holiday_data:
        return False

    # 2. 数据清洗转换：适配holiday_config表结构
    insert_data = []

    for _, day_info in holiday_data.items():
        holiday_date = datetime.strptime(
            day_info["date"], "%Y-%m-%d"
        ).date()

        is_working_day = 0 if day_info.get("holiday", False) else 1
        description = day_info.get("name", "")
        wage = int(day_info.get("wage", 1))
        after = 1 if day_info.get("after", False) else 0
        target = day_info.get("target", "")

        rest = day_info.get("rest")
        rest = int(rest) if rest is not None else None

        insert_data.append(
            (holiday_date, is_working_day, description, wage, after, target, rest)
        )

    # 3. 同步到MySQL：先删除该年份的旧数据，再批量插入新数据（避免主键冲突/数据冗余）
    conn = None
    cursor = None
    try:
        conn = get_mysql_conn()
        cursor = conn.cursor()
        # 先删除该年份的所有数据（DATE字段按年份过滤）
        deleted = cursor.execute(
            "DELETE FROM holiday_config WHERE YEAR(holiday_date) = %s",
            (year,)
        )
        logger.info(f"准备插入数据条数：{len(insert_data)}")
        # 批量插入新数据（executemany提升效率）
        insert_sql = """
                     INSERT INTO holiday_config (holiday_date, is_working_day, description, wage, after, target, rest)
                     VALUES (%s, %s, %s, %s, %s, %s, %s); \
                     """
        inserted = cursor.executemany(insert_sql, insert_data)
        conn.commit()  # 提交事务
        logger.info(
            f"{year} 年同步完成：删除 {deleted} 条，插入 {inserted} 条"
        )
        return True
    except pymysql.MySQLError as e:
        if conn:
            conn.rollback()  # 异常回滚
        logger.error(f"{year}年节假日数据同步数据库异常：{e}")
        return False
    finally:
        close_mysql_conn(conn, cursor)

def batch_sync(years=None):
    """
    批量同步多个年份的节假日数据
    :param years: 要同步的年份列表（如[2026,2027]），None则使用默认配置
    """
    if not years:
        years = DEFAULT_SYNC_YEARS
    logger.info(f"开始批量同步节假日数据，同步年份：{years}")
    success_count = 0
    for year in years:
        if sync_holiday_to_mysql(year):
            success_count += 1
    logger.info(f"批量同步完成，共{len(years)}个年份，成功{success_count}个，失败{len(years)-success_count}个")


# -------------------------- 定时任务与主入口 --------------------------
def start_scheduler():
    """启动定时任务调度器"""
    scheduler = BlockingScheduler(timezone="Asia/Shanghai")  # 设置时区为北京时间，避免时间偏移
    # 添加cron定时触发器
    trigger = CronTrigger(**CRON_CONFIG)
    # 绑定定时执行的函数（同步默认年份）
    scheduler.add_job(
        func=batch_sync,
        trigger=trigger,
        id="holiday_sync_cron",
        name="节假日定时同步任务",
        replace_existing=True  # 重复启动时替换现有任务，避免冲突
    )
    logger.info(f"定时任务已启动，Cron规则：{CRON_CONFIG}，同步年份：{DEFAULT_SYNC_YEARS}")
    logger.info("程序运行中，按Ctrl+C停止...")
    try:
        scheduler.start()
    except KeyboardInterrupt:
        scheduler.shutdown()
        logger.info("定时任务已手动停止")
    except Exception as e:
        scheduler.shutdown()
        logger.error(f"定时任务运行异常：{e}")

if __name__ == "__main__":
    """
    主程序入口，支持两种运行方式：
    1. 手动触发：python3 holiday_sync.py 2026 （指定同步的年份，多个用空格分隔）
    2. 定时触发：python3 holiday_sync.py （直接运行，启动定时任务）
    """

    args = sys.argv[1:]
    if args:
        logger.info(f"手动模式启动，同步年份：{args}")
        # 手动触发：解析命令行参数为年份列表
        try:
            sync_years = [int(year) for year in args]
            batch_sync(sync_years)
        except ValueError:
            logger.error("手动同步失败，参数必须为整数年份（如2026 2027）")
            sys.exit(1)
        else:
            logger.info("定时模式启动，仅注册 Cron 任务")
            logger.info("启动时先执行一次节假日同步")
            batch_sync()
            start_scheduler()