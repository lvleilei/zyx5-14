#!/usr/bin/env python
#encoding: utf-8

from flask import Flask, render_template, request, jsonify, Blueprint, send_from_directory, url_for, session
from economy.db import *
from . import index
import json
from economy.es import *
from economy.config import *
from lxml import etree
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

@index.route('/platform/')
def platform():
    if session:
        username = session['username']
        role_id = session['role']
        uid = session['uid']
    else:
        username = ""
        role_id = ""
        uid = ""
    return render_template('index/platform.html',username=username,role_id=role_id,uid=uid)

@index.route('/monitor/')
def monitor():
    name = request.args.get('name','')
    flag = request.args.get('flag','')
    pid = request.args.get('pid','')
    if session:
        username = session['username']
        role_id = session['role']
        uid = session['uid']
    else:
        username = ""
        role_id = ""
        uid = ""
    return render_template('index/monitorDetails.html',name=name,flag=flag,pid=pid,username=username,role_id=role_id,uid=uid)

@index.route('/company/')
def company():
    name = request.args.get('name','')
    flag = request.args.get('flag','')
    pid = request.args.get('pid','')
    if session:
        username = session['username']
        role_id = session['role']
        uid = session['uid']
    else:
        username = ""
        role_id = ""
        uid = ""
    return render_template('index/company.html',name=name,flag=flag,pid=pid,username=username,role_id=role_id,uid=uid)

# 画像页复制本
@index.route('/company_monitor/')
def company_monitor():
    name = request.args.get('name','')
    flag = request.args.get('flag','')
    pid = request.args.get('pid','')
    if session:
        username = session['username']
        role_id = session['role']
        uid = session['uid']
    else:
        username = ""
        role_id = ""
        uid = ""
    return render_template('index/company_monitor.html',name=name,flag=flag,pid=pid,username=username,role_id=role_id,uid=uid)

@index.route('/project/')
def project():
    name = request.args.get('name','')
    flag = request.args.get('flag','')
    if session:
        username = session['username']
        role_id = session['role']
        uid = session['uid']
    else:
        username = ""
        role_id = ""
        uid = ""
    return render_template('index/project.html',name=name,flag=flag,username=username,role_id=role_id,uid=uid)

@index.route('/entityType/')
def entity_type():
    id = int(request.args.get('id',''))
    result = platform_detail(TABLE_ENTITY_LIST,TABLE_PLAT_DETAIL,TABLE_GONGSHANG,TABLE_MONITOR,id)
    return json.dumps(result,ensure_ascii=False)


@index.route('/ad/')
def adData():
    id = int(request.args.get('id',''))
    result = get_ad(TABLE_AD_STATIS,id)
    return json.dumps(result,ensure_ascii=False)

@index.route('/comment/')
def commentData():
    id = int(request.args.get('id',''))
    result = get_comment(TABLE_COMMENT_STATIS,id)
    return json.dumps(result,ensure_ascii=False)

@index.route('/gongshang/')
def gongshangData():
    id = int(request.args.get('id',''))
    result = get_gongshang(TABLE_GONGSHANG,id)
    return json.dumps(result,ensure_ascii=False)

@index.route('/guarantee/')
def guaranteeData():
    id = int(request.args.get('id',''))
    result = get_guarantee(TABLE_GUARANTEE_PROMISE,id)
    return json.dumps(result,ensure_ascii=False)

@index.route('/returnRate/')
def returnRateData():
    id = int(request.args.get('id',''))
    result = get_return_rate(TABLE_RETURN_RATE_MORE, TABLE_PLAT_DETAIL, id)
    return json.dumps(result,ensure_ascii=False)


@index.route('/returnRateThreeNum/')
def return_rate_three_num():
    id = int(request.args.get('id',''))
    result = []
    data = returnRateThreeNum(TABLE_RETURN_RATE_MORE, TABLE_PLAT_DETAIL, id)
    result.append(data)
    return json.dumps(result,ensure_ascii=False)


