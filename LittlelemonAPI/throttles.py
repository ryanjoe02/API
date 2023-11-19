from rest_framework.throttling import UserRateThrottle


# Authenticated user can access ten times per minute
class TenCallsPerMinute(UserRateThrottle):
    scope = "ten"
