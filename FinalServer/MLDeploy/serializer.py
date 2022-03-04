from .models import TweetRequest
from rest_framework import serializers

class TweetRequestSerializers(serializers.ModelSerializer):
    class meta:
        model = TweetRequest
        fields='__all__'

    