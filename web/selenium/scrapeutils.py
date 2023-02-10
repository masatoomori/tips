import time
import datetime
from logging import basicConfig, getLogger, DEBUG

from selenium.webdriver.common.by import By

basicConfig(level=DEBUG)
logger = getLogger(__name__)

SEC_TO_WAIT = 5


def click_item(driver, by, value):
	start_time = datetime.datetime.now()
	elapsed = 0
	while elapsed < SEC_TO_WAIT:
		try:
			item = driver.find_element(by, value)
			item.click()
			logger.debug('"{}" by "{}" clicked!'.format(value, by))
			return True
		except Exception as e:
			logger.debug(e)
			time.sleep(0.5)
			elapsed = (datetime.datetime.now() - start_time).seconds

	return False


def click_btn(driver, btn_title, attribute_name='name'):
    start_time = datetime.datetime.now()
    elapsed = 0
    while elapsed < SEC_TO_WAIT:
        items = [tag for tag in driver.find_elements(by='tag name', value='input') if tag.get_attribute(attribute_name) == btn_title]
        if len(items) > 0:
            items[0].click()
            return True
        logger.debug('Button of which tile is {} is not found'.format(btn_title), elapsed)
        time.sleep(0.5)
        elapsed = (datetime.datetime.now() - start_time).seconds

    return False


def click_img(driver, value, attribute_name):
    start_time = datetime.datetime.now()
    elapsed = 0
    while elapsed < SEC_TO_WAIT:
        items = [tag for tag in driver.find_elements(by='tag name', value='img') if tag.get_attribute(attribute_name) == value]
        if len(items) > 0:
            items[0].click()
            return True
        logger.debug('Image of which {a} is {v} is not found'.format(a=attribute_name, v=value), elapsed)
        time.sleep(0.5)
        elapsed = (datetime.datetime.now() - start_time).seconds

    return False


def select_pull_down_by_text(driver, title, text, element_pos=0, exact_match=True):
    start_time = datetime.datetime.now()
    elapsed = 0
    while elapsed < SEC_TO_WAIT:
        els = [tag for tag in driver.find_elements(by='name', value=title)]
        try:
            logger.debug(els)
            el = els[element_pos]
        except IndexError:
            time.sleep(0.5)
            elapsed = (datetime.datetime.now() - start_time).seconds
            continue

        for option in el.find_elements(by='tag name', value='option'):
            if exact_match:
                if text == option.text:
                    option.click()
                    return True
            else:
                if text in option.text:
                    option.click()
                    return True

    return False


def select_pull_down_by_position(driver, title, position):
    els = [tag for tag in driver.find_elements(by='name', value=title)]

    if len(els) == 0:
        logger.debug('Pull down menu of which title is {} is not found'.format(title))
        return False
    el = els[0]

    options = el.find_elements(by='tag name', value='option')
    if not position < len(options):
        logger.debug('Pull down menu of which title is {t} does not have {n} options'.format(t=title, n=position+1))
        return False

    options[position].click()
    return True


def login_sbi(driver, account_info):
    textbox = driver.find_element(By.NAME, 'user_id')
    textbox.send_keys(account_info['id'])

    textbox = driver.find_element(By.NAME, 'user_password')
    textbox.send_keys(account_info['password'])

    click_btn(driver, 'ACT_login')


def login_dot(driver, account_info):
	textbox = driver.find_element(By.NAME, 'SsLogonUser')
	textbox.send_keys(account_info['id'])

	textbox = driver.find_element(By.NAME, 'SsLogonPassword')
	textbox.send_keys(account_info['password'])

	click_item(driver, By.ID, 'image1')


def login_monex(driver, account_info):
	textbox = driver.find_element(By.NAME, 'loginid')
	textbox.send_keys(account_info['id'])

	textbox = driver.find_element(By.NAME, 'passwd')
	textbox.send_keys(account_info['password'])

	click_btn(driver, 'ログイン', attribute_name='value')
