"""
Aggregation helpers for building a volunteer's portfolio.
"""

from .models import PortfolioProfile, SavedListing


def get_or_create_portfolio_profile(user):
    profile, _created = PortfolioProfile.objects.get_or_create(user=user)
    return profile


def build_portfolio_context(user):
    """
    Aggregate a user's profile settings and saved opportunities into a
    single context dict, used both by the JSON summary endpoint and the
    PDF export template.
    """
    profile = get_or_create_portfolio_profile(user)
    saved_listings = (
        SavedListing.objects.filter(user=user)
        .select_related('listing')
        .prefetch_related('listing__tags')
        .order_by('-created_at')
    )

    return {
        'user': user,
        'profile': profile,
        'saved_listings': saved_listings,
    }
