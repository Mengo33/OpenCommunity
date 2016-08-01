from __future__ import unicode_literals

import time
import urlparse

import requests

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
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

    def is_element_present(self, how, what):
        try:
            self.selenium.find_element(by=how, value=what)
        except NoSuchElementException:
            return False
        return True

    def test_redirect_login(self):
        # self.selenium.maximize_window()
        url = self.full_url(self.community.get_absolute_url())
        self.selenium.get(url)
        # time.sleep(2)
        self.assert_current_path(reverse('login'))

        self.login(self.u1)

    def test_community_is_open_for_superuser(self):
        # login by superuser
        self.login(self.u1)
        # Try enter to community page
        url = self.full_url(self.community.get_absolute_url())
        self.selenium.get(url)
        # If the status code is 200 its OK. TODO
        # r = requests.get(url)
        # self.assertEquals(r.status_code, 200)

        # If the link element 'Committee' is exist, Its OK.
        # time.sleep(0.2)
        self.assertTrue(self.is_element_present(By.XPATH, '//a[@href="{}main/"]'.format(
            self.community.get_absolute_url())))

    def test_logout(self):
        # login for trying logout
        self.login(self.u1)

        # Flow of all clicking to logout
        self.selenium.find_element_by_class_name('dropdown-toggle').click()
        self.selenium.find_element_by_xpath('//a[@href="/logout/"]').click()

        # Try to enter to community page after logout.
        url = self.full_url(self.community.get_absolute_url())
        self.selenium.get(url)

        # If now its redirect to login page, that's OK.
        self.assert_current_path(reverse('login'))

    # def test_community_is_visible_for_superuser(self): TODO
    #     # login by superuser
    #     self.login(self.u1)
    #
    #     url = self.full_url(self.community.get_absolute_url())
    #     self.selenium.get(url)

    def test_create_quick_new_issue_for_new_meeting(self):
        self.login(self.u1)
        url = self.full_url(self.community.get_absolute_url())
        self.selenium.get(url)
        self.selenium.find_element_by_xpath('//a[@href="{}main/"]'.format(
            self.community.get_absolute_url())
        ).click()
        self.selenium.find_element_by_xpath(
            '//input[@type="text"]').send_keys("Building a new road")
        self.selenium.find_element_by_xpath('//button[@id="quick-issue-add"]').click()

        # If the link element 'Issue' is exist, Its OK.
        time.sleep(0.2)
        self.assertTrue(self.is_element_present(By.XPATH, '//a[@href="{}main/issues/1/"]'.format(
            self.community.get_absolute_url())))

    # def test_create_lazy_new_issue_for_new_meeting(self): TODO
    #     self.login(self.u1)
    #     url = self.full_url(self.community.get_absolute_url())
    #     self.selenium.get(url)
    #     self.selenium.find_element_by_xpath('//a[@href="{}main/"]'.format(
    #         self.community.get_absolute_url())
    #     ).click()
    #     self.selenium.find_element_by_xpath('//a[@href="{}main/issues/upcoming-create/"]'.format(
    #         self.community.get_absolute_url())
    #     ).click()
    #
    #     # div_modal_content = self.selenium.find_element_by_class_name("modal-dialog").click()
    #     # form = self.selenium.find_element_by_xpath('//form[@method="post"]')
    #     # # self.selenium.switch_to_window(form)
    #     self.selenium.find_element_by_xpath(
    #         '//input[@type="text"]').send_keys("Building a new road")
    #     # raw_input()
    #
    #     html_area = div_modal_content.find_element_by_class_name("htmlarea")
    #     iframe = self.selenium.find_element_by_xpath('//iframe[@class="wysihtml5-sandbox"]')
    #     self.selenium.switch_to_frame(iframe)
    #     self.selenium.find_element_by_xpath('//body[@class="form-control wysihtml5-editor"]').send_keys(
    #         "The Kibutz needs a new access road from the other side.."
    #     )
    #     self.selenium.find_element_by_class_name(
    #         "form-control wysihtml5-editor").send_keys(
    #         "The Kibutz needs a new access road from the other side..")
    #     self.selenium.find_element_by_css_selector("ul li:last-child").click()
    #     self.selenium.find_element_by_id("id_proposal-title").send_keys("Rent a building contractor")
    #     self.selenium.find_element_by_class_name(
    #         "form-control wysihtml5-editor").send_keys(
    #         "Needs to talk with a building contractor about the new road building program..")
    #     self.selenium.find_element_by_id("id_proposal-assigned_to").send_keys("menahem")
    #     self.selenium.find_element_by_id("id_proposal-due_by").send_keys("08/25/2016")
    #     form.find_element_by_xpath('//input[@type="submit"]').click()
    #     self.selenium.find_element_by_xpath('//button[@id="quick-issue-add"]').click()
    #     # raw_input()
    #     time.sleep(0.2)
    #
    #     self.assertTrue(self.is_element_present(By.XPATH, '//a[@href="{}main/issues/1/"]'.format(
    #                         self.community.get_absolute_url())))
    #
    #     # self.assertTrue(self.selenium.find_element_by_xpath('//a[@href="{}main/"]'.format(
    #     #     self.community.get_absolute_url())))

