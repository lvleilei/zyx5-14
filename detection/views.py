#!/usr/bin/env python
#encoding: utf-8

from flask import Flask, render_template, request, jsonify, Blueprint, send_from_directory, url_for, session
from economy.db import *
from . import detection
import codecs
import json
from economy.config import *
from pybloom import ScalableBloomFilter
import csv
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

@detection.route('/detect/')
def detect():
	fullnum = request.args.get('fullnum','')
	if session:
		username = session['username']
		role_id = session['role']
		uid = session['uid']
	else:
		username = ""
		role_id = ""
		uid = ""
	return render_template('detection/detection.html',username=username,role_id=role_id,uid=uid,fullnum=fullnum)

# 分页请求数据
@detection.route('/detectData/',methods=['POST','GET'])
def detect_data():
	date = int(request.args.get('date',''))
	operation_mode = int(request.args.get('operation_mode',''))
	illegal_type = int(request.args.get('illegal_type',''))
	entity_type = int(request.args.get('entity_type',''))
	warn_distribute = request.args.get('warn_distribute','')
	page_number = int(request.args.get('page_number',''))
	page_size = int(request.args.get('page_size',''))
	detectionCount = int(request.args.get('detectionCount',''))
	result = getDetectData(date,TABLE_ENTITY_LIST,TABLE_MONITOR,TABLE_GONGSHANG,RISK_LEVEL,ILLEGAL_SCORE,operation_mode,illegal_type,entity_type,warn_distribute,page_number,page_size,detectionCount)
	return json.dumps(result,ensure_ascii=False)

# 完整报表导出
@detection.route('/saveAllCsv/',methods=['POST','GET'])
def save_csv():
	# 新建csv文件
	now = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(int(time.time())))
	filename = 'economy/static/report/' + u'疑似非法集资预警记录:' + now + '.csv'
	c = codecs.open(filename,'a+','utf_8_sig')
	writer = csv.writer(c,delimiter=",")
	# 获取结果
	result = totalDetectDataFromBigTable(1,TABLE_REPORT_ILLEGAL,'all',0,0,'all','all',0,'all')
	# result = secondDetectFromBigTable(365,TABLE_REPORT_ILLEGAL,0,0,'all',0,0,'all','all',TABLE_LOGS,'all')	
	# 将illegal_type不同的两个实体合并
	b = ScalableBloomFilter(1000000,0.001)
	doubleId = []
	for dict in result:
		if not dict['entity_id'] in b:
			[b.add(dict['entity_id'])]
		else:
			doubleId.append(dict['entity_id'])
	for id in doubleId:
		num = 0
		illegalTypeList = []
		for dict in result:
			if dict['entity_id'] == id:
				num += 1
				illegalTypeList.append(dict['illegal_type'])
				dict.update({'illegal_type':illegalTypeList})
				if num > 1:
					result.remove(dict)
	# 将最早预警时间加入字典
	minDates = getMinDate1(TABLE_MONITOR,RISK_LEVEL,ILLEGAL_SCORE,ILLEGAL_TYPE,TABLE_REPORT_ILLEGAL)
	for each in result:
		each.update({'minDate':minDates[each['entity_id']]})
	# 处理结果
	handledResult = []
	for dict in result:
		riskReason = ""
		if dict['comment_rank'] > 75:
			riskReason += u"负面舆情多；" + "\n"
		if dict['suit_rank'] > 75:
			riskReason += u"诉讼记录多；" + "\n"
		if dict['ad_rank'] > 75:
			riskReason += u"煽动性广告多；" + "\n"
		if dict['return_rank'] > 75:
			riskReason += u"收益率过高；" + "\n"
		if dict['abnor_rank'] > 75:
			riskReason += u"经营异常多；" + "\n"
		if dict['promise_type'] == 1 or dict['promise_type'] == 2:
			riskReason += u"存在担保承诺；"
		if not riskReason:
			riskReason += u"暂无"
		if dict['risk_rank']:
			if dict['risk_rank'] == 0:
				risk_rank = u'无'
			elif dict['risk_rank'] == 1:
				risk_rank = u'小'
			elif dict['risk_rank'] == 2:
				risk_rank = u'大'
		else:
			risk_rank = u'不详'
		if dict['return_num']:
			return_num = str(dict['return_num'])+'%'
		else:
			return_num = u"不详"
		if int(dict['entity_type']) == 1:
			entity_type = u'平台'
		elif int(dict['entity_type']) == 2:
			entity_type = u'工司'
		elif int(dict['entity_type']) == 3:
			entity_type = u'项目'
		if int(dict['entity_source']) == 1:
			entity_source = u'网贷之家'
		elif int(dict['entity_source']) == 2:
			entity_source = u'人工导入'
		elif int(dict['entity_source']) == 3:
			entity_source = u'数据库'
		elif int(dict['entity_source']) == 4:
			entity_source = u'系统感知'
		if dict['return_rank']:
			return_rank = str(dict['return_rank'])+'%'
		else:
			return_rank = u"不详"
		if dict['ad_rank']:
			ad_rank = str(dict['ad_rank'])+'%'
		else:
			ad_rank = u"不详"
		if dict['comment_rank']:
			comment_rank = str(dict['comment_rank'])+'%'
		else:
			comment_rank = u"不详"
		if dict['suit_rank']:
			suit_rank = str(dict['suit_rank'])+'%'
		else:
			suit_rank = u"不详"
		if dict['abnor_rank']:
			abnor_rank = str(dict['abnor_rank'])+'%'
		else:
			abnor_rank = u"不详"

		# cur = defaultDatabase()
		# remarkList = []
		# sql100 = 'select remark from %s where entity_id=%d'%(TABLE_LOGS, dict['entity_id'])
		# cur.execute(sql100)
		# res = cur.fetchall()
		# if res:
		# 	for e in res:
		# 		remarkList.append(e['remark'])
		# 	remark = ''.join(remarkList)
		# else:
		# 	remark = ''


		handledDict = {u"实体id":dict['entity_id'], u"实体名称":dict['entity_name'], u"预警指数":dict['illegal_score'],\
						 u"此次预警时间":dict['date'], u"最早预警时间":dict['minDate'], u"预警理由":riskReason, u"集资模式":dict['fund_mode'],\
						  u"风险评级":risk_rank, u"业态类型":dict['operation_mode'], u"所属行业":dict['industry'], u"问题平台":dict['problem'],\
						   u"省份":dict['province'], u"城市":dict['city'], u"实体类别":entity_type, u"实体来源":entity_source,\
						    u"收益率":return_num, u"收益率大小所属分位点":return_rank, u"担保承诺":dict['promise_type'], u"煽动性广告数量":dict['ad_num'],\
						     u"煽动性广告数所属分位点":ad_rank, u"负面舆情数量":dict['comment_num'], u"负面舆情数所属分位点":comment_rank,\
						      u"诉讼记录数量":dict['suit_num'], u"诉讼记录数所属分位点":suit_rank, u"经营异常数量":dict['abnor_num'],\
						       u"经营异常数所属分位点":abnor_rank, u"赞成数":dict['support_num'], u"反对数":dict['against_num']}
		handledResult.append(handledDict)
	# 存表头
	NEWS_KEYS = [u"实体id", u"实体名称", u"预警指数", u"此次预警时间", u"最早预警时间",\
				 u"预警理由", u"集资模式", u"风险评级", u"业态类型", u"所属行业", u"问题平台",\
				  u"省份", u"城市", u"实体类别", u"实体来源", u"收益率", u"收益率大小所属分位点",\
				   u"担保承诺", u"煽动性广告数量", u"煽动性广告数所属分位点", u"负面舆情数量",\
				    u"负面舆情数所属分位点", u"诉讼记录数量", u"诉讼记录数所属分位点",\
				     u"经营异常数量", u"经营异常数所属分位点", u"赞成数", u"反对数"]
	writer.writerow(NEWS_KEYS)
	# 存数据
	for r in handledResult:
		csvrow = []
		for key in NEWS_KEYS:
			if key in r:
				csvrow.append(r[key])
		writer.writerow(csvrow)
	c.close()
	dict = {'status':filename}
	return json.dumps(dict,ensure_ascii=False)

