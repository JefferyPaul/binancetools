import time
import json
import hmac
import hashlib
import requests
from urllib.parse import urljoin, urlencode
import os
import sys
import argparse
from pprint import pprint


PATH_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PATH_ROOT)

from bntools.common import BINANCE_BASE_URL
from helper.simpleLogger import MyLogger

# 參數輸入
arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-i', '--input', )
args = arg_parser.parse_args()
PATH_INPUT_FILE = os.path.abspath(args.input)
assert os.path.isfile(PATH_INPUT_FILE)


class BinanceException(Exception):
    def __init__(self, status_code, data):
        self.status_code = status_code
        if data:
            self.code = data['code']
            self.msg = data['msg']
        else:
            self.code = None
            self.msg = None
        message = f"{status_code} [{self.code}] {self.msg}"
        super().__init__(message)


def set_position_mode(use_hedge_mode: bool = False):
    method_url = '/v1/positionSide/dual'
    timestamp = int(time.time() * 1000)
    params = {
        'dualSidePosition': use_hedge_mode,
        'timestamp': timestamp
    }
    query_string = urlencode(params)
    params['signature'] = hmac.new(SECRET_KEY.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

    url = BASE_URL + method_url
    r = requests.post(url, headers=HEADERS, params=params)
    if r.status_code == 200:
        data = r.json()
        print(json.dumps(data, indent=2))
    elif 'no need to change' in r.json()['msg'].lower():
        print('no need to change')
    else:
        raise BinanceException(status_code=r.status_code, data=r.json())


def set_margin_mode(symbol, margin_type='CROSSED', ):
    assert margin_type.upper() in ['CROSSED', 'ISOLATED']

    method_url = '/v1/marginType'
    timestamp = int(time.time() * 1000)
    params = {
        'symbol': symbol,
        'marginType': margin_type.upper(),
        'timestamp': timestamp
    }
    query_string = urlencode(params)
    params['signature'] = hmac.new(SECRET_KEY.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

    url = BASE_URL + method_url
    r = requests.post(url, headers=HEADERS, params=params)

    if r.status_code == 200:
        data = r.json()
        print(json.dumps(data, indent=2))
    elif 'no need to change' in r.json()['msg'].lower():
        print('no need to change')
    else:
        raise BinanceException(status_code=r.status_code, data=r.json())


def set_leverage(symbol, leverage=5,):
    method_url = '/v1/leverage'
    timestamp = int(time.time() * 1000)
    params = {
        'symbol': symbol,
        'leverage': leverage,
        'timestamp': timestamp
    }
    query_string = urlencode(params)
    params['signature'] = hmac.new(SECRET_KEY.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

    url = BASE_URL + method_url
    r = requests.post(url, headers=HEADERS, params=params)
    if r.status_code == 200:
        data = r.json()
        print(json.dumps(data, indent=2))
    elif 'no need to change' in r.json()['msg'].lower():
        print('no need to change')
    else:
        raise BinanceException(status_code=r.status_code, data=r.json())


if __name__ == '__main__':
    #
    PATH_ACCOUNT_CONFIG = os.path.join(os.path.join(PATH_ROOT, 'Config', 'Config.json'))
    assert os.path.isfile(PATH_ACCOUNT_CONFIG)
    d_account_config = json.loads(open(PATH_ACCOUNT_CONFIG, encoding='utf-8').read())
    API_KEY = d_account_config['apiKey']
    SECRET_KEY = d_account_config['secret']

    HEADERS = {
        'X-MBX-APIKEY': API_KEY
    }
    logger = MyLogger('set_basic_config', output_root=os.path.join(PATH_ROOT, 'logs'))

    # 读取输入
    d_setting_info = json.loads(open(PATH_INPUT_FILE, encoding='utf-8').read())

    # 参数
    _margin_type = d_setting_info['config']['margin_mode']
    _leverage = int(d_setting_info['config']['leverage'])
    _position_mode_use_hedge = d_setting_info['config']['position_mode_use_hedge']
    assert _margin_type.upper() in ['CROSSED', 'ISOLATED']
    assert type(_position_mode_use_hedge) is bool

    # 修改
    for _item_info in d_setting_info['items']:
        _exchange = _item_info['exchange']
        _symbols = _item_info['symbols']

        BASE_URL = BINANCE_BASE_URL[_exchange]
        print('\n\n')
        logger.info(f'changing {_exchange} ...')

        for _symbol in _symbols:
            #
            # r = exchange.set_margin_mode('cross', CHECKING_SYMBOL)
            logger.info(f'set margin mode, {_symbol}, {_margin_type}')
            set_margin_mode(symbol=_symbol, margin_type=_margin_type)

            #
            # r = exchange.set_leverage(5, CHECKING_SYMBOL)
            logger.info(f'set leverage, {_symbol}, {_leverage}')
            set_leverage(leverage=_leverage, symbol=_symbol)

        # set hedged to True or False for a market
        logger.info(f'set position mode, {["One-way", "Hedge"][int(_position_mode_use_hedge)]}')
        set_position_mode(use_hedge_mode=_position_mode_use_hedge)

    logger.info('Finished')