@index.route('/returnRate_content/')
def returnrateContent():
    index_name = request.args.get('index_name','')
    text_id = request.args.get('text_id','')
    result = get_returnrate_content(index_name,text_id)
    return json.dumps(result,ensure_ascii=False)

@index.route('/promise_content/')
def promiseContent():
    index_name = request.args.get('index_name','')
    text_id = request.args.get('text_id','')
    result = get_promise_content(index_name,text_id)
    return json.dumps(result,ensure_ascii=False)


@index.route('/ad_content/')
def adContent():
    results = []
    entity_name_list = request.args.get('entity_name','').split('(')
    if len(entity_name_list) == 1:
        entity_name_list = request.args.get('entity_name').split('（')
    entity_name = entity_name_list[0]
    source = request.args.get('source','')
    date = int(request.args.get('date',''))
    ad123 = int(request.args.get('ad123',''))
    if source == 'all':
        for each in TYPE.items():
            index_name = each[0]
            type = each[1]
            result = get_adContent(entity_name, 0.5, index_name, type, date, ad123, ad_date)
            for each in result:
                results.append(each)
    else:
        index_name = source
        type = TYPE[index_name]
        result = get_adContent(entity_name, 0.5, index_name, type, date, ad123, ad_date)
        for each in result:
            results.append(each)
    results.sort(key=lambda x:x['publish_time'],reverse=True)
    return json.dumps(results[0:50],ensure_ascii=False)


@index.route('/editAd/')
def edit_ad():
    id = request.args.get('_id','')
    index_name = request.args.get('source','')
    type = TYPE[index_name]
    ad123 = int(request.args.get('ad123',''))
    result = editAd(id, index_name, type, ad123)
    return json.dumps(result,ensure_ascii=False)


@index.route('/comment_content/')
def commentContent():
    results = []
    entity_name_list = request.args.get('entity_name','').split('(')
    if len(entity_name_list) == 1:
        entity_name_list = request.args.get('entity_name').split('（')
    entity_name = entity_name_list[0]
    source = request.args.get('source','')
    date = int(request.args.get('date',''))
    em = int(request.args.get('em',''))
    if source == 'all':
        for each in TYPE.items():
            index_name = each[0]
            type = each[1]
            result = get_commentContent(entity_name, 0, index_name, type, date, em, comment_date)
            for each in result:
                results.append(each)
    else:
        index_name = source
        type = TYPE[index_name]
        result = get_commentContent(entity_name, 0, index_name, type, date, em, comment_date)
        for each in result:
            results.append(each)
    #如果检索一般负面的数据，则存在em1=1的数据不显示
    if em == 0:
        result0 = []
        for dict in results:
            if not 'em1' in dict:
                result0.append(dict)
            else:
                if dict['em1'] == 0:
                    result0.append(dict)
        result0.sort(key=lambda x:x['publish_time'],reverse=True)
        return json.dumps(result0[0:50],ensure_ascii=False)
    results.sort(key=lambda x:x['publish_time'],reverse=True)
    return json.dumps(results[0:50],ensure_ascii=False)

@index.route('/otherComment/')
def other_comment():
    results = []
    entity_name_list = request.args.get('entity_name','').split('(')
    if len(entity_name_list) == 1:
        entity_name_list = request.args.get('entity_name').split('（')
    entity_name = entity_name_list[0]
    source = request.args.get('source','')
    date = int(request.args.get('date',''))

    # 筛选来源
    if source == 'all':
        for each in TYPE.items():
            index_name = each[0]
            type = each[1]
            result = get_other_comment(entity_name, index_name, type, date, comment_date)
            for each in result:
                results.append(each)
    else:
        index_name = source
        type = TYPE[index_name]
        result = get_other_comment(entity_name, index_name, type, date, comment_date)
        for each in result:
            results.append(each)

    results.sort(key=lambda x:x['publish_time'],reverse=True)
    return json.dumps(results[0:300],ensure_ascii=False)


