from django.contrib import admin

from .models import PortfolioProfile, SavedListing


@admin.register(PortfolioProfile)
class PortfolioProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'is_public', 'updated_at')
    search_fields = ('user__email', 'title')


@admin.register(SavedListing)
class SavedListingAdmin(admin.ModelAdmin):
    list_display = ('user', 'listing', 'created_at')
    search_fields = ('user__email', 'listing__title')
