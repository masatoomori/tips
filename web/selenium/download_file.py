import os
import time
from selenium import webdriver

DOWNLOAD_PATH = os.path.join(os.path.expandvars("%userprofile%"), 'Downloads')
SEC_TO_WAIT = 5
SEC_TO_TIMEOUT = 60

FILE_STARTS = '<file pattern>'
FILE_SUFFIX = '.csv'


def click_link(driver, link_title):
    items = [tag for tag in driver.find_elements_by_link_text(link_title)]
    if len(items) == 0:
        print('Image of which title is {} is not found'.format(link_title))
        return False

    items[0].click()
    return True


def download_file(driver, download_link, download_path, file_starts, suffix, full_path=True):
    # ダウンロード前の同様のファイルを取得し、新しいファイルが増えていたらダウンロード完了と見做す
    files = [f for f in os.listdir(download_path) if f.startswith(file_starts) and f.endswith(suffix)]
    existing_files = files
    new_file_num = len(set(files) - set(existing_files))

    if click_link(driver, download_link):
        # ダウンロードが完了するまで待つ
        time_elapsed = 0
        while new_file_num == 0 and time_elapsed < SEC_TO_TIMEOUT:
            files = [f for f in os.listdir(download_path) if f.startswith(file_starts) and f.endswith(suffix)]
            new_file_num = len(set(files) - set(existing_files))
            time.sleep(SEC_TO_WAIT)
            time_elapsed = time_elapsed + SEC_TO_WAIT

        if new_file_num > 0:
            new_file = list(set(files) - set(existing_files))[0]

            if full_path:
                return os.path.join(download_path, new_file)
            else:
                return new_file
        else:
            print('No new file downloaded from {}'.format(download_link))
    else:
        print('fail to click download link: {}'.format(download_link))
        return None


def test():
    driver = webdriver.Chrome()
    driver.get("<URL>")
    new_file = download_file(driver, 'ダウンロード', DOWNLOAD_PATH, FILE_STARTS, FILE_SUFFIX)

    print(new_file)


if __name__ == '__main__':
    test()
