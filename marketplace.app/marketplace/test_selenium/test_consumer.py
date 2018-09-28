from append_path import *
from testing_utils import uniqueEmail, uniqueShopName, login, logout, getPhoneMask, getEditElements, setDictValues, \
    getDataFromElements
import unittest
from selenium import webdriver
from marketplace.models import User


firefox_opts = webdriver.FirefoxOptions()
firefox_opts.add_argument('--headless')
driver = webdriver.Firefox(firefox_options=firefox_opts)

unique_email = uniqueEmail()
unique_shop_name = uniqueShopName()


class TestConsumer(unittest.TestCase):

    def setUp(self):
        self.url = 'http://127.0.0.1:8000'
        self.consumer = User.query.filter_by(entity='consumer').order_by(User.id.desc()).first()
        self.password = "123123"
        self.load_data = {"first_name": "",
                          "last_name": "",
                          "patronymic": "",
                          "phone": "",
                          "address": "",
                          }

    def test_01_consumer_register(self):
        url, pw = self.url, self.password
        driver.get(url)
        driver.find_element_by_css_selector(".header-login").click()
        driver.find_element_by_css_selector(
            "p.registration-link:nth-child(4) > a:nth-child(1)").click()
        driver.find_element_by_id("emailRegistration").send_keys(unique_email)
        driver.find_element_by_id("passwordRegistration").send_keys(pw)
        driver.find_element_by_id("re_passwordRegistration").send_keys(pw)
        driver.find_element_by_id("reg_button").click()


    def test_02_consumer_logout(self):
        logout(driver)


    def test_03_consumer_login(self):
        login(driver, self.consumer.email, self.password)


    def test_04_consumer_go_to_edit_profile(self):
        driver.find_element_by_css_selector("button.btn:nth-child(1)").click() # User menu btn
        driver.find_element_by_css_selector("a.dropdown-item:nth-child(1)").click() # Profile btn
        driver.find_element_by_css_selector(
            ".edit-profile > a:nth-child(1)").click()  # Edit profile btn


    def test_05_consumer_edit_profile(self):
        elements_to_edit = getEditElements(driver)
        data_to_edit = getDataFromElements(elements_to_edit)
        save_profile = driver.find_element_by_id("save_consumer_profile")

        # filling new data in the fields on the Edit User Page
        load_data = setDictValues(self.load_data) #set random user data to edit
        keys = list(load_data.keys())
        for arg in range(len(data_to_edit)):
            key = keys[arg]
            elements_to_edit[arg].clear()
            elements_to_edit[arg].send_keys(load_data[key])
        edited_data = getDataFromElements(elements_to_edit)
        save_profile.click()

        driver.find_element_by_xpath("/html/body/main/div[1]/div/p/a").click() # Edit profile btn
        # verification that saved values corresponds loading data
        for arg in range(len(edited_data)):
            key = keys[arg]
            if key == "phone":
                phone_number = getPhoneMask(load_data[key])  # in load data string of nums
                self.assertEqual(phone_number, edited_data[arg])
            else:
                self.assertEqual(load_data[key], edited_data[arg])


    def test_06_delete_consumer(self):
        driver.find_element_by_xpath("/html/body/main/div[1]/div/p/a").click()  # Edit profile btn
        driver.find_element_by_css_selector(".out-of-stock > a:nth-child(1)").click()  # Delete profile btn
        driver.find_element_by_id("deleteConsumerBtn").click()
        self.assertIsNone(User.query.filter_by(id=self.consumer.id).first())
        driver.close()