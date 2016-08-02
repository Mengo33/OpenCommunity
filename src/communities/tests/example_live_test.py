from __future__ import unicode_literals

import time
import urlparse

import requests

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.urlresolvers import reverse
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

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

    @staticmethod
    def type_tabs(element, num):
        for i in range(0, num):
            # time.sleep(0.5)
            element.send_keys(Keys.TAB)

    def test_redirect_login(self):
        # self.selenium.maximize_window()
        url = self.full_url(self.community.get_absolute_url())
        self.selenium.get(url)
        # time.sleep(2)

        # Test: If there is 'login' in the URL, its OK.
        self.assert_current_path(reverse('login'))
        # self.login(self.u1)

    def test_community_is_open_for_superuser(self):
        # login by superuser
        self.login(self.u1)
        # Try enter to community page
        url = self.full_url(self.community.get_absolute_url())
        self.selenium.get(url)
        # If the status code is 200 its OK.
        # r = requests.get(url)
        # self.assertEquals(r.status_code, 200)

        # Test: If the link element 'Committee' is exist, Its OK.
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

        # Test: If now its redirect to login page, that's OK.
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

        # Test: If there is at least one element of 'Issue' in line, Its OK.
        time.sleep(0.2)
        agenda_lines = self.selenium.find_elements_by_xpath('//ul[@id="agenda"]')
        self.assertTrue(len(agenda_lines) > 0)

    def test_create_lazy_new_issue_for_new_meeting(self):
        self.login(self.u1)
        url = self.full_url(self.community.get_absolute_url())
        self.selenium.get(url)
        self.selenium.find_element_by_xpath('//a[@href="{}main/"]'.format(
            self.community.get_absolute_url())
        ).click()
        self.selenium.find_element_by_xpath('//a[@href="{}main/issues/upcoming-create/"]'.format(
            self.community.get_absolute_url())
        ).click()

        time.sleep(0.25)
        self.type_tabs(self.selenium.find_element_by_id("upcoming-meeting"), 6)
        current_element = self.selenium.switch_to.active_element
        current_element.send_keys("Building a new road", Keys.TAB)
        current_element = self.selenium.switch_to.active_element
        current_element.send_keys("The Kibutz needs a new access road from the other side..")
        self.type_tabs(self.selenium.find_element_by_id("upcoming-meeting"), 6)
        current_element = self.selenium.switch_to.active_element
        current_element.send_keys(Keys.SPACE)

        # Test: If there is at least one element of 'Issue' in line, Its OK.
        time.sleep(0.5)
        agenda_lines = self.selenium.find_elements_by_xpath('//ul[@id="agenda"]')
        self.assertTrue(len(agenda_lines) > 0)

    def test_create_new_restricted_issue_for_new_meeting(self):
        self.login(self.u1)
        url = self.full_url(self.community.get_absolute_url())
        self.selenium.get(url)
        self.selenium.find_element_by_xpath('//a[@href="{}main/"]'.format(
            self.community.get_absolute_url())
        ).click()
        self.selenium.find_element_by_xpath('//a[@href="{}main/issues/upcoming-create/"]'.format(
            self.community.get_absolute_url())
        ).click()

        # Choose to be restricted issue by clicking on reason 2.
        time.sleep(0.25)
        self.type_tabs(self.selenium.find_element_by_id("upcoming-meeting"), 5)
        current_element = self.selenium.switch_to.active_element
        current_element.send_keys(Keys.ENTER)
        self.selenium.find_element_by_xpath('//label[@for="id_confidential_reason_2"]').click()

        # Filling up all the fields just to be sure everything is ok.
        time.sleep(0.25)
        self.type_tabs(self.selenium.find_element_by_id("upcoming-meeting"), 1)
        current_element = self.selenium.switch_to.active_element
        current_element.send_keys("Restricted issue", Keys.TAB)
        current_element = self.selenium.switch_to.active_element
        current_element.send_keys("Restricted issue for example..")
        self.type_tabs(self.selenium.find_element_by_id("upcoming-meeting"), 6)
        current_element = self.selenium.switch_to.active_element
        current_element.send_keys(Keys.SPACE)

        # Test: If there is a link text "Restricted issue", Its OK.
        time.sleep(0.6)
        self.assertTrue(self.is_element_present(By.LINK_TEXT, "Restricted issue"))
        # self.assertTrue(self.is_element_present(By.XPATH, "//*[contains(text(), 'Restricted issue')]"))

    def test_start_new_meeting(self):
        self.login(self.u1)
        url = self.full_url(self.community.get_absolute_url())
        self.selenium.get(url)
        self.selenium.find_element_by_xpath('//a[@href="{}main/"]'.format(
            self.community.get_absolute_url())
        ).click()

        # Click on button of "Start Meeting"
        self.selenium.find_element_by_xpath('//button[@data-url="{}main/upcoming/start/"]'.format(
            self.community.get_absolute_url())).click()

        # Move to the correct element by typing 12 tabs.
        self.type_tabs(self.selenium.find_element_by_id("upcoming-meeting"), 12)
        current_element = self.selenium.switch_to.active_element
        current_element.send_keys(Keys.SPACE)

        # Test: If the link element 'Stop Meeting' is exist, Its OK.
        time.sleep(0.3)
        self.assertTrue(self.is_element_present(By.CLASS_NAME, "fa"))

    def test_create_quick_new_proposal_for_issue(self):
        self.login(self.u1)
        url = self.full_url(self.community.get_absolute_url())
        self.selenium.get(url)
        self.selenium.find_element_by_xpath('//a[@href="{}main/"]'.format(
            self.community.get_absolute_url())
        ).click()
        self.selenium.find_element_by_xpath(
            '//input[@type="text"]').send_keys("Building a new road")
        self.selenium.find_element_by_xpath('//button[@id="quick-issue-add"]').click()

        # Add a quick proposal to the issue
        button = WebDriverWait(self.selenium, 10).until(
            ec.presence_of_element_located((
                By.XPATH, '//a[@href="{}main/issues/1/"]'.format(self.community.get_absolute_url()))))
        button.click()
        self.selenium.find_element_by_xpath('//a[@href="{}main/issues/1/"]'.format(
            self.community.get_absolute_url())
        ).click()
        self.selenium.find_element_by_id("quick-proposal-title").send_keys("New Proposal")
        self.selenium.find_element_by_id("quick-proposal-add").click()

        # Test: If there is a line with text "New Proposal", Its OK.
        time.sleep(0.6)
        self.assertTrue(self.is_element_present(By.XPATH, "//* [contains(text(), 'New Proposal')]"))

    def test_create_new_draft_meeting(self):
        self.login(self.u1)
        url = self.full_url(self.community.get_absolute_url())
        self.selenium.get(url)
        self.selenium.find_element_by_xpath('//a[@href="{}main/"]'.format(
            self.community.get_absolute_url())
        ).click()

        self.selenium.find_element_by_xpath('//a[@href="{}main/upcoming/edit/"]'.format(
            self.community.get_absolute_url())).click()

        title = WebDriverWait(self.selenium, 10).until(
            ec.presence_of_element_located((By.ID, "id_upcoming_meeting_title"))
        )
        title.send_keys("Meeting Title")
        self.selenium.find_element_by_id("id_upcoming_meeting_location").send_keys("Tel Aviv")
        self.selenium.find_element_by_id("id_upcoming_meeting_scheduled_at_0").send_keys("01/01/2017")
        self.selenium.find_element_by_id("id_upcoming_meeting_scheduled_at_1").send_keys("02:00PM", Keys.TAB)
        current_element = self.selenium.switch_to.active_element
        current_element.send_keys("Background...")
        self.selenium.find_element_by_xpath('//input[@type="submit"]').click()

        # Test: If there is a h1 title "Meeting Title", Its OK.
        time.sleep(0.6)
        self.assertTrue(self.is_element_present(By.XPATH, "//* [contains(text(), 'Meeting Title')]"))
