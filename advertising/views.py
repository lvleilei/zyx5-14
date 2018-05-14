#!/usr/bin/env python
#encoding: utf-8

from flask import Flask, render_template, request, jsonify, Blueprint, send_from_directory, url_for, session
from economy.db import *
from . import advertising
import json

field = ['id','entity_type','entity_name','location','start_time']

@advertising.route('/billing/')
def billing():
	fullnum = request.args.get('fullnum','')
	if session:
		username = session['username']
		role_id = session['role']
		uid = session['uid']
	else:
		username = ""
		role_id = ""
		uid = ""
	return render_template('advertising/billing.html',username=username,role_id=role_id,uid=uid,fullnum=fullnum)

@advertising.route('/adDetails/')
def adDetails():
	name = request.args.get('name','')
	pid = request.args.get('pid','')
	return render_template('advertising/adDetails.html',name=name,pid=pid)

