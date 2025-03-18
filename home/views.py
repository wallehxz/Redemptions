import json
from django.db.models import Q
from django.shortcuts import render,redirect
from django.views.decorators.csrf import csrf_exempt
from account.models import Shipping, Region
from series.models import Series, Prize
from django.http import JsonResponse
from redeem.models import Redeem, Redemption
from urllib.parse import parse_qs

def post_data(body):
    decoded_str = body.decode('utf-8')
    parsed_data = parse_qs(decoded_str)
    single_value_data = {k: v[0] if v else '' for k, v in parsed_data.items()}
    json_data = json.dumps(single_value_data, ensure_ascii=False)
    return json.loads(json_data)

def index(request):
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
                new_redemption = Redemption.objects.create(redeem_id=redeem.id, consumer_id=request.user.id, prize_id=prize.id)
                default_shipping = Shipping.objects.filter(Q(is_default=True) & Q(consumer_id=request.user.id)).first()
                if default_shipping:
                    new_redemption.shipping_id = default_shipping.id
                    new_redemption.save()
                return JsonResponse({'status': 'success', 'msg': f'获得奖品【{prize.name}】一件'})
            else:
                return JsonResponse({'status': 'warning', 'msg': f'奖品库存不足，我们会尽快完成补货！'})
        else:
            return JsonResponse({'status': 'error', 'msg': '无效的抽将码!'})

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
        data = post_data(request.body)
        consumer_id = request.user.id
        district = data.get('district')
        id_default = data.get('id_default')
        redemption_id = data.get('redemption_id')
        if '请选择' in district:
            district = ''
        street = data.get('street')
        if '请选择' in street:
            street = ''
        if id_default == 'true':
            Shipping.objects.filter(Q(consumer_id=consumer_id) & Q(is_default=True)).update(is_default=False)
            id_default = True
        else:
            id_default = False
        if data.get('id'):
            old_shipping = Shipping.objects.get(id=data.get('id'))
            old_shipping.nick_name = data.get('nick_name')
            old_shipping.mobile = data.get('mobile')
            old_shipping.province = data.get('province')
            old_shipping.city = data.get('city')
            old_shipping.district = district
            old_shipping.street = street
            old_shipping.is_default = id_default
            old_shipping.address = data.get('address')
            old_shipping.save()
        else:
            new_shipping= Shipping.objects.create(consumer_id=consumer_id,
                nick_name=data.get('nick_name'),
                mobile=data.get('mobile'),
                province=data.get('province'),
                city=data.get('city'),
                district=district,
                street=street,
                id_default=id_default,
                address=data.get('address')
            )
            if redemption_id != '':
                Redemption.objects.filter(Q(id=redemption_id) & Q(consumer_id=request.user.id)).update(shipping_id=new_shipping.id)
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
    return render(request,'show_redemption.html', locals())

def new_shipping(request):
    if request.user is None:
        return redirect('sign_in')
    redemption_id = request.GET.get('redemption_id')
    if redemption_id is None:
        redemption_id = ''
    provinces_list = Region.objects.filter(Q(city='0') & Q(area='0') & Q(town='0'))
    return render(request, 'new_shipping.html', locals())
# Create your views here.
