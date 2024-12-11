from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from .models import Profile, ReferralActivity, Reward, Activity, Product, Visit
from .serializers import UserSerializer, ProfileSerializer, ReferralActivitySerializer, RewardSerializer, ProductSerializer, VisitSerializer
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from rest_framework.permissions import IsAdminUser
from django.utils import timezone
from django.contrib import messages
from django.views import View



class ConfirmVisitView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        admin_password = request.data.get('password')
        user = request.user  # The logged-in user making the request

        # Authenticate admin (replace 'mmaleka' with the actual admin username or get dynamically)
        admin_user = authenticate(username='mmaleka', password=admin_password)

        if admin_user and admin_user.is_staff:
            # Award points if admin authentication is successful
            points = 10
            visit = Visit.objects.create(user=user, points_awarded=points)

            # Update the user's profile points balance
            user_profile = user.profile
            user_profile.points_balance += points
            user_profile.save()

            return Response(
                {'points_balance': user_profile.points_balance, "message": f"Visit confirmed! {points} points awarded. Total points: {user_profile.points_balance}"},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {"detail": "Invalid admin password."},
                status=status.HTTP_403_FORBIDDEN
            )
    

# Rewards view to show available rewards
class ProductView(APIView):
    def get(self, request, *args, **kwargs):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # Handle POST request: Create a new product
    def post(self, request, *args, **kwargs):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Handle PATCH request: Update an existing product
    def patch(self, request, *args, **kwargs):
        try:
            product_id = kwargs.get('pk')
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class ConfirmRewardView(View):
    def post(self, request, pk):
        reward = get_object_or_404(Reward, pk=pk)

        # Check if the reward is already confirmed
        if reward.status == 'Pending':
            reward.status = 'Confirmed'
            reward.save()

            # Add a success message
            messages.success(request, f'Reward "{reward.reward_name}" confirmed successfully.')
        else:
            messages.warning(request, 'Reward is already confirmed.')

        # Redirect back to the rewards list in the admin panel
        return redirect('/admin/your_app/reward/')

# View to redeem multiple rewards
class RedeemRewardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        rewards = request.data.get('rewards', [])

        # Validate rewards list
        if not rewards or not isinstance(rewards, list):
            return Response(
                {'success': False, 'message': 'Invalid reward data.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        profile = request.user.profile
        total_points_required = sum(reward.get('reward_points', 0) for reward in rewards)

        # Check if the user has enough points
        if profile.points_balance < total_points_required:
            return Response(
                {'success': False, 'message': 'Insufficient points for the selected rewards.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        

        # Check for unconfirmed redemptions for the same reward
        for reward in rewards:
            reward_name = reward.get('reward_name')
            if Activity.objects.filter(user=request.user, action=f"Redeemed {reward_name}", confirmed=False).exists():
                return Response(
                    {'success': False, 'message': f'You already have a pending redemption for {reward_name}.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            


        # Deduct points and log each reward redemption
        for reward in rewards:
            reward_name = reward.get('reward_name')
            reward_points = int(reward.get('reward_points', 0))

            if reward_name and reward_points > 0:
                # Deduct points for each reward
                profile.update_points(-reward_points, action_type='reward')

                Reward.objects.create(
                    user=request.user,
                    reward_name=reward_name,
                    reward_points=reward_points,
                    date_redeemed=timezone.now(),
                    status='Pending'
                )


        profile.save()

        return Response({
            'success': True,
            'message': 'Rewards redeemed successfully and are pending confirmation.',
            'new_balance': profile.points_balance
        }, status=status.HTTP_200_OK)


class ConfirmRedemptionAPIView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, activity_id):
        try:
            activity = Activity.objects.get(id=activity_id, confirmed=False)
            activity.confirmed = True
            activity.save()

            return Response({'success': True, 'message': 'Redemption confirmed successfully.'}, status=status.HTTP_200_OK)
        except Activity.DoesNotExist:
            return Response({'success': False, 'message': 'Activity not found or already confirmed.'}, status=status.HTTP_404_NOT_FOUND)



# View to fetch the user's current points balance
class PointsBalanceAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = request.user.profile
        return Response({'points': profile.points_balance}, status=status.HTTP_200_OK)



class UserActivityView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        activities = Activity.objects.filter(user=user).order_by('-date')

        # Format data for the response
        activity_data = [
            {
                'action': activity.get_action_display(),
                'date': activity.date.strftime("%Y-%m-%d"),
                'points': activity.points
            }
            for activity in activities
        ]

        return Response(activity_data, status=status.HTTP_200_OK)

class UserSearchView(APIView):
    def get(self, request, username, format=None):
        # Attempt to find the user by username
        user = get_object_or_404(User, username=username)
        # Serialize the user data
        serializer = UserSerializer(user)
        return Response(serializer.data)
    

# Signup view for new users
class SignupView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        first_name = request.data.get('first_name')
        referral_code = request.data.get('referral_code')  # Optional referral code

        if not username or not password or not first_name:
            return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

        # Create the user
        user = User.objects.create_user(username=username, password=password, first_name=first_name)

        # Create the profile
        profile = Profile.objects.get(user=user)

        # Handle referral code
        if referral_code:
            try:
                referrer_profile = Profile.objects.get(referral_code=referral_code)
                profile.referred_by = referrer_profile.user
                profile.points_balance += 10  # Reward the new user with 10 points
                referrer_profile.points_balance += 20  # Reward the referrer with 20 points

                referrer_profile.update_points(20, action_type='referral')

                referrer_profile.save()
                profile.save()
            except Profile.DoesNotExist:
                return Response({'error': 'Invalid referral code'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
    

# Login view to authenticate users
class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)



# Profile view to retrieve user points balance
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        profile = Profile.objects.get(user=user)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure only authenticated users can access this

    def get(self, request):
        user = request.user  # The authenticated user
        profile = Profile.objects.get(user=user)  # Fetch the profile for the user
        return Response({
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'points_balance': profile.points_balance,  # Include points balance
            "referral_code": profile.referral_code,  # Include the referral code
        })



# Referral view to refer a friend and add points
class ReferView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        referred_email = request.data.get('referred_email')
        user = request.user

        # Avoid duplicate referrals
        if ReferralActivity.objects.filter(user=user, referred_user_email=referred_email).exists():
            return Response({'error': 'This email has already been referred.'}, status=status.HTTP_400_BAD_REQUEST)

        # Award points for the referral
        points_awarded = 10
        ReferralActivity.objects.create(user=user, referred_user_email=referred_email, points_awarded=points_awarded)

        # Update user's profile points
        profile = Profile.objects.get(user=user)
        profile.points_balance += points_awarded
        profile.save()

        return Response({'message': 'Referral successful, points awarded.'})


# Rewards view to show available rewards
class RewardView(APIView):
    def get(self, request, *args, **kwargs):
        rewards = Reward.objects.all()
        serializer = RewardSerializer(rewards, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



# git remote add origin https://github.com/mmaleka/salon_management_app_backend.git
# git branch -M main
# git push -u origin main