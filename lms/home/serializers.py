from .models import *
from rest_framework import serializers
from django.contrib.auth.models import User


class BookSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Book
        fields = ('title','author','isbn','quantity')


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ('user','name','contact_no')
 

class BorrowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrower
        fields = ('member','book')
 


from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super(MyTokenObtainPairSerializer, cls).get_token(user)

        # Add custom claims
        token['username'] = user.username
        return token