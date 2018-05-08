import os
import FozrWebApp
import unittest
import tempfile


class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        # self.db_fd, FiveOzRacer.app.config['DATABASE'] = tempfile.mkstemp()
        # FiveOzRacer.app.config['TESTING'] = True
        # self.app = FiveOzRacer.app.test_client()
        # FiveOzRacer.init_db()
        pass

    def tearDown(self):
        # os.close(self.db_fd)
        # os.unlink(FiveOzRacer.app.config['DATABASE'])
        pass

    def test_nada(self):
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
