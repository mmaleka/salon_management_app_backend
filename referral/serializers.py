from rest_framework import serializers
from .models import Profile, ReferralActivity, Reward
from django.contrib.auth.models import User
from .models import Product
from .models import Visit


# ProductSerializer for visits
class VisitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visit
        fields = '__all__'


# ProductSerializer for product 
class ProductSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'stock', 'image']


    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None


# UserSerializer to handle user registration and login
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'first_name']  # Add 'first_name' here
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', '')  # Save the first name
        )
        
        return user


# ProfileSerializer for user profile (points balance)
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['user', 'points_balance']


# ReferralActivitySerializer to record referral activities
class ReferralActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferralActivity
        fields = ['user', 'referred_user_email', 'points_awarded', 'created_at']


# RewardSerializer to display rewards
class RewardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reward
        fields = ['name', 'description', 'points_required']
