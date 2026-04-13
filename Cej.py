from playwright.sync_api import sync_playwright
import time
import requests
import hashlib

# --- Configuration ---
SITES_TO_WATCH = [
    {
        "url": "https://udlejning.cej.dk/find-bolig/overblik?collection=residences&monthlyPrice=0-12000&p=sj%C3%A6lland%2Ck%C3%B8benhavn%2Cfrederiksberg%2Cfrederiksberg+c",
        "name": "CEJ",
        "type": "hash",
        "xpath": "//div[contains(@class,'grid')]/div/a/div/h6"
    },
    {
        "url": "https://kerebyudlejning.dk/",
        "name": "Kereby",
        "type": "set"
    }
]




# Telegram bot settings
BOT_TOKEN = "8671894349:AAGjNwzoWIV0-w-jLOyxQZ-U_5YnarWkqoc"
CHAT_ID = "-1003730924906"

# --- Helper functions ---
def normalize_text(text):
    return ' '.join(text.split()).strip()

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=payload)
        print("Telegram message sent!")
    except Exception as e:
        print(f"Error sending Telegram message: {e}")

# --- CEJ extractor (hash-based) ---
def extract_cej_hash(page, xpath):
    page.wait_for_selector(f"xpath={xpath}", timeout=15000)
    page.wait_for_timeout(2000)

    elements = page.query_selector_all(f"xpath={xpath}")
    texts = [normalize_text(el.inner_text()) for el in elements if normalize_text(el.inner_text())]

    combined = " | ".join(texts)
    return hashlib.md5(combined.encode("utf-8")).hexdigest(), combined

# --- Kereby extractor (set-based) ---
def extract_kereby_listings(page):
    page.wait_for_selector("a.rental-card", timeout=15000)

    elements = page.query_selector_all("a.rental-card")

    listings = set()
    for el in elements:
        href = el.get_attribute("href")
        if href:
            listings.add(href.strip())

    return listings

# --- Main monitoring loop ---
def main():
    last_hashes = {}
    last_seen_sets = {}

    print("Starting robust housing monitor...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        pages = {}

        # Open pages
        for site in SITES_TO_WATCH:
            page = browser.new_page()
            page.goto(site["url"])
            pages[site["name"]] = page

            if site["type"] == "hash":
                last_hashes[site["name"]] = None
            else:
                last_seen_sets[site["name"]] = set()

        while True:
            for site in SITES_TO_WATCH:
                page = pages[site["name"]]

                try:
                    page.reload()
                    page.wait_for_timeout(2000)

                    # --- HASH BASED (CEJ) ---
                    if site["type"] == "hash":
                        current_hash, text = extract_cej_hash(page, site["xpath"])

                        print(f"{site['name']} - Hash: {current_hash}")

                        if last_hashes[site["name"]] is None:
                            last_hashes[site["name"]] = current_hash
                            print(f"{site['name']} - Initial state stored.")

                        elif current_hash != last_hashes[site["name"]]:
                            print(f"{site['name']} - Change detected!")
                            send_telegram(
                                f"🚨 Ny opdatering ved {site['name']}!\n{site['url']}"
                            )
                            last_hashes[site["name"]] = current_hash

                        else:
                            print(f"{site['name']} - No change.")

                    # --- SET BASED (Kereby) ---
                    elif site["type"] == "set":
                        current_listings = extract_kereby_listings(page)

                        if not last_seen_sets[site["name"]]:
                            last_seen_sets[site["name"]] = current_listings
                            print(f"{site['name']} - Initial listings stored.")

                        else:
                            new_listings = current_listings - last_seen_sets[site["name"]]

                            if new_listings:
                                print(f"{site['name']} - New listings found!")

                                for listing in new_listings:
                                    send_telegram(
                                        f"🚨 Ny lejlighed ved {site['name']}!\n{listing}"
                                    )
                            else:
                                print(f"{site['name']} - No new listings.")

                            last_seen_sets[site["name"]] = current_listings

                except Exception as e:
                    print(f"{site['name']} - Error: {e}")

            print("Waiting 1 seconds...\n")
            time.sleep(1)

if __name__ == "__main__":
    main()
