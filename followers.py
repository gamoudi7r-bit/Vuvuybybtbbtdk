import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import warnings
import json
import re
import random

warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)

TELEGRAM_TOKEN = '7333758497:AAFolfOO-7bpJgdirCim0h9RNOOwjN43t2g'
TELEGRAM_CHAT_ID = '5443761489'

def send_telegram_notification(text):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        params = {'chat_id': TELEGRAM_CHAT_ID, 'text': text}
        requests.get(url, params=params, timeout=5)
    except Exception as e:
        print(f"Telegram notification failed: {e}")

LOGIN_PAGES = [
    "https://takipzan.com/login2",
    "https://fastfollow.in/member",
    "https://takipcikrali.com/login",
    "https://takipcimx.net/login",
    "https://takipciking.net/login",
    "https://takipcigen.com/login",
    "https://bigtakip.net/login",
    "https://takipcitime.net/login",
    "https://followersize.net/login",
    "https://birtakipci.net/login",
    "https://mixtakip.com/login",
    "https://takipcitime.com/login",
    "https://birtakipci.com/member",
    "https://takipcibase.com/login",
    "https://takip88.com/login",
    "https://followersize.com/member",
    "https://medyahizmeti.com/member",
    "https://www.hepsitakipci.com/member",
    "https://instamoda.org/login",
    "https://takipcimx.com/member",
    "https://takipcimax.com/login",
]

accounts = [
    "aabdennedi|ali123456",
    "hamma_garraoui|hama12345",
    "azizhanzouli7|aziz123456789",
    "sii___fon|saif12345",
    "omri_4165|ahmed123456",
  #  "ademmmmm__07|ademadem",
  #  "ayoub.ilahi|ayoub123456789",
    "aziz_ferchichi19|ferchichi123",
    "ademhassine_|ademhassine123",
    "belgarouiyoussef|youssef123",
]

random.shuffle(LOGIN_PAGES)
random.shuffle(accounts)

def run(target_username, log_callback=None, stop_check=None):
    def log(msg):
        if log_callback:
            log_callback(msg)
        else:
            print(msg)

    if not target_username:
        log("No target username")
        return

    send_telegram_notification(f"✅---Started Followers tool for @{target_username}")

    log(f"Target: {target_username}")
    cycle = 0
    while True:
        if stop_check and stop_check():
            log("\n Stop requested. Exiting tool.")
            break
        cycle += 1
        log(f"\n--- Cycle {cycle} ---")
        for site_idx, login_url in enumerate(LOGIN_PAGES, 1):
            if stop_check and stop_check():
                return
            log(f"→ Waiting {site_idx}")
            for acc_idx, acc in enumerate(accounts, 1):
                if stop_check and stop_check():
                    return
                log(f"  -Account {acc_idx}")
                try:
                    username, password = [x.strip() for x in acc.split("|")]
                    session = requests.Session()
                    session.verify = False
                    login_data = {"username": username, "password": password}
                    resp_login = session.post(login_url, data=login_data, timeout=30)
                    if resp_login.status_code != 200:
                        log("    Login failed")
                        continue
                    base_url = "/".join(login_url.split("/")[:3])
                    send_follower_url = f"{base_url}/tools/send-follower"
                    resp_page = session.get(send_follower_url, timeout=30)
                    if resp_page.status_code != 200:
                        log("    Cannot access send page")
                        continue
                    soup = BeautifulSoup(resp_page.text, "html.parser")
                    form = None
                    for f in soup.find_all("form"):
                        btn = f.find("button", string=lambda t: t and "Find User" in (t or ""))
                        if btn:
                            form = f
                            break
                    if not form:
                        log("    Form not found")
                        continue
                    action = form.get("action") or send_follower_url
                    if not action.startswith("http"):
                        action = urljoin(send_follower_url, action)
                    post_data = {}
                    for inp in form.find_all(["input", "textarea"]):
                        name = inp.get("name")
                        if name:
                            post_data[name] = inp.get("value", "")
                    post_data["username"] = target_username
                    resp_submit = session.post(action, data=post_data, timeout=30)
                    log("    User found")
                    if resp_submit.status_code != 200:
                        log("    Error submitting")
                        continue
                    time.sleep(1)
                    if stop_check and stop_check():
                        return
                    soup2 = BeautifulSoup(resp_submit.text, "html.parser")
                    adet_tag = soup2.find("input", {"name": "adet"})
                    adet = adet_tag.get("value", "20") if adet_tag else "20"
                    userID_tag = soup2.find("input", {"name": "userID"})
                    userID = userID_tag.get("value") if userID_tag else None
                    userName_tag = soup2.find("input", {"name": "userName"})
                    userName = userName_tag.get("value") if userName_tag else None
                    log(f"    Send-followers")
                    log(f"    UserID: {userID}, UserName: {userName}")
                    if not userID or not userName:
                        log("    Missing userID/userName")
                        continue
                    start_url = f"{base_url}/tools/send-follower/{userID}?formType=send"
                    start_data = {"adet": adet, "userID": userID, "userName": userName}
                    resp_start = session.post(start_url, data=start_data, timeout=30)
                    try:
                        json_match = re.search(r'\{.*\}', resp_start.text, re.DOTALL)
                        if json_match:
                            data = json.loads(json_match.group(0))
                            status = data.get("status", "").lower()
                            message = data.get("message", "")
                            log(f"    Status: {status}, Message: {message}")
                            if status == "success":
                                log("     -Success-")
                            else:
                                log(f"     Error: {message}")
                        else:
                            log("    No JSON response")
                    except Exception as e:
                        log(f"    JSON parse error: {e}")
                    time.sleep(3.5)
                except Exception as e:
                    log(f"    Exception: {type(e).__name__} - {e}")
                    continue
                log("  --------------------")
            log("-----------------------")
        log("\n Waiting 10 seconds...")
        for _ in range(10):
            if stop_check and stop_check():
                log("Stop requested during wait, exiting...")
                return
            time.sleep(1)

if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else input("Target: ")
    run(target)
