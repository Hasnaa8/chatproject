from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from accounts.models import EmailOTP, Profile, CustomUser

admin.site.site_header = "Chat App Admin"
admin.site.site_title = "Chat App Admin Area"
admin.site.index_title = "Welcome to the Chat App Admin Area"

# admin.site.register(CustomUser)
# admin.site.register(Profile)
# admin.site.register(EmailOTP)

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'is_verified', 'is_staff', 'is_active']
    
    list_filter = ['is_verified', 'is_staff', 'is_active', 'date_joined']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Custom App Fields', {
            'fields': ('is_verified', 'following'),
        }),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'first_name', 'last_name', 'gender', 'phone_number', 'is_completed', 'updated']
    
    search_fields = ['user__username', 'user__email', 'first_name', 'last_name', 'phone_number']
    list_filter = ['gender', 'is_completed', 'created']
    
    readonly_fields = ['is_completed', 'created', 'updated']
    
    fieldsets = (
        ('Account Linking', {
            'fields': ('user', 'profile_picture')
        }),
        ('Personal Details', {
            'fields': ('first_name', 'last_name', 'gender', 'bio')
        }),
        ('Contact & Links', {
            'fields': ('phone_number', 'other_email', 'url', 'links')
        }),
        ('System Info', {
            'fields': ('is_completed', 'created', 'updated'),
        }),
    )


@admin.register(EmailOTP)
class EmailOTPAdmin(admin.ModelAdmin):
    list_display = ['user', 'otp', 'created_at', 'is_currently_valid']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at']

    # Custom column to show if the OTP is still valid based on your model method
    @admin.display(boolean=True, description='Is Valid (10 min)')
    def is_currently_valid(self, obj):
        return obj.is_valid()