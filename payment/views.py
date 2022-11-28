import os

import stripe
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView
from dotenv import load_dotenv

from payment.models import Item, Order, Content
from users.models import Profile

load_dotenv()


class ListProductsView(View):
    def post(self, request, *args, **kwargs):
        order = Order.objects.get(profile__user=self.request.user)
        item = Item.objects.get(id=request.POST['add'])

        total_amount = order.total_amount + item.price
        order.total_amount = total_amount
        order.save()

        Content.objects.get_or_create(item=item, order=order)
        product = Item.objects.all()

        context = {
            "products": product,
            "user": self.request.user.is_authenticated,
            "PUBLIC_API_KEY": os.getenv('PUBLIC_API_KEY'),
        }
        return render(request, 'payment/index.html', context)

    def get(self, request, *args, **kwargs):
        product = Item.objects.all()
        context = {
            "products": product,
            "user": self.request.user.is_authenticated,
            "PUBLIC_API_KEY": os.getenv('PUBLIC_API_KEY'),
        }
        return render(request, 'payment/index.html', context)


class BasketView(View):
    def post(self, request, *args, **kwargs):
        order = Order.objects.get(profile__user=self.request.user)
        products = Item.objects.filter(content__order=order)

        if 'delete' in request.POST:
            delete_item = request.POST['delete']
            item = Item.objects.get(id=int(delete_item))
            order.total_amount -= item.price
            order.save()

        context = {
            "PUBLIC_API_KEY": os.getenv('PUBLIC_API_KEY'),
            "order": order,
            "user": self.request.user.is_authenticated,
            "flag": order.get_current_currency(products),
            "products": products
        }
        return render(request, "payment/basket.html", context)

    def get(self, request, *args, **kwargs):
        try:
            order = Order.objects.get(profile__user=self.request.user)
            products = Item.objects.filter(content__order=order)
        except:
            profile = Profile.objects.get(user=self.request.user)
            Order.objects.create(profile=profile, currency='usd')
            order = Order.objects.get(profile__user=self.request.user)
            products = Item.objects.filter(content__order=order)

        context = {
            "flag": order.get_current_currency(products),
            "PUBLIC_API_KEY": os.getenv('PUBLIC_API_KEY'),
            "order": order,
            "user": self.request.user.is_authenticated,
            "products": products,
        }
        return render(request, "payment/basket.html", context)


class CreateCheckoutSession(View):
    def post(self, request, *args, **kwargs) -> JsonResponse:
        product_id = self.kwargs['pk']
        product = Item.objects.get(id=product_id)
        DOMAIN = os.getenv('DOMAIN')
        SECRET_API_KEY = os.getenv('SECRET_API_KEY')

        checkout_session = stripe.checkout.Session.create(
            api_key=SECRET_API_KEY,
            line_items=[
                {
                    'price_data': {
                        'currency': product.currency,
                        'unit_amount': product.price,
                        'product_data': {
                            'name': product.product_name
                        }
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=DOMAIN + '/api/v1/success/',
            cancel_url=DOMAIN + '/api/v1/cancel/',
        )

        return JsonResponse({'id': checkout_session.id})


class CreateCheckoutSessionOrder(View):
    def post(self, request, *args, **kwargs) -> JsonResponse:
        product_id = self.kwargs['pk']
        order = Order.objects.get(id=product_id)
        tax_model = Order.get_tax(order)
        discount_model = Order.get_discount(order)

        DOMAIN = os.getenv('DOMAIN')
        SECRET_API_KEY = os.getenv('SECRET_API_KEY')

        line_items = [
            {
                'price_data': {
                    'currency': order.currency,
                    'unit_amount': order.total_amount,
                    'product_data': {
                        'name': order.order_name
                    }
                },
                'quantity': 1,
            },
        ]
        discounts = []

        if tax_model != 0:
            tax = stripe.TaxRate.create(
                api_key=SECRET_API_KEY,
                display_name=tax_model.display_name,
                jurisdiction=tax_model.jurisdiction,
                percentage=tax_model.percentage,
                inclusive=tax_model.inclusive
            )
            line_items[0]['tax_rates'] = [tax.id]

        if discount_model != 0:
            coupon = stripe.Coupon.create(
                api_key=SECRET_API_KEY,
                duration=discount_model.duration,
                percent_off=discount_model.percents,
            )
            discounts.append({'coupon': coupon})

        checkout_session = stripe.checkout.Session.create(
            api_key=SECRET_API_KEY,
            line_items=line_items,
            mode='payment',
            discounts=discounts,
            success_url=DOMAIN + '/api/v1/success/',
            cancel_url=DOMAIN + '/api/v1/cancel/',
        )

        return JsonResponse({'id': checkout_session.id})


class SuccessView(View):
    def get(self, request, *args, **kwargs):
        Order.objects.get(profile__user=self.request.user).delete()
        return render(request, 'payment/success.html')


class CancelView(TemplateView):
    template_name = 'payment/cancel.html'
