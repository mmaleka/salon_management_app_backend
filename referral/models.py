import random
import string

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Visit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    visit_date = models.DateTimeField(auto_now_add=True)
    points_awarded = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.visit_date}"

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)  # Quantity in stock
    image = models.ImageField(upload_to='product_images/')  # Image field

    def __str__(self):
        return self.name
    


class Activity(models.Model):
    ACTION_CHOICES = [
        ('referral', 'Referred a Friend'),
        ('reward', 'Redeemed Reward'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    action = models.CharField(max_length=255, choices=ACTION_CHOICES)
    points = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    confirmed = models.BooleanField(default=False)  # New field to track admin confirmation

    def __str__(self):
        return f"{self.user.username} - {self.get_action_display()} - {self.points} points"


# Profile model linked to the user model
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    points_balance = models.IntegerField(default=0)  # User's points balance
    referral_code = models.CharField(max_length=10, unique=False, blank=True)  # Referral code
    referred_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='referrals')

    def update_points(self, points, action_type):
        # Update points balance
        self.points_balance += points
        self.save()

        # Log the activity
        Activity.objects.create(user=self.user, action=action_type, points=points)


    def __str__(self):
        return f"{self.user.username} Profile"


# Function to generate a random referral code
def generate_referral_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))


# Signal to automatically create Profile and generate referral code
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance)
        profile.referral_code = generate_referral_code()
        profile.save()

# ReferralActivity model to track user referral actions
class ReferralActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    referred_user_email = models.EmailField()
    points_awarded = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Referral by {self.user.username} to {self.referred_user_email}"


class Reward(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rewards')
    reward_name = models.CharField(max_length=255, null=True, blank=True)
    reward_points = models.PositiveIntegerField(null=True, blank=True)
    date_redeemed = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    confirmed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='confirmed_rewards')
    confirmed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.reward_name} - {self.user.username} - {self.status}"

    def confirm_reward(self, manager):
        """Confirm the reward and log the manager and timestamp."""
        self.status = 'Confirmed'
        self.confirmed_by = manager
        self.confirmed_at = timezone.now()
        self.save()
