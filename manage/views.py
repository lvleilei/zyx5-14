#!/usr/bin/env python
#encoding: utf-8

from flask import Flask, render_template, request, jsonify, Blueprint, send_from_directory, url_for, session, redirect
from economy.db import *
from . import manage
import json
import hashlib

salt = '98b85629951ab584feaf87e28c073088'

@manage.route('/')
def index():
	if not session:
		return redirect('manage/login')
	else:
		username = session['username']
	return render_template('homePage/homePage.html',username=username)


#用户列表
@manage.route('/userManage/')
def userManage():
	if not session or session['role'] != 1:
		return redirect('/manage/login')
	else:
		username = session['username']
		role_id = session['role']
		uid = session['uid']
	return render_template('manage/userManage.html',username=username,role_id=role_id,uid=uid)


#注册
@manage.route('/register',methods=['GET','POST'])
def Register():
	field = ['username', 'password']
	if request.method == 'POST':
		data = {k:v[0] for k,v in dict(request.form).items()}
		data['password'] = hashlib.md5(data['password']+salt).hexdigest()

		#判断用户是否存在
		if check_user(TABLE_USERINFO, data):
			error = u'用户 %s 已存在' % (data['username'])
			return render_template('manage/register.html',error=error)

		#存入数据库
		else:
			field = ['username', 'password']
			if register(TABLE_USERINFO, data, field):
				return redirect('manage/login')

	return render_template('manage/register.html')


#登录
@manage.route('/login',methods=['GET','POST'])
def login():
	if request.method == 'POST':
		data = {k:v[0] for k,v in dict(request.form).items()}
		data['password'] = hashlib.md5(data['password']+salt).hexdigest()

		if check_user(TABLE_USERINFO, data):
			result = getUser(TABLE_USERINFO, data)
			if result['password'] == data['password']:
				session['username'] = data['username']
				session['role'] = result['role_id']
				session['uid'] = result['id']
				return render_template('homePage/homePage.html',username=session['username'],role_id=session['role'],uid=session['uid'])
			else:
				error = u'密码错误'
				return render_template('manage/login.html',error=error)
		else:
			error = u'用户不存在'
			return render_template('manage/login.html',error=error)
	return render_template('manage/login.html')


#退出
@manage.route('/logout')
def logOut():
	if session:
		session.clear()
	return redirect('manage/login')


#删除
@manage.route('/delete',methods=['GET','POST'])
def Delete():
	if not session or session['role'] != 1:
		return redirect('manage/login')
	uid = int(request.args.get('uid',''))
	result = deleteUser(TABLE_USERINFO, uid)
	return json.dumps(result,ensure_ascii=False)


#添加用户
@manage.route('/addUser',methods=['GET','POST'])
def add_user():
	if not session or session['role'] != 1:
		return redirect('/manage/login')
	if request.method == 'POST':
		data = {k:v[0] for k,v in dict(request.form).items()}
		data['password'] = hashlib.md5(data['password']+salt).hexdigest()

		#判断用户是否存在
		if check_user(TABLE_USERINFO, data):
			error = u'用户 %s 已存在' % (data['username'])
			return render_template('manage/register.html',error=error)

		#存入数据库
		else:
			field = ['username', 'password','role_id']
			status = addUser(TABLE_USERINFO, data, field)
			return redirect('manage/userManage/')
	return render_template('manage/userManage.html')

#用户列表数据
@manage.route('/userList/')
def user_list():
	if not session or session['role'] != 1:
		return redirect('/homepage')
	result = getUserList(TABLE_USERINFO)
	return json.dumps(result,ensure_ascii=False)

#编辑用户名、密码、权限
@manage.route('/EditUser',methods=['GET','POST'])
def edit_user():
	if not session or session['role'] != 1:
		return redirect('/manage/login')
	if request.method == 'POST':
		data = {k:v[0] for k,v in dict(request.form).items()}
		data['uid'] = int(data['uid'])
		data['role_id'] = int(data['role_id'])
		if data['password']:
			data['password'] = hashlib.md5(data['password']+salt).hexdigest()
		else:
			data['password'] = getPassword(TABLE_USERINFO, data)

		#判断用户名是否存在
		result = getUser(TABLE_USERINFO, data)
		if result:
			if not result['id'] == data['uid']:	#用户名存在
				error = u'用户 %s 已存在' % (data['username'])
				return render_template('manage/userManage.html',error=error)
			else:	#用户名不变
				status = EditUser(TABLE_USERINFO, data)
				return redirect('manage/userManage/')
		else:	#用户名无重复
			status = EditUser(TABLE_USERINFO, data)
			return redirect('manage/userManage/')
	return render_template('manage/userManage.html')

#修改密码
@manage.route('/changePassword',methods=['GET','POST'])
def change_password():
	if request.method == 'POST':
		data = {k:v[0] for k,v in dict(request.form).items()}
		data['uid'] = int(data['uid'])
		data['password'] = hashlib.md5(data['password']+salt).hexdigest()
		status = changePassword(TABLE_USERINFO, data)
		session.clear()
		return redirect('manage/login')
	return render_template('manage/login.html')


