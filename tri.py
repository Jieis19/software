=import os
import time
import pickle
from pathlib import Path
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

COOKIES_FILE = "cookies_tixcraft.pkl"
TARGET = "https://tixcraft.com/"

def make_driver(headless=False):
    options = uc.ChromeOptions()
    # 基本選項（你可以依需要新增）
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-notifications")
    # 不建議一開始就用 headless（容易被檢測）
    if headless:
        options.add_argument("--headless=new")  # 若要使用 headless，改成 new 模式試試
    # 模擬一般用戶 Agent
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.62 Safari/537.36")
    # 防止一些自動化 flag
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    # 建立 driver（uc 會自行管理 driver binary）
    driver = uc.Chrome(options=options)
    driver.set_page_load_timeout(60)
    return driver

def save_cookies(driver, path=COOKIES_FILE):
    cookies = driver.get_cookies()
    with open(path, "wb") as f:
        pickle.dump(cookies, f)
    print(f"[+] Cookies saved to {path}")

def load_cookies(driver, path=COOKIES_FILE):
    if not os.path.exists(path):
        return False
    with open(path, "rb") as f:
        cookies = pickle.load(f)
    # 必須先開啟 domain 才能加入 cookie
    driver.get(TARGET)
    time.sleep(1)
    for c in cookies:
        # selenium cookie needs domain not None, adjust if necessary
        try:
            driver.add_cookie(c)
        except Exception as e:
            # 有些 cookie 含有 'sameSite' 或其他屬性可能導致加入失敗，略過
            # print("skip cookie:", e)
            pass
    print("[+] Cookies loaded into browser")
    driver.refresh()
    return True

def page_blocked(page_source):
    # 根據你提供的訊息簡易判斷是否中間被擋（可擴充）
    markers = [
        "Your browser hit a snag",
        "we need to make sure you're not a bot",
        "請確定您的 Cookie 和 JavaScript 已啟用",
        "您是機器人"
    ]
    src_lower = page_source.lower()
    for m in markers:
        if m.lower() in src_lower:
            return True
    return False

def main():
    driver = make_driver(headless=False)  # 建議先用 headful (False)
    try:
        # 1) 若有 cookies 檔，先嘗試載入（比較可能直接通過）
        if os.path.exists(COOKIES_FILE):
            print("[*] Found cookies file, trying to use it...")
            load_cookies(driver, COOKIES_FILE)
            time.sleep(2)
            # 載入後檢查是否被擋
            src = driver.page_source
            if page_blocked(src):
                print("[!] Page still blocked after loading cookies. Will open interactive page for manual login.")
            else:
                print("[+] Page loaded successfully with cookies.")
                print(driver.title)
                print("---- page snippet ----")
                print(driver.page_source[:1000])
                return

        # 2) 沒 cookie 或 cookie 無效 -> 讓使用者手動登入並儲存 cookie
        print("[*] Opening target page. Please manually login if needed, then press Enter here to continue.")
        driver.get(TARGET)
        # 等待網頁載入或登入流程（你可以改成等待某個登入完成的 element）
        try:
            WebDriverWait(driver, 300).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
        except TimeoutException:
            print("[!] Page load timed out but continuing...")

        # 使用者互動：等使用者完成登入
        print("請在開啟的瀏覽器完成登入/驗證（如果需要），然後回到這個終端按 Enter。")
        input("按 Enter 繼續...")

        # 儲存 cookies，供下次使用
        save_cookies(driver, COOKIES_FILE)

        # 重新整理並檢查是否成功
        driver.get(TARGET)
        time.sleep(2)
        if page_blocked(driver.page_source):
            print("[!] 仍被擋：建議檢查是否需要進一步的 JS 驗證或 CAPTCHA，或改變 UA/移除 headless。")
            # 幫你截圖方便檢查
            img_path = "blocked_screenshot.png"
            driver.save_screenshot(img_path)
            print(f"[!] 已儲存截圖：{img_path}")
        else:
            print("[+] 成功進入目標頁面，下面列出標題與部分 HTML：")
            print(driver.title)
            print(driver.page_source[:1500])

    except WebDriverException as e:
        print("[ERROR] WebDriver exception:", e)
    finally:
        # 不馬上關閉，視情況你可以註解掉 driver.quit() 來觀察
        try:
            driver.quit()
        except Exception:
            pass

