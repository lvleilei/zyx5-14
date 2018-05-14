#/usr/bin/env python
#coding: utf-8

import pymysql as mysql
import pymysql.cursors
from elasticsearch import Elasticsearch
import csv
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def defaultDatabase():
	conn = mysql.connect(host="10.110.0.104",user="root",password="",db="itfin_on",charset="utf8",cursorclass=pymysql.cursors.DictCursor)
	conn.autocommit(True)
	cur = conn.cursor()
	return cur

es = Elasticsearch([{'host':"10.110.0.106",'port':9200}])
TYPE = {"bbs":"type1","webo":"type1","zhihu":"type1","forum":"type1","wechat":"type1"}

keywordList = []
with open('keyword.txt','r+') as f:
	for k in f.readlines():
		k = k.strip()
		keywordList.append(k)

cur = defaultDatabase()

result = []
for entity_name in keywordList:
	try:
		rateList = []
		adContentList = []
		sql = 'select entity_name,ad_num from %s where entity_name="%s" order by date' % ("report_illegal_daily",entity_name)
		cur.execute(sql)
		dict = cur.fetchone()
		
		sql1 = 'select entity_name,return_rate from %s where entity_name="%s" and return_type=1' % ("return_rate_daily_more",entity_name)
		cur.execute(sql1)
		res = cur.fetchall()
		for each in res:
			rateList.append(each['return_rate'])

		sql2 = 'select entity_name,return_rate from %s where entity_name="%s"' % ("gw_rate_daily",entity_name)
		cur.execute(sql2)
		res1 = cur.fetchall()
		for each in res1:
			rateList.append(each['return_rate'])

		dict.update({'return_rate':rateList})



		for item in TYPE.items():
			index_name = item[0]
			type = item[1]
			query_body = {	"size":500,
							"query":{
								"bool":{
									"must":{"match":{"query_name":entity_name}},
									"should":[
										],
									"minimum_should_match":1
									}
								}
							}
			query_body['query']['bool']['should'].append({"match":{"ad123":1}})
			query_body['query']['bool']['should'].append({"match":{"ad123":2}})
			query_body['query']['bool']['should'].append({"match":{"ad123":3}})
			res = es.search(index=index_name, doc_type=type, body=query_body, request_timeout=100)
			hits = res['hits']['hits']
			if(len(hits)):
				for i in hits:
					if entity_name in i['_source']['query_name']:
						r = i['_source']
						adContentList.append(r)
		dict.update({'adContent':adContentList})
		result.append(dict)
	except Exception as e:
		print(e)

c = open('ffjz.csv','wb')
writer = csv.writer(c,delimiter=",")
KEYS = ['entity_name', 'ad_num', 'return_rate', 'adContent']
for line in result:
	csvrow = []
	for key in KEYS:
		csvrow.append(line[key])
	writer.writerow(csvrow)
c.close()

