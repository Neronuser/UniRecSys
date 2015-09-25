import os
import uniRecSys
import unittest


class UniRecSysTestCase(unittest.TestCase):
    def setUp(self):
        uniRecSys.app.config['TESTING'] = True
        uniRecSys.app.config['MONGO_DB'] = 'RecTesting'

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(uniRecSys.app.config['DATABASE'])

if __name__ == '__main__':
    unittest.main()
