from __future__ import unicode_literals

import time
import urlparse

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.urlresolvers import reverse
from selenium.webdriver.chrome.webdriver import WebDriver

from communities.models import Community
from users.models import OCUser


class ExampleCommunityLiveTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super(ExampleCommunityLiveTests, cls).setUpClass()
        cls.selenium = WebDriver()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.close()
        cls.selenium.quit()
        super(ExampleCommunityLiveTests, cls).tearDownClass()

    def login(self, user):
        login_url = self.full_url(reverse("login"))
        self.selenium.get(login_url)

        username_input = self.selenium.find_element_by_id("id_username")
        username_input.send_keys(user.email)
        password_input = self.selenium.find_element_by_id("id_password")
        password_input.send_keys("secret")
        self.selenium.find_element_by_xpath('//input[@type="submit"]').click()

    def setUp(self):
        self.community = Community.objects.create(
            name="Kibbutz Broken Dream",
        )
        self.u1 = OCUser.objects.create_superuser("menahem@dream.org", "Menahem", "secret")

    def full_url(self, s):
        return self.live_server_url + s

    def get_current_path(self):
        return urlparse.urlsplit(self.selenium.current_url).path

    def assert_current_path(self, path):
        self.assertEqual(path, self.get_current_path())

    def test_redirect_login(self):
        # self.selenium.maximize_window()
        url = self.full_url(self.community.get_absolute_url())
        self.selenium.get(url)
        # time.sleep(2)
        self.assert_current_path(reverse('login'))

        self.login(self.u1)

    def test_direct_login(self):
        self.login(self.u1)
        url = self.full_url(self.community.get_absolute_url())
        self.selenium.get(url)
        self.assert_current_path(self.community.get_absolute_url())

        self.login(self.u1)

    # def test_logout(self):
    #     self.login(self.u1)
    #     TODO

    # from IPython import embed
    # embed()

