from .forms import TweetRequestForm 
from rest_framework import viewsets 
from django.core import serializers 
from rest_framework.response import Response 
from rest_framework import status 
from django.http import JsonResponse 
from .models import TweetRequest 
from .serializer import TweetRequestSerializers 

import json
import requests
import pickle

import keras
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
import re

from django.shortcuts import render 
from django.contrib import messages 

class TweetView(viewsets.ModelViewSet): 
    queryset = TweetRequest.objects.all() 
    serializer_class = TweetRequestSerializers 


def create_header():
    with open('./.twitter_cred.json') as f:
        data = json.load(f)

        bearer = data["bearer_token"]
        headers = {
            'Authorization': 'Bearer '+bearer,
            'User-Agent': 'v2RecentSearchPython'
        }
        
        return headers

def get_tweet(category):
    query_params = {
        "query": category + " -is:retweet -has:images -has:emoji lang:en",
    }

    response = requests.get("https://api.twitter.com/2/tweets/search/recent", params=query_params, headers=create_header())

    if (response.status_code != 200):
        print("Error: status code not 200")
        print(response, query_params)
        raise Exception()

    print(response.text)

    return response.json()['data'][0]

def process_tweet(tweet, tweet_size):
    print(tweet)
    
    stop_words = stopwords.words('english')
    stemmer = SnowballStemmer('english')

    text_cleaning_re = "@\S+|https?:\S+|http?:\S|[^A-Za-z0-9]+"

    tweet = re.sub(text_cleaning_re, ' ', str(tweet).lower()).strip()
    tokens = []
    for token in tweet.split():
        if token not in stop_words:
            tokens.append(stemmer.stem(token))
    tweet =  ' '.join(tokens)

    tokenizer = pickle.load(open("../models/tokenizer.p", 'rb'))

    return pad_sequences(tokenizer.texts_to_sequences([tweet]), maxlen=tweet_size)

def status(category):
    try:
        tweet = process_tweet(get_tweet(category))
        clf_model = keras.models.load_model('../models/final_model.h5')
        return "positive" if clf_model.predict(tweet) else "negative"

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