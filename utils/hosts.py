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
import utils

HOST_KEY = 'hosts'
SSH_USER_KEY = 'ssh:user'
SSH_KEY_KEY = 'ssh:key'

def add_host(hostname=None):
    """
    Adds a host

    :param hostname: Hostname

    """
    rds = utils.get_redis_connection()
    return rds.sadd(HOST_KEY, hostname)

def delete_host(hostname=None):
    """
    Deletes a host

    :param hostname: Hostname

    """
    rds = utils.get_redis_connection()
    return rds.srem(HOST_KEY, hostname)

def get_hosts():
    """
    Gets all hosts

    """
    rds = utils.get_redis_connection()
    return rds.smembers(HOST_KEY)

def set_ssh_user(username=None):
    """
    Sets host username

    :param username: SSH username

    """
    rds = utils.get_redis_connection()
    ret = None
    if username:
        ret = rds.set(SSH_USER_KEY, username)
    return ret

def set_ssh_key(key=None):
    """
    Sets host key

    :param key: SSH private key (as text)

    """
    rds = utils.get_redis_connection()
    ret = None
    if key:
        ret = rds.set(SSH_KEY_KEY, key)
    return ret

def get_ssh_user():
    """
    Gets host user

    """
    rds = utils.get_redis_connection()
    return rds.get(SSH_USER_KEY)

def get_ssh_key():
    """
    Gets host key

    """
    rds = utils.get_redis_connection()
    return rds.get(SSH_KEY_KEY)

