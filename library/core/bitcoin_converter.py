import requests

from library.core.errors import UnsuccessfulRequest


class BitcoinConverter:
    def convert(self, amount: float, currency: str) -> float:
        pass


class BitcoinToCurrency:
    def convert(self, amount: float, currency: str = 'USD') -> float:
        try:
            url = f'https://blockchain.info/tobtc?currency={currency}&value=1'
            response = requests.get(url)
            assert response.status_code == 200
            return 1/response.json()
        except UnsuccessfulRequest:
            pass
