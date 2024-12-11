from django.contrib import admin
from .models import Profile, ReferralActivity, Reward, Activity, Product, Visit

# Register your models here.
admin.site.register(Product)
admin.site.register(Profile)
admin.site.register(ReferralActivity)
admin.site.register(Activity)
admin.site.register(Visit)


@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ('user', 'reward_name', 'reward_points', 'date_redeemed', 'status', 'confirm_reward_action')
    list_filter = ('status', 'date_redeemed')
    search_fields = ('user__username', 'reward_name')
    actions = ['confirm_selected_rewards']

    def confirm_reward_action(self, obj):
        if obj.status == 'Pending':
            return '<a href="/admin/confirm-reward/{}/" class="button">Confirm</a>'.format(obj.id)
        return 'Confirmed'
    confirm_reward_action.allow_tags = True
    confirm_reward_action.short_description = 'Confirm Reward'

    # Bulk action to confirm selected rewards
    def confirm_selected_rewards(self, request, queryset):
        count = queryset.update(status='Confirmed')
        self.message_user(request, f'{count} reward(s) confirmed successfully.')
    confirm_selected_rewards.short_description = 'Confirm selected rewards'
    



