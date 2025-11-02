
import requests
import time


class ExecutionEngine:
    def __init__(self, mode='backtest', tradovate_username=None, tradovate_password=None, tradovate_app_id=None, tradovate_app_secret=None, tradovate_demo=True):
        print("Initializing Execution Engine")
        self.mode = mode  # 'backtest', 'paper', or 'live'
        self.tradovate_username = tradovate_username
        self.tradovate_password = tradovate_password
        self.tradovate_app_id = tradovate_app_id
        self.tradovate_app_secret = tradovate_app_secret
        self.tradovate_demo = tradovate_demo
        self.access_token = None
        self.account_id = None
        if self.mode in ['paper', 'live']:
            self._tradovate_authenticate()

    def execute(self, signals):
        if self.mode == 'backtest':
            print(f"Simulating trade execution: {signals}")
        elif self.mode in ['paper', 'live']:
            print(f"Sending order to Tradovate API: {signals}")
            self._tradovate_send_order(signals)
        else:
            print(f"Unknown mode: {self.mode}")

    def _tradovate_authenticate(self):
        base_url = 'https://demo.tradovateapi.com/v1' if self.tradovate_demo else 'https://live.tradovateapi.com/v1'
        auth_url = f'{base_url}/auth/accesstokenrequest'
        payload = {
            'name': self.tradovate_username,
            'password': self.tradovate_password,
            'appId': self.tradovate_app_id,
            'appVersion': '1.0',
            'cid': self.tradovate_app_secret,
            'sec': self.tradovate_app_secret,
            'deviceId': f'device_{int(time.time())}'
        }
        try:
            response = requests.post(auth_url, json=payload)
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get('accessToken')
                print("Tradovate authentication successful.")
                # Get account id
                self.account_id = self._tradovate_get_account_id(base_url)
            else:
                print(f"Tradovate authentication failed: {response.status_code} {response.text}")
        except Exception as e:
            print(f"Tradovate authentication error: {e}")

    def _tradovate_get_account_id(self, base_url):
        if not self.access_token:
            print("No access token. Cannot get account id.")
            return None
        headers = {'Authorization': f'Bearer {self.access_token}'}
        try:
            response = requests.get(f'{base_url}/account/list', headers=headers)
            if response.status_code == 200:
                accounts = response.json()
                if accounts:
                    print(f"Tradovate accounts: {accounts}")
                    return accounts[0]['id']
            else:
                print(f"Failed to get Tradovate accounts: {response.status_code} {response.text}")
        except Exception as e:
            print(f"Error getting Tradovate account id: {e}")
        return None

    def _tradovate_send_order(self, signals):
        if not self.access_token or not self.account_id:
            print("Tradovate not authenticated or account id missing.")
            return
        base_url = 'https://demo.tradovateapi.com/v1' if self.tradovate_demo else 'https://live.tradovateapi.com/v1'
        order_url = f'{base_url}/order/placeorder'
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        # Example: signals should contain symbol, action, quantity, orderType, price, etc.
        # You must adapt this to your signal structure
        order_payload = {
            'accountId': self.account_id,
            'action': signals.get('action', 'Buy'),  # 'Buy' or 'Sell'
            'symbol': signals.get('symbol'),
            'orderQty': signals.get('quantity', 1),
            'orderType': signals.get('orderType', 'Market'),
            'price': signals.get('price'),  # Only for limit/stop orders
            'isAutomated': True
        }
        # Remove None values
        order_payload = {k: v for k, v in order_payload.items() if v is not None}
        try:
            response = requests.post(order_url, json=order_payload, headers=headers)
            if response.status_code == 200:
                print("Order sent to Tradovate successfully.")
            else:
                print(f"Tradovate order failed: {response.status_code} {response.text}")
        except Exception as e:
            print(f"Error sending Tradovate order: {e}")
