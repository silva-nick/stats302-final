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
import requests
import os

from keras.models import load_model
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
    with open(os.path.join(os.path.dirname(__file__), './.twitter_cred.json')) as f:
        data = json.load(f)

        bearer = data["bearer_token"]
        headers = {
            'Authorization': 'Bearer '+bearer,
            'User-Agent': 'v2RecentSearchPython'
        }
        
        return headers

def get_tweet(category):
    query_params = {
        "query": category + " -is:retweet -has:images lang:en",
    }

    response = requests.get("https://api.twitter.com/2/tweets/search/recent", params=query_params, headers=create_header())

    if (response.status_code != 200):
        print("Error: status code not 200")
        print(response, query_params)
        raise Exception("ERROR", response.text)

    print(response.text)

    return response.json()['data'][0]['text']

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

    cur_dir = os.path.dirname(__file__)
    tokenizer = pickle.load(open(os.path.join(cur_dir, 'models\\tokenizer.p'), 'rb'))

    return pad_sequences(tokenizer.texts_to_sequences([tweet]), maxlen=tweet_size)

def status_(category):
    try:
        tweet_raw = get_tweet(category)
        tweet = process_tweet(tweet_raw, 40)
        cur_dir = os.path.dirname(__file__)
        clf_model = load_model(os.path.join(cur_dir, 'models\\final_model.h5'))
        return ("Positive", tweet_raw, "#9cd6a3") if round(clf_model.predict(tweet)[0][0]) else ("Negative", tweet_raw, "#d69c9c")
    except ValueError as e: 
        return Response(e.args[0], status.HTTP_400_BAD_REQUEST) 

def FormView(request):
    if request.method=='POST':
        form=TweetRequestForm(request.POST or None)

        if form.is_valid():
            category = form.cleaned_data['category']
            result, tweet, color = status_(category)
            return render(request, 'status.html', {"status": result, "tweet":tweet, "color":color}) 
            
    form=TweetRequestForm()
    return render(request, 'form.html', {'form':form})