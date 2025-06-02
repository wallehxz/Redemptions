
import json
from datetime import datetime
from django.db.models import Q
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from home.views import post_data
from account.models import Shipping, Region
from credits.models import Product, RedemptionCode, PointsTransaction, ProductSpec, ExchangeOrder
from redeem.models import Redemption


def mall(request):
    products = Product.objects.all()
    return render(request, "mall.html", locals())


@csrf_exempt
def redeem_points(request):
    if request.method == 'POST':
        if request.user is None:
            return JsonResponse({"status": 'error', "msg": '请登录操作'})
        redeem_code = json.loads(request.body).get('redeem_code')
        redeem = RedemptionCode.objects.filter(Q(code=redeem_code) & Q(is_used=False)).first()
        if redeem:
            redeem.is_used = True
            redeem.used_by = request.user
            redeem.used_at = datetime.now()
            redeem.save()
            current_user = request.user
            current_user.points = current_user.points + redeem.points_value
            current_user.save()
            PointsTransaction.objects.create(user=current_user, amount=redeem.points_value, transaction_type='earn', description='兑换码福力奖励')
            return JsonResponse({"status": 'success', "msg": f'兑换成功,奖励 {redeem.points_value} 福力', "points": current_user.human_points()})
        else:
            return JsonResponse({"status": 'error', "msg": '无效的兑换码'})


def redeem_history(request):
    redeem_list = ExchangeOrder.objects.filter(user=request.user).all()
    return render(request, "redeem_history.html", locals())


def transactions(request):
    trans_list = PointsTransaction.objects.filter(user=request.user).order_by('-created_at')
    return render(request, "transactions.html", locals())


def harvest(request):
    address_list = Shipping.objects.filter(consumer_id=request.user.id).all()
    provinces_list = Region.objects.filter(Q(city='0') & Q(area='0') & Q(town='0'))
    return render(request, "harvest.html", locals())


def product_detail(request, product_id):
    product = Product.objects.get(id=product_id)
    default = product.default_spec()
    harvest = Shipping.objects.filter(Q(consumer=request.user) & Q(is_default=True)).first()
    address_list = Shipping.objects.filter(consumer_id=request.user.id).all()
    if not harvest:
        harvest = Shipping.objects.filter(consumer=request.user).first()
    return render(request, "product_detail.html", locals())


@csrf_exempt
def exchange_product(request):
    if request.method == 'POST':
        current_user = request.user
        data = post_data(request.body)
        data = {key: int(value) for (key, value) in data.items()}
        spec = ProductSpec.objects.filter(id=data['spec_id']).first()
        if spec:
            if spec.stock < data['quantity']:
                return JsonResponse({'status': 'warning', 'msg': '当前商品规格库存不足，请减少兑换数量'})
        else:
            return JsonResponse({'status': 'error', 'msg': '当前商品规格已下架，请更换其他规格'})
        product = Product.objects.filter(id=data['product_id']).first()
        if not product:
            return JsonResponse({'status': 'error', 'msg': '当前商品已下架，请更换其他商品'})
        if current_user.points < data['total_points']:
            return JsonResponse({'status': 'error', 'msg': '福力余额不足，请继续积攒'})
        note_string = f"{product.name} - {spec.name} x {data['quantity']}"
        harvest = Shipping.objects.filter(Q(consumer=current_user) & Q(id=data['harvest_id'])).first()
        if not harvest:
            return JsonResponse({'status': 'error', 'msg': '收获地址与用户不匹配'})
        order = ExchangeOrder.objects.create(
            product=product,
            spec=spec,
            user=current_user,
            quantity=data['quantity'],
            total_points=data['total_points'],
            harvest=harvest,
            note=note_string,
        )
        spec.stock -= data['quantity']
        spec.save()
        current_user = request.user
        current_user.points -= data['total_points']
        current_user.save()
        PointsTransaction.objects.create(
            user=current_user,
            amount=data['total_points'],
            transaction_type='exchange',
            description=note_string
        )
        return JsonResponse({'status': 'success', 'order_id': order.id})


def redemption(request, order_id):
    redemption = ExchangeOrder.objects.filter(Q(id=order_id) & Q(user=request.user)).first()
    redemption
    return render(request, "redemption.html", locals())
