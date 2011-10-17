import marcel

class FlaskrTestCase(unittest.TestCase):
    def setUp(self):
        flaskr.app.config['TESTING'] = True
