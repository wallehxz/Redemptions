import hashlib
import hmac
import json
import os
import uuid
from collections import OrderedDict
from urllib.parse import urlencode, quote_plus
import pytz
import requests
from datetime import datetime
from django.conf import settings

ALGORITHM = 'ACS3-HMAC-SHA256'


class SignatureRequest:
    def __init__(self):
        self.http_method = "POST"
        self.canonical_uri = "/"
        self.host = "dysmsapi.aliyuncs.com"
        self.x_acs_action = "SendSms"
        self.x_acs_version = "2017-05-25"
        self.headers = self._init_headers()
        self.query_param = OrderedDict()
        self.body = None

    def _init_headers(self):
        headers = OrderedDict()
        headers['host'] = self.host
        headers['x-acs-action'] = self.x_acs_action
        headers['x-acs-version'] = self.x_acs_version
        current_time = datetime.now(pytz.timezone('Etc/GMT'))
        headers['x-acs-date'] = current_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        headers['x-acs-signature-nonce'] = str(uuid.uuid4())
        return headers

    def sorted_query_params(self):
        # 对查询参数按名称排序并返回编码后的字符串
        sorted_query_params = sorted(self.query_param.items(), key=lambda item: item[0])
        self.query_param = {k: v for k, v in sorted_query_params}

    def sorted_headers(self):
        # 对请求头按名称排序并返回编码后的字符串
        sorted_headers = sorted(self.headers.items(), key=lambda item: item[0])
        self.headers = {k: v for k, v in sorted_headers}


def get_authorization(request):
    try:
        new_query_param = OrderedDict()
        process_object(new_query_param, '', request.query_param)
        request.query_param = new_query_param
        # 步骤 1：拼接规范请求串
        canonical_query_string = '&'.join(
            f'{percent_code(quote_plus(k))}={percent_code(quote_plus(str(v)))}' for k, v in
            request.query_param.items())
        hashed_request_payload = sha256_hex(request.body or ''.encode('utf-8'))
        request.headers['x-acs-content-sha256'] = hashed_request_payload
        request.sorted_headers()

        # 构建规范化请求头和已签名消息头列表
        filtered_headers = OrderedDict()
        for k, v in request.headers.items():
            if k.lower().startswith('x-acs-') or k.lower() in ['host', 'content-type']:
                filtered_headers[k.lower()] = v

        canonical_headers = '\n'.join(f'{k}:{v}' for k, v in filtered_headers.items()) + '\n'
        signed_headers = ';'.join(k for k in filtered_headers.keys())

        canonical_request = (
            f'{request.http_method}\n{request.canonical_uri}\n{canonical_query_string}\n'
            f'{canonical_headers}\n{signed_headers}\n{hashed_request_payload}')
        print(canonical_request)

        # 步骤 2：拼接待签名字符串
        hashed_canonical_request = sha256_hex(canonical_request.encode('utf-8'))
        string_to_sign = f'{ALGORITHM}\n{hashed_canonical_request}'
        print(string_to_sign)

        # 步骤 3：计算签名
        signature = hmac256(settings.ALIYUN_API_SECRET.encode('utf-8'), string_to_sign).hex().lower()
        print(signature)

        # 步骤 4：拼接Authorization
        authorization = f'{ALGORITHM} Credential={settings.ALIYUN_API_KEY},SignedHeaders={signed_headers},Signature={signature}'
        print(authorization)
        request.headers['Authorization'] = authorization
    except Exception as e:
        print("Failed to get authorization")
        print(e)


def form_data_to_string(form_data):
    tile_map = OrderedDict()
    process_object(tile_map, '', form_data)
    return urlencode(tile_map)


def process_object(result_map, key, value):
    # 如果值为空，则无需进一步处理
    if value is None:
        return

    if key is None:
        key = ""

    # 当值为列表类型时，遍历列表中的每个元素，并递归处理
    if isinstance(value, (list, tuple)):
        for i, item in enumerate(value):
            process_object(result_map, f"{key}.{i + 1}", item)
    elif isinstance(value, dict):
        # 当值为字典类型时，遍历字典中的每个键值对，并递归处理
        for sub_key, sub_value in value.items():
            if isinstance(sub_value, dict):
                process_object(result_map, f"{key}.{sub_key}", json.dumps(sub_value))
            else:
                process_object(result_map, f"{key}.{sub_key}", sub_value)
    else:
        # 对于以"."开头的键，移除开头的"."以保持键的连续性
        if key.startswith("."):
            key = key[1:]

        # 对于字节类型的值，将其转换为 UTF-8 编码的字符串
        if isinstance(value, bytes):
            result_map[key] = value.decode('utf-8')
        else:
            # 对于其他类型的值，直接转换为字符串
            result_map[key] = str(value)


def hmac256(key, msg):
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()


def sha256_hex(s):
    return hashlib.sha256(s).hexdigest()


def call_api(request):
    url = f'https://{request.host}{request.canonical_uri}'
    if request.query_param:
        url += '?' + urlencode(request.query_param, doseq=True, safe='*')
    print(url)
    headers = {k: v for k, v in request.headers.items()}
    if request.body:
        data = request.body
    else:
        data = None

    try:
        response = requests.request(method=request.http_method, url=url, headers=headers, data=data)
        response.raise_for_status()
        print(response.text)
    except requests.RequestException as e:
        print("Failed to send request")
        print(e)


def percent_code(encoded_str):
    return encoded_str.replace('+', '%20').replace('*', '%2A').replace('%7E', '~')


def send_sms(phone_number, code):
    request = SignatureRequest()
    request.query_param['PhoneNumbers'] = phone_number
    request.query_param['SignName'] = '福赏'
    request.query_param['TemplateCode'] = 'SMS_317840165'
    request.query_param['TemplateParam'] = {"code": code}
    request.sorted_query_params()
    get_authorization(request)
    call_api(request)
