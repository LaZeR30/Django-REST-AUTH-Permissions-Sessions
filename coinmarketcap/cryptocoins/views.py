from django.db.models import Q
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404

from cryptocoins.forms import CryptocurrencyForm
from cryptocoins.models import Cryptocurrency, Exchange


def is_staff(user):
    return user.is_staff


def index(request):
    order_param = request.GET.get('order_param', 'rank')
    order_direction = request.GET.get('order_direction', 'asc')
    order_by = 'rank'

    coins = Cryptocurrency.objects.all()

    search = request.GET.get('search')
    if search:
        coins = coins.filter(
            Q(name__icontains=search) | Q(exchange__name__icontains=search)
        )

    if order_param == 'price':
        order_by = 'price_usd'
    if order_direction == 'desc':
        order_by = '-' + order_by

    coins = coins.order_by(order_by)

    # initialize list of favorite books for current session
    request.session.setdefault('favorite_currencies', [])
    request.session.save()

    return render(request, 'index.html', {
        'order_param': order_param,
        'order_direction': order_direction,
        'coins': coins
    })


def detail(request, coin_id):
    coin = get_object_or_404(Cryptocurrency, id=coin_id)
    return render(request, 'detail.html', {
        'coin': coin
    })


def delete(request, coin_id):
    currency = Cryptocurrency.objects.get(id=coin_id)
    if request.method == 'GET':
        return render(
            request,
            'delete_cryptocurrency.html',
            context={'currency': currency}
        )
    elif request.method == "POST":
        currency.delete()
        return redirect('index')


@login_required
@user_passes_test(is_staff)
def create(request):
    if request.method == 'GET':
        cryptocurrency_form = CryptocurrencyForm()
        return render(
            request,
            'create_cryptocurrency.html',
            context={'cryptocurrency_form': cryptocurrency_form}
        )
    elif request.method == 'POST':
        cryptocurrency_form = CryptocurrencyForm(request.POST)
        if cryptocurrency_form.is_valid():
            cryptocurrency = cryptocurrency_form.save()
            return redirect('index')

        return render(
            request,
            'create_cryptocurrency.html',
            context={'cryptocurrency_form': cryptocurrency_form}
        )




@login_required
@user_passes_test(is_staff)
def edit(request, coin_id=None):
    cryptocurrency = get_object_or_404(Cryptocurrency, id=coin_id)
    if request.method == 'GET':
        cryptocurrency_form = CryptocurrencyForm(instance=cryptocurrency)
        return render(
            request,
            'edit_cryptocurrency.html',
            context={
                'cryptocurrecy': cryptocurrency,
                'cryptocurrency_form': cryptocurrency_form
            }
        )
    elif request.method == 'POST':
        cryptocurrency_form = CryptocurrencyForm(
            request.POST, instance=cryptocurrency)
        if cryptocurrency_form.is_valid():
            cryptocurrency_form.save()
            return redirect('index')
        return render(
            request,
            'edit_cryptocurrency.html',
            context={
                'cryptocurrecy': cryptocurrecy,
                'cryptocurrency_form': cryptocurrency_form
            }
        )


def favorites(request):
    currencies_ids = request.session.get('favorite_currencies', [])
    favorite_currencies = Cryptocurrency.objects.filter(id__in=currencies_ids)
    return render(
        request,
        'favorites.html',
        context={
            'favorite_currencies': favorite_currencies,
        }
    )


def add_to_favorites(request):
    request.session.setdefault('favorite_currencies', [])
    request.session['favorite_currencies'].append(request.POST.get('coin_id'))
    request.session.save()
    return redirect('index')


def remove_from_favorites(request):
    if request.session.get('favorite_currencies'):
        request.session['favorite_currencies'].remove(request.POST.get('coin_id'))
        request.session.save()
    return redirect('index')
