from datetime import datetime
import json
from datetime import datetime
import requests
from django.conf import settings
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .models import BranchStore, CashExchange, SalesInviteCode
from django.core.cache import cache

def complete_store(request, code):
    current_user = request.user
    active_code = SalesInviteCode.objects.filter(Q(code=code) & Q(is_used=False)).first()
    if not current_user.is_authenticated:
        return redirect('home')
    if not active_code:
        return redirect('home')
    if current_user.is_sales():
        return redirect('home')
    active_code.is_used = True
    active_code.save()
    current_user.sales_rep = True
    current_user.save()
    return render(request, 'complete_store.html', locals())


def create_staff_store(request):
    if request.method == 'POST':
        if request.user.sales_rep:
            cur_staff = BranchStore.objects.filter(consumer=request.user).first()
            if cur_staff:
                cur_staff.name = request.POST['name']
                cur_staff.address = request.POST['address']
                cur_staff.employee = request.POST['employee']
                cur_staff.save()
            else:
                BranchStore.objects.create(consumer=request.user,
                    employee=request.POST['employee'],
                    name=request.POST['name'],
                    address=request.POST['address']
                )
            return redirect('home')
        else:
            return redirect('home')
    else:
        return None

def exchange_history(request):
    if request.user.sales_rep:
        exchange_lists = CashExchange.objects.filter(user=request.user).all()
        total_cash = 0
        pending_cash = 0
        completed_cash = 0
        for exchange in exchange_lists:
            total_cash += exchange.cash
            if exchange.status == 'pending':
                pending_cash += exchange.cash
            else:
                completed_cash += exchange.cash
        return render(request, 'exchange_history.html', locals())
    else:
        return redirect('home')


def redemption_detail(request, redemption_id):
    if request.user.sales_rep:
        exchange = CashExchange.objects.filter(Q(user=request.user) & Q(id=redemption_id)).first()
        if exchange:
            openid = request.user.openid
            appid = settings.WECHAT_APPID
            mch_id = settings.WECHAT_MCHID
            return render(request, 'redemption_detail.html', locals())
        else:
            return redirect('home')
    else:
        return redirect('home')


def withdrawal(request, redemption_id):
    if request.user.is_sales():
        order = CashExchange.objects.filter(Q(user=request.user) & Q(id=redemption_id)).first()
        if order and order.status == 'pending':
            status_code, body = request.user.wechat_transfer(order)
            if status_code == 200:
                order.status = 'processing'
                order.withdrawal_at = datetime.now()
                order.save()
                return JsonResponse(json.loads(body))
            else:
                return JsonResponse(json.loads(body))
        else:
            return JsonResponse({'status': 'error', 'msg': '数据异常'})
    else:
        return JsonResponse({'status': 'error', 'msg': '数据异常'})


def confirm_transfer(request, redemption_id):
    if request.user.is_sales():
        order = CashExchange.objects.filter(Q(user=request.user) & Q(id=redemption_id)).first()
        if order and order.status == 'processing':
            order.status = 'completed'
            order.save()
            return JsonResponse({'status': 'success', 'msg': '成功确认提现'})
        else:
            return JsonResponse({'status': 'error', 'msg': '数据异常'})
    else:
        return JsonResponse({'status': 'error', 'msg': '数据异常'})


def cancel_transfer(request, redemption_id):
    if request.user.is_sales():
        order = CashExchange.objects.filter(Q(user=request.user) & Q(id=redemption_id)).first()
        if order and order.status == 'processing':
            order.status = 'pending'
            order.withdrawal_at = None
            order.save()
            return JsonResponse({'status': 'success', 'msg': '取消提现'})
        else:
            return JsonResponse({'status': 'error', 'msg': '数据异常'})
    else:
        return JsonResponse({'status': 'error', 'msg': '数据异常'})


def manual_openid(request, redemption_id):
    code = request.GET.get('code')
    url = 'https://api.weixin.qq.com/sns/oauth2/access_token'
    params = {
        'appid': settings.WECHAT_APPID,
        'secret': settings.WECHAT_SECRET,
        'code': code,
        'grant_type': 'authorization_code'
    }
    data = requests.get(url, params=params, timeout=3).json()
    openid = data.get('openid')
    current_user = request.user
    if current_user.is_authenticated and current_user.openid is None:
        current_user.openid = openid
        current_user.save()
    return redirect('redemption_detail', redemption_id)
# Create your views here.
