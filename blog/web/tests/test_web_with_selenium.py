import os
import shutil
from faker import Faker
from dotenv import load_dotenv

from django.conf import settings
from django.test import override_settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from ..models import Profile, Article

fake = Faker()

load_dotenv()


class WebDriver:

    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.binary_location = os.environ.get("chrome_options_binary_location")
        self.driver = webdriver.Chrome(service=Service(os.environ.get('path_to_webdriver_selenium')),
                                       options=chrome_options)
        self.driver.implicitly_wait(10)

    def quit(self):
        self.driver.quit()


class ProfileMixin:

    def __init__(self, driver, live_server_url, profile_attributes=None):
        self.driver = driver
        self.live_server_url = live_server_url
        if profile_attributes is not None:
            self.profile_attributes = profile_attributes
        else:
            self.profile_attributes = {
                'username': fake.name(),
                'email': fake.email(),
                'password': 'password',
            }

    def create_profile(self):
        return Profile.objects.create_user(**self.profile_attributes)

    def login(self):
        self.driver.get(f'{self.live_server_url}/web/login/')
        username_input = self.driver.find_element(By.ID, "id_username")
        password_input = self.driver.find_element(By.ID, "id_password")
        submit_button = self.driver.find_element(By.XPATH, '//form/p[3]/input')

        username_input.send_keys(self.profile_attributes.get('username'))
        password_input.send_keys(self.profile_attributes.get('password'))
        submit_button.click()


class HomePageWithAuthorizationTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.driver = WebDriver()
        cls.profile = ProfileMixin(cls.driver.driver, cls.live_server_url)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def add_articles(self, quantity, profile):
        for article_num in range(1, quantity + 1):
            Article.objects.create(
                title=fake.words(nb=3),
                content=f'Test title №{article_num}',
                profile=profile
            )

    def test_home_page_title(self):
        self.profile.create_profile()
        self.profile.login()
        self.assertIn("Home", self.driver.driver.title)

    def test_home_page_with_all_articles(self):
        current_user_profile = self.profile.create_profile()
        current_user_number_of_articles = 6
        self.add_articles(current_user_number_of_articles, current_user_profile)
        self.profile.login()

        rows = self.driver.driver.find_elements(By.XPATH, "//table[@class='table table-hover']/tbody/tr")
        self.assertEqual(current_user_number_of_articles, len(rows))

    def test_My_articles_link_on_home_page(self):
        current_user_profile = self.profile.create_profile()
        current_user_number_of_articles = 6
        self.add_articles(current_user_number_of_articles, current_user_profile)

        another_user_profile = ProfileMixin(self.driver.driver, self.live_server_url).create_profile()
        another_user_number_of_articles = 2
        self.add_articles(another_user_number_of_articles, another_user_profile)

        self.profile.login()
        my_articles_link = self.driver.driver.find_element(By.LINK_TEXT, "My_articles")
        my_articles_link.click()
        rows = self.driver.driver.find_elements(By.XPATH, "//table[@class='table table-hover']/tbody/tr")
        self.assertEqual(current_user_number_of_articles, len(rows))

    def test_All_articles_link_on_home_page(self):
        current_user_profile = self.profile.create_profile()
        current_user_number_of_articles = 1
        self.add_articles(current_user_number_of_articles, current_user_profile)

        another_user_profile = ProfileMixin(self.driver.driver, self.live_server_url).create_profile()
        another_user_number_of_articles = 2
        self.add_articles(another_user_number_of_articles, another_user_profile)

        self.profile.login()
        my_articles_link = self.driver.driver.find_element(By.LINK_TEXT, "My_articles")
        my_articles_link.click()
        rows = self.driver.driver.find_elements(By.XPATH, "//table[@class='table table-hover']/tbody/tr")
        self.assertEqual(current_user_number_of_articles, len(rows))

        all_articles_link = self.driver.driver.find_element(By.LINK_TEXT, "All_articles")
        all_articles_link.click()
        rows = self.driver.driver.find_elements(By.XPATH, "//table[@class='table table-hover']/tbody/tr")
        self.assertEqual(current_user_number_of_articles + another_user_number_of_articles, len(rows))

    def test_home_page_logout(self):
        self.profile.create_profile()
        self.profile.login()

        logout_link = self.driver.driver.find_element(By.CLASS_NAME, "logout")
        logout_link.click()
        p = self.driver.driver.find_element(By.TAG_NAME, "p").text
        self.assertEqual("In order to be able to view articles or write new articles you need to sign in", p)

    def test_going_to_edit_profile_page(self):
        self.profile.create_profile()
        self.profile.login()

        logout_link = self.driver.driver.find_element(By.LINK_TEXT, "Edit profile")
        logout_link.click()

        self.assertEqual("Edit an account", self.driver.driver.title)

    def test_home_page_adding_new_article(self):
        current_user_profile = self.profile.create_profile()
        current_user_number_of_articles = 1
        self.add_articles(current_user_number_of_articles, current_user_profile)
        self.profile.login()

        article_add_link = self.driver.driver.find_element(By.CLASS_NAME, "article_add")
        article_add_link.click()

        title_input = self.driver.driver.find_element(By.ID, "id_title")
        content_input = self.driver.driver.find_element(By.ID, "id_content")
        submit_button = self.driver.driver.find_element(By.XPATH, " //form/input[@class='btn btn-primary']")

        title_input.send_keys("Current_user_last_article_title")
        content_input.send_keys("Current_user_last_article_content")
        submit_button.click()

        first_row = self.driver.driver.find_element(By.XPATH, "//table[@class='table table-hover']/tbody/tr[1]")
        title_cell_first_row = first_row.find_element(By.XPATH, "//td[1]")
        content_cell_first_row = first_row.find_element(By.XPATH, "//td[2]")

        self.assertEqual("Current_user_last_article_title", title_cell_first_row.text)
        self.assertEqual("Current_user_last_article_content", content_cell_first_row.text)

    def test_home_page_editing_first_article(self):
        current_user_profile = self.profile.create_profile()
        current_user_number_of_articles = 1
        self.add_articles(current_user_number_of_articles, current_user_profile)
        self.profile.login()
        edit_first_article = self.driver.driver.find_element(By.CLASS_NAME, "article_edit")
        edit_first_article.click()

        self.assertEqual("Edit article", self.driver.driver.title)

        title_input = self.driver.driver.find_element(By.ID, "id_title")
        title_input.clear()
        content_input = self.driver.driver.find_element(By.ID, "id_content")
        content_input.clear()
        submit_button = self.driver.driver.find_element(By.XPATH, " //form/input[@class='btn btn-primary']")
        title_input.send_keys("Corrected_Current_user_last_article_title")
        content_input.send_keys("Corrected_Current_user_last_article_content")
        submit_button.click()

        first_row = self.driver.driver.find_element(By.XPATH, "//table[@class='table table-hover']/tbody/tr[1]")
        title_cell_first_row = first_row.find_element(By.XPATH, "//td[1]")
        content_cell_first_row = first_row.find_element(By.XPATH, "//td[2]")

        self.assertEqual("Corrected_Current_user_last_article_title", title_cell_first_row.text)
        self.assertEqual("Corrected_Current_user_last_article_content", content_cell_first_row.text)

    def test_home_page_deleting_first_article(self):
        current_user_profile = self.profile.create_profile()
        current_user_number_of_articles = 1
        self.add_articles(current_user_number_of_articles, current_user_profile)
        self.profile.login()
        edit_first_article = self.driver.driver.find_element(By.CLASS_NAME, "article_delete")
        edit_first_article.click()
        self.assertEqual("Delete article", self.driver.driver.title)

        confirm_button = self.driver.driver.find_element(By.XPATH, "//input[@value='Confirm']")
        confirm_button.click()

        no_articles_text = self.driver.driver.find_element(By.CLASS_NAME, "no-table").text
        self.assertEqual("Articles hasn't had yet (((", no_articles_text)


class HomePageWithoutAuthorizationTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.driver = WebDriver()

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def test_home_page_title(self):
        self.driver.driver.get(f'{self.live_server_url}/web/')
        text_about_needed_authorization = self.driver.driver.find_element(By.TAG_NAME, "p").text
        self.assertEqual(
            "In order to be able to view articles or write new articles you need to sign in",
            text_about_needed_authorization)

    def test_going_to_login_page(self):
        self.driver.driver.get(f'{self.live_server_url}/web/')
        login_link = self.driver.driver.find_element(By.LINK_TEXT, "Sign in")
        login_link.click()
        self.assertEqual("Log-in", self.driver.driver.title)

    def test_going_to_registration_page(self):
        self.driver.driver.get(f'{self.live_server_url}/web/')
        registration_link = self.driver.driver.find_element(By.LINK_TEXT, "Sign up")
        registration_link.click()
        self.assertEqual("register", self.driver.driver.title)


class LoginPageTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.driver = WebDriver()
        cls.profile = ProfileMixin(cls.driver.driver, cls.live_server_url)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def test_login_success(self):
        profile = self.profile.create_profile()
        self.driver.driver.get(f'{self.live_server_url}/web/login/')
        username_input = self.driver.driver.find_element(By.ID, "id_username")
        password_input = self.driver.driver.find_element(By.ID, "id_password")
        submit_button = self.driver.driver.find_element(By.XPATH, '//form/p[3]/input')

        username_input.send_keys(profile.username)
        password_input.send_keys("password")
        submit_button.click()

        greetings_text = self.driver.driver.find_element(By.CLASS_NAME, "greetings").text
        self.assertEqual(f"Hi, {profile.username}!", greetings_text)

    def test_login_failure(self):
        profile_attributes = {
            'username': fake.name(),
            'email': fake.email(),
            'password': 'password',
        }
        self.driver.driver.get(f'{self.live_server_url}/web/login/')
        username_input = self.driver.driver.find_element(By.ID, "id_username")
        password_input = self.driver.driver.find_element(By.ID, "id_password")
        submit_button = self.driver.driver.find_element(By.XPATH, '//form/p[3]/input')

        username_input.send_keys(profile_attributes.get('username'))
        password_input.send_keys(profile_attributes.get('password'))
        submit_button.click()

        error_text = self.driver.driver.find_element(By.XPATH, "//body/main/p").text
        self.assertEqual(
            "Your username and password didn't match. Please try again.",
            error_text)

    def test_going_to_password_reset(self):
        self.driver.driver.get(f'{self.live_server_url}/web/login/')
        password_reset_link = self.driver.driver.find_element(By.LINK_TEXT, "Forgotten your password")
        password_reset_link.click()

        self.assertEqual("Reset your password", self.driver.driver.title)

    def test_going_to_registration_page(self):
        self.driver.driver.get(f'{self.live_server_url}/web/login/')
        registration_link = self.driver.driver.find_element(By.LINK_TEXT, "Create an account")
        registration_link.click()

        self.assertEqual("register", self.driver.driver.title)


class RegistrationPageTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.driver = WebDriver()

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()
        try:
            shutil.rmtree(settings.TEST_MEDIA_ROOT)
        except OSError:
            pass

    @override_settings(MEDIA_ROOT=settings.TEST_MEDIA_ROOT)
    def test_registration_success(self):
        self.profile_attributes = {
            'username': 'test_user',
            'email': fake.email(),
            'password': 'password',
        }
        self.driver.driver.get(f'{self.live_server_url}/web/register/')
        username_input = self.driver.driver.find_element(By.ID, "id_username")
        email_input = self.driver.driver.find_element(By.ID, "id_email")
        avatar_input = self.driver.driver.find_element(By.ID, "id_avatar")
        password_input = self.driver.driver.find_element(By.ID, "id_password")
        password2_input = self.driver.driver.find_element(By.ID, "id_password2")

        submit_button = self.driver.driver.find_element(By.XPATH, "//input[@value='Create my account']")

        username_input.send_keys(self.profile_attributes.get('username'))
        email_input.send_keys(self.profile_attributes.get('email'))
        password_input.send_keys(self.profile_attributes.get('password'))
        password2_input.send_keys(self.profile_attributes.get('password'))
        avatar_input.send_keys(os.path.join(os.getcwd(), 'web/tests/test_avatar.jpeg'))
        submit_button.click()
        self.assertEqual("Welcome", self.driver.driver.title)

    @override_settings(MEDIA_ROOT=settings.TEST_MEDIA_ROOT)
    def test_registration_failure(self):
        profile = ProfileMixin(self.driver.driver, self.live_server_url)
        first_profile = profile.create_profile()

        self.profile_attributes = {
            'username': first_profile.username,
            'email': fake.email(),
            'password': 'password',
        }
        self.driver.driver.get(f'{self.live_server_url}/web/register/')
        username_input = self.driver.driver.find_element(By.ID, "id_username")
        email_input = self.driver.driver.find_element(By.ID, "id_email")
        avatar_input = self.driver.driver.find_element(By.ID, "id_avatar")
        password_input = self.driver.driver.find_element(By.ID, "id_password")
        password2_input = self.driver.driver.find_element(By.ID, "id_password2")

        submit_button = self.driver.driver.find_element(By.XPATH, "//input[@value='Create my account']")

        username_input.send_keys(self.profile_attributes.get('username'))
        email_input.send_keys(self.profile_attributes.get('email'))
        password_input.send_keys(self.profile_attributes.get('password'))
        password2_input.send_keys('qwerty')
        avatar_input.send_keys(os.path.join(os.getcwd(), 'web/tests/test_avatar.jpeg'))
        submit_button.click()
        errors = self.driver.driver.find_elements(By.XPATH, "//ul[@class='errorlist']")
        self.assertEqual(
            [error.text for error in errors],
            ['Enter a valid username. This value may contain only letters, numbers, and @/./+/-/_ characters.',
             'Passwords don\'t match.']
        )


class EditProfilePageTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.driver = WebDriver()
        cls.profile = ProfileMixin(cls.driver.driver, cls.live_server_url)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()
        try:
            shutil.rmtree(settings.TEST_MEDIA_ROOT)
        except OSError:
            pass

    @override_settings(MEDIA_ROOT=settings.TEST_MEDIA_ROOT)
    def test_edit_profile_success(self):
        self.profile.create_profile()
        self.profile.login()

        self.update_profile_attributes = {
            'username': 'update_test_user',
            'email': fake.email(),
            'avatar': os.path.join(os.getcwd(), 'web/tests/test_avatar.jpeg'),
        }
        self.driver.driver.get(f'{self.live_server_url}/web/edit_profile/')
        username_input = self.driver.driver.find_element(By.ID, "id_username")
        email_input = self.driver.driver.find_element(By.ID, "id_email")
        avatar_input = self.driver.driver.find_element(By.ID, "id_avatar")
        username_input.clear()
        email_input.clear()
        submit_button = self.driver.driver.find_element(By.XPATH, "//input[@value='Edit my account']")

        username_input.send_keys(self.update_profile_attributes.get('username'))
        email_input.send_keys(self.update_profile_attributes.get('email'))
        avatar_input.send_keys(self.update_profile_attributes.get('avatar'))
        submit_button.click()

        self.assertEqual("Home", self.driver.driver.title)
        greetings_text = self.driver.driver.find_element(By.CLASS_NAME, "greetings").text
        self.assertEqual(f"Hi, {self.update_profile_attributes.get('username')}!", greetings_text)