# 已审核报表导出
@detection.route('/saveCheckedCsv/',methods=['POST','GET'])
def save_checked_csv():
	# 新建csv文件
	now = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(int(time.time())))
	filename = 'economy/static/report/' + u'已预警报表:' + now + '.csv'
	c = codecs.open(filename,'a+','utf_8_sig')
	writer = csv.writer(c,delimiter=",")
	# 获取结果
	list = request.get_json()
	date_id = {}
	bDates = ScalableBloomFilter(100000,0.0001)
	for dict in list:
		if not dict['date'] in bDates:
			[bDates.add(dict['date'])]
			date_id.update({dict['date']:[]})
	for dict in list:
		date_id[dict['date']].append(str(dict['id']))
	result = getCheckedCsvData(TABLE_REPORT_ILLEGAL, date_id)
	# 处理结果
	handledResult = []
	for dict in result:
		if dict['return_num']:
			return_num = str(dict['return_num'])+'%'
		else:
			return_num = u"不详"
		riskPoint = ""
		if dict['comment_rank'] > 75:
			riskPoint += u"负面舆情多：" + str(dict['comment_num']) + u"条，高于" + str(dict['comment_rank']) + u"%的监测对象；" + "\n"
		if dict['suit_rank'] > 75:
			riskPoint += u"诉讼记录多：" + str(dict['suit_num']) + u"条，高于" + str(dict['suit_rank']) + u"%的监测对象；" + "\n"
		if dict['ad_rank'] > 75:
			riskPoint += u"煽动性广告多：" + str(dict['ad_num']) + u"条，高于" + str(dict['ad_rank']) + u"%的监测对象；" + "\n"
		return_rank = 100 - dict['return_rank']
		if return_rank == 0:
			return_rank = 10
		return_rank = str(return_rank) + "%"
		if dict['return_rank'] > 75:
			riskPoint += u"收益率过高：" + str(dict['return_num']) + u"%，处于所有监测对象收益率排序的前" + return_rank + "；" + "\n"
		if dict['abnor_rank'] > 75:
			riskPoint += u"经营异常多：" + str(dict['abnor_num']) + u"条，高于" + str(dict['abnor_rank']) + u"%的监测对象；" + "\n"
		if dict['promise_type'] == 1:
			riskPoint += u"存在担保承诺：本息类担保"
		elif dict['promise_type'] == 2:
			riskPoint += u"存在担保承诺：非本息类担保"
		if not riskPoint:
			riskPoint += u"暂无"
		district = u"地区：" + dict['province'] + dict['city'] + dict['district'] + "\n" + "人数：不详" + "\n" + "金额：不详" + "\n" + "是否立案：不详"
		riskPointSummary = ""
		if dict['comment_rank'] > 75:
			riskPointSummary += u"负面舆情多；" + "\n"
		if dict['suit_rank'] > 75:
			riskPointSummary += u"诉讼记录多；" + "\n"
		if dict['ad_rank'] > 75:
			riskPointSummary += u"煽动性广告多；" + "\n"
		if dict['return_rank'] > 75:
			riskPointSummary += u"收益率过高；" + "\n"
		if dict['abnor_rank'] > 75:
			riskPointSummary += u"经营异常多；" + "\n"
		if dict['promise_type'] == 1 or dict['promise_type'] == 2:
			riskPointSummary += u"存在担保承诺；"
		if not riskPointSummary:
			riskPointSummary += u"暂无"
		try:
			capital = str(dict['capital'])
		except:
			capital = ""
		if dict['set_time']:
			set_time = str(dict['set_time'])
		else:
			set_time = ""
		if dict['legal_person']:
			legal_person = str(dict['legal_person'])
		else:
			legal_person = ""
		gongshangDetail = u"注册资本：" + capital + '\n' + u"注册日期：" + set_time + '\n' + u"法人代表：" + legal_person

		handledDict = {u'平台名称':dict['entity_name'], u'企业名称':dict['firm_name'], u'行业分类':dict['industry'],\
						 u'集资模式':dict['fund_mode'], u'集资手段':u'不详', u'年化收益率':return_num, u'非法集资风险点':riskPoint,\
						  u'非法集资涉案情况':district, u'非法集资风险点归纳':riskPointSummary, u'工商情况':gongshangDetail,\
						   u'备注':'', u'网站':dict['website'], u'其他':''}
		handledResult.append(handledDict)
	# 存表头
	NEWS_KEYS = [u'平台名称', u'企业名称', u'行业分类', u'集资模式', u'集资手段', u'年化收益率', u'非法集资风险点',\
				 u'非法集资涉案情况', u'非法集资风险点归纳', u'工商情况', u'备注', u'网站', u'其他']
	writer.writerow(NEWS_KEYS)
	# 存数据
	for r in handledResult:
		csvrow = []
		for key in NEWS_KEYS:
			if key in r:
				csvrow.append(r[key])
		writer.writerow(csvrow)
	c.close()
	dict = {'status':filename}
	return json.dumps(dict,ensure_ascii=False)

