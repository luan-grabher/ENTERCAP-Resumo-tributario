from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def waitCss(driver, cssSelector, timeout=10):
    WebDriverWait(driver, timeout).until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, cssSelector)))

def waitAndClick(driver, cssSelector, timeout=10):
    waitCss(driver, cssSelector, timeout)
    driver.find_element(By.CSS_SELECTOR, cssSelector).click()

def waitAndSendKeys(driver, cssSelector, keys, timeout=10):
    waitCss(driver, cssSelector, timeout)
    driver.find_element(By.CSS_SELECTOR, cssSelector).send_keys(keys)
    