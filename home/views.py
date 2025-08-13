import json
import uuid
import requests
from django.conf import settings
from django.db.models import Q
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from account.models import Shipping, Region
from series.models import Series, Prize
from django.http import JsonResponse
from redeem.models import Redeem, Redemption
from distribution.models import CashRedemption, CashExchange
from urllib.parse import parse_qs
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import base64


def wechat_decrypt(nonce, ciphertext, associated_data):
    key = settings.WECHAT_APIV3KEY
    key_bytes = str.encode(key)
    nonce_bytes = str.encode(nonce)
    ad_bytes = str.encode(associated_data)
    data = base64.b64decode(ciphertext)
    aesgcm = AESGCM(key_bytes)
    return aesgcm.decrypt(nonce_bytes, data, ad_bytes)


def post_data(body):
    decoded_str = body.decode('utf-8')
    parsed_data = parse_qs(decoded_str)
    single_value_data = {k: v[0] if v else '' for k, v in parsed_data.items()}
    json_data = json.dumps(single_value_data, ensure_ascii=False)
    return json.loads(json_data)


def index(request):
    if request.user.is_staff:
        if request.user.staff_store_info_complete() is False:
            return redirect('complete_store')
        pending_cash = 0
        exchange_lists = CashExchange.objects.filter(Q(user=request.user) & Q(status='pending')).all()
        for exchange in exchange_lists:
            pending_cash += exchange.cash
    series = Series.objects.all()
    return render(request, 'index.html', locals())


def sign_in(request):
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'sign_in.html')


def get_prizes(request):
    series_id = request.GET.get('series_id')
    obj_list = Prize.objects.filter(series_id=series_id).all()
    prize_list = []
    for prize in obj_list:
        prize_list.append({'name': prize.name, 'image': prize.logo_url(), 'description': f'库存数量:  {prize.inventory}'})
    return JsonResponse(prize_list, safe=False)


@csrf_exempt
def redemption(request):
    if request.method == 'POST':
        redeem_code = json.loads(request.body).get('redeem_code')
        if request.user.is_staff:
            cash_redemption = CashRedemption.objects.filter(Q(number=redeem_code) & Q(status=False)).first()
            if cash_redemption:
                CashExchange.objects.create(redemption=cash_redemption,
                    user=request.user,
                    number=uuid.uuid4().hex.upper(),
                    cash=cash_redemption.cash,
                )
                cash_redemption.status = True
                cash_redemption.save()
                return JsonResponse({'status': 'success', 'msg': f'成功兑换奖励现金 {cash_redemption.cash} 元', 'redirect_url': '/employee/exchange_history'})
        redeem = Redeem.objects.filter(Q(number=redeem_code) & Q(status=0)).first()
        if redeem:
            prize = redeem.prize
            if prize:
                if prize.inventory > 0:
                    prize.inventory -= 1
                    prize.save()
                    redeem.status = 1
                    redeem.save()
                    new_redemption = Redemption.objects.create(redeem_id=redeem.id, consumer_id=request.user.id,
                                                               prize_id=prize.id)
                    default_shipping = Shipping.objects.filter(Q(is_default=True) & Q(consumer_id=request.user.id)).first()
                    if default_shipping:
                        new_redemption.shipping_id = default_shipping.id
                        new_redemption.save()
                    return JsonResponse({'status': 'success', 'msg': f'获得奖品【{prize.name}】一件', 'redirect_url': f"/redemptions/show/{new_redemption.id}"})
                else:
                    return JsonResponse({'status': 'warning', 'msg': f'奖品库存不足，我们会尽快补货！'})
            else:
                redeem.status = 1
                redeem.save()
                redemption = Redemption.objects.create(redeem_id=redeem.id, consumer_id=request.user.id)
                redemption.save()
                return JsonResponse({'status': 'warning', 'msg': '很遗憾，未能抽中奖品，感谢参与'})
        else:
            return JsonResponse({'status': 'error', 'msg': '很遗憾，未能抽中奖品，感谢参与'})


def redemptions(request):
    if request.user is None:
        return redirect('sign_in')
    redemption_list = Redemption.objects.filter(consumer_id=request.user.id,prize__isnull=False).order_by('-created_at')
    shipping_list = Shipping.objects.filter(consumer_id=request.user.id).all()
    return render(request, 'redemptions.html', locals())


def all_history(request):
    if request.user is None:
        return redirect('sign_in')
    redemption_list = Redemption.objects.filter(consumer_id=request.user.id).order_by('-created_at')
    shipping_list = Shipping.objects.filter(consumer_id=request.user.id).all()
    return render(request, 'all_history.html', locals())


def shipping(request):
    if request.user is None:
        return redirect('sign_in')
    shipping_list = Shipping.objects.filter(consumer_id=request.user.id).all()
    provinces_list = Region.objects.filter(Q(city='0') & Q(area='0') & Q(town='0'))
    return render(request, 'shipping.html', locals())


