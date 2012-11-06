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
import os
from fabric.api import sudo, env, run
from fabric.context_managers import hide
from flask import current_app, json, Response, request
from flask.ext.mail import Message
import tempfile
from utils import hosts
from redis import Redis
import hashlib
import config

def get_redis_connection():
    """
    Returns a Redis connection

    """
    try:
        rds = current_app.config.get('redis')
    except:
        rds = Redis(host=getattr(config, 'REDIS_HOST'),
            port=getattr(config, 'REDIS_PORT'),
            db=getattr(config, 'REDIS_DB'),
            password=getattr(config, 'REDIS_PASSWORD'))
    return rds

def hash_text(text):
    """
    Hashes text with app key

    :param text: Text to encrypt

    """
    h = hashlib.sha256()
    h.update(getattr(config, 'SECRET_KEY'))
    h.update(text)
    return h.hexdigest()

def generate_api_response(data, status=200, content_type='application/json'):
    """
    `flask.Response` factory for api responses

    :param data: Data that gets serialized to JSON
    :param status: Status code (default: 200)
    :param content_type: Content type (default: application/json)

    """
    indent = None
    if request.args.get('indent'):
        indent = 2
    # check if need to add status_code
    if data == type({}) and not data.has_key('status_code'):
        data['status_code'] = status
    # serialize
    if type(data) != type(''):
        data = json.dumps(data, sort_keys=True, indent=indent)
    resp = Response(data, status=status, content_type=content_type)
    return resp

def send_mail(subject=None, text=None, to=[]):
    """
    Sends mail

    :param subject: Subject
    :param text: Message
    :param to: Recipients as list

    """
    mail = current_app.config.get('mail')
    msg = Message(subject, sender=current_app.config.get('DEFAULT_SENDER'), \
        recipients=to)
    msg.body = text
    return mail.send(msg)

def reset_password(username=None, password=None):
    """
    Resets specified user password on all hosts

    :param username: Username
    :param password: Password

    """
    ret = True
    ssh_user = hosts.get_ssh_user()
    ssh_key = hosts.get_ssh_key()
    all_hosts = list(hosts.get_hosts())
    env.user = ssh_user
    env.hosts = all_hosts
    env.disable_known_hosts = True
    # create temporary key file for fabric
    tmp_key = tempfile.mktemp()
    with open(tmp_key, 'w') as f:
        f.write(ssh_key)
    os.chmod(tmp_key, 0600)
    env.key_filename = tmp_key
    try:
        for host in all_hosts:
            env.host_string = host
            with hide('running', 'stdout', 'stderr'):
                sudo("echo -e '{0}\n{0}' | (sudo passwd -q {1})".format(
                    password, username))
    except:
        ret = False
    # remove key
    os.remove(tmp_key)
    return ret