@index.route('/editComment/')
def edit_comment():
    id = request.args.get('_id','')
    index_name = request.args.get('source','')
    type = TYPE[index_name]
    em = int(request.args.get('em',''))
    result = editComment(id, index_name, type, em)
    return json.dumps(result,ensure_ascii=False)


@index.route('/abnormal_info/')
def abnormalInfo():
    firm_name = request.args.get('firm_name','')
    result = get_ab_info(INDEX_GONGSHANG,'abnormal_info',firm_name)
    return json.dumps(result,ensure_ascii=False)

@index.route('/change_info/')
def changelInfo():
    firm_name = request.args.get('firm_name','')
    result = get_ch_info(INDEX_GONGSHANG,'change_info',firm_name)
    return json.dumps(result,ensure_ascii=False)

@index.route('/law_info/')
def lawInfo():
    firm_name = request.args.get('firm_name','')
    result = get_law_info(INDEX_GONGSHANG,'law_info',firm_name)
    for each in result:
        html = etree.HTML(each['content'])
        if ''.join(html.xpath('//div/text()')):
            each['content'] = ''.join(html.xpath('//div/text()'))
    return json.dumps(result,ensure_ascii=False)


@index.route('/sub_firm/')
def subfirmContent():
    results = []
    index_name = INDEX_GONGSHANG
    firm_name = request.args.get('firm_name', '')
    # print firm_name
    level1_subfirms = get_subfirmContent(firm_name,index_name)

    results.append(firm_name)       #根节点
    level1_temp = []
    for item in level1_subfirms:
        level1_temp.append(item['asset_name'])
    results.append({firm_name:level1_temp})


    level2_names = []           #用于存储所有的二级公司名
    level2_subfirms = {}
    for sub_firm in level1_subfirms:
        level2_temp = get_subfirmContent(sub_firm['asset_name'], index_name)
        level2_subfirms[sub_firm['asset_name']] = [x['asset_name'] for x in level2_temp]
        level2_names += [x['asset_name'] for x in level2_temp]

    results.append(level2_subfirms)


    level3_subfirms = {}
    for sub_firm in level2_names:
        level3_temp = get_subfirmContent(sub_firm, index_name)
        level3_subfirms[sub_firm] = [x['asset_name'] for x in level3_temp]
    results.append(level3_subfirms)

    # 返回的数据结构为
    # [根公司，{根公司:[一级子公司A,B,C...]},{一级子公司A:[二级子公司A1,A2,A3],一级子公司B:[二级子公司B1,B2,B3]},{二级子公司A1:[三级子公司a1a2a3]}]

    return json.dumps(results, ensure_ascii=False)

@index.route('/holder/')
def holderContent():
    results = []
    index_name = INDEX_GONGSHANG
    firm_name = request.args.get('firm_name', '')
    # print firm_name
    level1_holders = get_holderContent(firm_name, index_name)

    results.append(firm_name)  # 根节点
    level1_temp = []
    for item in level1_holders:
        level1_temp.append(item['holder'])
    results.append({firm_name: level1_temp})


    level2_holders = {}
    level2_names = []       #用于存储所有二层公司名
    for item in level1_holders:
        level2_temp = get_holderContent(item['holder'], index_name)
        level2_holders[item['holder']] = [x['holder'] for x in level2_temp]
        level2_names += [x['holder'] for x in level2_temp]
    results.append(level2_holders)

    level3_holders = {}
    for item in level2_names:
        level3_temp = get_holderContent(item, index_name)
        level3_holders[item] = [x['holder'] for x in level3_temp]
    results.append(level3_holders)


    # 返回的数据结构为
    # [根公司，{根公司:[一级股东A,B,C...]},{一级股东A:[二级股东A1,A2,A3],一级股东B:[二级子股东B1,B2,B3]},{二级股东A2:三级股东a1a2a3}]

    return json.dumps(results, ensure_ascii=False)


