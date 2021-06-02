# Python

## 初期化

```python
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get('<url>')
```

## Click

### Click Button

```python
import time
import datetime

SEC_TO_WAIT = 0.5
SEC_TO_TIMEOUT = 5


def click_btn(driver, btn_title, attribute_name='name'):
    start_time = datetime.datetime.now()
    elapsed = 0
    while elapsed < SEC_TO_TIMEOUT:
        items = [tag for tag in driver.find_elements_by_tag_name('input') if tag.get_attribute(attribute_name) == btn_title]
        if len(items) > 0:
            items[0].click()
            return True
        print('Button of which tile is {} is not found'.format(btn_title), elapsed)
        time.sleep(SEC_TO_WAIT)
        elapsed = (datetime.datetime.now() - start_time).seconds

    return False
```

### Click Image

```python
import time
import datetime

SEC_TO_WAIT = 0.5
SEC_TO_TIMEOUT = 5


def click_img(driver, value, attribute_name):
    start_time = datetime.datetime.now()
    elapsed = 0
    while elapsed < SEC_TO_TIMEOUT:
        items = [tag for tag in driver.find_elements_by_tag_name('img') if tag.get_attribute(attribute_name) == value]
        if len(items) > 0:
            items[0].click()
            return True
        print('Image of which {a} is {v} is not found'.format(a=attribute_name, v=value), elapsed)
        time.sleep(SEC_TO_WAIT)
        elapsed = (datetime.datetime.now() - start_time).seconds

    return False
```

### Click Link

```python
import time
import datetime

SEC_TO_WAIT = 0.5
SEC_TO_TIMEOUT = 5


def click_link(driver, link_title):
    start_time = datetime.datetime.now()
    elapsed = 0
    while elapsed < SEC_TO_TIMEOUT:
        items = [tag for tag in driver.find_elements_by_link_text(link_title)]
        if len(items) > 0:
            items[0].click()
            return True
        print('Image of which title is {} is not found'.format(link_title), elapsed)
        time.sleep(SEC_TO_WAIT)
        elapsed = (datetime.datetime.now() - start_time).seconds

    return False
```

### Click Rectangle

```python
import time
import datetime

SEC_TO_WAIT = 0.5
SEC_TO_TIMEOUT = 5


def click_area_rect(driver, rect_title):
    start_time = datetime.datetime.now()
    elapsed = 0
    while elapsed < SEC_TO_TIMEOUT:
        items = [tag for tag in driver.find_elements_by_xpath("//*[@shape='rect']")
                 if tag.get_attribute('title') == rect_title]
        if len(items) > 0:
            items[0].click()
            return True
        print("@shape='rect' of which title is {} is not found".format(rect_title))
        time.sleep(SEC_TO_WAIT)
        elapsed = (datetime.datetime.now() - start_time).seconds

    return False
```

## Pull Down Menu

### Select by Position

```python
def select_pull_down_by_position(driver, title, position):
    els = [tag for tag in driver.find_elements_by_tag_name('select') if tag.get_attribute('name') == title]

    if len(els) == 0:
        print('Pull down menu of which title is {} is not found'.format(title))
        return False
    el = els[0]

    options = [o for o in el.find_elements_by_tag_name('option')]
    if not position < len(options):
        print('Pull down menu of which title is {t} does not have {n} options'.format(t=title, n=position+1))
        return False

    options[position].click()
    return True
```

### Select by Text

```python
def select_pull_down_by_text(driver, title, text, exact_match=True):
    el = [tag for tag in driver.find_elements_by_tag_name('select') if tag.get_attribute('name') == title][0]
    for option in el.find_elements_by_tag_name('option'):
        if exact_match:
            if text == option.text:
                option.click()
                return True
        else:
            if text in option.text:
                option.click()
                return True
    return False
```

## File Download

```python
import os
import time

DOWNLOAD_PATH = os.path.join(os.path.expanduser("~"), 'Downloads')
SEC_TO_WAIT = 5
SEC_TO_TIMEOUT = 60


def click_img(driver, value, attribute_name):
    """see above"""


def click_link(driver, link_title):
    """see above"""


def download_file(driver, download_link, file_starts, suffix, full_path=True):
    # ダウンロード前の同様のファイルを取得し、新しいファイルが増えていたらダウンロード完了と見做す
    files = [f for f in os.listdir(DOWNLOAD_PATH) if f.startswith(file_starts) and f.endswith(suffix)]
    existing_files = files
    new_file_num = len(set(files) - set(existing_files))

    if download_link['type'] == 'img':
        click_img(driver, download_link['val'], download_link['attr'])
    elif download_link['type'] == 'link':
        click_link(driver, download_link['val'])

    # ダウンロードが完了するまで待つ
    time_elapsed = 0
    while new_file_num == 0 and time_elapsed < SEC_TO_TIMEOUT:
        files = [f for f in os.listdir(DOWNLOAD_PATH) if f.startswith(file_starts) and f.endswith(suffix)]
        new_file_num = len(set(files) - set(existing_files))
        time.sleep(SEC_TO_WAIT)
        time_elapsed = time_elapsed + SEC_TO_WAIT

    new_file = list(set(files) - set(existing_files))[0]

    if full_path:
        return os.path.join(DOWNLOAD_PATH, new_file)
    else:
        return new_file
```

## Window

### Close All Windows

```python
def close_all_windows(driver):
    n_trial = 100
    while n_trial > 0:
        try:
            window_handle = driver.window_handles[-1]
            driver.switch_to.window(window_handle)
            driver.close()
            n_trial -= 1
        except Exception as e:
            print(e)
            break
```
