import json
from django.db.models import Q
from django.shortcuts import render,redirect
from django.views.decorators.csrf import csrf_exempt
from account.models import Shipping, Region
from series.models import Series, Prize
from django.http import JsonResponse
from redeem.models import Redeem, Redemption
from urllib.parse import parse_qs

def index(request):
    series = Series.objects.all()
    print(request.user)
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
        prize_list.append({'name': prize.name, 'image': prize.logo.url, 'description': f'库存数量({prize.inventory})'})
    return JsonResponse(prize_list, safe=False)

@csrf_exempt
def redemption(request):
    if request.method == 'POST':
        redeem_code = json.loads(request.body).get('redeem_code')
        redeem = Redeem.objects.filter(Q(number=redeem_code) & Q(status=0)).first()
        if redeem:
            prize = redeem.prize
            if prize.inventory > 0:
                prize.inventory -= 1
                prize.save()
                redeem.status = 1
                redeem.save()
                Redemption.objects.create(redeem_id=redeem.id, consumer_id=request.user.id, prize_id=prize.id)
                return JsonResponse({'status': 'success', 'msg': f'兑换奖品【{prize.name}】一件'})
            else:
                return JsonResponse({'status': 'warning', 'msg': f'奖品库存不足，我们会尽快完成补货！'})
        else:
            return JsonResponse({'status': 'error', 'msg': '错误！无效的兑换码。'})

def redemptions(request):
    if request.user is None:
        return redirect('sign_in')
    redemption_list = Redemption.objects.filter(consumer_id=request.user.id).order_by('-created_at')
    shipping_list = Shipping.objects.filter(consumer_id=request.user.id).all()
    return render(request,'redemptions.html', locals())

def shipping(request):
    if request.user is None:
        return redirect('sign_in')
    shipping_list = Shipping.objects.filter(consumer_id=request.user.id).all()
    provinces_list = Region.objects.filter(Q(city='0') & Q(area='0') & Q(town='0'))
    return render(request, 'shipping.html', locals())

def region_children(request):
    parent_id = request.GET.get('parent_id')
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
        decoded_str = request.body.decode('utf-8')
        parsed_data = parse_qs(decoded_str)
        single_value_data = {k: v[0] if v else '' for k, v in parsed_data.items()}
        json_data = json.dumps(single_value_data, ensure_ascii=False)
        data = json.loads(json_data)
        consumer_id = request.user.id
        district = data.get('district')
        if '请选择' in district:
            district = ''
        street = data.get('street')
        if '请选择' in street:
            street = ''
        if data.get('id'):
            shipping = Shipping.objects.get(id=data.get('id'))
            shipping.nick_name = data.get('nick_name')
            shipping.mobile = data.get('mobile')
            shipping.province = data.get('province')
            shipping.city = data.get('city')
            shipping.district = district
            shipping.street = street
            shipping.address = data.get('address')
            shipping.save()
        else:
            Shipping.objects.create(consumer_id=consumer_id,
                nick_name=data.get('nick_name'),
                mobile=data.get('mobile'),
                province=data.get('province'),
                city=data.get('city'),
                district=district,
                street=street,
                address=data.get('address')
            )
        return JsonResponse({'status':'success','msg':'添加成功'})

def set_default_shipping(request):
    if request.user is None:
        return redirect('sign_in')
    shipping_id = request.GET.get('shipping_id')
    Shipping.objects.filter(consumer_id=request.user.id).update(is_default=False)
    Shipping.objects.filter(Q(id=shipping_id) & Q(consumer_id=request.user.id)).update(is_default=True)
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
        decoded_str = request.body.decode('utf-8')
        parsed_data = parse_qs(decoded_str)
        single_value_data = {k: v[0] if v else '' for k, v in parsed_data.items()}
        json_data = json.dumps(single_value_data, ensure_ascii=False)
        data = json.loads(json_data)
        redemption_id = data.get('redemption_id')
        shipping_id = data.get('shipping_id')
        Redemption.objects.filter(Q(id=redemption_id) & Q(consumer_id=request.user.id)).update(shipping_id=shipping_id)
        return JsonResponse({'status': 'success'})
# Create your views here.
