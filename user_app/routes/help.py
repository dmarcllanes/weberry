from user_app.frontend.pages.help import help_page

async def show_help(req):
    user = req.scope.get("user")
    return help_page(user)
