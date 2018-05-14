#!/usr/bin/env python
#encoding: utf-8

from flask import Flask, render_template, request, jsonify, Blueprint, send_from_directory, url_for, session
from economy.db import *
from . import caseBase
import json
from economy.config import *
from economy.es import *
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

@caseBase.route('/caseBasetem/')
def case_base():
	fullnum = request.args.get('fullnum','')
	if session:
		username = session['username']
		role_id = session['role']
		uid = session['uid']
	else:
		username = ""
		role_id = ""
		uid = ""
	return render_template('caseBase/caseBase.html',username=username,role_id=role_id,uid=uid,fullnum=fullnum)

