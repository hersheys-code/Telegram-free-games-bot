import requests
import time

TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

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

    requests.post(url, json=payload)

# 🔹 Epic Games
def get_epic_games():
    url = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"
    data = requests.get(url).json()

    games = data['data']['Catalog']['searchStore']['elements']
    result = []

    for game in games:
        try:
            if game['promotions'] and game['promotions']['promotionalOffers']:
                title = game['title']
                image = game['keyImages'][0]['url']
                slug = game['productSlug']
                link = f"https://store.epicgames.com/en-US/p/{slug}"

                result.append((title, image, link, "Epic Games"))
        except:
            pass

    return result

# 🔹 Steam (using unofficial API)
def get_steam_games():
    url = "https://www.cheapshark.com/api/1.0/deals?price=0"
    data = requests.get(url).json()

    result = []
    for game in data[:5]:
        title = game['title']
        image = game['thumb']
        link = f"https://www.cheapshark.com/redirect?dealID={game['dealID']}"

        result.append((title, image, link, "Steam"))

    return result

# 🔹 GOG (basic scraping alternative)
def get_gog_games():
    # GOG rarely gives free games, placeholder logic
    return []

def main():
    games = []

    games.extend(get_epic_games())
    games.extend(get_steam_games())
    games.extend(get_gog_games())

    if not games:
        message = "❌ No free games available right now."
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={
            "chat_id": CHAT_ID,
            "text": message
        })
        return

    for title, image, link, platform in games:
        caption = f"🎮 *{title}*\nPlatform: {platform}"
        send_telegram_photo(image, caption, "🎯 Claim Now", link)
        time.sleep(1)

if __name__ == "__main__":
    main()