# 从六个表中取出数据(第一屏)
@detection.route('/totalDetectDataOld/',methods=['POST','GET'])
def total_detect_data():
	b = ScalableBloomFilter(1000000,0.001)
	date = int(request.args.get('date',''))
	operation_mode = request.args.get('operation_mode','')
	illegal_type = int(request.args.get('illegal_type',''))
	entity_type = int(request.args.get('entity_type',''))
	warn_distribute = request.args.get('warn_distribute','')
	problem = request.args.get('problem','')
	newEntity = int(request.args.get('newEntity',''))
	checked = int(request.args.get('checked',''))
	result = totalDetectData(date,TABLE_ENTITY_LIST,TABLE_MONITOR,TABLE_GONGSHANG,RISK_LEVEL,ILLEGAL_SCORE,operation_mode,illegal_type,entity_type,warn_distribute,problem,TABLE_INDEX_QUANTILE,TABLE_GUARANTEE_PROMISE,checked)
	doubleId = []
	for dict in result:
		if not dict['id'] in b:
			[b.add(dict['id'])]
		else:
			doubleId.append(dict['id'])
	for id in doubleId:
		num = 0
		illegalTypeList = []
		for dict in result:
			if dict['id'] == id:
				num += 1
				illegalTypeList.append(dict['illegal_type'])
				dict.update({'illegal_type':illegalTypeList})
				if num > 1:
					result.remove(dict)
	if newEntity:
		bb = ScalableBloomFilter(1000000,0.001)
		newResult = []
		minDates = getMinDate1(TABLE_MONITOR,RISK_LEVEL,ILLEGAL_SCORE,ILLEGAL_TYPE,TABLE_REPORT_ILLEGAL)
		row_monitor_date = datetime.strptime(monitor_date,'%Y-%m-%d')
		for i,k in minDates.items():
			dateTime = datetime.strptime(k,'%Y-%m-%d')
			dValue = int((row_monitor_date-dateTime).total_seconds())/86400
			if dValue < date:
				[bb.add(i)]
		for dict in result:
			if dict['id'] in bb:
				newResult.append(dict)
		return json.dumps(newResult,ensure_ascii=False)
	return json.dumps(result,ensure_ascii=False)

# 从大表（report_illegal_daily）中取出数据(第一屏)
@detection.route('/totalDetectData/',methods=['POST','GET'])
def total_detect_data_test():
	b = ScalableBloomFilter(1000000,0.001)
	date = int(request.args.get('date',''))
	operation_mode = request.args.get('operation_mode','')	#多选
	illegal_type = int(request.args.get('illegal_type',''))
	entity_type = int(request.args.get('entity_type',''))
	warn_distribute = request.args.get('warn_distribute','')	#多选
	problem = request.args.get('problem','')	#多选
	newEntity = int(request.args.get('newEntity',''))
	checked = int(request.args.get('checked',''))
	fund_mode = request.args.get('fund_mode','')
	result = totalDetectDataFromBigTable(date,TABLE_REPORT_ILLEGAL,operation_mode,illegal_type,entity_type,warn_distribute,problem,checked,fund_mode)
	# 将illegal_type不同的两个实体合并
	doubleId = []
	for dict in result:
		if not dict['entity_id'] in b:
			[b.add(dict['entity_id'])]
		else:
			doubleId.append(dict['entity_id'])
	for id in doubleId:
		num = 0
		illegalTypeList = []
		for dict in result:
			if dict['entity_id'] == id:
				num += 1
				illegalTypeList.append(dict['illegal_type'])
				dict.update({'illegal_type':illegalTypeList})
				if num > 1:
					result.remove(dict)
	# 筛选新增实体
	if newEntity:
		bb = ScalableBloomFilter(1000000,0.001)
		newResult = []
		minDates = getMinDate1(TABLE_MONITOR,RISK_LEVEL,ILLEGAL_SCORE,ILLEGAL_TYPE,TABLE_REPORT_ILLEGAL)
		row_monitor_date = datetime.strptime(monitor_date,'%Y-%m-%d')
		for i,k in minDates.items():
			dateTime = datetime.strptime(k,'%Y-%m-%d')
			dValue = int((row_monitor_date-dateTime).total_seconds())/86400
			if dValue < date and dValue >= 0:
				[bb.add(i)]
		for dict in result:
			if dict['entity_id'] in bb:
				newResult.append(dict)
		return json.dumps(newResult,ensure_ascii=False)
	return json.dumps(result,ensure_ascii=False)

# 已审核赞成大于零且无反对的实体数据(第二屏)
@detection.route('/secondDetectDataOld/',methods=['POST','GET'])
def second_detect_data():
	b = ScalableBloomFilter(1000000,0.001)
	date = int(request.args.get('date',''))
	operation_mode = request.args.get('operation_mode','')
	illegal_type = int(request.args.get('illegal_type',''))
	entity_type = int(request.args.get('entity_type',''))
	warn_distribute = request.args.get('warn_distribute','')
	problem = request.args.get('problem','')
	newEntity = int(request.args.get('newEntity',''))
	result = secondDetectData(date,TABLE_ENTITY_LIST,TABLE_MONITOR,TABLE_GONGSHANG,RISK_LEVEL,ILLEGAL_SCORE,operation_mode,illegal_type,entity_type,warn_distribute,problem,TABLE_INDEX_QUANTILE,TABLE_GUARANTEE_PROMISE,TABLE_LOGS)	
	doubleId = []
	for dict in result:
		if not dict['id'] in b:
			[b.add(dict['id'])]
		else:
			doubleId.append(dict['id'])
	for id in doubleId:
		num = 0
		illegalTypeList = []
		for dict in result:
			if dict['id'] == id:
				num += 1
				illegalTypeList.append(dict['illegal_type'])
				dict.update({'illegal_type':illegalTypeList})
				if num > 1:
					result.remove(dict)
	if newEntity:
		bb = ScalableBloomFilter(1000000,0.001)
		newResult = []
		minDates = getMinDate1(TABLE_MONITOR,RISK_LEVEL,ILLEGAL_SCORE,ILLEGAL_TYPE,TABLE_REPORT_ILLEGAL)
		row_monitor_date = datetime.strptime(monitor_date,'%Y-%m-%d')
		for i,k in minDates.items():
			dateTime = datetime.strptime(k,'%Y-%m-%d')
			dValue = int((row_monitor_date-dateTime).total_seconds())/86400
			if dValue < date:
				[bb.add(i)]
		for dict in result:
			if dict['id'] in bb:
				newResult.append(dict)
		return json.dumps(newResult,ensure_ascii=False)
	try:
		result.sort(key=lambda x:x['datetime'],reverse=True)
	except:
		pass
	return json.dumps(result,ensure_ascii=False)

