from django.urls import path
from .views import  SignupView, \
                    LoginView, \
                    ProfileView, \
                    ReferView, \
                    RewardView, \
                    UserSearchView, \
                    UserProfileView, \
                    UserActivityView, \
                    RedeemRewardAPIView, \
                    PointsBalanceAPIView, \
                    ConfirmRedemptionAPIView, \
                    ConfirmRewardView, \
                    ProductView, \
                    ConfirmVisitView


urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('refer/', ReferView.as_view(), name='refer'),
    path('rewards/', RewardView.as_view(), name='rewards'),
    path('user/search/<str:username>/', UserSearchView.as_view(), name='user-search'),
    path('user/profile/', UserProfileView.as_view(), name='user_profile'),
    path('user/activity/', UserActivityView.as_view(), name='user-activity'),
    path('redeem-reward/', RedeemRewardAPIView.as_view(), name='redeem-reward'),
    path('profile/points/', PointsBalanceAPIView.as_view(), name='points-balance'),

    path('confirm-redemption/<int:activity_id>/', ConfirmRedemptionAPIView.as_view(), name='confirm_redemption'),
    path('admin/confirm-reward/<int:pk>/', ConfirmRewardView.as_view(), name='confirm_reward'),

    path('products/', ProductView.as_view(), name='product'),
    path('products/<int:pk>/', ProductView.as_view(), name='product-update'),
    
    path('confirm-visit/', ConfirmVisitView.as_view(), name='confirm-visit'),

]