import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import warnings
import random
import json
import re
import threading

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

def run(target_media_url, log_callback=None, stop_check=None):
    def log(msg):
        if log_callback:
            log_callback(msg)
        else:
            print(msg)

    if not target_media_url:
        log(" No post URL provided → stopping")
        return

    send_telegram_notification(f"✅---post like URL: {target_media_url}")

    log(f"\n Target: {target_media_url}")
    log(f" Number of accounts: {len(accounts)}\n")
    log(" Starting infinite cycles... (press Stop to exit)\n")

    cycle = 0

    # ----- خيط heartbeat -----
    heartbeat_stop = threading.Event()
    def heartbeat_worker():
        while not heartbeat_stop.wait(300):
            send_telegram_notification(f"🔄 المستخدم لايزال يضيف إعجابات لـ {target_media_url}")

    heartbeat_thread = threading.Thread(target=heartbeat_worker, daemon=True)
    heartbeat_thread.start()

    # ----- ضمان إرسال رسالة التوقف عند الخروج من الدالة -----
    try:
        while True:
            if stop_check and stop_check():
                log("\n Tool stopped by user.")
                return

            cycle += 1
            log(f"\n━━━━━━━━━━ Cycle #{cycle} ━━━━━━━━━━\n")

            for i, login_url in enumerate(LOGIN_PAGES, 1):
                if stop_check and stop_check():
                    return

                site_alias = f"V{i}"
                log(f"  Waiting: {site_alias}")

                for j, acc in enumerate(accounts, 1):
                    if stop_check and stop_check():
                        return

                    account_alias = f"V{j}"
                    log(f"    Working...: {account_alias}")

                    try:
                        username, password = [x.strip() for x in acc.split("|")]
                        session = requests.Session()
                        session.verify = False

                        login_data = {"username": username, "password": password}
                        resp_login = session.post(login_url, data=login_data, timeout=30)
                        if resp_login.status_code != 200:
                            log(f"       Login failed ({resp_login.status_code})")
                            continue

                        base_url = "/".join(login_url.split("/")[:3])
                        send_like_url = f"{base_url}/tools/send-like"

                        resp_page = session.get(send_like_url, timeout=30)
                        if resp_page.status_code != 200:
                            log(f"       send-like page unavailable ({resp_page.status_code})")
                            continue

                        soup = BeautifulSoup(resp_page.text, "html.parser")
                        form = None
                        for f in soup.find_all("form"):
                            btn = f.find("button", string=lambda t: t and "Gönderiyi Bul" in (t or ""))
                            if btn:
                                form = f
                                break

                        if not form:
                            log("       'Gönderiyi Bul' form not found")
                            continue

                        action = form.get("action") or send_like_url
                        if not action.startswith("http"):
                            action = urljoin(send_like_url, action)

                        post_data = {}
                        for inp in form.find_all(["input", "textarea"]):
                            name = inp.get("name")
                            if name:
                                post_data[name] = inp.get("value", "")

                        post_data["mediaUrl"] = target_media_url

                        resp_submit = session.post(action, data=post_data, timeout=30)
                        if resp_submit.status_code != 200:
                            log(f"       Search request failed ({resp_submit.status_code})")
                            continue

                        time.sleep(1)
                        if stop_check and stop_check():
                            return

                        soup2 = BeautifulSoup(resp_submit.text, "html.parser")

                        adet = "10"
                        adet_tag = soup2.find("input", {"name": "adet"})
                        if adet_tag and adet_tag.get("value"):
                            adet = adet_tag["value"]

                        mediaID = None
                        mediaID_tag = soup2.find("input", {"name": "mediaID"})
                        if mediaID_tag and mediaID_tag.get("value"):
                            mediaID = mediaID_tag["value"]

                        if not mediaID:
                            log("       Failed to extract mediaID")
                            continue

                        start_url = f"{base_url}/tools/send-like/{mediaID}?formType=send"
                        start_data = {"adet": adet, "mediaID": mediaID}
                        resp_start = session.post(start_url, data=start_data, timeout=30)

                        if 200 <= resp_start.status_code < 300:
                            log("      → Response: OK")
                            log("       Likes sent successfully ")
                        else:
                            log(f"      → Response: {resp_start.status_code}")
                            log("       Failed to send likes")

                        time.sleep(1)

                        try:
                            json_match = re.search(r'\{.*\}', resp_start.text, re.DOTALL)
                            if json_match:
                                data = json.loads(json_match.group(0))
                                st = data.get("status", "").lower()
                                if st == "success":
                                    log("         success")
                                elif st == "error":
                                    log("         error")
                                else:
                                    log("        Unknown status")
                            else:
                                log("        (No clear JSON found)")
                        except:
                            log("        (Error reading response)")

                        time.sleep(1)

                    except Exception as e:
                        log(f"      ⚠ Error: {type(e).__name__} - {str(e)}")
                        continue

                    log("  ────────────────────────────────")
                log("───────────────────────────────────")

            log(f"\n Cycle {cycle} finished → waiting 10 seconds...\n")
            for _ in range(10):
                if stop_check and stop_check():
                    return
                time.sleep(1)
    finally:
        # إرسال رسالة التوقف وإيقاف خيط heartbeat
        send_telegram_notification(f"🛑 Stop --- post like URL: {target_media_url}")
        heartbeat_stop.set()

if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else input("Enter post URL: ")
    run(target)
