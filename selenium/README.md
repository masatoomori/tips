# Python
## Click
### Click Button
```python
def click_btn(driver, attribute_name, btn_title):
    items = [tag for tag in driver.find_elements_by_tag_name('input') if tag.get_attribute(attribute_name) == btn_title]
    if len(items) == 0:
        print('Button of which tile is {} is not found'.format(btn_title))
        return False

    items[0].click()
    return True
```

### Click Image
```python
def click_img(driver, attribute_name, value):
    items = [tag for tag in driver.find_elements_by_tag_name('img') if tag.get_attribute(attribute_name) == value]
    if len(items) == 0:
        print('Image of which {a} is {v} is not found'.format(a=attribute_name, v=value))
        return False

    items[0].click()
    return True
```

### Click Link
```python
def click_link(driver, link_title):
    items = [tag for tag in driver.find_elements_by_link_text(link_title)]
    if len(items) == 0:
        print('Image of which title is {} is not found'.format(link_title))
        return False

    items[0].click()
    return True
```

### Click Rectangle
```python
def click_area_rect(driver, rect_title):
    items = [tag for tag in driver.find_elements_by_xpath("//*[@shape='rect']")
             if tag.get_attribute('title') == rect_title]
    if len(items) == 0:
        print("@shape='rect' of which title is {} is not found".format(rect_title))
        return False

    items[0].click()
    return True
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
