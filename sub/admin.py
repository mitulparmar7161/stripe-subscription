from django.contrib import admin
from .models import Product
from .form import ProductForm
import stripe
from django.http import JsonResponse


class StripePlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'interval', 'interval_count', 'trial_period_days')


    def response_change(self,request,obj):
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

        return JsonResponse({'success': 'Product created successfully'})

admin.site.register(Product, StripePlanAdmin)