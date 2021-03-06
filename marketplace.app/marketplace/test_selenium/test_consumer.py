from append_path import *
from testing_utils import init_driver_and_display, check_connection, uniqueEmail, uniqueShopName, login, logout, getPhoneMask, getEditElements, setDictValues, \
    getDataFromElements

import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as Wait
from marketplace.models import User


url = "http://127.0.0.1:8000"

driver, display = init_driver_and_display()
check_connection(driver, url)

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


    def test_01_get_home_page(self):
        driver.get(self.url)


    def test_02_consumer_open_registration_page(self):
        driver.find_element_by_css_selector(".header-login").click()
        driver.find_element_by_css_selector(
            "p.registration-link:nth-child(4) > a:nth-child(1)").click()


    def test_03_consumer_enter_registrtion_data(self):
        driver.find_element_by_id("emailRegistration").send_keys(unique_email)
        driver.find_element_by_id("passwordRegistration").send_keys(self.password)
        driver.find_element_by_id("re_passwordRegistration").send_keys(self.password)


    def test_04_consumer_submit_form(self):
        driver.find_element_by_id("reg_button").click()
        user_menu = None
        try:
            user_menu = Wait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/header/nav/div/div/div/button"))
            )
        finally:
            self.assertIsNotNone(user_menu, "producer is not authorized after registration")


    def test_05_consumer_logout(self):
        logout(driver)
        btn_auth = None
        try:
            btn_auth = Wait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".header-login > img:nth-child(1)"))
            )
        finally:
            self.assertIsNotNone(btn_auth, "no auth button after logout")


    def test_06_consumer_login(self):
        login(driver, self.consumer.email, self.password)



    def test_07_consumer_open_edit_profile(self):
        driver.find_element_by_css_selector("button.btn:nth-child(1)").click() # User menu btn
        driver.find_element_by_css_selector("a.dropdown-item:nth-child(1)").click() # Profile btn
        driver.find_element_by_css_selector(
            ".edit-profile > a:nth-child(1)").click()  # Edit profile btn
        driver.implicitly_wait(2)


    def test_08_consumer_edit_profile(self):
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


    def test_09_consumer_open_the_delete_page(self):
        driver.find_element_by_xpath("/html/body/main/div[1]/div/p/a").click()  # Edit profile btn
        driver.find_element_by_css_selector(".out-of-stock > a:nth-child(1)").click()  # Delete profile btn


    def test_10_consumer_confirm_delete(self):
        driver.find_element_by_css_selector("#deleteConsumerBtn").click()
        driver.implicitly_wait(2)
        self.assertIsNone(User.query.filter_by(id=self.consumer.id).first())


if __name__ == "__main__":
    unittest.main()