# 已审核赞成大于零且无反对的实体数据(第二屏)（report_illegal_daily）
@detection.route('/secondDetectData/',methods=['POST','GET'])
def second_detect_data_from_bigtable():
	b = ScalableBloomFilter(1000000,0.001)
	date = int(request.args.get('date',''))
	operation_mode = request.args.get('operation_mode','')
	illegal_type = int(request.args.get('illegal_type',''))
	entity_type = int(request.args.get('entity_type',''))
	warn_distribute = request.args.get('warn_distribute','')
	problem = request.args.get('problem','')
	newEntity = int(request.args.get('newEntity',''))
	fund_mode = request.args.get('fund_mode','')
	result = secondDetectFromBigTable(date,TABLE_REPORT_ILLEGAL,RISK_LEVEL,ILLEGAL_SCORE,operation_mode,illegal_type,entity_type,warn_distribute,problem,TABLE_LOGS,fund_mode)	
	doubleId = []
	for dict in result:
		if not dict['entity_id'] in b:
			[b.add(dict['entity_id'])]
		else:
			doubleId.append(dict['entity_id'])
	for id in doubleId:
		num = 0
		illegalTypeList = []
		for dict in result:
			if dict['entity_id'] == id:
				num += 1
				illegalTypeList.append(dict['illegal_type'])
				dict.update({'illegal_type':illegalTypeList})
				if num > 1:
					result.remove(dict)
	if newEntity:
		bb = ScalableBloomFilter(1000000,0.001)
		newResult = []
		minDates = getMinDate1(TABLE_MONITOR,RISK_LEVEL,ILLEGAL_SCORE,ILLEGAL_TYPE,TABLE_REPORT_ILLEGAL)
		row_monitor_date = datetime.strptime(monitor_date,'%Y-%m-%d')
		for i,k in minDates.items():
			dateTime = datetime.strptime(k,'%Y-%m-%d')
			dValue = int((row_monitor_date-dateTime).total_seconds())/86400
			if dValue < date and dValue >= 0:
				[bb.add(i)]
		for dict in result:
			if dict['entity_id'] in bb:
				newResult.append(dict)
			dict.update({'id':dict['entity_id']})
		return json.dumps(newResult,ensure_ascii=False)
	try:
		result.sort(key=lambda x:x['datetime'],reverse=True)
	except:
		pass
	# 前端传的是id，防止报错，加上id
	for dict in result:
		dict.update({'id':dict['entity_id']})
	return json.dumps(result,ensure_ascii=False)

# 已审核被反对的实体数据(第三屏)
@detection.route('/againstDetectDataOld/',methods=['POST','GET'])
def against_detect_data():
	b = ScalableBloomFilter(1000000,0.001)
	date = int(request.args.get('date',''))
	operation_mode = request.args.get('operation_mode','')
	illegal_type = int(request.args.get('illegal_type',''))
	entity_type = int(request.args.get('entity_type',''))
	warn_distribute = request.args.get('warn_distribute','')
	problem = request.args.get('problem','')
	newEntity = int(request.args.get('newEntity',''))
	result = againstDetectData(date,TABLE_ENTITY_LIST,TABLE_MONITOR,TABLE_GONGSHANG,RISK_LEVEL,ILLEGAL_SCORE,operation_mode,illegal_type,entity_type,warn_distribute,problem,TABLE_INDEX_QUANTILE,TABLE_GUARANTEE_PROMISE,TABLE_LOGS)	
	# 合并相同数据
	doubleId = []
	for dict in result:
		if not dict['id'] in b:
			[b.add(dict['id'])]
		else:
			doubleId.append(dict['id'])
	for id in doubleId:
		num = 0
		illegalTypeList = []
		for dict in result:
			if dict['id'] == id:
				num += 1
				illegalTypeList.append(dict['illegal_type'])
				dict.update({'illegal_type':illegalTypeList})
				if num > 1:
					result.remove(dict)
	# 筛选新增实体
	if newEntity:
		bb = ScalableBloomFilter(1000000,0.001)
		newResult = []
		minDates = getMinDate1(TABLE_MONITOR,RISK_LEVEL,ILLEGAL_SCORE,ILLEGAL_TYPE,TABLE_REPORT_ILLEGAL)
		row_monitor_date = datetime.strptime(monitor_date,'%Y-%m-%d')
		for i,k in minDates.items():
			dateTime = datetime.strptime(k,'%Y-%m-%d')
			dValue = int((row_monitor_date-dateTime).total_seconds())/86400
			if dValue < date:
				[bb.add(i)]
		for dict in result:
			if dict['id'] in bb:
				newResult.append(dict)
		return json.dumps(newResult,ensure_ascii=False)
	try:
		result.sort(key=lambda x:x['datetime'],reverse=True)
	except:
		pass
	return json.dumps(result,ensure_ascii=False)

# 已审核被反对的实体数据(第三屏)（report_illegal_daily）
@detection.route('/againstDetectData/',methods=['POST','GET'])
def against_detect_data_from_bigtable():
	b = ScalableBloomFilter(1000000,0.001)
	date = int(request.args.get('date',''))
	operation_mode = request.args.get('operation_mode','')
	illegal_type = int(request.args.get('illegal_type',''))
	entity_type = int(request.args.get('entity_type',''))
	warn_distribute = request.args.get('warn_distribute','')
	problem = request.args.get('problem','')
	newEntity = int(request.args.get('newEntity',''))
	fund_mode = request.args.get('fund_mode','')
	result = againstDetectDataFromBigTable(date,TABLE_REPORT_ILLEGAL,RISK_LEVEL,ILLEGAL_SCORE,operation_mode,illegal_type,entity_type,warn_distribute,problem,TABLE_LOGS,fund_mode)	
	# 合并相同数据
	doubleId = []
	for dict in result:
		if not dict['entity_id'] in b:
			[b.add(dict['entity_id'])]
		else:
			doubleId.append(dict['entity_id'])
	for id in doubleId:
		num = 0
		illegalTypeList = []
		for dict in result:
			if dict['entity_id'] == id:
				num += 1
				illegalTypeList.append(dict['illegal_type'])
				dict.update({'illegal_type':illegalTypeList})
				if num > 1:
					result.remove(dict)
	# 筛选新增实体
	if newEntity:
		bb = ScalableBloomFilter(1000000,0.001)
		newResult = []
		minDates = getMinDate1(TABLE_MONITOR,RISK_LEVEL,ILLEGAL_SCORE,ILLEGAL_TYPE,TABLE_REPORT_ILLEGAL)
		row_monitor_date = datetime.strptime(monitor_date,'%Y-%m-%d')
		for i,k in minDates.items():
			dateTime = datetime.strptime(k,'%Y-%m-%d')
			dValue = int((row_monitor_date-dateTime).total_seconds())/86400
			if dValue < date and dValue >= 0:
				[bb.add(i)]
		for dict in result:
			if dict['entity_id'] in bb:
				newResult.append(dict)
		# 前端传的是id，防止报错，加上id
		for dict in result:
			dict.update({'id':dict['entity_id']})
		return json.dumps(newResult,ensure_ascii=False)
	try:
		result.sort(key=lambda x:x['datetime'],reverse=True)
	except:
		pass
	# 前端传的是id，防止报错，加上id
	for dict in result:
		dict.update({'id':dict['entity_id']})
	return json.dumps(result,ensure_ascii=False)

