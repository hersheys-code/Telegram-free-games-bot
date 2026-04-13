import requests
import time
import schedule

TOKEN = "8780000176:AAET74oRiIlBg9lpC5dbWIXKWap2FQbXo0c"
CHAT_ID = "8679251267"

# ------------------------------------------------
# Telegram sender
# ------------------------------------------------
def send_telegram_photo(photo_url, caption, button_text, button_url):
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    payload = {
        "chat_id": CHAT_ID,
        "photo": photo_url,
        "caption": caption,
        "parse_mode": "Markdown",
        "reply_markup": {
            "inline_keyboard": [[
                {"text": button_text, "url": button_url}
            ]]
        }
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"[Telegram] Failed to send message: {e}")


# ------------------------------------------------
# Epic Games (India locale)
# ------------------------------------------------
def get_epic_games():
    url = (
        "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"
        "?locale=en-IN&country=IN&allowCountries=IN"
    )
    try:
        data = requests.get(url, timeout=10).json()
        games = data['data']['Catalog']['searchStore']['elements']
    except Exception as e:
        print(f"[Epic] API error: {e}")
        return []

    result = []
    for game in games:
        try:
            promos = game.get('promotions')
            if not promos:
                continue
            offers = promos.get('promotionalOffers', [])
            if not offers or not offers[0].get('promotionalOffers'):
                continue

            # Confirm it's actually free (originalPrice != 0 means it's a real giveaway)
            offer_detail = offers[0]['promotionalOffers'][0]
            discount = offer_detail.get('discountSetting', {})
            if discount.get('discountPercentage', 100) != 0:
                continue  # Not 100% off

            title = game['title']

            # Build store link — prefer productSlug, fall back to urlSlug
            s# Try multiple slug sources
            slug = (
                game.get('productSlug') or
                game.get('urlSlug') or
                game.get('catalogNs', {}).get('mappings', [{}])[0].get('pageSlug') or
                ''
            )
slug = slug.replace('/home', '').strip('/')
if not slug:
    continue

# Use free-games page as fallback if slug looks invalid
if len(slug) < 3 or slug == '[]':
    link = "https://store.epicgames.com/en-IN/free-games"
else:
    link = f"https://store.epicgames.com/en-IN/p/{slug}"

            # Get best available image
            images = game.get('keyImages', [])
            image = images[0]['url'] if images else None
            if not image:
                continue

            result.append((title, image, link, "Epic Games"))
        except Exception as e:
            print(f"[Epic] Skipping game due to error: {e}")

    return result


# ------------------------------------------------
# Steam free promotions via CheapShark
# ------------------------------------------------
def get_steam_games():
    url = "https://www.cheapshark.com/api/1.0/deals?upperPrice=0&storeID=1"
    try:
        data = requests.get(url, timeout=10).json()
    except Exception as e:
        print(f"[Steam] API error: {e}")
        return []

    result = []
    seen = set()
    for game in data:
        try:
            if game.get("salePrice") != "0.00":
                continue
            title = game['title']
            if title in seen:
                continue
            seen.add(title)

            steam_id = game.get('steamAppID')
            if not steam_id:
                continue

            image = f"https://cdn.cloudflare.steamstatic.com/steam/apps/{steam_id}/header.jpg"
            link = f"https://store.steampowered.com/app/{steam_id}"
            result.append((title, image, link, "Steam"))
        except Exception as e:
            print(f"[Steam] Skipping game due to error: {e}")

    return result[:5]


# ------------------------------------------------
# GOG placeholder (rarely has free games)
# ------------------------------------------------
def get_gog_games():
    return []


# ------------------------------------------------
# Main runner — call this on a schedule
# ------------------------------------------------
sent_titles = set()  # persists across scheduled runs

def check_and_notify():
    print("[Bot] Checking for free games...")
    games = []
    games.extend(get_epic_games())
    games.extend(get_steam_games())
    games.extend(get_gog_games())

    if not games:
        print("[Bot] No free games found right now.")
        return

    new_games_found = 0
    for title, image, link, platform in games:
        if title in sent_titles:
            continue  # Already notified

        sent_titles.add(title)
        new_games_found += 1

        emoji = "🎮" if platform == "Steam" else "🎁"
        caption = (
     f"{emoji} *Free on {platform}!*\n\n"
     f"🕹 *{title}*\n\n"
     f"Claim it for free before the offer expires!\n\n"
     f"⚠️ If the link doesn't work, visit the Epic free games page directly."
 )
        )
        send_telegram_photo(image, caption, f"Claim on {platform} →", link)
        print(f"[Bot] Sent: {title} ({platform})")
        time.sleep(1)  # avoid Telegram rate limits

    if new_games_found == 0:
        print("[Bot] No new games since last check.")


# ------------------------------------------------
# Entry point — runs every 6 hours
# ------------------------------------------------
if __name__ == "__main__":
    check_and_notify()  # Run immediately on start

    schedule.every(7).days.do(check_and_notify)
    print("[Bot] Scheduler started. Checking every 6 hours.")

    while True:
        schedule.run_pending()
        time.sleep(60)
