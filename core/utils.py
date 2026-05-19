from datetime import date

def has_active_subscription(user):
    if not user.is_authenticated:
        return False

    profile = user.userprofile

    if not profile.is_subscribed:
        return False

    if profile.subscription_expiry and profile.subscription_expiry < date.today():
        return False

    return True