# 停止预警的实体数据(第四屏)
@detection.route('/thirdDetectDataOld/',methods=['POST','GET'])
def third_detect_data():
	b = ScalableBloomFilter(1000000,0.001)
	date = int(request.args.get('date',''))
	operation_mode = request.args.get('operation_mode','')
	illegal_type = int(request.args.get('illegal_type',''))
	entity_type = int(request.args.get('entity_type',''))
	warn_distribute = request.args.get('warn_distribute','')
	problem = request.args.get('problem','')
	newEntity = int(request.args.get('newEntity',''))
	checked = int(request.args.get('checked',''))
	result = thirdDetectData(date,TABLE_ENTITY_LIST,TABLE_MONITOR,TABLE_GONGSHANG,RISK_LEVEL,ILLEGAL_SCORE,operation_mode,illegal_type,entity_type,warn_distribute,problem,TABLE_INDEX_QUANTILE,TABLE_GUARANTEE_PROMISE,checked)
	doubleId = []
	for dict in result:
		if not dict['id'] in b:
			[b.add(dict['id'])]
		else:
			doubleId.append(dict['id'])
	for id in doubleId:
		num = 0
		illegalTypeList = []
		for dict in result:
			if dict['id'] == id:
				num += 1
				illegalTypeList.append(dict['illegal_type'])
				dict.update({'illegal_type':illegalTypeList})
				if num > 1:
					result.remove(dict)
	if newEntity:
		bb = ScalableBloomFilter(1000000,0.001)
		newResult = []
		minDates = getMinDate(TABLE_MONITOR,RISK_LEVEL,ILLEGAL_SCORE,ILLEGAL_TYPE,TABLE_REPORT_ILLEGAL)
		row_monitor_date = datetime.strptime(monitor_date,'%Y-%m-%d')
		for i,k in minDates.items():
			dateTime = datetime.strptime(k,'%Y-%m-%d')
			dValue = int((row_monitor_date-dateTime).total_seconds())/86400
			if dValue < date:
				[bb.add(i)]
		for dict in result:
			if dict['id'] in bb:
				newResult.append(dict)
		return json.dumps(newResult,ensure_ascii=False)
	return json.dumps(result,ensure_ascii=False)

# 停止预警的实体数据(第四屏)（report_illegal_daily）
@detection.route('/thirdDetectData/',methods=['POST','GET'])
def third_detect_data_from_bigtable():
	b = ScalableBloomFilter(1000000,0.001)
	date = int(request.args.get('date',''))
	operation_mode = request.args.get('operation_mode','')
	illegal_type = int(request.args.get('illegal_type',''))
	entity_type = int(request.args.get('entity_type',''))
	warn_distribute = request.args.get('warn_distribute','')
	problem = request.args.get('problem','')
	newEntity = int(request.args.get('newEntity',''))
	checked = int(request.args.get('checked',''))
	fund_mode = request.args.get('fund_mode','')
	result = thirdDetectDataFromBigTable(date,TABLE_REPORT_ILLEGAL,RISK_LEVEL,ILLEGAL_SCORE,operation_mode,illegal_type,entity_type,warn_distribute,problem,checked,fund_mode)
	doubleId = []
	for dict in result:
		if not dict['entity_id'] in b:
			[b.add(dict['entity_id'])]
		else:
			doubleId.append(dict['entity_id'])
	for id in doubleId:
		num = 0
		illegalTypeList = []
		for dict in result:
			if dict['entity_id'] == id:
				num += 1
				illegalTypeList.append(dict['illegal_type'])
				dict.update({'illegal_type':illegalTypeList})
				if num > 1:
					result.remove(dict)
	if newEntity:
		bb = ScalableBloomFilter(1000000,0.001)
		newResult = []
		minDates = thirdNewWarnEntity(TABLE_ENTITY_LIST, TABLE_MONITOR, RISK_LEVEL, ILLEGAL_SCORE, ILLEGAL_TYPE, TABLE_REPORT_ILLEGAL)
		row_monitor_date = datetime.strptime(monitor_date,'%Y-%m-%d')
		for i,k in minDates.items():
			dateTime = datetime.strptime(k,'%Y-%m-%d')
			dValue = int((row_monitor_date-dateTime).total_seconds())/86400
			if dValue < date and dValue >= 0:
				[bb.add(i)]
		for dict in result:
			if dict['entity_id'] in bb:
				newResult.append(dict)
		# 前端传的是id，防止报错，加上id
		for dict in result:
			dict.update({'id':dict['entity_id']})
		return json.dumps(newResult,ensure_ascii=False)
	# 前端传的是id，防止报错，加上id
	for dict in result:
		dict.update({'id':dict['entity_id']})
	return json.dumps(result,ensure_ascii=False)


@detection.route('/detectionCount/',methods=['POST','GET'])
def detection_count():
	date = int(request.args.get('date',''))
	operation_mode = int(request.args.get('operation_mode',''))
	illegal_type = int(request.args.get('illegal_type',''))
	entity_type = int(request.args.get('entity_type',''))
	warn_distribute = request.args.get('warn_distribute','')
	result = detectionCount(date,TABLE_ENTITY_LIST,TABLE_MONITOR,TABLE_GONGSHANG,RISK_LEVEL,ILLEGAL_SCORE,operation_mode,illegal_type,entity_type,warn_distribute)
	return json.dumps(result,ensure_ascii=False)

@detection.route('/detectionResultCheck/',methods=['POST'])
def detection_result_check():
	data = request.get_json()
	print(data)
	entity_id = int(data['entity_id'])
	date = data['date']
	type = int(data['type'])
	uid = int(data['uid'])
	entity_name = data['entity_name']
	remark = data['remark']
	oldValue = data['oldValue']
	username = data['username']
	risk_rank = int(data['risk_rank'])
	industry = data['industry']
	fund_mode = data['fund_mode']
	result = detectionResultCheck(TABLE_ENTITY_LIST, entity_id, date, type, uid, entity_name, TABLE_LOGS, remark, oldValue, username, risk_rank, industry, fund_mode, TABLE_CHECK_LOGS, TABLE_REPORT_ILLEGAL)
	return json.dumps(result,ensure_ascii=False)

@detection.route('/getResultRemark/')
def get_result_remark():
	entity_id = int(request.args.get('entity_id',''))
	uid = int(request.args.get('uid',''))
	result = getResultRemark(TABLE_LOGS, entity_id, uid)
	return json.dumps(result,ensure_ascii=False)

