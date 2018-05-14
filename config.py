#!/usr/bin/env python
# coding:utf-8
from economy.db import *
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

#table
TABLE_ENTITY_LIST = 'entity_list'
TABLE_PLAT_DETAIL = 'plat_detail_daily'
TABLE_COMPANY_DETAIL = 'company_detail'
TABLE_PROJECT_DETAIL = 'project_detail'
TABLE_GONGSHANG = 'gongshang_daily'
TABLE_AD_STATIS = 'ad_statis_daily'
TABLE_COMMENT_STATIS = 'comment_statis_daily'
TABLE_GUARANTEE_PROMISE = 'guarantee_promise_daily'
TABLE_RETURN_RATE = 'return_rate_daily'
TABLE_SENSOR = 'sensor_daily'
TABLE_MONITOR = 'monitor_daily'
TABLE_OPERATION_LIST = 'operation_list'
TABLE_ILLEGAL_LIST = 'illegal_list'
TABLE_LOG = 'logs'
TABLE_CITY_RANK = 'city_rank_daily'
TABLE_PROVINCE_RANK = 'province_rank_daily'
TABLE_USERINFO = 'user_info'
TABLE_PROBLEM_LIST = 'problem_list'
TABLE_DATE_LIST = 'date_list'
TABLE_INDEX_QUANTILE = 'index_quantile_daily'
TABLE_LOGS_TYPE = 'logs_type'
TABLE_LOGS = 'logs'
TABLE_CHECK_LOGS = 'check_logs'
TABLE_INDUSTRY_LIST = 'industry_list'
TABLE_FUNDMODE_LIST = 'fundmode_list'
TABLE_REPORT_ILLEGAL = 'report_illegal_daily'
TABLE_RETURN_RATE_MORE = 'return_rate_daily_more'
TABLE_REPORT_TEST = 'report_test'
TABLE_GW_RATE = 'gw_rate_daily'

#es
ES_HOST = '10.110.0.106'
ES_PORT = 9200
INDEX_NAME = {"bbs":"bbs","webo":"webo","zhihu":"zhihu","forum":"forum","wechat":"wechat"}
SENSOR_INDEX_NAME = {"bbs":"bbs_sensor","webo":"webo_sensor","zhihu":"zhihu_sensor","forum":"forum_sensor","wechat":"wechat_sensor"}
TYPE = {"bbs":"type1","webo":"type1","zhihu":"type1","forum":"type1","wechat":"type1"}
SENSOR_TYPE = {"bbs_sensor":"type1","webo_sensor":"type1","zhihu_sensor":"type1","forum_sensor":"type1","wechat_sensor":"type1"}

#db
HOST = "10.110.0.104"
USER = "root"
PASSWORD = ""
DEFAULT_DB = "itfin_on"
CHARSET = "utf8"
TEST_DB = "zyz"

#para
RISK_LEVEL = -1
ILLEGAL_SCORE = 50
ILLEGAL_TYPE = 0

#index_name
INDEX_GONGSHANG = 'gongshang_1'


