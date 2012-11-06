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
from flask import redirect, url_for, render_template, request, flash, session
from flask.ext import redis
from flask.ext.babel import Babel
from flask.ext.mail import Mail
import config
import messages
import utils
from utils import db, accounts
from accounts.views import accounts_blueprint
from admin.views import admin_blueprint

app = config.create_app()
app.register_blueprint(accounts_blueprint, url_prefix='/accounts')
app.register_blueprint(admin_blueprint, url_prefix='/admin')
babel = Babel(app)
mail = Mail(app)
redis = redis.init_redis(app)
# add exts for blueprint use
app.config['babel'] = babel
app.config['mail'] = mail
app.config['redis'] = redis

# check for admin user ; create if missing
if not db.get_user('admin'):
    if not config.ADMIN_EMAIL:
        print('You must set ADMIN_EMAIL in config.py')
    else:
        print('Creating admin user; password: keymaker')
        db.create_user(username='admin', password='keymaker',
            email=config.ADMIN_EMAIL, is_admin=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/resetcode/', methods=['POST'])
def reset_code():
    username = request.form.get('username')
    user = db.get_user(username)
    if not user:
        flash(messages.INVALID_USERNAME, 'error')
        return redirect(url_for('index'))
    code = accounts.create_reset_code(username)
    url = 'http://{0}{1}'.format(request.headers.get('HOST'), 
        url_for('reset', code=code))
    tmpl = """
Greetings...

Please click the following link to reset your password.

{0}

If you did not request this reset, please ignore this email and the code will
automatically expire.

Thanks!
{1}""".format(url, config.APP_NAME)
    utils.send_mail('Keymaker Password Reset', tmpl, [user.get('email')])
    flash(messages.RESET_CODE_SENT, 'success')
    return redirect(url_for('index'))

@app.route('/reset/')
def reset(code=None):
    if not code:
        code = request.args.get('code')
        user = accounts.get_user_from_code(code)
        if user:
            session['user'] = user
            accounts.delete_reset_code(code)
            return redirect(url_for('accounts.change_password'))
    flash(messages.EXPIRED_INVALID_CODE, 'error')
    return redirect(url_for('index'))

if __name__=='__main__':
    from optparse import OptionParser
    op = OptionParser()
    op.add_option('--host', dest='host', action='store', default='127.0.0.1', \
        help='Hostname/IP on which to listen')
    op.add_option('--port', dest='port', action='store', type=int, \
        default=5000, help='Port on which to listen')
    opts, args = op.parse_args()

    app.run(host=opts.host, port=opts.port, debug=True)