@detection.route('/detectionResultRemark/')
def detection_result_remark():
	entity_id = int(request.args.get('entity_id',''))
	result = detectionResultRemark(TABLE_LOGS, entity_id, TABLE_ENTITY_LIST)
	return json.dumps(result,ensure_ascii=False)

@detection.route('/detectRank/')
def detect_rank():
	date = request.args.get('date','')
	entity_type = int(request.args.get('entity_type',''))
	result = getDetectRank(TABLE_MONITOR, date, RISK_LEVEL, ILLEGAL_SCORE, entity_type, ILLEGAL_TYPE)
	result.sort(key=lambda x:x['max(illegal_score)'],reverse=True)
	return json.dumps(result[0:20],ensure_ascii=False)

@detection.route('/detectDistribute/')
def detect_distribute():
	date = request.args.get('date','')
	result = getDetectDistribute(date,TABLE_MONITOR,TABLE_GONGSHANG,RISK_LEVEL,ILLEGAL_SCORE)
	result.sort(key=lambda x:x['sum'],reverse=True)
	return json.dumps(result,ensure_ascii=False)

@detection.route('/warnType/')
def warn_type():
	date = int(request.args.get('date',''))
	illegal_type = int(request.args.get('illegal_type',''))
	entity_type = int(request.args.get('entity_type',''))
	operation_mode = request.args.get('operation_mode','')
	warn_distribute = request.args.get('warn_distribute','')
	result = getWarnType(TABLE_MONITOR, TABLE_GONGSHANG, RISK_LEVEL, ILLEGAL_SCORE, date, illegal_type, entity_type, operation_mode, warn_distribute,TABLE_ENTITY_LIST)
	return json.dumps(result,ensure_ascii=False)


@detection.route('/OperationModeBox/')
def operation_mode_box():
	result = operationModeBox(TABLE_OPERATION_LIST)
	return json.dumps(result,ensure_ascii=False)

@detection.route('/IllegalTypeBox/')
def illegal_type_box():
	result = illegalTypeBox(TABLE_ILLEGAL_LIST)
	return json.dumps(result,ensure_ascii=False)

@detection.route('/ProblemBox/')
def problem_box():
	result = problemBox(TABLE_PROBLEM_LIST)
	return json.dumps(result,ensure_ascii=False)

@detection.route('/TimeDistribute/')
def time_Distribute():
	date = int(request.args.get('date',''))
	illegal_type = int(request.args.get('illegal_type',''))
	entity_type = int(request.args.get('entity_type',''))
	operation_mode = request.args.get('operation_mode','')
	warn_distribute = request.args.get('warn_distribute','')
	result = GetTimeDistribute(TABLE_MONITOR, TABLE_GONGSHANG, RISK_LEVEL, ILLEGAL_SCORE, date, illegal_type, entity_type, operation_mode, warn_distribute,TABLE_ENTITY_LIST, ILLEGAL_TYPE)
	return json.dumps(result,ensure_ascii=False)

@detection.route('/warnCount/')
def warn_count():
	result = getWarnCount(TABLE_MONITOR, RISK_LEVEL,ILLEGAL_SCORE)
	return json.dumps(result,ensure_ascii=False)

#第一屏预警数（正在监测）
@detection.route('/WarnEntityCount/')
def warn_entity_count():
	result = getWarnEntityCount(TABLE_REPORT_ILLEGAL, ILLEGAL_SCORE, TABLE_ENTITY_LIST)
	return json.dumps(result,ensure_ascii=False)

#第二屏预警数（已审核，赞成大于零且无反对）
@detection.route('/secondWarnEntityCount/')
def second_warn_entity_count():
	result = getSecondWarnEntityCount(TABLE_REPORT_ILLEGAL, RISK_LEVEL, ILLEGAL_SCORE)
	return json.dumps(result,ensure_ascii=False)

#第三屏预警数（已审核，且被反对）
@detection.route('/againstWarnEntityCount/')
def against_warn_entity_count():
	result = getAgainstWarnEntityCount(TABLE_REPORT_ILLEGAL, RISK_LEVEL, ILLEGAL_SCORE)
	return json.dumps(result,ensure_ascii=False)

#第四屏预警数（已停止监测）
@detection.route('/thirdWarnEntityCount/')
def third_warn_entity_count():
	result = getThirdWarnEntityCount(TABLE_REPORT_ILLEGAL, RISK_LEVEL, ILLEGAL_SCORE)
	return json.dumps(result,ensure_ascii=False)

@detection.route('/secondWarnCount/')
def second_warn_count():
	result = getSecondWarnCount(TABLE_MONITOR, TABLE_ENTITY_LIST, RISK_LEVEL,ILLEGAL_SCORE)
	return json.dumps(result,ensure_ascii=False)

@detection.route('/minDate/')
def min_date():
	result = getMinDate(TABLE_MONITOR,RISK_LEVEL,ILLEGAL_SCORE,ILLEGAL_TYPE,TABLE_REPORT_ILLEGAL)
	return json.dumps(result,ensure_ascii=False)

#第一屏新增预警数（正在监测）
@detection.route('/newWarnEntity/')
def new_warn_entity():
	#minDates = getMinDate(TABLE_MONITOR,RISK_LEVEL,ILLEGAL_SCORE)
	minDates = getMinDate1(TABLE_MONITOR,RISK_LEVEL,ILLEGAL_SCORE,ILLEGAL_TYPE,TABLE_REPORT_ILLEGAL)
	row_monitor_date = datetime.strptime(monitor_date,'%Y-%m-%d')
	ago7 = []
	ago30 = []
	ago90 = []
	for i,k in minDates.items():
		dateTime = datetime.strptime(k,'%Y-%m-%d')
		dValue = int((row_monitor_date-dateTime).total_seconds())/86400
		if dValue < 7 and dValue >= 0:
			ago7.append(i)
		if dValue < 30 and dValue >= 0:
			ago30.append(i)
		if dValue < 90 and dValue >= 0:
			ago90.append(i)
	result = {'count7':len(ago7),'count30':len(ago30),'count90':len(ago90)}
	return json.dumps(result,ensure_ascii=False)

#第四屏新增预警数（已停止监测）
@detection.route('/thirdNewWarnEntity/')
def third_new_warn_entity():
	minDates = thirdNewWarnEntity(TABLE_ENTITY_LIST, TABLE_MONITOR, RISK_LEVEL, ILLEGAL_SCORE, ILLEGAL_TYPE, TABLE_REPORT_ILLEGAL)
	row_monitor_date = datetime.strptime(monitor_date,'%Y-%m-%d')
	ago7 = []
	ago30 = []
	ago90 = []
	for i,k in minDates.items():
		dateTime = datetime.strptime(k,'%Y-%m-%d')
		dValue = int((row_monitor_date-dateTime).total_seconds())/86400
		if dValue < 7 and dValue >= 0:
			ago7.append(i)
		if dValue < 30 and dValue >= 0:
			ago30.append(i)
		if dValue < 90 and dValue >= 0:
			ago90.append(i)
	result = {'count7':len(ago7),'count30':len(ago30),'count90':len(ago90)}
	return json.dumps(result,ensure_ascii=False)
	
