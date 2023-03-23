from django.db import models

# Create your models here.

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    stripe_product_id = models.CharField(max_length=255)
    stripe_price_id = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    interval = models.CharField(max_length=50)
    interval_count = models.IntegerField(default=1)
    trial_period_days = models.IntegerField(default=0)

    def __str__(self):
        return str(self.name)
    