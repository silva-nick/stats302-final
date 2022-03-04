from .forms import TweetRequestForm 
from rest_framework import viewsets 
from django.core import serializers 
from rest_framework.response import Response 
from rest_framework import status 
from django.http import JsonResponse 
from .models import TweetRequest 
from .serializer import TweetRequestSerializers 

import pandas as pd 
from django.shortcuts import render 
from django.contrib import messages 

class TweetView(viewsets.ModelViewSet): 
    queryset = TweetRequest.objects.all() 
    serializer_class = TweetRequestSerializers 

def status(category):
    try:
        # Load tweet
        # Load model
        # Make prediction
        return "positive" 
    except ValueError as e: 
        return Response(e.args[0], status.HTTP_400_BAD_REQUEST) 

def FormView(request):
    if request.method=='POST':
        form=TweetRequestForm(request.POST or None)

        if form.is_valid():
            category = form.cleaned_data['category']
            result = status(category)
            return render(request, 'status.html', {"data": result}) 
            
    form=TweetRequestForm()
    return render(request, 'form.html', {'form':form})