#第二屏新增预警数（已审核，赞成大于零且无反对）
@detection.route('/secondNewWarnEntity/')
def second_new_warn_entity():
	minDates = getMinDate1(TABLE_MONITOR, RISK_LEVEL, ILLEGAL_SCORE,ILLEGAL_TYPE,TABLE_REPORT_ILLEGAL)
	row_monitor_date = datetime.strptime(monitor_date,'%Y-%m-%d')
	b7 = ScalableBloomFilter(100000,0.001)
	b30 = ScalableBloomFilter(100000,0.001)
	b90 = ScalableBloomFilter(100000,0.001)
	for i,k in minDates.items():
		dateTime = datetime.strptime(k,'%Y-%m-%d')
		dValue = int((row_monitor_date-dateTime).total_seconds())/86400
		if dValue < 7 and dValue >= 0:
			[b7.add(i)]
		if dValue < 30 and dValue >= 0:
			[b30.add(i)]
		if dValue < 90 and dValue >= 0:
			[b90.add(i)]
	result90 = secondDetectFromBigTable(90,TABLE_REPORT_ILLEGAL,RISK_LEVEL,ILLEGAL_SCORE,'all',0,0,'all','all',TABLE_LOGS,'all')	
	count7 = 0
	count30 = 0
	count90 = 0
	resultIds = []
	for each in result90:
		if not each['entity_id'] in resultIds:
			resultIds.append(each['entity_id'])
	for id in resultIds:
		if id in b7:
			count7 += 1
		if id in b30:
			count30 += 1
		if id in b90:
			count90 += 1
	result = {'count7':count7, 'count30':count30, 'count90':count90}
	return json.dumps(result,ensure_ascii=False)
	
#第三屏新增预警数（已审核，且被反对）
@detection.route('/againstNewWarnEntity/')
def against_new_warn_entity():
	minDates = getMinDate1(TABLE_MONITOR, RISK_LEVEL, ILLEGAL_SCORE,ILLEGAL_TYPE,TABLE_REPORT_ILLEGAL)
	row_monitor_date = datetime.strptime(monitor_date,'%Y-%m-%d')
	b7 = ScalableBloomFilter(100000,0.001)
	b30 = ScalableBloomFilter(100000,0.001)
	b90 = ScalableBloomFilter(100000,0.001)
	for i,k in minDates.items():
		dateTime = datetime.strptime(k,'%Y-%m-%d')
		dValue = int((row_monitor_date-dateTime).total_seconds())/86400
		if dValue < 7 and dValue >= 0:
			[b7.add(i)]
		if dValue < 30 and dValue >= 0:
			[b30.add(i)]
		if dValue < 90 and dValue >= 0:
			[b90.add(i)]
	# result90 = againstDetectData(90,TABLE_ENTITY_LIST,TABLE_MONITOR,TABLE_GONGSHANG,RISK_LEVEL,ILLEGAL_SCORE,'all',0,0,'all','all',TABLE_INDEX_QUANTILE,TABLE_GUARANTEE_PROMISE,TABLE_LOGS)	
	result90 = againstDetectDataFromBigTable(90,TABLE_REPORT_ILLEGAL,RISK_LEVEL,ILLEGAL_SCORE,'all',0,0,'all','all',TABLE_LOGS,'all')	
	count7 = 0
	count30 = 0
	count90 = 0
	resultIds = []
	for each in result90:
		if not each['entity_id'] in resultIds:
			resultIds.append(each['entity_id'])
	for id in resultIds:
		if id in b7:
			count7 += 1
		if id in b30:
			count30 += 1
		if id in b90:
			count90 += 1
	result = {'count7':count7, 'count30':count30, 'count90':count90}
	return json.dumps(result,ensure_ascii=False)


@detection.route('/addIndustry/')
def add_industry():
	industry = request.args.get('industry','')
	uid = int(request.args.get('uid',''))
	username = request.args.get('username','')
	result = addIndustry(TABLE_INDUSTRY_LIST, TABLE_LOGS, industry, uid, username)
	return json.dumps(result,ensure_ascii=False)


@detection.route('/addClass1Industry/')
def add_class1_industry():
	industry = request.args.get('industry','')
	uid = int(request.args.get('uid',''))
	username = request.args.get('username','')
	result = addClass1Industry(TABLE_INDUSTRY_LIST, industry, TABLE_LOGS, uid, username)
	return json.dumps(result,ensure_ascii=False)

@detection.route('/addClass2Industry/')
def add_class2_industry():
	industry = request.args.get('industry','')
	class_id = request.args.get('class_id','')
	uid = int(request.args.get('uid',''))
	username = request.args.get('username','')
	result = addClass2Industry(TABLE_INDUSTRY_LIST, industry, class_id, TABLE_LOGS, uid, username)
	return json.dumps(result,ensure_ascii=False)


@detection.route('/addFundmode/')
def add_fundmode():
	fund_mode = request.args.get('fund_mode','')
	uid = int(request.args.get('uid',''))
	username = request.args.get('username','')
	result = addFundmode(TABLE_FUNDMODE_LIST, TABLE_LOGS, fund_mode, uid, username)
	return json.dumps(result,ensure_ascii=False)

@detection.route('/IndustryBox/')
def industry_box():
	result = industryBox(TABLE_INDUSTRY_LIST)
	results = []
	class1_list = []
	dict = {}
	# 给所有一级行业建立一个空列表
	for each in result:
		if not re.findall(re.compile('\d+'),each['class_id']):
			class1_list.append(each['class_id'])
	for each in class1_list:
		dict.update({each:[]})
	# 把二级行业添加到相应一级行业列表中
	for each in result:
		num = re.findall(re.compile('\d+'),each['class_id'])
		if num:
			dict[each['class_id'].replace(num[0],'')].append(each)
	# 将带有二级行业列表的一级行业的字典存入新的列表中
	for each in result:
		if not re.findall(re.compile('\d+'),each['class_id']):
			letter = each['class_id']
			each.update({'sub':dict[letter]})
			results.append(each)

	return json.dumps(results,ensure_ascii=False)

@detection.route('/FundmodeBox/')
def fundmode_box():
	result = fundmodeBox(TABLE_FUNDMODE_LIST)
	return json.dumps(result,ensure_ascii=False)

