import unittest
import utils
from utils import db, hosts, accounts
import config

class UtilsTestCase(unittest.TestCase):
    def setUp(self):
        self.test_user_username = 'testuser'
        self.test_user_email = 'test@test.com'
        self.test_user_password = 't35t'
        self.test_user_is_admin = False
        self.test_hostname = 'testhost'
        self.test_ssh_user = 'sshuser'
        self.test_ssh_key = 'abcdefg12345'
        config.REDIS_DB = 14

    def tearDown(self):
        rds = utils.get_redis_connection()
        rds.flushdb()

    def _create_user(self):
        db.create_user(self.test_user_username, self.test_user_password,
            self.test_user_email, self.test_user_is_admin)
        user = db.get_user(self.test_user_username)
        return user

    def test_create_user(self):
        user = self._create_user()
        self.assertEqual(user.get('username'), self.test_user_username)
        self.assertEqual(user.get('email'), self.test_user_email)
        self.assertNotEqual(user.get('password'), self.test_user_password)
        self.assertEqual(user.get('password'),
            utils.hash_text(self.test_user_password))
        self.assertEqual(user.get('is_admin'), self.test_user_is_admin)

    def test_get_user(self):
        self._create_user()
        u = db.get_user(self.test_user_username)
        self.assertNotEqual(u, None)
        self.assertTrue(u.has_key('username'))

    def test_create_reset_code(self):
        user = self._create_user()
        self.assertEqual(user.get('username'), self.test_user_username)
        code = accounts.create_reset_code(self.test_user_username)
        self.assertNotEqual(code, None)

    def test_get_user_from_code(self):
        user = self._create_user()
        self.assertEqual(user.get('username'), self.test_user_username)
        code = accounts.create_reset_code(self.test_user_username)
        self.assertNotEqual(code, None)
        u = accounts.get_user_from_code(code)
        self.assertNotEqual(u, None)
        self.assertTrue(u.has_key('username'))

    def test_delete_user_code(self):
        rds = utils.get_redis_connection()
        user = self._create_user()
        self.assertEqual(user.get('username'), self.test_user_username)
        code = accounts.create_reset_code(self.test_user_username)
        self.assertNotEqual(code, None)
        accounts.delete_reset_code(code)
        self.assertEqual(rds.get(accounts.RESET_CODE_KEY.format(code)), None)

    def test_add_host(self):
        self.assertTrue(hosts.add_host(self.test_hostname))
        all_hosts = list(hosts.get_hosts())
        self.assertTrue(self.test_hostname in all_hosts)

    def test_delete_host(self):
        self.assertTrue(hosts.add_host(self.test_hostname))
        all_hosts = list(hosts.get_hosts())
        self.assertTrue(self.test_hostname in all_hosts)
        self.assertTrue(hosts.delete_host(self.test_hostname))

    def test_set_ssh_user(self):
        self.assertTrue(hosts.set_ssh_user(self.test_ssh_user))
        self.assertEqual(hosts.get_ssh_user(), self.test_ssh_user)

    def test_set_ssh_key(self):
        self.assertTrue(hosts.set_ssh_key(self.test_ssh_key))
        self.assertEqual(hosts.get_ssh_key(), self.test_ssh_key)