@index.route('/riskCommentTable/')
def risk_comment_table():
    entity_id = int(request.args.get('entity_id',''))
    result = get_risk_comment_table(TABLE_MONITOR,entity_id,ILLEGAL_TYPE,ILLEGAL_SCORE)
    return json.dumps(result,ensure_ascii=False)


@index.route('/EditDetail/',methods=['POST'])
def edit_detail():
    dict = request.get_json()[0]
    status = EditDetail(TABLE_ENTITY_LIST, TABLE_PLAT_DETAIL, TABLE_GONGSHANG, dict, TABLE_REPORT_ILLEGAL)
    return json.dumps(status,ensure_ascii=False)

@index.route('/EditReturnRate/',methods=['GET','POST'])
def edit_return_rate():
    id = int(request.args.get('id',''))
    entity_id = int(request.args.get('entity_id',''))
    return_rate = int(request.args.get('return_rate','').split('.')[0])
    status = EditReturnRate(TABLE_RETURN_RATE_MORE,return_rate,entity_id,id,TABLE_REPORT_ILLEGAL)
    return json.dumps(status,ensure_ascii=False)

@index.route('/EditRelatedPlat/',methods=['GET','POST'])
def edit_related_plat():
    entity_id = int(request.args.get('entity_id',''))
    related_plat = request.args.get('related_plat','')
    date = request.args.get('date','')
    status = EditRelatedPlat(TABLE_PLAT_DETAIL,entity_id,related_plat,date)
    return json.dumps(status,ensure_ascii=False)

@index.route('/EditRelatedCompany/',methods=['POST'])
def edit_related_company():
    entity_id = int(request.args.get('entity_id',''))
    related_company = request.args.get('related_company','')
    date = request.args.get('date','')
    status = EditRelatedCompany(TABLE_PLAT_DETAIL,entity_id,related_company,date)
    return json.dumps(status,ensure_ascii=False)

@index.route('/MonitorStatus/')
def monitor_status():
    entity_name = request.args.get('entity_name','')
    log_type = int(request.args.get('log_type',''))
    remark = request.args.get('remark','')
    uid = int(request.args.get('uid',''))
    entity_id = int(request.args.get('entity_id',''))
    date = request.args.get('date','')
    username = request.args.get('username','')
    status = MonitorStatus(TABLE_ENTITY_LIST, TABLE_LOGS, entity_name, log_type, remark, uid, entity_id, date, username, TABLE_REPORT_ILLEGAL)
    return json.dumps(status,ensure_ascii=False)

@index.route('/quantile/')
def Quantile():
    entity_id = int(request.args.get('entity_id',''))
    result = getQuantile(TABLE_INDEX_QUANTILE, entity_id)
    return json.dumps(result,ensure_ascii=False)

@index.route('/editProblem/')
def edit_problem():
    entity_id = int(request.args.get('entity_id',''))
    uid = int(request.args.get('uid',''))
    entity_name = request.args.get('entity_name','')
    remark = request.args.get('remark','')
    oldValue = request.args.get('oldValue','')
    newValue = request.args.get('newValue','')
    date = request.args.get('date','')
    username = request.args.get('username','')
    result = editProblem(TABLE_ENTITY_LIST, TABLE_LOGS, entity_id, uid, entity_name, remark, date, oldValue, newValue, username, TABLE_REPORT_ILLEGAL)
    return json.dumps(result,ensure_ascii=False)

@index.route('/addProblem/')
def add_problem():
    problem = request.args.get('problem','')
    uid = int(request.args.get('uid',''))
    username = request.args.get('username','')
    result = addProblem(TABLE_PROBLEM_LIST, TABLE_LOGS, problem, uid, username)
    return json.dumps(result,ensure_ascii=False)

@index.route('/platUrl/')
def plat_url():
    platname = request.args.get('platname','').strip()
    result = getPlatUrl(platname)
    return json.dumps(result,ensure_ascii=False)


