from __future__ import unicode_literals

import urlparse
import random

import silly
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.urlresolvers import reverse
from selenium.webdriver.firefox.webdriver import WebDriver

from communities.models import Community, Committee
from users.models import OCUser

NUM_OF_USERS = 1
DEFAULT_PASS = "secret"


class ExampleCommunityLiveTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super(ExampleCommunityLiveTests, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        # cls.selenium.quit()
        super(ExampleCommunityLiveTests, cls).tearDownClass()

    def tearDown(self):
        self.selenium.get(self.full_url(reverse('logout')))
        self.selenium.quit()

    def setUp(self):
        self.community = Community.objects.create(
            name="Kibbutz Broken Dream",
        )
        self.users_details = dict()
        for i in range(NUM_OF_USERS):
            name = silly.name(slugify=True)
            email = silly.email()
            self.users_details[name] = OCUser.objects.create_superuser(email, name, DEFAULT_PASS)
        self.committee = Committee.objects.create(name="Culture", slug="culture", community=self.community)
        self.selenium = WebDriver()

    def full_url(self, s):
        if s.startswith(self.live_server_url):
            return s
        else:
            return self.live_server_url + s

    def get_current_path(self):
        return urlparse.urlsplit(self.selenium.current_url).path

    def assert_current_path(self, path):
        self.assertEqual(self.full_url(path), self.full_url(self.get_current_path()))

    def selenium_get_and_assert(self, url):
        """
        Tries to go url (as is) and then asserts that current_path == url
        """
        self.selenium.get(url)
        self.assert_current_path(url)

    def login(self, goto_login, name, pswd=DEFAULT_PASS):
        if goto_login is True:
            self.selenium.get(self.full_url(reverse('login')))
        self.assert_current_path(reverse('login'))
        username_input = self.selenium.find_element_by_id("id_username")
        username_input.send_keys(self.users_details[name].email)
        password_input = self.selenium.find_element_by_id("id_password")
        password_input.send_keys(pswd)
        self.selenium.find_element_by_xpath('//input[@type="submit"]').click()

    def test_redirect_and_login(self):
        url = self.full_url(self.community.get_absolute_url())
        # from IPython import embed
        # embed()
        self.selenium.get(url)
        name = random.choice(self.users_details.keys())
        self.login(False,
                   name)  # False since the community we created is private - it should automatically redircet to login

    def test_create_meeting(self):
        name = random.choice(self.users_details.keys())
        self.login(True, name)
        """
        TODO - after login goto the community page, locate the relevant html element for the committee - and 'click()' it
        (The below code didn't work because click didn't work for me - idk y
        url = self.full_url(self.community.get_absolute_url())
        self.selenium_get_and_assert(url)
        self.selenium.find_element_by_class_name(
            "panel-heading").click()  # goto "Next meeting" (TODO: check if this works if we have single \ multiple meetings in the system)
        self.assert_current_path(
            self.committee.get_absolute_url())  # note: we're seeing a new meeting in progress - hence its' url is the committees'
        """
        url = self.full_url(self.committee.get_absolute_url())
        self.selenium_get_and_assert(url)
        # TODO: assert that we're seeing all the communities we're a member of
        new_subject_input = self.selenium.find_element_by_id("quick-issue-title")
        new_subject_input.send_keys("dummy-subject1")

        self.selenium.find_element_by_xpath(
            '//button[@type="submit"]').click()  # should behave exactly like: self.selenium.find_element_by_id("quick-issue-add").click()
        # Create a new committee & assert what's needed