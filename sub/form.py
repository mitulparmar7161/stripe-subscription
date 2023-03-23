from django import forms
from .models import Product
import stripe
from django.shortcuts import render, redirect




class ProductForm(forms.ModelForm):
    
    class Meta:
        model = Product
        fields = '__all__'




