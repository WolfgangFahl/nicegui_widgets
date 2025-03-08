"""
Created on 2025-02-15

@author: wf
"""

from fastapi.responses import RedirectResponse
from ngwidgets.login import Login
from ngwidgets.webserver import WebSolution, NiceGuiWebserver
from nicegui import Client, ui
from wikibot3rd.sso import User
from wikibot3rd.sso_users import Sso_Users

class SsoSolution(WebSolution):
    """
    Encapsulates SSO authentication setup and user handling
    """
    def __init__(self, webserver: NiceGuiWebserver, client: Client = None, credentials_path=None):
        """
        Initialize SSO authentication

        Args:
            webserver: The webserver instance to set up SSO for
            client: The client instance (can be None for non-client specific solutions)
            credentials_path: Optional path to the SSO credentials file
        """
        super().__init__(webserver, client)  # Call parent constructor with both required parameters
        self.users = Sso_Users(webserver.config.short_name, credentials_path=credentials_path)

        self.login = Login(webserver, self.users)

    def get_user(self) -> User:
        """
        Get the current authenticated user

        Returns:
            User: The current user object or None if not authenticated
        """
        user = None
        username = self.login.get_username()
        if username and self.users.is_available:
            user = self.users.sso.get_user(username)
        return user

    def get_user_display_name(self) -> str:
        """
        Get the display name for the current user with admin indicator

        Returns:
            str: Username with optional admin indicator
        """
        username = self.login.get_username()
        if username is None:
            username = "?"
        user = self.get_user()
        admin_flag = "🔑" if user and user.is_admin else ""
        user_display = f"{username}{admin_flag}"
        return user_display

    async def logout(self):
        """Handle user logout"""
        await self.login.logout()

    def as_html(self) -> str:
        """
        Get the user details as HTML markup

        Returns:
            str: HTML markup for the user details or error message
        """
        user = self.get_user()
        html_markup = "<h1>User Details</h1>"
        if not user:
            html_markup += "<p>No user logged in</p>"
        else:
            html_markup += f"""
            <p><strong>ID:</strong> {user.id}</p>
            <p><strong>Name:</strong> {user.name}</p>
            <p><strong>Real Name:</strong> {user.real_name}</p>
            <p><strong>Email:</strong> {user.email}</p>
            <p><strong>Edit Count:</strong> {user.editcount}</p>
            """
        return html_markup

    async def show_login(self):
        """Show the login page"""
        await self.login.login(self)

    async def show_user_details(self):
        """Show the user details page"""
        def show():
            self.logout_button = ui.button(
                "logout", icon="logout",
                on_click=self.logout
            )
            ui.html(self.as_html())
        await self.setup_content_div(show)

    def configure_menu(self):
        """Configure the user menu"""
        display_name = self.get_user_display_name()
        self.link_button(display_name, "/user", "person")
        # make sure the link exists
        self.register_pages()

    def register_pages(self):
        """Register the SSO-related pages"""
        @ui.page("/user")
        async def show_user(client: Client):
            if not  self.login.authenticated():
                return RedirectResponse("/login")
            return await self.webserver.execute_action(
                client,
                solution_class=SsoSolution,
                wanted_action=SsoSolution.show_user_details
            )

        @ui.page("/login")
        async def login(client: Client):
            return await self.webserver.execute_action(
                client,
                solution_class=SsoSolution,
                wanted_action=SsoSolution.show_login
            )