"""
FastHTML Beforeware that injects the current user into every request.
"""

from user_app.auth.login import get_current_user


async def auth_beforeware(req, sess):
    user = get_current_user()
    req.scope["user"] = user
