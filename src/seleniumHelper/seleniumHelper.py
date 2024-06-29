import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def waitCss(driver, cssSelector, timeout=10):
    try:
        WebDriverWait(driver, timeout).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, cssSelector)))
    except Exception as e:
        raise Exception(f'Elemento {cssSelector} não encontrado')

def waitAndClick(driver, cssSelector, timeout=10):
    waitCss(driver, cssSelector, timeout)
    driver.find_element(By.CSS_SELECTOR, cssSelector).click()

def waitAndSendKeys(driver, cssSelector, keys, timeout=10):
    waitCss(driver, cssSelector, timeout)
    driver.find_element(By.CSS_SELECTOR, cssSelector).clear()
    driver.find_element(By.CSS_SELECTOR, cssSelector).send_keys(keys)
    
def waitDisappear(driver, cssSelector, timeout=300):
    waitCss(driver, cssSelector, 10)
    
    init_time = time.time()
    while True:
        try:
            elemento = driver.find_element(By.CSS_SELECTOR, cssSelector)
            display = elemento.value_of_css_property('display')
            if display == 'none':
                break
        except:
            break
        
        if time.time() - init_time > timeout:
            raise Exception(f'Elemento {cssSelector} não desapareceu')
        else:
            time.sleep(1)
        
    