@detection.route('/EditReportStatus/')
def edit_report_status():
	entity_id = int(request.args.get('entity_id',''))
	report_status = int(request.args.get('report_status',''))
	result = EditReportStatus(TABLE_REPORT_ILLEGAL, entity_id, report_status)
	return json.dumps(result,ensure_ascii=False)

@detection.route('/getIndustry/')
def get_industry():
	entity_id = int(request.args.get('entity_id',''))
	result = getIndustry(TABLE_REPORT_ILLEGAL, TABLE_INDUSTRY_LIST, entity_id)
	return json.dumps(result,ensure_ascii=False)





# 完整报表导出(时间筛选)
@detection.route('/saveAllCsvWithTime/',methods=['POST','GET'])
def save_csv_with_time():
	date = int(request.args.get('date',''))
	# 新建csv文件
	now = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(int(time.time())))
	filename = 'economy/static/report/' + u'疑似非法集资预警记录:' + now + '.csv'
	c = codecs.open(filename,'a+','utf_8_sig')
	#c = codecs.open(filename,'a+','gbk2312')
	writer = csv.writer(c,delimiter=",")
	# 获取结果
	result = totalDetectDataFromBigTable(date,TABLE_REPORT_ILLEGAL,'all',0,0,'all','all',0,'all')
	# 将illegal_type不同的两个实体合并
	b = ScalableBloomFilter(1000000,0.001)
	doubleId = []
	for dict in result:
		if not dict['entity_id'] in b:
			[b.add(dict['entity_id'])]
		else:
			doubleId.append(dict['entity_id'])
	for id in doubleId:
		num = 0
		illegalTypeList = []
		for dict in result:
			if dict['entity_id'] == id:
				num += 1
				illegalTypeList.append(dict['illegal_type'])
				dict.update({'illegal_type':illegalTypeList})
				if num > 1:
					result.remove(dict)
	# 将最早预警时间加入字典
	minDates = getMinDate1(TABLE_MONITOR,RISK_LEVEL,ILLEGAL_SCORE,ILLEGAL_TYPE,TABLE_REPORT_ILLEGAL)
	for each in result:
		each.update({'minDate':minDates[each['entity_id']]})
	# 处理结果
	handledResult = []
	for dict in result:
		riskReason = ""
		if dict['comment_rank'] > 75:
			riskReason += u"负面舆情多；" + "\n"
		if dict['suit_rank'] > 75:
			riskReason += u"诉讼记录多；" + "\n"
		if dict['ad_rank'] > 75:
			riskReason += u"煽动性广告多；" + "\n"
		if dict['return_rank'] > 75:
			riskReason += u"收益率过高；" + "\n"
		if dict['abnor_rank'] > 75:
			riskReason += u"经营异常多；" + "\n"
		if dict['promise_type'] == 1 or dict['promise_type'] == 2:
			riskReason += u"存在担保承诺；"
		if not riskReason:
			riskReason += u"暂无"
		if dict['risk_rank']:
			if dict['risk_rank'] == 0:
				risk_rank = u'无'
			elif dict['risk_rank'] == 1:
				risk_rank = u'小'
			elif dict['risk_rank'] == 2:
				risk_rank = u'大'
		else:
			risk_rank = u'不详'
		if dict['return_num']:
			return_num = str(dict['return_num'])+'%'
		else:
			return_num = u"不详"
		if int(dict['entity_type']) == 1:
			entity_type = u'平台'
		elif int(dict['entity_type']) == 2:
			entity_type = u'工司'
		elif int(dict['entity_type']) == 3:
			entity_type = u'项目'
		if int(dict['entity_source']) == 1:
			entity_source = u'网贷之家'
		elif int(dict['entity_source']) == 2:
			entity_source = u'人工导入'
		elif int(dict['entity_source']) == 3:
			entity_source = u'数据库'
		elif int(dict['entity_source']) == 4:
			entity_source = u'系统感知'
		if dict['return_rank']:
			return_rank = str(dict['return_rank'])+'%'
		else:
			return_rank = u"不详"
		if dict['ad_rank']:
			ad_rank = str(dict['ad_rank'])+'%'
		else:
			ad_rank = u"不详"
		if dict['comment_rank']:
			comment_rank = str(dict['comment_rank'])+'%'
		else:
			comment_rank = u"不详"
		if dict['suit_rank']:
			suit_rank = str(dict['suit_rank'])+'%'
		else:
			suit_rank = u"不详"
		if dict['abnor_rank']:
			abnor_rank = str(dict['abnor_rank'])+'%'
		else:
			abnor_rank = u"不详"

		handledDict = {u"实体id":dict['entity_id'], u"实体名称":dict['entity_name'], u"预警指数":dict['illegal_score'],\
						 u"此次预警时间":dict['date'], u"最早预警时间":dict['minDate'], u"预警理由":riskReason, u"集资模式":dict['fund_mode'],\
						  u"风险评级":risk_rank, u"业态类型":dict['operation_mode'], u"所属行业":dict['industry'], u"问题平台":dict['problem'],\
						   u"省份":dict['province'], u"城市":dict['city'], u"实体类别":entity_type, u"实体来源":entity_source,\
						    u"收益率":return_num, u"收益率大小所属分位点":return_rank, u"担保承诺":dict['promise_type'], u"煽动性广告数量":dict['ad_num'],\
						     u"煽动性广告数所属分位点":ad_rank, u"负面舆情数量":dict['comment_num'], u"负面舆情数所属分位点":comment_rank,\
						      u"诉讼记录数量":dict['suit_num'], u"诉讼记录数所属分位点":suit_rank, u"经营异常数量":dict['abnor_num'],\
						       u"经营异常数所属分位点":abnor_rank, u"赞成数":dict['support_num'], u"反对数":dict['against_num']}
		handledResult.append(handledDict)
	# 存表头
	NEWS_KEYS = [u"实体id", u"实体名称", u"预警指数", u"此次预警时间", u"最早预警时间",\
				 u"预警理由", u"集资模式", u"风险评级", u"业态类型", u"所属行业", u"问题平台",\
				  u"省份", u"城市", u"实体类别", u"实体来源", u"收益率", u"收益率大小所属分位点",\
				   u"担保承诺", u"煽动性广告数量", u"煽动性广告数所属分位点", u"负面舆情数量",\
				    u"负面舆情数所属分位点", u"诉讼记录数量", u"诉讼记录数所属分位点",\
				     u"经营异常数量", u"经营异常数所属分位点", u"赞成数", u"反对数"]
	writer.writerow(NEWS_KEYS)
	# 存数据
	for r in handledResult:
		csvrow = []
		for key in NEWS_KEYS:
			if key in r:
				csvrow.append(r[key])
		writer.writerow(csvrow)
	c.close()
	dict = {'status':filename}
	return json.dumps(dict,ensure_ascii=False)




