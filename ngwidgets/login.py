"""
Created on 2023-10-31

@author: wf
"""

from fastapi.responses import RedirectResponse
from nicegui import app, ui


class Login(object):
    """
    nicegui login support
    """

    def __init__(self, webserver, users):
        """
        Constructor
        """
        self.webserver = webserver
        self.users = users

    def authenticated(self) -> bool:
        """
        check whether the current user is authenticated
        """
        result = app.storage.user.get("authenticated", False)
        return result

    async def logout(self):
        """
        logout
        """
        app.storage.user.update({"username": None, "authenticated": False})

    def get_username(self) -> str:
        """
        Get the username of the currently logged-in user
        """
        return app.storage.user.get("username", "?")

    async def login(self, solution):
        """
        login
        """
        # this might not work if there as already been HTML output
        if self.authenticated():
            return RedirectResponse("/")

        await solution.setup_content_div(self.show_login)

    async def show_login(self):
        """
        show the login view
        """

        def try_login() -> (
            None
        ):  # local function to avoid passing username and password as arguments
            if self.users.check_password(username.value, password.value):
                app.storage.user.update(
                    {"username": username.value, "authenticated": True}
                )
                ui.navigate.to("/")
            else:
                ui.notify("Wrong username or password", color="negative")

        with ui.card().classes("absolute-center"):
            username = ui.input("Username").on("keydown.enter", try_login)
            password = ui.input(
                "Password", password=True, password_toggle_button=True
            ).on("keydown.enter", try_login)
            ui.button("Log in", on_click=try_login)
