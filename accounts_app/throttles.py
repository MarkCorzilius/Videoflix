from rest_framework.throttling import SimpleRateThrottle


class LoginEmailThrottle(SimpleRateThrottle):

    scope = "login"

    def get_cache_key(self, request, view):
        """Throttle login attempts per submitted email address."""

        email = request.data.get("email")
        if not email:
            return None
        return email


class RegisterEmailThrottle(SimpleRateThrottle):

    scope = "register"

    def get_cache_key(self, request, view):
        """Throttle registration attempts per client identity."""

        return self.get_ident(request)