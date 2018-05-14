#!/usr/bin/env python
#encoding: utf-8

from flask import Flask, render_template, request, jsonify, Blueprint, send_from_directory, url_for, session
from economy.db import *
from . import homePage
import json
from economy.config import *
from economy.entityPortrait import views
from economy.es import *

@homePage.route('/')
def index():
	if session:
		username = session['username']
		role_id = session['role']
		uid = session['uid']
	else:
		username = ""
		role_id = ""
		uid = ""
	return render_template('homePage/homePage.html',username=username,role_id=role_id,uid=uid)

@homePage.route('/warnCount/')
def warn_count():
	result = h_getWarnCount(TABLE_MONITOR, RISK_LEVEL, ILLEGAL_SCORE, TABLE_REPORT_ILLEGAL)
	return json.dumps(result,ensure_ascii=False)

@homePage.route('/cityRank/')
def city_rank():
	province = request.args.get('province','')
	result = get_city_rank(TABLE_MONITOR,TABLE_GONGSHANG,province, RISK_LEVEL, ILLEGAL_SCORE, ILLEGAL_TYPE)#读取预存储数据需要注释掉这句
	#result = get_prepared_city_rank(province)    #建好表计算出数据后把这句恢复了就可以读取预存储数据了
	return json.dumps(result,ensure_ascii=False)

@homePage.route('/provinceRank/')
def province_rank():
	result = get_province_rank(TABLE_MONITOR,TABLE_GONGSHANG, RISK_LEVEL, ILLEGAL_SCORE, ILLEGAL_TYPE)
	result.sort(key=lambda x:x['count7'],reverse=True)
	return json.dumps(result,ensure_ascii=False)

@homePage.route('/timeDistribute/')
def time_distribute():
	result = getTimeDistribute(TABLE_MONITOR,RISK_LEVEL,ILLEGAL_SCORE,ILLEGAL_TYPE)
	return json.dumps(result,ensure_ascii=False)

@homePage.route('/hotSpot/')
def hot_spot():
	list = get(TABLE_ENTITY_LIST,TABLE_PLAT_DETAIL,TABLE_GONGSHANG,'all',10000,0,'all','all',TABLE_INDEX_QUANTILE,TABLE_GUARANTEE_PROMISE)['data'][0:1000]
	entity_list = []
	for dict in list:
		entity_list.append({'id':dict['id'],'name':dict['entity_name'],'entity_type':dict['entity_type']})
	result = getHotSpot(entity_list)
	return json.dumps(result,ensure_ascii=False)
