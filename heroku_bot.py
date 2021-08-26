from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from time import sleep

import os


class Bot:

    def __init__(self, credentials):

        options = Options()
        options.headless = True  # comment this line if you want to debug

        options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")

        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")

        self.driver = webdriver.Chrome(
            executable_path=os.environ.get("CHROMEDRIVER_PATH"),
            options=options
        )

        self.wait = WebDriverWait(self.driver, 60)

        self.credentials = credentials

    def enter_heroku(self):
        print("Entering Heroku...")

        self.driver.get("https://id.heroku.com/login")

        print(f"Entering form data for {self.credentials['email']}...")
        
        # fill up form
        email_field = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#email"))
        )
        email_field.send_keys(self.credentials["email"])

        password_field = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#password"))
        )
        password_field.send_keys(self.credentials["password"])

        # submit form
        password_field.submit()  # selenium will walk up the DOM and find the form to submit

        # click on "Later" to tell that you don't want Two-Factor-Auth
        later_button = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn.btn-link"))
        )
        later_button.click()

        print("Successfully entered Heroku!")

        # wait the dashboard to load
        sleep(3)

    def activate_dyno(self, app_name, dyno_identifier):

        # enter and log in heroku
        self.enter_heroku()

        print(f"Activating dyno {app_name}...")

        # go to dyno page
        self.driver.get(
            f"https://dashboard.heroku.com/apps/{app_name}/resources")

        # <code></code> element used to find the desired dyno
        dyno_identifier_code_tag = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, f"//*[text()='{dyno_identifier}']"))
        )

        # using the <code></code> tag with the identifier, get the div with the activation buttons
        div_with_interaction_buttons = dyno_identifier_code_tag.find_element_by_xpath(
            "./parent::div/following-sibling::div"
        )

        # enter edit mode
        edit_button = div_with_interaction_buttons.find_element_by_xpath(
            "./descendant::button"
        )
        edit_button.click()

        # deactivate dyno
        activation_slider = div_with_interaction_buttons.find_element_by_xpath(
            "./descendant::input"
        )

        # if the slider isn't checked (toggled off), click it to activate
        if not activation_slider.is_selected():
            activation_slider.click()
        # if it is, just close the browser - there's nothing to do here
        else:
            print("Dyno already activated!")
            self.end_session()
            return

        # click confirm
        confirm_button = div_with_interaction_buttons.find_element_by_xpath(
            "./descendant::button"
        )
        confirm_button.click()

        # wait for the activation to load
        while activation_slider.is_enabled():
            sleep(0.1)

        print("Dyno succesfully activated!")

        self.end_session()

    def deactivate_dyno(self, app_name, dyno_identifier):
        # enter and log in heroku
        self.enter_heroku()

        print(f"Deactivating dyno {app_name}...")

        # go to dyno page
        self.driver.get(
            f"https://dashboard.heroku.com/apps/{app_name}/resources")

        # <code></code> element used to find the desired dyno
        dyno_identifier_code_tag = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, f"//*[text()='{dyno_identifier}']"))
        )

        # using the <code></code> tag with the identifier, get the div with the activation buttons
        div_with_interaction_buttons = dyno_identifier_code_tag.find_element_by_xpath(
            "./parent::div/following-sibling::div"
        )

        # enter edit mode
        edit_button = div_with_interaction_buttons.find_element_by_xpath(
            "./descendant::button"
        )
        edit_button.click()

        # deactivate dyno
        deactivation_slider = div_with_interaction_buttons.find_element_by_xpath(
            "./descendant::input"
        )

        # if the slider is checked (toggled on), click it to deactivate
        if deactivation_slider.is_selected():
            deactivation_slider.click()
        # if it isn't, just close the browser - there's nothing to do here
        else:
            print("Dyno already deactivated!")
            self.end_session()
            return

        # click confirm
        confirm_button = div_with_interaction_buttons.find_element_by_xpath(
            "./descendant::button"
        )
        confirm_button.click()

        # wait for the deactivation to load
        while deactivation_slider.is_enabled():
            sleep(0.1)

        print("Dyno succesfully deactivated!")

        self.end_session()

    def end_session(self):
        self.driver.quit()


if __name__ == "__main__":
    pass
