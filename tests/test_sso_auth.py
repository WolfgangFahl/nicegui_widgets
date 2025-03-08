"""
Created on 15.02.2025

@author: wf
"""
import logging
import os
import shutil
import tempfile
import yaml
from ngwidgets.basetest import Basetest
from wikibot3rd.sso import SSO, User
from wikibot3rd.sso_users import Sso_Users
from ngwidgets.sso_users_solution import SsoSolution
from unittest.mock import Mock, patch


class TestSsoAuth(Basetest):
    """
    test SSO Authentication
    """
    def setUp(self, debug=True, profile=True):
        """
        setup the test
        """
        Basetest.setUp(self, debug, profile)
        mock_ws = Mock()
        mock_ws.config = Mock()
        mock_ws.config.short_name = "test"
        self.mock_credentials(mock_ws)

    def tearDown(self):
        """
        cleanup temporary test directory
        """
        self.mock_credentials()
        Basetest.tearDown(self)

    def mock_credentials(self,webserver=None):
        """
        when called with webserver setup else tear down
        """
        def mocked_SSO_constructor(
               i_self,  # inner self for the patched SSO constructor
               host: str,
               database: str,
               sql_port: int = 3306,
               db_username: str = None,
               db_password: str = None,
               with_pool: bool = True,
               timeout: float = 3,
               debug: bool = False):
            # set properties
            i_self.host = host
            i_self.database = database
            i_self.sql_port = sql_port
            i_self.db_username = db_username
            i_self.db_password = db_password
            i_self.with_pool = with_pool
            i_self.timeout = timeout
            i_self.debug = debug
            # mock functions
            i_self.check_port = lambda: True
            i_self.get_user = lambda: self.mock_user
            i_self.check_credentials = lambda: True
            i_self.verify_password = lambda: True
            i_self.fetch_user_data_from_database = lambda: None
            msg=f"providing mocked SSO {i_self.__dict__} with check_port, get_user, ... returning default values"
            if self.debug:
                logging.warn(msg)
            else:
                logging.info(msg)
        if not webserver:
            if os.path.exists(self.test_dir):
                shutil.rmtree(self.test_dir)
        else:
            # Create temp test directory with credentials
            test_dir = tempfile.mkdtemp()
            solutions_path = os.path.join(test_dir, ".solutions", "test")
            os.makedirs(solutions_path)

            # Create minimal credentials file
            creds = {
                "server_url": "http://test-server",
                "username": "test-user",
                "password": "test-password",
                "secret": "test-secret",
                "wiki_id": "test-wiki"
            }
            self.credentials_path=os.path.join(solutions_path, "sso_credentials.yaml")
            with open(self.credentials_path, "w") as f:
                yaml.dump(creds, f)

            self.test_dir = test_dir
            # lets mock the SSO and user handling
            # from wikibot3rd to avoid actually creating
            # a database connection to the target wiki
            # mock a user (as would be returned from a
            # row in the mediawiki user table)
            mock_user = Mock(spec=User)
            mock_user.id = 1
            mock_user.name = "test_user"
            mock_user.is_admin = False
            # mock the Mediawiki Single Signon
            # which behaves as if we did a successful
            # remote MySQL DB access and port checking
            # (which we absolutely must avoid in the test environment!
            self.mock_sso = Mock(spec=SSO)
            with patch.object(SSO, "__init__", mocked_SSO_constructor):
                self.sso_auth = SsoSolution(webserver, credentials_path=self.credentials_path)
                self.sso_auth.users = Sso_Users(solution_name="test", debug=self.debug, credentials_path=self.credentials_path)

    def test_get_user_display_name(self):
        """
        test the user display name handling with different cases
        """
        test_cases = [
            # username, expected_display, is_admin, is_available, msg
            (None, "?", False, True, "sso available but no user"),
            ("test_user", "test_user", False, True, "regular user logged in"),
            ("admin_user", "admin_user🔑", True, True, "admin user logged in"),
        ]

        for username, expected_display, is_admin, is_available, msg in test_cases:
            with self.subTest(msg=msg):

                # Verify SSO availability
                self.assertEqual(self.sso_auth.users.is_available, is_available,
                                 f"Expected is_available={is_available}, but got {self.sso_auth.users.is_available}")

                # Setup login mock
                mock_login = Mock()
                self.sso_auth.login = mock_login
                mock_login.get_username.return_value = username

                if username and is_available:
                    mock_user = Mock()
                    mock_user.is_admin = is_admin
                    self.sso_auth.get_user = Mock(return_value=mock_user)

                user_display = self.sso_auth.get_user_display_name()
                if self.debug:
                    print(user_display)
                self.assertEqual(expected_display, user_display)
