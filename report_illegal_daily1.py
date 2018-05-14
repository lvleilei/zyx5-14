#!/usr/bin/env python
# coding:utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from datetime import datetime,timedelta
import pymysql as mysql
import pymysql.cursors
from pybloom import ScalableBloomFilter
import time

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
TABLE_REPORT_TEST = 'report_test'
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



def defaultDatabase():
	conn = mysql.connect(host=HOST,user=USER,password=PASSWORD,db=DEFAULT_DB,charset=CHARSET,cursorclass=pymysql.cursors.DictCursor)
	conn.autocommit(True)
	cur = conn.cursor()
	return cur

#最大日期
def MaxDate(table):
	cur = defaultDatabase()
	sql = 'select * from %s'%table
	cur.execute(sql)
	data = cur.fetchone()
	return data

TABLE_DATE = MaxDate(TABLE_DATE_LIST)
gongshang_date = TABLE_DATE['gongshang_date']
promise_date = TABLE_DATE['promise_date']
quantile_date = TABLE_DATE['quantile_date']
monitor_date = TABLE_DATE['monitor_date']
comment_date = TABLE_DATE['comment_date']
ad_date = TABLE_DATE['ad_date']
plat_date = TABLE_DATE['plat_date']
return_date = TABLE_DATE['return_date']
table1 = TABLE_ENTITY_LIST
table2 = TABLE_MONITOR
table3 = TABLE_GONGSHANG
table4 = TABLE_INDEX_QUANTILE
table5 = TABLE_GUARANTEE_PROMISE
table6 = TABLE_COMMENT_STATIS
table7 = TABLE_AD_STATIS
table8 = TABLE_PLAT_DETAIL
table9 = TABLE_RETURN_RATE
risk_level = RISK_LEVEL
illegal_score = ILLEGAL_SCORE
date = 1
def totalDetectData(table1,table2,table3,risk_level,illegal_score,table4,table5,table6,table7,table8,table9):
	cur = defaultDatabase()

	#查询数据
	end_time = monitor_date
	start_time = datetime.strptime(end_time,"%Y-%m-%d") - timedelta(days=int(date))
	start_time = start_time.strftime("%Y-%m-%d")
	sql1 = "select el.website,gs.firm_name,gs.capital,gs.legal_person,gs.set_time,pd.entity_id,el.entity_name,el.entity_type,el.operation_mode,gs.province,gs.city,gs.district,pd.illegal_type,pd.date,el.support_num,el.against_num,el.entity_source,el.problem,pd.illegal_score,qu.return_rank,qu.comment_rank,qu.ad_rank,qu.suit_rank,qu.abnor_rank,pro.promise_type,el.monitor_status,el.risk_rank,el.industry,el.fund_mode,(gs.admin_suit_num+gs.civil_suit_num+gs.crime_suit_num+gs.other_suit_num) as suit_num,(gs.uncontact_abnormal_num+gs.fake_abnormal_num+gs.daily_report_abnormal_num+gs.other_abnormal_num) as abnor_num,(com.em0_text_bbs+com.em0_text_forum+com.em0_text_webo+com.em0_text_wechat+com.em0_text_zhihu+com.em1_text_bbs+com.em1_text_forum+com.em1_text_webo+com.em1_text_wechat+com.em1_text_zhihu) as comment_num,(ad.inf2_bbs+ad.inf2_forum+ad.inf2_webo+ad.inf2_wechat+ad.inf2_zhihu+ad.inf3_bbs+ad.inf3_forum+ad.inf3_webo+ad.inf3_wechat+ad.inf3_zhihu) as ad_num from %s as el inner join %s as pd on pd.entity_id=el.id inner join %s as gs on gs.entity_id=el.id and gs.date='%s' inner join %s as qu on qu.entity_id=el.id and qu.date='%s' inner join %s as pro on pro.entity_id=el.id and pro.date='%s' inner join %s as com on com.entity_id=el.id and com.date='%s' inner join %s as ad on ad.entity_id=el.id and ad.date='%s' where el.monitor_status>=1 and pd.date>'%s' and pd.date<='%s' and pd.illegal_type>=%d and pd.risk_level>%d and pd.illegal_score>=%d order by pd.date desc,pd.illegal_score desc,el.id desc" % (table1, table2, table3, gongshang_date, table4, quantile_date, table5, promise_date, table6, comment_date, table7, ad_date, start_time, end_time, illegal_type, risk_level, illegal_score)
	cur.execute(sql1)
	result = cur.fetchall()

	# 收益率
	return_rate_dict = {}
	order = "select id,entity_id,avg_return from " + table8 + \
				" where date = '%s' and avg_return > 0 " % plat_date
	cur.execute(order)
	result1 = cur.fetchall()
	for item in result1:
		if(item['avg_return'] and item['avg_return']!= '-%'):
			return_rate_dict[item['entity_id']] = float(item['avg_return'].replace('-','').replace('%',''))
		else:
			return_rate_dict[item['entity_id']] = 0.0
	order = "select id,entity_id,return_rate from " + table9 + \
		" where return_type<=2 and date = '%s' " % return_date
	cur.execute(order)
	result2 = cur.fetchall()
	for item in result2:
		if(return_rate_dict.has_key(item['entity_id'])):
			if(return_rate_dict[item['entity_id']]<float(item['return_rate'])*100):
				return_rate_dict[item['entity_id']] = float(item['return_rate'])*100
		else:
			return_rate_dict[item['entity_id']] = float(item['return_rate'])*100
	for d in result:
		try:
			return_num = return_rate_dict[d['entity_id']]
		except:
			return_num = 0
		d.update({'return_num':return_num})

	#拼接key
	keys = ','.join([k for k in result[0].keys()])

	#拼接values
	vals = []
	for each in result:
		vs = []
		for value in each.values():
			if value:
				try:
					int(value)
				except:
					value = '"' + value + '"'
			else:
				if not value == 0:
					value = 'null'
			vs.append(str(value))
		val = '(' + ','.join(vs) + ')'
		vals.append(val)
	values = ','.join(vals)

	#插入大表
	sql2 = "insert into %s(%s) values %s" % ('report_illegal_daily', keys, values)
	cur.execute(sql2)
	cur.close()
	return result

result = totalDetectData(table1,table2,table3,risk_level,illegal_score,table4,table5,table6,table7,table8,table9)