@index.route('/returnRateMaxMinMid/')
def return_rate_max_min_mid():
    id = int(request.args.get('id',''))
    result = returnRateMaxMinMid(TABLE_RETURN_RATE_MORE, TABLE_PLAT_DETAIL, id)
    return json.dumps(result,ensure_ascii=False)


@index.route('/returnRateAllResult/')
def return_rate_all_result():
    id = int(request.args.get('id',''))
    result = returnRateAllResult(TABLE_RETURN_RATE_MORE, id)
    return json.dumps(result,ensure_ascii=False)


@index.route('/avgReturn/')
def avg_return():
    id = int(request.args.get('id',''))
    result = avgReturn(TABLE_PLAT_DETAIL, id)
    return json.dumps(result,ensure_ascii=False)

@index.route('/gwReturnRate/')
def gw_return_rate():
    id = int(request.args.get('id',''))
    result = gwReturnRate(TABLE_GW_RATE, id)
    return json.dumps(result,ensure_ascii=False)

@index.route('/EditGwReturnRate/',methods=['POST','GET'])
def edit_gw_return_rate():
    id = int(request.args.get('id',''))
    entity_id = int(request.args.get('entity_id',''))
    return_rate = int(request.args.get('return_rate','').split('.')[0])
    status = EditGwReturnRate(TABLE_GW_RATE, id, entity_id, return_rate)
    return json.dumps(status,ensure_ascii=False)

@index.route('/LendingRate/',methods=['POST','GET'])
def lending_rate():
    id = int(request.args.get('id',''))
    result = LendingRate(TABLE_RETURN_RATE_MORE, id)
    return json.dumps(result,ensure_ascii=False)

@index.route('/EditLendingRate/',methods=['POST','GET'])
def edit_lending_rate():
    id = int(request.args.get('id',''))
    entity_id = int(request.args.get('entity_id',''))
    return_rate = int(request.args.get('return_rate','').split('.')[0])
    status = EditLendingRate(TABLE_RETURN_RATE_MORE, id, entity_id, return_rate)
    return json.dumps(status, ensure_ascii=False)

@index.route('/isReturnRateEmpty/')
def is_return_rate_empty():
    id = int(request.args.get('id',''))
    result = isReturnRateEmpty(TABLE_RETURN_RATE_MORE, TABLE_PLAT_DETAIL, TABLE_GW_RATE, id)
    return json.dumps(result, ensure_ascii=False)

@index.route('/subInstitution/')
def sub_institution():
    company = request.args.get('company','')
    result = subInstitution(INDEX_GONGSHANG, company)
    result.sort(key=lambda x:x['regDate'],reverse=True)
    return json.dumps(result, ensure_ascii=False)

@index.route('/dishonInfo/')
def dishon_info():
    company = request.args.get('company','')
    result = dishonInfo(INDEX_GONGSHANG, company)
    result.sort(key=lambda x:x['publishtime'],reverse=True)
    return json.dumps(result, ensure_ascii=False)

@index.route('/mortageInfo/')
def mortage_info():
    company = request.args.get('company','')
    result = mortageInfo(INDEX_GONGSHANG, company)
    result.sort(key=lambda x:x['regdate'],reverse=True)
    return json.dumps(result, ensure_ascii=False)

@index.route('/equitInfo/')
def equit_info():
    company = request.args.get('company','')
    result = equitInfo(INDEX_GONGSHANG, company)
    result.sort(key=lambda x:x['regdate'],reverse=True)
    return json.dumps(result, ensure_ascii=False)

@index.route('/punishInfo/')
def punish_info():
    company = request.args.get('company','')
    result = punishInfo(INDEX_GONGSHANG, company)
    result.sort(key=lambda x:x['publishdate'],reverse=True)
    return json.dumps(result, ensure_ascii=False)

@index.route('/badillInfo/')
def badill_info():
    company = request.args.get('company','')
    result = badillInfo(INDEX_GONGSHANG, company)
    result.sort(key=lambda x:x['putdate'],reverse=True)
    return json.dumps(result, ensure_ascii=False)


