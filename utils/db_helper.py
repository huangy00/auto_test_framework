# -*- coding: utf-8 -*-
"""
数据库操作工具模块
使用 pymysql 封装数据库增删改查操作
连接参数从 config.ini 读取，支持 DictCursor 返回字典格式结果
"""
import pymysql
from pymysql.cursors import DictCursor
from utils.config_reader import config
from utils.logger import logger


class DBHelper:
    """数据库操作助手，封装 pymysql 实现便捷的 CRUD 操作"""

    def __init__(self):
        """初始化数据库连接参数（从 config.ini 读取）"""
        self.db_config = {
            "host": config.get("db", "host"),
            "port": config.getint("db", "port"),
            "user": config.get("db", "user"),
            "password": config.get("db", "password"),
            "database": config.get("db", "database"),
            "charset": "utf8mb4",
            "cursorclass": DictCursor,
            # 自动提交：db_helper 是全局共享单连接，若开启隐式事务，长时间
            # 运行后连接会停留在旧的一致性快照，看不到应用（PHP）后续提交的
            # 新数据（曾导致全套件中"注册成功但 DB 查不到用户"的偶发失败）。
            "autocommit": True,
        }
        self.connection = None
        logger.info(f"DBHelper initialized, database={self.db_config['database']}")

    def _get_connection(self):
        """
        获取数据库连接（懒加载，按需创建）
        :return: pymysql Connection 对象
        """
        if self.connection is None or not self.connection.open:
            self.connection = pymysql.connect(**self.db_config)
            logger.info("Database connection established")
        return self.connection

    def query_one(self, sql: str, params: tuple = None) -> dict:
        """
        查询单条记录
        :param sql: SQL 查询语句
        :param params: 查询参数（防止 SQL 注入）
        :return: 单条记录字典，无结果返回 None
        """
        logger.debug(f"Query one: {sql} | params: {params}")
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                result = cursor.fetchone()
                logger.debug(f"Result: {result}")
                return result
        except Exception as e:
            logger.error(f"Query one failed: {e}")
            raise

    def query_all(self, sql: str, params: tuple = None) -> list:
        """
        查询多条记录
        :param sql: SQL 查询语句
        :param params: 查询参数
        :return: 记录列表（字典格式）
        """
        logger.debug(f"Query all: {sql} | params: {params}")
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                result = cursor.fetchall()
                logger.debug(f"Result count: {len(result)}")
                return result
        except Exception as e:
            logger.error(f"Query all failed: {e}")
            raise

    def execute(self, sql: str, params: tuple = None) -> int:
        """
        执行增删改操作
        :param sql: SQL 语句
        :param params: 操作参数
        :return: 受影响的行数
        """
        logger.debug(f"Execute: {sql} | params: {params}")
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                affected = cursor.execute(sql, params)
                conn.commit()
                logger.debug(f"Affected rows: {affected}")
                return affected
        except Exception as e:
            conn.rollback()
            logger.error(f"Execute failed: {e}, rolled back")
            raise

    def close(self):
        """关闭数据库连接"""
        if self.connection and self.connection.open:
            self.connection.close()
            logger.info("Database connection closed")


# 全局数据库助手实例
db_helper = DBHelper()
