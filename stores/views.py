from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.serializers import serialize
from django.conf import settings
import json
import requests
from .models import Store, Plush
from django.core.cache import cache


def store_list(request):
    """店铺列表页面"""
    stores = Store.objects.filter(is_active=True)
    return render(request, 'stores/store_list.html', {'stores': stores})


@csrf_exempt
@require_http_methods(["POST"])
def get_nearest_stores(request):
    """获取最近的店铺列表API"""
    try:
        data = json.loads(request.body)
        user_lat = float(data.get('latitude'))
        user_lng = float(data.get('longitude'))
        limit = int(data.get('limit', 10))

        # 获取最近的店铺
        nearest_stores = Store.get_nearest_stores(user_lat, user_lng, limit)

        # 构建响应数据
        result = []
        for store, distance in nearest_stores:
            human_distance = ""
            if distance > 1:
                human_distance = f"{round(distance, 2)} km"
            else:
                human_distance = f"{int(distance * 1000)} m"
            result.append({
                'id': store.id,
                'name': store.name,
                'address': store.address,
                'phone': store.phone,
                'description': store.description,
                'latitude': store.latitude,
                'longitude': store.longitude,
                'business_hours': store.business_hours,
                'distance': human_distance
            })

        return JsonResponse({
            'success': True,
            'stores': result,
            'count': len(result)
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@csrf_exempt
@require_http_methods(["POST"])
def geocode_address(request):
    """地址地理编码API - 将地址转换为经纬度"""
    try:
        data = json.loads(request.body)
        address = data.get('address')

        if not address:
            return JsonResponse({
                'success': False,
                'error': '地址参数不能为空'
            })

        # 调用高德地理编码API
        api_key = '12233ccf85da7031c00a3f4ca01eebd1'
        if not api_key:
            return JsonResponse({
                'success': False,
                'error': '高德地图API Key未配置'
            })

        url = 'https://restapi.amap.com/v3/geocode/geo'
        params = {
            'key': api_key,
            'address': address,
            'output': 'json'
        }

        response = requests.get(url, params=params)
        result = response.json()

        if result.get('status') == '1' and result.get('geocodes'):
            location = result['geocodes'][0]['location']
            lng, lat = location.split(',')

            return JsonResponse({
                'success': True,
                'latitude': float(lat),
                'longitude': float(lng),
                'formatted_address': result['geocodes'][0].get('formatted_address', address)
            })
        else:
            return JsonResponse({
                'success': False,
                'error': '地址解析失败'
            })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@csrf_exempt
@require_http_methods(["POST"])
def reverse_geocode(request):
    """逆地理编码API - 将经纬度转换为地址"""
    try:
        data = json.loads(request.body)
        latitude = float(data.get('latitude'))
        longitude = float(data.get('longitude'))

        # 调用高德逆地理编码API
        api_key = '12233ccf85da7031c00a3f4ca01eebd1'
        if not api_key:
            return JsonResponse({
                'success': False,
                'error': '高德地图API Key未配置'
            })

        url = 'https://restapi.amap.com/v3/geocode/regeo'
        params = {
            'key': api_key,
            'location': f'{longitude},{latitude}',
            'output': 'json'
        }

        response = requests.get(url, params=params)
        result = response.json()

        if result.get('status') == '1' and result.get('regeocode'):
            regeocode = result['regeocode']
            human_address = ''
            if len(regeocode['formatted_address']) > 0:
                human_address = regeocode['formatted_address']
            else:
                human_address = f'纬度：{latitude} ,经度：{longitude}'
            return JsonResponse({
                'success': True,
                'address': human_address,
                'province': regeocode.get('addressComponent', {}).get('province', ''),
                'city': regeocode.get('addressComponent', {}).get('city', ''),
                'district': regeocode.get('addressComponent', {}).get('district', ''),
            })
        else:
            return JsonResponse({
                'success': False,
                'error': '坐标解析失败'
            })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


def search_store(request):
    url = 'https://restapi.amap.com/v5/place/text'
    params = {
        'key': '12233ccf85da7031c00a3f4ca01eebd1',
        'keywords': f'{request.GET.get("keywords")}',
    }
    response = requests.get(url, params=params)
    result = response.json()
    return JsonResponse(result)


def nearby_shops(request):
    fuxion_title = cache.get('fuxion_title', '福赏活动-附近门店')
    stores = Store.objects.filter(is_active=True)
    return render(request, 'nearby_shops.html', locals())


def introduction(request):
    fuxion_title = cache.get('fuxion_title', '福赏活动-介绍')
    return render(request, 'introduction.html', locals())


def tutorials(request):
    fuxion_title = cache.get('fuxion_title', '福赏活动-购买流程')
    return render(request, 'tutorials.html', locals())


def trophy(request):
    fuxion_title = cache.get('fuxion_title', '福赏活动-本期周边')
    plush = Plush.objects.filter(is_latest=True).first()
    return render(request, 'trophy.html', locals())
