import stripe
from django.conf import settings
from django.views import View
from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.views.decorators.csrf import csrf_exempt
import datetime
import stripe
from django.conf import settings
from django.shortcuts import render, redirect
from .form import ProductForm
from .models import Product
# Create your views here.
# stripe API key
stripe.api_key = 'sk_test_51MmEURSCqNOD6uDi2mQxr1hwCSu7AVI4A3bYetbnmg6JKwqlPcTo7b0CZAn7snyKMNjxkbKa0H6e3p7KK1Cygdn500g53jMfBT'

# Stripe secrate key = sk_test_51MmEURSCqNOD6uDi2mQxr1hwCSu7AVI4A3bYetbnmg6JKwqlPcTo7b0CZAn7snyKMNjxkbKa0H6e3p7KK1Cygdn500g53jMfBT

class subscription(View):
    @swagger_auto_schema(tags=['sub'], responses={200: openapi.Response('Success')})
    def create_checkout_session(request):
        if request.method == 'GET':
            customer_id = None
            customer = stripe.Customer.list(email='mitul7161@gmail.com', limit=1).data
            if customer:
                customer_id = customer[0].id
            else:
                # Create a new customer object in Stripe
                customer = stripe.Customer.create(email='mitul7161@gmail.com')
                customer_id = customer.id
            domain_url = 'http://127.0.0.1:8000/'
            stripe.api_key = settings.STRIPE_SECRET_KEY
            try:
                checkout_session = stripe.checkout.Session.create(
                    customer=customer_id,
                    client_reference_id=request.user.id if request.user.is_authenticated else None,
                    success_url=domain_url + 'success?session_id={CHECKOUT_SESSION_ID}',
                    cancel_url=domain_url + 'cancel/',
                    payment_method_types=['card'],
                    mode='subscription',
                    metadata ={
                        # 'user_id': request.user.id if request.user.is_authenticated else None,
                        # 'user_email': request.user.email if request.user.is_authenticated else None,
                        'user_id': '1',
                        'user_email': 'mitul7161@gmail.com',
                        'price_id': 'price_1MmEdSSCqNOD6uDiGdYbJJHJ',
                        'subscription_type': 'monthly',
                    },
                    line_items=[
                        {
                            'price': 'price_1MmEdSSCqNOD6uDiGdYbJJHJ',
                            'quantity': 1,
                        }
                    ],
                )
                # return JsonResponse(checkout_session)
                return redirect(checkout_session.url, code=303)
            except Exception as e:
                return JsonResponse({'error': str(e)})

    @swagger_auto_schema(tags=['sub'], responses={200: openapi.Response('Success')})
    def success(request):
        return JsonResponse({'success': True})

    @swagger_auto_schema(tags=['sub'] , responses={200: openapi.Response('Cancelled')})
    def cancel(request):
        return JsonResponse({'cancelled': True})

    @swagger_auto_schema(tags=['sub'] , responses={200: openapi.Response('History')})
    def history(request):
        payment_list = stripe.PaymentIntent.list(customer='cus_NXKO7TCIv5stCU')


        for payment in payment_list.data:
            payment_amount = payment.amount / 100
            payment_date = datetime.datetime.fromtimestamp(payment.created).strftime('%Y-%m-%d %H:%M:%S')
            payment_status = payment.status
            print(f"Payment of {payment_amount} was made on {payment_date} and has a status of {payment_status}.")
        return JsonResponse(payment_list)
    
    @csrf_exempt
    @swagger_auto_schema(tags=['sub'] , responses={200: openapi.Response('Webhook')})
    def webhook(request):
        event = None
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            # Invalid payload
            raise e
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            raise e
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
        else :
            return JsonResponse({'error': 'Invalid event type'})

        user_id = session['metadata']['user_id']
        customer_id = session['customer']
        user_email = session['metadata']['user_email']
        price_id = session['metadata']['price_id']
        subscription_type = session['metadata']['subscription_type']
        subscription = session['subscription']
        start_date_time = datetime.datetime.fromtimestamp(session['created']).strftime('%Y-%m-%d %H:%M:%S')
        end_date_time = datetime.datetime.fromtimestamp(session['expires_at']).strftime('%Y-%m-%d %H:%M:%S') 
        amount = session['amount_total']
        currency = session['currency']
    
        



        # invoice = session['invoice']
        # stripe.Invoice.send_invoice(invoice)
        print(session,start_date_time,end_date_time)
        return JsonResponse(session)
    
    @swagger_auto_schema(tags=['sub'] , responses={200: openapi.Response('Subscription')})
    def cancel_subscription(request):
        subscription = stripe.Subscription.retrieve(
            'sub_1Mo0hnSCqNOD6uDi96NLdLC5',
        )
        subscription.delete()
        return JsonResponse(subscription)
    



    def create_product(request):
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            stripe_product = stripe.Product.create(
                name=product.name,
                description=product.description
            )
            stripe_price = stripe.Price.create(
                product=stripe_product.id,
                unit_amount=int(product.price * 100),
                currency='usd',
                recurring={
                    'interval': product.interval,
                    'interval_count': product.interval_count,
                    'trial_period_days': product.trial_period_days
                }
            )
            product.stripe_product_id = stripe_product.id
            product.stripe_price_id = stripe_price.id
            product.save()
            return redirect('product_list')
        return render(request, 'create_product.html', {'form': form})
    
    def product_list(request):
        products = Product.objects.all()
        return render(request, 'product_list.html', {'products': products})