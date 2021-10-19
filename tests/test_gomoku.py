import unittest

from contracting.client import ContractingClient


class GomokuTests(unittest.TestCase):
    def setUp(self):
        self.client = ContractingClient()
        self.client.flush()

        with open('test_currency.py') as file:
            currency = file.read()
            self.client.submit(currency, name='currency')
            self.currency = self.client.get_contract('currency')

        with open('gomoku.py') as file:
            gomoku = file.read()
            self.client.submit(gomoku, name='gomoku')
            self.gomoku = self.client.get_contract('gomoku')

    def tearDown(self):
        self.client.flush()

    def test_sample(self):
        pass
