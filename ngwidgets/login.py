'''
Created on 2023-10-31

@author: wf
'''
from nicegui import app,storage, ui,Client
from fastapi.responses import RedirectResponse

class Login(object):
    '''
    nicegui login support
    '''
    
    def __init__(self,webserver,users):
        '''
        Constructor
        '''
        self.webserver=webserver
        self.users=users
        
    def authenticated(self)->bool:
        """
        check whether the current user is authenticated
        """
        result=app.storage.user.get('authenticated', False)
        return result
    
    async def login(self,_client:Client):
        """
        login 
        """
        def try_login() -> None:  # local function to avoid passing username and password as arguments
            if self.users.check_password(username.value, password.value):
                app.storage.user.update({'username': username.value, 'authenticated': True})
                ui.open('/')
            else:
                ui.notify('Wrong username or password', color='negative')

        if self.authenticated():
            return RedirectResponse('/')
        self.webserver.setup_menu()
        with ui.card().classes('absolute-center'):
            username = ui.input('Username').on('keydown.enter', try_login)
            password = ui.input('Password', password=True, password_toggle_button=True).on('keydown.enter', try_login)
            ui.button('Log in', on_click=try_login)

        