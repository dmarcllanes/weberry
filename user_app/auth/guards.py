"""
FastHTML Beforeware: session-aware auth guard.
Redirects to /login if no session; otherwise injects user into request scope.
"""

from fasthtml.common import RedirectResponse

from user_app.auth.login import get_current_user

login_redir = RedirectResponse("/login", status_code=303)


async def auth_beforeware(req, sess):
    user_id = sess.get("user_id", None)
    if not user_id:
        return login_redir
    user = get_current_user(sess)
    if user is None:
        sess.clear()
        return login_redir
    
    # Inject avatar from session (transient)
    avatar_url = sess.get("avatar_url")
    if avatar_url:
        user.avatar_url = avatar_url
        
    req.scope["user"] = user