if __name__ == "__main__":
    main()







from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
import time, pickle, os

CHROME_DRIVER_PATH = r"E:/tixcraft_b/chromedriver.exe"  # 改成你的 chromedriver 路徑
TARGET = "https://tixcraft.com/"
COOKIES_FILE = "cookies_tixcraft.pkl"

def make_driver(headless=False):
    opts = Options()
    # 基本選項
    opts.add_argument("--disable-notifications")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-gpu")
    # 建議: 先用 headful 模式測試
    if headless:
        # 若要 headless，可試 new headless
        opts.add_argument("--headless=new")
    # 模擬真實 user agent（可更新到你的真實瀏覽器 UA）
    ua = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.62 Safari/537.36")
    opts.add_argument(f"--user-agent={ua}")

    # 移除 automation flags
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)

    # optional: disable webdriver blink feature
    opts.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(service=Service(CHROME_DRIVER_PATH), options=opts)
    driver.set_page_load_timeout(60)

    # 使用 CDP 覆寫一些 navigator 屬性與 headers
    try:
        # 1) 覆寫 navigator.webdriver
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
                // 覆寫 navigator.webdriver
                Object.defineProperty(navigator, 'webdriver', {
                  get: () => undefined
                });
                // 模擬 languages
                Object.defineProperty(navigator, 'languages', {get: () => ['en-US','en']});
                // 模擬 plugins 長度 (簡單 hack)
                Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4]});
                // 有些站會檢查 permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                  parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
                );
                """
            }
        )

        # 2) 覆寫 UA & 加 extra headers（accept-language 等）
        driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": ua})
        driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {
            "headers": {
                "accept-language": "en-US,en;q=0.9,zh-TW;q=0.8",
            }
        })
    except Exception as e:
        print("[!] CDP commands failed:", e)

    return driver

def save_cookies(driver, path=COOKIES_FILE):
    with open(path, "wb") as f:
        pickle.dump(driver.get_cookies(), f)
    print("[*] Cookies saved to", path)

def load_cookies(driver, path=COOKIES_FILE):
    if not os.path.exists(path):
        return False
    driver.get(TARGET)  # 必須先開 domain
    time.sleep(1)
    with open(path, "rb") as f:
        cookies = pickle.load(f)
    for c in cookies:
        try:
            driver.add_cookie(c)
        except Exception:
            pass
    driver.refresh()
    print("[*] Cookies loaded")
    return True

def is_blocked(page_source):
    markers = [
        "Your browser hit a snag",
        "we need to make sure you're not a bot",
        "請確定您的 Cookie 和 JavaScript 已啟用",
        "您是機器人"
    ]
    low = page_source.lower()
    for m in markers:
        if m.lower() in low:
            return True
    return False

def main():
    driver = make_driver(headless=False)  # 先用有頭模式
    try:
        # 若有 cookie，先嘗試載入
        if os.path.exists(COOKIES_FILE):
            print("[*] cookies found, trying to use them")
            load_cookies(driver)

        # 打開頁面
        driver.get(TARGET)
        time.sleep(2)

        # 如果被擋，截圖並輸出提示
        if is_blocked(driver.page_source):
            print("[!] Page shows anti-bot / blocked. Saving screenshot blocked.png")
            driver.save_screenshot("blocked.png")
            print("Saved blocked.png for inspection.")
            # 嘗試等待並讓使用者手動處理
            print("If needed, complete any manual verification in the opened browser, then press Enter here.")
            input("Press Enter to continue after manual verification...")

        # 到這裡可能已登入或成功進入
        # 若尚未登入，可在此由 user 手動登入再存 cookie
        print("Page title:", driver.title)
        if not os.path.exists(COOKIES_FILE):
            # 讓使用者手動登入然後儲存 cookie
            print("If you have just logged in manually, press Enter to save cookies.")
            input("Press Enter to save cookies now (or Ctrl+C to cancel)...")
            save_cookies(driver)

        # 你可以在這裡加入後續的資料抓取邏輯
        # ex: print snippet
        print(driver.page_source[:2000])

    except (WebDriverException, TimeoutException) as e:
        print("WebDriver error:", e)
    finally:
        try:
            driver.quit()
        except Exception:
            pass

if __name__ == "__main__":
    main()





