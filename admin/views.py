#!/usr/bin/env python
# Copyright 2012 Participatory Culture Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import operator
from flask import Blueprint, render_template, request, url_for, redirect, flash
from decorators import admin_required
from utils import db, hosts, get_task, generate_api_response
import pickle
import messages

bp = admin_blueprint = Blueprint('admin', __name__,
    template_folder='templates')

@bp.route('/')
@admin_required
def index():
    users = db.get_all_users()
    users.sort(key=operator.itemgetter('username')),
    all_hosts = list(hosts.get_hosts())
    all_hosts.sort()
    ctx = {
        'users': users,
        'hosts': all_hosts,
    }
    return render_template('admin/index.html', **ctx)

@bp.route('/hosts/add/', methods=['POST'])
@admin_required
def add_host():
    form = request.form
    hostname = form.get('hostname')
    if hostname:
        hosts.add_host(hostname)
        flash(messages.HOST_ADDED, 'success')
    return redirect(url_for('admin.index'))

@bp.route('/hosts/setsshuser', methods=['POST'])
@admin_required
def set_ssh_info():
    form = request.form
    username = form.get('username')
    key = form.get('key')
    if username and key:
        hosts.set_ssh_user(username)
        hosts.set_ssh_key(key)
        flash(messages.SSH_INFO_UPDATED, 'success')
    return redirect(url_for('admin.index'))

@bp.route('/hosts/delete')
@bp.route('/hosts/delete/<hostname>')
@admin_required
def delete_host(hostname=None):
    if hostname:
        hosts.delete_host(hostname)
        flash(messages.HOST_DELETED, 'success')
    return redirect(url_for('admin.index'))

@bp.route('/tasks/<task_id>')
def view_task(task_id=None):
    data = {}
    if task_id:
        task = get_task(task_id)
        data['status'] = task.get('status')
        res = task.get('result')
        if res:
            res = pickle.loads(res)
        data['result'] = res
    return generate_api_response(data)