def region_children(request):
    parent_id = request.GET.get('parent_id')
    if parent_id == '0':
        children_list = Region.objects.filter(Q(city='0') & Q(area='0') & Q(town='0'))
    else:
        children_list = Region.objects.filter(parent_id=parent_id).all()
    children_json = []
    for child in children_list:
        children_json.append({'id': child.id, 'name': child.name})
    return JsonResponse(children_json, safe=False)


@csrf_exempt
def create_shipping(request):
    if request.user is None:
        return redirect('sign_in')
    if request.method == 'POST':
        data = post_data(request.body)
        consumer_id = request.user.id
        is_default = data.get('is_default')
        redemption_id = data.get('redemption_id')
        shipping_id = int(data.get('shipping_id'))
        if is_default == 'true':
            Shipping.objects.filter(Q(consumer_id=consumer_id) & Q(is_default=True)).update(is_default=False)
            is_default = True
        else:
            is_default = False
        if shipping_id > 0:
            old_shipping = Shipping.objects.get(id=shipping_id)
            old_shipping.nick_name = data.get('nick_name')
            old_shipping.mobile = data.get('mobile')
            old_shipping.province = data.get('province')
            old_shipping.city = data.get('city', '')
            old_shipping.district = data.get('district', '')
            old_shipping.street = data.get('street', '')
            old_shipping.is_default = is_default
            old_shipping.address = data.get('address')
            old_shipping.save()
        else:
            new_shipping = Shipping.objects.create(consumer_id=consumer_id,
                                                   nick_name=data.get('nick_name'),
                                                   mobile=data.get('mobile'),
                                                   province=data.get('province'),
                                                   city=data.get('city', ''),
                                                   district=data.get('district', ''),
                                                   street=data.get('street', ''),
                                                   is_default=is_default,
                                                   address=data.get('address')
                                                   )
            if redemption_id != '':
                Redemption.objects.filter(Q(id=redemption_id) & Q(consumer_id=request.user.id)).update(
                    shipping_id=new_shipping.id)
        return JsonResponse({'status': 'success', 'msg': '添加成功'})


def set_default_shipping(request):
    if request.user is None:
        return redirect('sign_in')
    shipping_id = request.GET.get('shipping_id')
    Shipping.objects.filter(consumer_id=request.user.id).update(is_default=False)
    Shipping.objects.filter(Q(id=shipping_id) & Q(consumer_id=request.user.id)).update(is_default=True)
    redirect_path = request.GET.get('redirect_path')
    if redirect_path:
        return redirect(redirect_path)
    else:
        return redirect('shipping')


def delete_shipping(request):
    if request.user is None:
        return redirect('sign_in')
    shipping_id = request.GET.get('shipping_id')
    Shipping.objects.filter(Q(id=shipping_id) & Q(consumer_id=request.user.id)).delete()
    return redirect('shipping')


@csrf_exempt
def set_redemption_shipping(request):
    if request.user is None:
        return redirect('sign_in')
    if request.method == 'POST':
        data = post_data(request.body)
        redemption_id = data.get('redemption_id')
        shipping_id = data.get('shipping_id')
        Redemption.objects.filter(Q(id=redemption_id) & Q(consumer_id=request.user.id)).update(shipping_id=shipping_id)
        return JsonResponse({'status': 'success'})


def show_redemption(request, id):
    if request.user is None:
        return redirect('sign_in')
    redemption = Redemption.objects.filter(Q(id=id) & Q(consumer_id=request.user.id)).first()
    if not redemption:
        return redirect('redemptions')
    return render(request, 'show_redemption.html', locals())


def new_shipping(request):
    if request.user is None:
        return redirect('sign_in')
    redemption_id = request.GET.get('redemption_id', '')
    redirect_path = request.GET.get('redirect_path', '')
    shipping_id = request.GET.get('id', 0)
    if int(shipping_id) > 0:
        address = Shipping.objects.filter(id=shipping_id).first()
    return render(request, 'new_shipping.html', locals())


from account.models import wxpay
@csrf_exempt
def transfer_notify(request):
    try:
        result = wxpay.callback(request.headers, request.body)
        print(result)
        if result.get('event_type') == 'TRANSFER.SUCCESS':
            # 处理成功逻辑，如更新订单状态
            pass
        return JsonResponse({'code': 'SUCCESS'})
    except Exception as e:
        return JsonResponse({'code': 'FAIL', 'message': str(e)})


def get_openid(request):
    code = request.GET.get('code')
    redemption_id = request.GET.get('redemption_id')
    if not code:
        return JsonResponse({'errmsg': 'missing code'}, status=400)

    # 用 code 换 openid
    url = 'https://api.weixin.qq.com/sns/oauth2/access_token'
    params = {
        'appid': settings.WECHAT_APPID,
        'secret': settings.WECHAT_SECRET,
        'code': code,
        'grant_type': 'authorization_code'
    }
    data = requests.get(url, params=params, timeout=3).json()
    openid = data.get('openid')
    if not openid:
        return JsonResponse({'errmsg': data}, status=400)

    # 保存数据库（幂等）
    if request.user.is_authenticated:
        request.user.openid = openid
        request.user.save()

    return JsonResponse({'openid': openid})

