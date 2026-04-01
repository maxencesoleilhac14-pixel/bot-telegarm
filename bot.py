import json
import logging
import os
from copy import deepcopy
from html import escape
from pathlib import Path
from time import time

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters


TOKEN = os.getenv("BOT_TOKEN", "PUT_YOUR_BOT_TOKEN_HERE")
ADMIN_ID = int(os.getenv("ADMIN_ID", "8567294409"))
DATA_FILE = Path(__file__).with_name("shop_data.json")
LOGO_FILE = Path(__file__).with_name("logo.png")
PAYPAL_LINK = os.getenv("PAYPAL_LINK", "https://www.paypal.me/crz843026")
LEETCHI_LINK = os.getenv("LEETCHI_LINK", "https://www.leetchi.com/fr/contribution/2tech-1019764/amount")
SUPPORT_HANDLE = os.getenv("SUPPORT_HANDLE", "@sky13k")
SERVER_LINK = os.getenv("SERVER_LINK", "https://t.me/+2uteXORftB02Mzc0")
CRYPTO_TEXT = os.getenv(
    "CRYPTO_TEXT",
    "Bitcoin : bc1q0mwntue4rkz6rygcc40y2lwx0mc6y8clj6svhw\n\n"
    "Solana : 89zWXgADYNeYz9H46kgokLYyA7CxAbAbxNKrtUBsr3dh\n\n"
    "Ethereum : 0xf776906e1A254f9043C0994346c446fe0569F6b2",
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

DEFAULT_PRODUCTS = {
    "mcdo_50_74": {"name": "McDo 50-74 pts", "price": 3.0, "category": "fastfood", "subcategory": "mcdo", "type": "manual", "active": True},
    "mcdo_75_99": {"name": "McDo 75-99 pts", "price": 4.5, "category": "fastfood", "subcategory": "mcdo", "type": "manual", "active": True},
    "mcdo_100_124": {"name": "McDo 100-124 pts", "price": 6.0, "category": "fastfood", "subcategory": "mcdo", "type": "manual", "active": True},
    "mcdo_125_149": {"name": "McDo 125-149 pts", "price": 7.0, "category": "fastfood", "subcategory": "mcdo", "type": "manual", "active": True},
    "mcdo_150_174": {"name": "McDo 150-174 pts", "price": 8.0, "category": "fastfood", "subcategory": "mcdo", "type": "manual", "active": True},
    "mcdo_175_199": {"name": "McDo 175-199 pts", "price": 9.0, "category": "fastfood", "subcategory": "mcdo", "type": "manual", "active": True},
    "mcdo_200_224": {"name": "McDo 200-224 pts", "price": 10.0, "category": "fastfood", "subcategory": "mcdo", "type": "manual", "active": True},
    "mcdo_225_249": {"name": "McDo 225-249 pts", "price": 14.0, "category": "fastfood", "subcategory": "mcdo", "type": "manual", "active": True},
    "mcdo_250_274": {"name": "McDo 250-274 pts", "price": 15.0, "category": "fastfood", "subcategory": "mcdo", "type": "manual", "active": True},
    "mcdo_275_299": {"name": "McDo 275-299 pts", "price": 16.0, "category": "fastfood", "subcategory": "mcdo", "type": "manual", "active": True},
    "kfc_600_799": {"name": "KFC 600-799 pts", "price": 5.0, "category": "fastfood", "subcategory": "kfc", "type": "manual", "active": True},
    "kfc_800_999": {"name": "KFC 800-999 pts", "price": 6.25, "category": "fastfood", "subcategory": "kfc", "type": "manual", "active": True},
    "kfc_1000_1299": {"name": "KFC 1000-1299 pts", "price": 7.25, "category": "fastfood", "subcategory": "kfc", "type": "manual", "active": True},
    "kfc_1300_1599": {"name": "KFC 1300-1599 pts", "price": 8.0, "category": "fastfood", "subcategory": "kfc", "type": "manual", "active": True},
    "kfc_1600_1799": {"name": "KFC 1600-1799 pts", "price": 8.75, "category": "fastfood", "subcategory": "kfc", "type": "manual", "active": True},
    "kfc_1800_2099": {"name": "KFC 1800-2099 pts", "price": 9.5, "category": "fastfood", "subcategory": "kfc", "type": "manual", "active": True},
    "kfc_2100_2499": {"name": "KFC 2100-2499 pts", "price": 11.0, "category": "fastfood", "subcategory": "kfc", "type": "manual", "active": True},
    "kfc_2500": {"name": "KFC 2500 pts", "price": 12.5, "category": "fastfood", "subcategory": "kfc", "type": "manual", "active": True},
    "ubereats_offer": {"name": "Uber Eats -50%", "price": 20.0, "category": "ubereats", "type": "manual", "active": True},
    "osint_offer": {"name": "Recherche OSINT", "price": 5.0, "category": "osint", "type": "manual", "active": True},
    "deezer_premium": {"name": "Deezer Premium", "price": 5.0, "category": "subscriptions", "type": "stock", "active": False},
    "spotify_premium": {"name": "Spotify Premium", "price": 15.5, "category": "subscriptions", "type": "manual", "active": True},
    "netflix": {"name": "Netflix", "price": 13.5, "category": "subscriptions", "type": "stock", "active": False},
    "crunchyroll": {"name": "Crunchyroll", "price": 6.0, "category": "subscriptions", "type": "stock", "active": False},
    "chatgpt": {"name": "ChatGPT", "price": 12.5, "category": "subscriptions", "type": "stock", "active": False},
    "disney_plus": {"name": "Disney+", "price": 9.99, "category": "subscriptions", "type": "stock", "active": False},
    "amazon_prime": {"name": "Amazon Prime", "price": 8.0, "category": "subscriptions", "type": "stock", "active": False},
    "snapchat": {"name": "Snapchat", "price": 10.0, "category": "subscriptions", "type": "stock", "active": False},
    "discord_nitro": {"name": "Nitro", "price": 1.9, "category": "boosts", "subcategory": "discord", "type": "manual", "active": True},
    "basic_fit": {"name": "Basic Fit", "price": 35.0, "category": "subscriptions", "type": "stock", "active": False},
    "tiktok_boost": {"name": "1K vues TikTok", "price": 0.6, "category": "boosts", "subcategory": "tiktok", "type": "manual", "active": True},
    "tiktok_followers": {"name": "1K abonnes TikTok", "price": 2.0, "category": "boosts", "subcategory": "tiktok", "type": "manual", "active": True},
    "insta_boost": {"name": "1K abonnes Instagram", "price": 2.0, "category": "boosts", "subcategory": "instagram", "type": "manual", "active": True},
    "insta_views": {"name": "1K vues Instagram", "price": 0.6, "category": "boosts", "subcategory": "instagram", "type": "manual", "active": True},
    "discord_boost": {"name": "Nitro Boost", "price": 3.9, "category": "boosts", "subcategory": "discord", "type": "manual", "active": True},
    "refund_eneba": {"name": "Rfund Eneba", "price": 50.0, "category": "refunds", "type": "manual", "active": False},
    "refund_uber": {"name": "Rfund Uber", "price": 50.0, "category": "refunds", "type": "manual", "active": False},
    "burger_king": {"name": "Burger King", "price": 1.5, "category": "fastfood", "type": "manual", "active": False},
    "kfc": {"name": "KFC", "price": 5.0, "category": "fastfood", "type": "manual", "active": False},
    "quick": {"name": "Quick", "price": 4.0, "category": "fastfood", "type": "manual", "active": False},
    "flunch": {"name": "Flunch", "price": 5.0, "category": "fastfood", "type": "manual", "active": False},
    "otacos": {"name": "O'Tacos", "price": 5.0, "category": "fastfood", "type": "manual", "active": False},
    "card_zalando": {"name": "Carte Zalando", "price": 10.0, "category": "giftcards", "type": "stock", "active": False},
    "card_carrefour": {"name": "Carte Carrefour", "price": 10.0, "category": "giftcards", "type": "stock", "active": False},
    "card_conforama": {"name": "Carte Conforama", "price": 10.0, "category": "giftcards", "type": "stock", "active": False},
}

FASTFOOD_SUBCATEGORY_NAMES = {
    "mcdo": "🍔 McDo",
    "kfc": "🍗 KFC",
}

BOOST_SUBCATEGORY_NAMES = {
    "tiktok": "🎵 TikTok",
    "instagram": "📸 Instagram",
    "discord": "💬 Discord",
}

CATEGORY_NAMES = {
    "ubereats": "🛵 Uber Eats -50%",
    "osint": "🕵️ Recherche OSINT",
    "fastfood": "🍔 Fast Food",
    "subscriptions": "🎧 Abonnements",
    "giftcards": "🎁 Cartes cadeaux",
    "boosts": "🚀 Boost reseaux",
    "refunds": "💸 Rfunds",
}
STATUS_NAMES = {
    "quote_pending": "Tarif en attente",
    "awaiting_proof": "En attente de preuve",
    "proof_received": "Preuve recue",
    "awaiting_delivery": "A livrer",
    "delivered": "Livree",
    "cancelled": "Annulee",
}

TICKET_STATUS_NAMES = {
    "pending": "En attente",
    "open": "Ouvert",
    "closed": "Ferme",
}


def default_data():
    return {
        "users": {},
        "balance_logs": [],
        "products": deepcopy(DEFAULT_PRODUCTS),
        "stock": {},
        "orders": {},
        "deposits": {},
        "tickets": {},
        "support_admins": [],
        "shop_open": True,
        "next_order_id": 1,
        "next_deposit_id": 1,
        "next_ticket_id": 1,
    }


def save_data():
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(DATA, file, indent=2, ensure_ascii=False)


def load_data():
    if DATA_FILE.exists():
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
    else:
        data = default_data()
    data.setdefault("users", {})
    data.setdefault("balance_logs", [])
    data.setdefault("products", {})
    data.setdefault("stock", {})
    data.setdefault("orders", {})
    data.setdefault("deposits", {})
    data.setdefault("tickets", {})
    data.setdefault("support_admins", [])
    data.setdefault("shop_open", True)
    data.setdefault("next_order_id", 1)
    data.setdefault("next_deposit_id", 1)
    data.setdefault("next_ticket_id", 1)
    for product_id, product in DEFAULT_PRODUCTS.items():
        data["products"].setdefault(product_id, deepcopy(product))
    for product_id, product in data["products"].items():
        if product_id.startswith("mcdo_"):
            product.setdefault("subcategory", "mcdo")
        elif product_id.startswith("kfc_"):
            product.setdefault("subcategory", "kfc")
        elif product_id in {"tiktok_boost", "tiktok_followers"}:
            product["category"] = "boosts"
            product["subcategory"] = "tiktok"
            product["type"] = "manual"
        elif product_id in {"insta_boost", "insta_views"}:
            product["category"] = "boosts"
            product["subcategory"] = "instagram"
            product["type"] = "manual"
        elif product_id in {"discord_nitro", "discord_boost"}:
            product["category"] = "boosts"
            product["subcategory"] = "discord"
            product["type"] = "manual"
        elif product_id == "spotify_premium":
            product["category"] = "subscriptions"
            product["type"] = "manual"
    for product_id, product in data["products"].items():
        if product["type"] == "stock":
            data["stock"].setdefault(product_id, [])
    for migrated_id in ["tiktok_boost", "tiktok_followers", "insta_boost", "insta_views", "discord_nitro", "discord_boost"]:
        if migrated_id in data["products"]:
            data["products"][migrated_id]["name"] = DEFAULT_PRODUCTS[migrated_id]["name"]
            data["products"][migrated_id]["price"] = DEFAULT_PRODUCTS[migrated_id]["price"]
            data["products"][migrated_id]["active"] = True
            data["products"][migrated_id]["category"] = DEFAULT_PRODUCTS[migrated_id]["category"]
            data["products"][migrated_id]["type"] = DEFAULT_PRODUCTS[migrated_id]["type"]
            data["products"][migrated_id]["subcategory"] = DEFAULT_PRODUCTS[migrated_id].get("subcategory")
    if "spotify_premium" in data["products"]:
        data["products"]["spotify_premium"]["name"] = DEFAULT_PRODUCTS["spotify_premium"]["name"]
        data["products"]["spotify_premium"]["price"] = DEFAULT_PRODUCTS["spotify_premium"]["price"]
        data["products"]["spotify_premium"]["category"] = DEFAULT_PRODUCTS["spotify_premium"]["category"]
        data["products"]["spotify_premium"]["type"] = DEFAULT_PRODUCTS["spotify_premium"]["type"]
        data["products"]["spotify_premium"]["active"] = True
    for forced_off in [
        "deezer_premium",
        "netflix",
        "crunchyroll",
        "chatgpt",
        "disney_plus",
        "amazon_prime",
        "snapchat",
        "basic_fit",
        "refund_eneba",
        "refund_uber",
        "burger_king",
        "kfc",
        "quick",
        "flunch",
        "otacos",
        "card_zalando",
        "card_carrefour",
        "card_conforama",
    ]:
        if forced_off in data["products"]:
            data["products"][forced_off]["active"] = False
    for ticket in data["tickets"].values():
        ticket.setdefault("category", "question")
        ticket.setdefault("username", "Aucun")
        ticket.setdefault("details", {})
    for order in data["orders"].values():
        order.setdefault("manual_delivery_queue", [])
        order.setdefault("manual_delivery_sent", [])
        order.setdefault("payment_method", None)
        order.setdefault("result_buffer", [])
        if order.get("status") == "awaiting_delivery" and not order["manual_delivery_queue"]:
            manual_items = []
            for product_id in order.get("items", []):
                product = data["products"].get(product_id)
                if product and product.get("type") == "manual":
                    manual_items.append(product_id)
            order["manual_delivery_queue"] = manual_items
    for deposit in data["deposits"].values():
        deposit.setdefault("payment_method", None)
    return data


DATA = load_data()
save_data()


def ensure_user(user_id):
    user_key = str(user_id)
    if user_key not in DATA["users"]:
        DATA["users"][user_key] = {
            "cart": [],
            "balance": 0.0,
            "awaiting_order_id": None,
            "awaiting_deposit_id": None,
            "admin_state": None,
            "state": None,
            "username": None,
            "display_name": None,
        }
        save_data()
    else:
        DATA["users"][user_key].setdefault("state", None)
        DATA["users"][user_key].setdefault("balance", 0.0)
        DATA["users"][user_key].setdefault("awaiting_deposit_id", None)
        DATA["users"][user_key].setdefault("username", None)
        DATA["users"][user_key].setdefault("display_name", None)
    return DATA["users"][user_key]


def sync_user_profile(user):
    user_data = ensure_user(user.id)
    username = f"@{user.username}" if user.username else None
    display_name = " ".join(part for part in [user.first_name, user.last_name] if part) or username or str(user.id)
    changed = False
    if user_data.get("username") != username:
        user_data["username"] = username
        changed = True
    if user_data.get("display_name") != display_name:
        user_data["display_name"] = display_name
        changed = True
    if changed:
        save_data()
    return user_data


def is_owner(user_id):
    return user_id == ADMIN_ID


def is_support_admin(user_id):
    return str(user_id) in {str(value) for value in DATA.get("support_admins", [])}


def is_admin(user_id):
    return is_owner(user_id) or is_support_admin(user_id)


def fmt_price(value):
    return f"{value:.2f}".rstrip("0").rstrip(".") + "€"


def get_product(product_id):
    return DATA["products"].get(product_id)


def ubereats_product():
    return get_product("ubereats_offer")


def osint_product():
    return get_product("osint_offer")


def boost_product(product_id):
    return get_product(product_id)


def stock_count(product_id):
    return len(DATA["stock"].get(product_id, []))


def cart_total(items):
    total = 0.0
    for product_id in items:
        product = get_product(product_id)
        if product:
            total += float(product["price"])
    return total


def extract_product_order(product_id):
    for prefix in ("mcdo_", "kfc_"):
        if product_id.startswith(prefix):
            suffix = product_id[len(prefix):]
            try:
                return int(suffix.split("_")[0])
            except ValueError:
                return 9999
    return 9999


def product_rows(category, include_inactive=False, subcategory=None):
    rows = []
    for product_id, product in DATA["products"].items():
        if product["category"] != category:
            continue
        if subcategory and product.get("subcategory") != subcategory:
            continue
        if not include_inactive and not product.get("active", True):
            continue
        rows.append((product_id, product))

    def sort_key(row):
        product_id, product = row
        if product_id.startswith(("mcdo_", "kfc_")):
            return (0, extract_product_order(product_id), product["name"].lower())
        return (1, product["name"].lower())

    return sorted(rows, key=sort_key)


def order_lines(order):
    if order.get("order_kind") == "ubereats":
        label = "Uber Eats -50%"
        price = fmt_price(float(order.get("total", 0))) if float(order.get("total", 0)) > 0 else "montant a fixer"
        return f"- {label} ({price})"
    if order.get("order_kind") == "osint":
        price = fmt_price(float(order.get("total", 0))) if float(order.get("total", 0)) > 0 else "montant a fixer"
        return f"- Recherche OSINT ({price})"
    if order.get("order_kind") == "spotify":
        return f"- Spotify Premium ({fmt_price(float(order.get('total', 0)))})"
    if order.get("order_kind") == "boost":
        product = get_product(order["items"][0]) if order.get("items") else None
        label = product["name"] if product else "Boost reseaux"
        return f"- {label} ({fmt_price(float(order.get('total', 0)))})"
    lines = []
    for product_id in order["items"]:
        product = get_product(product_id)
        if product:
            lines.append(f"- {product['name']} ({fmt_price(float(product['price']))})")
    return "\n".join(lines) if lines else "- Produit inconnu"


def admin_order_item_lines(order):
    if order.get("order_kind") == "ubereats":
        price = fmt_price(float(order.get("total", 0))) if float(order.get("total", 0)) > 0 else "montant a fixer"
        return f"- Uber Eats -50% | {price} | {'En attente' if order.get('status') != 'delivered' else 'Livre'}"
    if order.get("order_kind") == "osint":
        price = fmt_price(float(order.get("total", 0))) if float(order.get("total", 0)) > 0 else "montant a fixer"
        return f"- Recherche OSINT | {price} | {'En attente' if order.get('status') != 'delivered' else 'Livre'}"
    if order.get("order_kind") == "spotify":
        price = fmt_price(float(order.get("total", 0)))
        return f"- Spotify Premium | {price} | {'En attente' if order.get('status') != 'delivered' else 'Livre'}"
    if order.get("order_kind") == "boost":
        product = get_product(order["items"][0]) if order.get("items") else None
        label = product["name"] if product else "Boost reseaux"
        price = fmt_price(float(order.get("total", 0)))
        return f"- {label} | {price} | {'En attente' if order.get('status') != 'delivered' else 'Livre'}"
    lines = []
    waiting_queue = list(order.get("manual_delivery_queue") or [])
    delivered_manual = list(order.get("manual_delivery_sent") or [])
    for product_id in order["items"]:
        product = get_product(product_id)
        if not product:
            lines.append("- Produit inconnu")
            continue
        status = "A traiter"
        if not product.get("active", True):
            status = "Indispo actuellement"
        if product["type"] == "stock":
            status = "Auto / stock"
        elif product_id in delivered_manual:
            status = "Livre"
        elif product_id in waiting_queue:
            status = "En attente"
        lines.append(f"- {product['name']} | {fmt_price(float(product['price']))} | {status}")
    return "\n".join(lines)


def removable_order_buttons(order_id, order):
    rows = []
    for index, product_id in enumerate(order["items"]):
        product = get_product(product_id)
        if not product:
            continue
        rows.append(
            [
                InlineKeyboardButton(
                    f"Retirer {index + 1}. {product['name']}",
                    callback_data=f"admin:modifyremove:{order_id}:{index}",
                )
            ]
        )
    return rows


def client_recent_transactions(user_id, limit=5):
    entries = []
    user_key = str(user_id)
    balance = float(DATA["users"].get(user_key, {}).get("balance", 0.0))

    for order_id, order in DATA["orders"].items():
        if str(order.get("user_id")) != str(user_id):
            continue
        entries.append(
            (
                int(order_id),
                f"Commande {order_id} | {STATUS_NAMES.get(order.get('status'), order.get('status'))} | {fmt_price(float(order.get('total', 0)))}"
            )
        )

    for deposit_id, deposit in DATA["deposits"].items():
        if str(deposit.get("user_id")) != str(user_id):
            continue
        deposit_status = {
            "awaiting_proof": "En attente",
            "proof_received": "Preuve recue",
            "approved": "Valide",
            "cancelled": "Refuse",
        }.get(deposit.get("status"), deposit.get("status"))
        entries.append(
            (
                1000000 + int(deposit_id),
                f"Depot {deposit_id} | {deposit_status} | {fmt_price(float(deposit.get('amount', 0)))}"
            )
        )

    entries.sort(key=lambda item: item[0], reverse=True)
    return balance, [text for _, text in entries[:limit]]


def payment_method_label(method):
    labels = {
        "paypal": "PayPal",
        "applepay": "Apple Pay",
        "googlepay": "Google Pay",
        "bitcoin": "Bitcoin",
        "solana": "Solana",
        "ethereum": "Ethereum",
        "balance": "Solde",
        None: "Non renseigne",
    }
    return labels.get(method, str(method))


def log_balance_event(user_id, delta, reason, source, payment_method=None):
    DATA.setdefault("balance_logs", []).append(
        {
            "event_id": len(DATA.get("balance_logs", [])) + 1,
            "user_id": int(user_id),
            "delta": round(float(delta), 2),
            "reason": reason,
            "source": source,
            "payment_method": payment_method,
        }
    )


def client_label(user_id):
    user_data = ensure_user(user_id)
    return user_data.get("username") or user_data.get("display_name") or str(user_id)


def admin_client_header(user_id):
    label = client_label(user_id)
    if label == str(user_id):
        return str(user_id)
    return f"{label} | {user_id}"


def client_has_activity(user_id):
    user_key = str(user_id)
    if any(str(order.get("user_id")) == user_key for order in DATA["orders"].values()):
        return True
    if any(str(deposit.get("user_id")) == user_key for deposit in DATA["deposits"].values()):
        return True
    if any(str(ticket.get("user_id")) == user_key for ticket in DATA["tickets"].values()):
        return True
    if any(str(entry.get("user_id")) == user_key for entry in DATA.get("balance_logs", [])):
        return True
    return False


def all_client_transactions(user_id, limit=25):
    entries = []
    user_key = str(user_id)
    for order_id, order in DATA["orders"].items():
        if str(order.get("user_id")) != user_key:
            continue
        order_kind = "Uber Eats" if order.get("order_kind") == "ubereats" else "Commande"
        entries.append(
            (
                int(order_id),
                f"{order_kind} {order_id} | {STATUS_NAMES.get(order.get('status'), order.get('status'))} | {fmt_price(float(order.get('total', 0)))} | {payment_method_label(order.get('payment_method'))}"
            )
        )
    for deposit_id, deposit in DATA["deposits"].items():
        if str(deposit.get("user_id")) != user_key:
            continue
        deposit_status = {
            "awaiting_proof": "En attente",
            "proof_received": "Preuve recue",
            "approved": "Valide",
            "cancelled": "Refuse",
        }.get(deposit.get("status"), deposit.get("status"))
        entries.append(
            (
                1000000 + int(deposit_id),
                f"Depot {deposit_id} | {deposit_status} | {fmt_price(float(deposit.get('amount', 0)))} | {payment_method_label(deposit.get('payment_method'))}"
            )
        )
    for entry in DATA.get("balance_logs", []):
        if str(entry.get("user_id")) != user_key:
            continue
        entries.append(
            (
                2000000 + int(entry.get("event_id", 0)),
                f"Solde | {entry.get('reason', 'Mouvement')} | {fmt_price(abs(float(entry.get('delta', 0))))} | {'+' if float(entry.get('delta', 0)) >= 0 else '-'} | {payment_method_label(entry.get('payment_method'))}"
            )
        )
    entries.sort(key=lambda item: item[0], reverse=True)
    return [text for _, text in entries[:limit]]


def fastfood_order_hint(order):
    if order.get("order_kind") == "ubereats":
        return "Commande Uber Eats -50%"
    if order.get("order_kind") == "osint":
        return "Recherche OSINT"
    if order.get("order_kind") == "spotify":
        return "Spotify Premium"
    if order.get("order_kind") == "boost":
        if order.get("items"):
            product = get_product(order["items"][0])
            if product:
                return product["name"]
        return "Boost reseaux"
    brands = []
    for product_id in order["items"]:
        product = get_product(product_id)
        if not product or product.get("category") != "fastfood":
            continue
        subcategory = product.get("subcategory")
        if subcategory == "mcdo" and "McDo" not in brands:
            brands.append("McDo")
        if subcategory == "kfc" and "KFC" not in brands:
            brands.append("KFC")
    if not brands:
        return "Commande"
    if len(brands) == 1:
        return f"Commande {brands[0]}"
    return "Commande " + " + ".join(brands)


def shop_is_open():
    return bool(DATA.get("shop_open", True))


def shop_status_label():
    return "🟢 Boutique ON" if shop_is_open() else "🔴 Boutique OFF"


def active_delivery_order_id(user_id):
    admin_state = ensure_user(user_id).get("admin_state") or {}
    if admin_state.get("action") in {"deliver", "uber_link", "osint_result", "boost_result", "spotify_result"}:
        return admin_state.get("order_id")
    return None


def main_menu(user_id):
    rows = [
        [InlineKeyboardButton("🛒 Boutique", callback_data="menu:shop")],
        [InlineKeyboardButton("💰 Depot", callback_data="deposit:home")],
        [InlineKeyboardButton("📦 Panier", callback_data="menu:cart")],
        [InlineKeyboardButton("📋 Mes commandes", callback_data="menu:orders")],
        [InlineKeyboardButton("🆘 Report / ticket", callback_data="ticket:new")],
        [InlineKeyboardButton("🔥 Serveur", url=SERVER_LINK)],
    ]
    if is_admin(user_id):
        rows.append([InlineKeyboardButton("🛠️ Panel admin", callback_data="admin:home")])
    return InlineKeyboardMarkup(rows)


def payment_methods_menu():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("💙 PayPal", callback_data="pay:method:paypal")],
            [InlineKeyboardButton(" Apple Pay", callback_data="pay:method:applepay")],
            [InlineKeyboardButton("🅖 Google Pay", callback_data="pay:method:googlepay")],
            [InlineKeyboardButton("₿ Bitcoin", callback_data="pay:method:bitcoin")],
            [InlineKeyboardButton("◎ Solana", callback_data="pay:method:solana")],
            [InlineKeyboardButton("◆ Ethereum", callback_data="pay:method:ethereum")],
            [InlineKeyboardButton("❌ Annuler", callback_data="pay:cancel")],
        ]
    )


def deposit_amounts_menu():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("15€", callback_data="deposit:amount:15"), InlineKeyboardButton("20€", callback_data="deposit:amount:20")],
            [InlineKeyboardButton("30€", callback_data="deposit:amount:30"), InlineKeyboardButton("50€", callback_data="deposit:amount:50")],
            [InlineKeyboardButton("100€", callback_data="deposit:amount:100")],
            [InlineKeyboardButton("✍️ Montant personnalise", callback_data="deposit:custom")],
            [InlineKeyboardButton("⬅️ Retour", callback_data="menu:start")],
        ]
    )


def checkout_methods_menu(balance, total):
    rows = [
        [InlineKeyboardButton("💙 PayPal", callback_data="pay:method:paypal")],
        [InlineKeyboardButton(" Apple Pay", callback_data="pay:method:applepay")],
        [InlineKeyboardButton("🅖 Google Pay", callback_data="pay:method:googlepay")],
        [InlineKeyboardButton("₿ Bitcoin", callback_data="pay:method:bitcoin")],
        [InlineKeyboardButton("◎ Solana", callback_data="pay:method:solana")],
        [InlineKeyboardButton("◆ Ethereum", callback_data="pay:method:ethereum")],
    ]
    if balance >= total:
        rows.append([InlineKeyboardButton("💼 Payer par solde", callback_data="pay:method:balance")])
    rows.append([InlineKeyboardButton("❌ Annuler", callback_data="pay:cancel")])
    return InlineKeyboardMarkup(rows)


def payment_detail_menu():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✅ J'ai payé", callback_data="pay:confirm")],
            [InlineKeyboardButton("❌ Annuler la commande", callback_data="pay:cancel")],
        ]
    )


def fastfood_menu():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🍔 McDo", callback_data="subcat:mcdo")],
            [InlineKeyboardButton("🍗 KFC", callback_data="subcat:kfc")],
            [InlineKeyboardButton("👑 Burger King", callback_data="soon:burger_king")],
            [InlineKeyboardButton("🍟 Quick", callback_data="soon:quick")],
            [InlineKeyboardButton("🥗 Flunch", callback_data="soon:flunch")],
            [InlineKeyboardButton("🌮 O'Tacos", callback_data="soon:otacos")],
            [InlineKeyboardButton("⬅️ Retour", callback_data="menu:shop")],
        ]
    )


def boosts_menu():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🎵 TikTok", callback_data="boostsubcat:tiktok")],
            [InlineKeyboardButton("📸 Instagram", callback_data="boostsubcat:instagram")],
            [InlineKeyboardButton("💬 Discord", callback_data="boostsubcat:discord")],
            [InlineKeyboardButton("⬅️ Retour", callback_data="menu:shop")],
        ]
    )


def categories_menu():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🛵 Uber Eats -50%", callback_data="cat:ubereats")],
            [InlineKeyboardButton("🕵️ Recherche OSINT", callback_data="cat:osint")],
            [InlineKeyboardButton("🍔 Fast Food", callback_data="cat:fastfood")],
            [InlineKeyboardButton("🎧 Abonnements", callback_data="cat:subscriptions")],
            [InlineKeyboardButton("🎁 Cartes cadeaux", callback_data="cat:giftcards")],
            [InlineKeyboardButton("🚀 Boost reseaux", callback_data="cat:boosts")],
            [InlineKeyboardButton("💸 Refunds", callback_data="cat:refunds")],
            [InlineKeyboardButton("⬅️ Retour", callback_data="menu:start")],
        ]
    )


def admin_menu():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📦 Produits", callback_data="admin:products")],
            [InlineKeyboardButton("🧾 Commandes", callback_data="admin:orders")],
            [InlineKeyboardButton("👤 Clients", callback_data="admin:clients")],
            [InlineKeyboardButton("💼 Ajouter du solde", callback_data="admin:addbalance")],
            [InlineKeyboardButton(shop_status_label(), callback_data="admin:shoptoggle")],
            [InlineKeyboardButton("👥 Gerer les admins", callback_data="admin:staff")],
            [InlineKeyboardButton("🎫 Gestion tickets", callback_data="admin:tickets")],
            [InlineKeyboardButton("🔑 Stock", callback_data="admin:stock")],
            [InlineKeyboardButton("📊 Stats", callback_data="admin:stats")],
            [InlineKeyboardButton("🏠 Accueil", callback_data="menu:start")],
        ]
    )


def support_admin_menu():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(shop_status_label(), callback_data="admin:shoptoggle")],
            [InlineKeyboardButton("🎫 Tickets support", callback_data="admin:ticketsupport")],
            [InlineKeyboardButton("🏠 Accueil", callback_data="menu:start")],
        ]
    )


def admin_staff_menu():
    rows = [
        [InlineKeyboardButton("➕ Ajouter un admin", callback_data="admin:staff:add")],
    ]
    for admin_id in DATA.get("support_admins", []):
        rows.append([InlineKeyboardButton(f"➖ Retirer {admin_id}", callback_data=f"admin:staff:remove:{admin_id}")])
    rows.append([InlineKeyboardButton("⬅️ Retour", callback_data="admin:home")])
    return InlineKeyboardMarkup(rows)


def create_order(user_id):
    user_data = ensure_user(user_id)
    if not user_data["cart"]:
        return None
    order_id = str(DATA["next_order_id"])
    DATA["next_order_id"] += 1
    DATA["orders"][order_id] = {
        "user_id": user_id,
        "items": user_data["cart"][:],
        "total": cart_total(user_data["cart"]),
        "status": "awaiting_proof",
        "payment_method": None,
        "expires_at": int(time()) + (8 * 60),
        "proof_file_id": None,
        "stock_keys_sent": [],
        "manual_delivery_queue": [],
        "manual_delivery_sent": [],
    }
    user_data["cart"] = []
    user_data["awaiting_order_id"] = order_id
    save_data()
    return order_id


def create_ubereats_order(user_id, address, order_total, screenshot_file_id):
    order_id = str(DATA["next_order_id"])
    DATA["next_order_id"] += 1
    DATA["orders"][order_id] = {
        "user_id": user_id,
        "items": [],
        "total": 0.0,
        "status": "quote_pending",
        "payment_method": None,
        "expires_at": None,
        "proof_file_id": None,
        "stock_keys_sent": [],
        "manual_delivery_queue": [],
        "manual_delivery_sent": [],
        "order_kind": "ubereats",
        "request_file_id": screenshot_file_id,
        "ubereats_address": address,
        "ubereats_total": float(order_total),
    }
    save_data()
    return order_id


def create_osint_order(user_id, request_text):
    order_id = str(DATA["next_order_id"])
    DATA["next_order_id"] += 1
    DATA["orders"][order_id] = {
        "user_id": user_id,
        "items": [],
        "total": 0.0,
        "status": "quote_pending",
        "payment_method": None,
        "expires_at": None,
        "proof_file_id": None,
        "stock_keys_sent": [],
        "manual_delivery_queue": [],
        "manual_delivery_sent": [],
        "order_kind": "osint",
        "osint_request": request_text,
        "result_buffer": [],
    }
    save_data()
    return order_id


def create_boost_order(user_id, product_id, boost_details):
    product = get_product(product_id)
    if not product:
        return None
    order_id = str(DATA["next_order_id"])
    DATA["next_order_id"] += 1
    DATA["orders"][order_id] = {
        "user_id": user_id,
        "items": [product_id],
        "total": float(product["price"]),
        "status": "awaiting_proof",
        "payment_method": None,
        "expires_at": None,
        "proof_file_id": None,
        "stock_keys_sent": [],
        "manual_delivery_queue": [],
        "manual_delivery_sent": [],
        "order_kind": "boost",
        "boost_details": boost_details,
    }
    save_data()
    return order_id


def create_spotify_order(user_id, mode, details):
    product = get_product("spotify_premium")
    if not product:
        return None
    order_id = str(DATA["next_order_id"])
    DATA["next_order_id"] += 1
    DATA["orders"][order_id] = {
        "user_id": user_id,
        "items": ["spotify_premium"],
        "total": float(product["price"]),
        "status": "awaiting_proof",
        "payment_method": None,
        "expires_at": None,
        "proof_file_id": None,
        "stock_keys_sent": [],
        "manual_delivery_queue": [],
        "manual_delivery_sent": [],
        "order_kind": "spotify",
        "spotify_mode": mode,
        "spotify_details": details,
    }
    save_data()
    return order_id


def create_deposit(user_id, amount):
    deposit_id = str(DATA["next_deposit_id"])
    DATA["next_deposit_id"] += 1
    DATA["deposits"][deposit_id] = {
        "user_id": user_id,
        "amount": float(amount),
        "status": "awaiting_proof",
        "payment_method": None,
        "proof_file_id": None,
        "expires_at": int(time()) + (8 * 60),
    }
    user_data = ensure_user(user_id)
    user_data["awaiting_deposit_id"] = deposit_id
    save_data()
    return deposit_id


def expire_pending_deposit(user_data):
    deposit_id = user_data.get("awaiting_deposit_id")
    if not deposit_id:
        return False
    deposit = DATA["deposits"].get(deposit_id)
    if not deposit:
        user_data["awaiting_deposit_id"] = None
        save_data()
        return False
    if deposit["status"] != "awaiting_proof":
        return False
    if int(time()) <= int(deposit.get("expires_at", 0)):
        return False
    DATA["deposits"].pop(deposit_id, None)
    user_data["awaiting_deposit_id"] = None
    save_data()
    return True


def deliver_stock(order_id):
    order = DATA["orders"][order_id]
    sent = []
    missing = []
    for product_id in order["items"]:
        product = get_product(product_id)
        if not product or product["type"] != "stock":
            continue
        values = DATA["stock"].setdefault(product_id, [])
        if values:
            key_value = values.pop(0)
            order["stock_keys_sent"].append({"product_id": product_id, "key": key_value})
            sent.append(f"{product['name']} : {key_value}")
        else:
            missing.append(product["name"])
    save_data()
    return sent, missing


def has_manual_items(order):
    for product_id in order["items"]:
        product = get_product(product_id)
        if product and product["type"] == "manual":
            return True
    return False


def manual_order_items(order):
    items = []
    for product_id in order["items"]:
        product = get_product(product_id)
        if product and product["type"] == "manual":
            items.append(product_id)
    return items


def current_manual_delivery(order):
    queue = order.get("manual_delivery_queue") or []
    if not queue:
        return None
    product_id = queue[0]
    return get_product(product_id)


def osint_buffer_count(order):
    return len(order.get("result_buffer") or [])


def osint_delivery_menu(order_id):
    order = DATA["orders"].get(str(order_id), {})
    count = osint_buffer_count(order)
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(f"✅ Finaliser l'envoi ({count})", callback_data=f"admin:osintfinish:{order_id}")],
            [InlineKeyboardButton("🗑️ Vider le brouillon", callback_data=f"admin:osintclear:{order_id}")],
            [InlineKeyboardButton("🔎 Ouvrir la commande", callback_data=f"admin:order:{order_id}")],
        ]
    )


def append_osint_result_chunk(order, chunk):
    order.setdefault("result_buffer", []).append(chunk)
    save_data()


async def flush_osint_result_buffer(context, order_id):
    order = DATA["orders"].get(str(order_id))
    if not order:
        return False
    chunks = order.get("result_buffer") or []
    if not chunks:
        return False
    user_id = order["user_id"]
    await context.bot.send_message(user_id, "🕵️ Résultat de ta recherche OSINT\n\nVoici l'envoi complet :")
    for chunk in chunks:
        chunk_type = chunk.get("type")
        if chunk_type == "text":
            await context.bot.send_message(user_id, chunk.get("text", ""))
        elif chunk_type == "photo":
            await context.bot.send_photo(
                user_id,
                photo=chunk.get("file_id"),
                caption=chunk.get("caption") or None,
            )
        elif chunk_type == "document":
            await context.bot.send_document(
                user_id,
                document=chunk.get("file_id"),
                caption=chunk.get("caption") or None,
            )
    await context.bot.send_message(
        user_id,
        "✅ Envoi terminé.\n\n🆘 Si besoin, tu peux toujours créer un ticket depuis l'accueil.",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("🔎 Approfondir la recherche - 2€", callback_data=f"osint:deepen:{order_id}")],
                [InlineKeyboardButton("🏠 Retour a l'accueil", callback_data="menu:start")],
                [InlineKeyboardButton("🆘 Creer un ticket", callback_data="ticket:new")],
            ]
        ),
    )
    return True


def create_ticket(user_id, username, category, reason, details=None):
    ticket_id = str(DATA["next_ticket_id"])
    DATA["next_ticket_id"] += 1
    DATA["tickets"][ticket_id] = {
        "user_id": user_id,
        "username": username,
        "category": category,
        "reason": reason,
        "status": "pending",
        "messages": [],
        "details": details or {},
    }
    save_data()
    return ticket_id


def open_tickets():
    items = []
    for ticket_id, ticket in DATA["tickets"].items():
        if ticket["status"] in {"open", "pending"}:
            items.append((ticket_id, ticket))
    return sorted(items, key=lambda row: int(row[0]), reverse=True)


def tickets_by_status(status):
    items = []
    for ticket_id, ticket in DATA["tickets"].items():
        if ticket.get("status") == status:
            items.append((ticket_id, ticket))
    return sorted(items, key=lambda row: int(row[0]), reverse=True)


def tickets_by_status_and_category(status, category):
    items = []
    for ticket_id, ticket in DATA["tickets"].items():
        if ticket.get("status") == status and ticket.get("category") == category:
            items.append((ticket_id, ticket))
    return sorted(items, key=lambda row: int(row[0]), reverse=True)


def can_manage_ticket(user_id, ticket):
    if is_owner(user_id):
        return True
    return is_support_admin(user_id) and ticket.get("category") == "question"


async def notify_support_admins(context, text, reply_markup=None):
    for admin_id in DATA.get("support_admins", []):
        try:
            await context.bot.send_message(int(admin_id), text, reply_markup=reply_markup)
        except Exception:
            continue


def ticket_status_badge(status):
    badges = {
        "open": "🟢",
        "pending": "🟠",
        "closed": "🔴",
    }
    return badges.get(status, "⚪")


def admin_ticket_sections_menu():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🟢 Tickets ouverts", callback_data="admin:tickets:open")],
            [InlineKeyboardButton("🟠 Tickets en attente", callback_data="admin:tickets:pending")],
            [InlineKeyboardButton("🔴 Tickets fermes", callback_data="admin:tickets:closed")],
            [InlineKeyboardButton("⬅️ Retour", callback_data="admin:home")],
        ]
    )


def ticket_category_menu():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🛠️ SAV", callback_data="ticket:type:sav")],
            [InlineKeyboardButton("❓ Question", callback_data="ticket:type:question")],
            [InlineKeyboardButton("⬅️ Retour", callback_data="menu:start")],
        ]
    )


def cancelled_order_menu():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🏠 Retour a l'accueil", callback_data="menu:start")],
            [InlineKeyboardButton("🆘 Creer un ticket", callback_data="ticket:new")],
        ]
    )


async def edit_or_reply(message, text, reply_markup=None):
    try:
        if getattr(message, "photo", None):
            await message.edit_caption(caption=text, reply_markup=reply_markup, parse_mode="HTML")
        else:
            await message.edit_text(text, reply_markup=reply_markup, parse_mode="HTML")
    except Exception:
        try:
            await message.delete()
        except Exception:
            pass
        await message.reply_text(text, reply_markup=reply_markup, parse_mode="HTML")


def expire_pending_order(user_data):
    order_id = user_data.get("awaiting_order_id")
    if not order_id:
        return False
    order = DATA["orders"].get(order_id)
    if not order:
        user_data["awaiting_order_id"] = None
        save_data()
        return False
    if order["status"] != "awaiting_proof":
        return False
    expires_at = order.get("expires_at")
    if expires_at is None:
        return False
    if int(time()) <= int(expires_at):
        return False
    DATA["orders"].pop(order_id, None)
    user_data["awaiting_order_id"] = None
    save_data()
    return True


async def welcome(message, user):
    name = f"@{user.username}" if user.username else user.first_name
    user_data = ensure_user(user.id)
    shop_status = "🟢 Boutique ouverte" if shop_is_open() else "🔴 Boutique fermee"
    text = (
        "🔥 Bienvenue sur O'Market !\n\n"
        f"👤 : {name}\n"
        f"🆔 : {user.id}\n\n"
        f"💰 Solde : {fmt_price(float(user_data['balance']))}\n\n"
        f"{shop_status}\n\n"
        "🛍️ Ici, tu peux commander simplement et rapidement.\n"
        "Tout est pense pour que ce soit propre, fluide et efficace.\n\n"
        f"🆘 Support : {SUPPORT_HANDLE}\n\n"
        "👇 Clique sur les boutons ci-dessous :"
    )
    if LOGO_FILE.exists():
        with LOGO_FILE.open("rb") as photo:
            await message.reply_photo(photo=photo, caption=text, reply_markup=main_menu(user.id))
    else:
        await message.reply_text(text, reply_markup=main_menu(user.id))


async def show_shop_closed(message, user_id):
    text = (
        "🔴 Boutique actuellement fermee\n\n"
        "✨ Le shop est temporairement indisponible.\n"
        "Repasses un peu plus tard pour voir si tout est revenu en ligne.\n\n"
        "🆘 Si tu as besoin d'aide, tu peux toujours creer un ticket."
    )
    markup = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🆘 Creer un ticket", callback_data="ticket:new")],
            [InlineKeyboardButton("🏠 Retour a l'accueil", callback_data="menu:start")],
        ]
    )
    await edit_or_reply(message, text, reply_markup=markup)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sync_user_profile(update.effective_user)
    await welcome(update.message, update.effective_user)


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Commande reservee a l admin.")
        return
    sync_user_profile(update.effective_user)
    menu = admin_menu() if is_owner(update.effective_user.id) else support_admin_menu()
    await update.message.reply_text("🛠️ Panel admin", reply_markup=menu)


async def show_cart(message, user_id):
    user_data = ensure_user(user_id)
    if not user_data["cart"]:
        await edit_or_reply(message, "🛒 Ton panier est vide pour le moment.", reply_markup=main_menu(user_id))
        return
    lines = ["📦 Ton panier", ""]
    rows = []
    for index, product_id in enumerate(user_data["cart"], start=1):
        product = get_product(product_id)
        if not product:
            continue
        lines.append(f"{index}. {product['name']} - {fmt_price(float(product['price']))}")
        rows.append([InlineKeyboardButton(f"Retirer {index}", callback_data=f"cart:remove:{index - 1}")])
    lines.append("")
    lines.append(f"💰 Total : {fmt_price(cart_total(user_data['cart']))}")
    lines.append(f"💼 Solde disponible : {fmt_price(float(user_data['balance']))}")
    rows.append([InlineKeyboardButton("💳 Payer", callback_data="cart:pay")])
    rows.append([InlineKeyboardButton("🗑️ Vider le panier", callback_data="cart:clear")])
    rows.append([InlineKeyboardButton("⬅️ Retour", callback_data="menu:start")])
    await edit_or_reply(message, "\n".join(lines), reply_markup=InlineKeyboardMarkup(rows))


async def show_orders(message, user_id):
    rows = []
    for order_id, order in sorted(DATA["orders"].items(), key=lambda row: int(row[0]), reverse=True):
        if order["user_id"] == user_id:
            rows.append(f"Commande {order_id} - {STATUS_NAMES.get(order['status'], order['status'])} - {fmt_price(float(order['total']))}")
    await edit_or_reply(message, "\n".join(rows[:10]) if rows else "📋 Tu n'as encore aucune commande pour le moment.", reply_markup=main_menu(user_id))


async def show_category(query, category):
    rows = []
    for product_id, product in product_rows(category):
        label = f"{product['name']} - {fmt_price(float(product['price']))}"
        if product["type"] == "stock":
            label += f" (📦 {stock_count(product_id)})"
        elif category == "boosts":
            label += " 🚀"
        elif category == "subscriptions":
            label += " 🎧"
        else:
            label += " 🍔"
        rows.append([InlineKeyboardButton(label, callback_data=f"product:view:{product_id}")])
    if not rows:
        await edit_or_reply(
            query.message,
            f"{CATEGORY_NAMES.get(category, category)}\n\n🚧 Cette categorie est en travaux pour le moment.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Retour", callback_data="menu:shop")]]),
        )
        return
    rows.append([InlineKeyboardButton("⬅️ Retour", callback_data="menu:shop")])
    await edit_or_reply(query.message, f"{CATEGORY_NAMES.get(category, category)}\n\nChoisis une option ci-dessous.", reply_markup=InlineKeyboardMarkup(rows))


async def show_boost_subcategory(query, subcategory):
    rows = []
    title = BOOST_SUBCATEGORY_NAMES.get(subcategory, "Boost reseaux")
    for product_id, product in product_rows("boosts", subcategory=subcategory):
        rows.append([InlineKeyboardButton(f"🚀 {product['name']} - {fmt_price(float(product['price']))}", callback_data=f"product:view:{product_id}")])
    if not rows:
        await edit_or_reply(
            query.message,
            f"{title}\n\n🚧 Cette categorie est en travaux pour le moment.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Retour", callback_data="cat:boosts")]]),
        )
        return
    rows.append([InlineKeyboardButton("⬅️ Retour", callback_data="cat:boosts")])
    await edit_or_reply(query.message, f"{title}\n\nChoisis maintenant une option.", reply_markup=InlineKeyboardMarkup(rows))


async def show_ubereats_intro(query):
    product = ubereats_product()
    if product and not product.get("active", True):
        await edit_or_reply(
            query.message,
            "🛵 Uber Eats -50%\n\n🚧 Cette categorie est temporairement indisponible pour le moment.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Retour", callback_data="menu:shop")]]),
        )
        return
    text = (
        "🛵 Uber Eats -50%\n\n"
        "❓ Comment ca marche ?\n\n"
        "1️⃣ Clique sur <b>Demarrer une commande</b> puis envoie un screen de ta commande avec le recapitulatif complet.\n\n"
        "2️⃣ Nous calculons ensuite le montant a regler.\n"
        "En general, tu paies environ <b>50 % du prix total TTC</b> de la commande, livraison et taxes incluses.\n"
        "⚠️ Le montant peut varier legerement selon les frais Uber Eats.\n\n"
        "3️⃣ Effectue le paiement via crypto, PayPal, Apple Pay ou Google Pay.\n\n"
        "4️⃣ Une fois le paiement valide, je tente de passer la commande.\n\n"
        "5️⃣ Si je n'arrive pas a passer la commande dans un delai de 30 minutes, tu recois un remboursement complet.\n\n"
        "📸 Le screen doit bien montrer le recap complet avec le prix final affiche."
    )
    markup = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🚀 Demarrer une commande", callback_data="ubereats:start")],
            [InlineKeyboardButton("⬅️ Retour", callback_data="menu:shop")],
        ]
    )
    await edit_or_reply(query.message, text, reply_markup=markup)


async def show_osint_intro(query):
    product = osint_product()
    if product and not product.get("active", True):
        await edit_or_reply(
            query.message,
            "🕵️ Recherche OSINT\n\n🚧 Cette categorie est temporairement indisponible pour le moment.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Retour", callback_data="menu:shop")]]),
        )
        return
    text = (
        "🕵️ Recherche OSINT\n\n"
        "Tu peux lancer une recherche a partir de :\n"
        "email, nom, prenom, nom de naissance, pseudo, telephone, mot de passe, vehicule, plaque, VIN,\n"
        "compte Telegram, compte Facebook, adresse IP, localisation, infos FiveM / GTA RP, numero de secu, IBAN, BIC ou autre.\n\n"
        "📌 Plus tu fournis d'informations, plus il y a de chances de trouver ta cible.\n\n"
        "👤 La recherche vise en priorite une vraie personne / un profil cible principal.\n"
        "Si tu veux inclure des proches ou des membres de la famille, precise-le directement dans ta demande.\n\n"
        "💰 Le prix est entre 5€ et 15€ selon les informations trouvees.\n"
        "✅ Tu ne paies que si on a un resultat.\n"
        "❌ Si on ne trouve rien, tu ne paies pas."
    )
    markup = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🚀 Lancer une recherche", callback_data="osint:start")],
            [InlineKeyboardButton("⬅️ Retour", callback_data="menu:shop")],
        ]
    )
    await edit_or_reply(query.message, text, reply_markup=markup)


async def show_spotify_intro(query):
    product = get_product("spotify_premium")
    if not product or not product.get("active", True):
        await edit_or_reply(
            query.message,
            "🎧 Spotify Premium\n\n🚧 Cette offre est temporairement indisponible pour le moment.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Retour", callback_data="cat:subscriptions")]]),
        )
        return
    text = (
        "🎧 Spotify Premium\n\n"
        f"💰 Prix : {fmt_price(float(product['price']))}\n\n"
        "🔗 Tu recevras un acces Spotify Premium via lien / mise a niveau.\n"
        "♻️ L'acces est renouvelable.\n"
        "🆘 En cas de souci, cree un ticket SAV depuis l'accueil.\n\n"
        "⚡ La plupart des mises a niveau sont effectuees en 5 a 10 minutes,\n"
        "mais cela peut parfois prendre jusqu'a 24h.\n\n"
        "Choisis maintenant si tu veux garder ton compte personnel ou recevoir un nouveau compte."
    )
    await edit_or_reply(
        query.message,
        text,
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("🔒 Garder mon compte", callback_data="spotify:start:keep")],
                [InlineKeyboardButton("🆕 Nouveau compte", callback_data="spotify:start:new")],
                [InlineKeyboardButton("⬅️ Retour", callback_data="cat:subscriptions")],
            ]
        ),
    )


def boost_intro_text(product):
    name = product["name"]
    if product["id"] == "tiktok_boost":
        return (
            f"🚀 {name}\n\n"
            "💶 Tarif : 0.60€\n"
            "📦 Livraison progressive\n"
            "⏱️ Delai maximum : 24h\n\n"
            "Envoie le lien de la video TikTok concernee avant le paiement.\n"
            "Plus ton message est clair, plus le lancement sera rapide."
        )
    if product["id"] == "tiktok_followers":
        return (
            f"🚀 {name}\n\n"
            "💶 Tarif : 2€\n"
            "📦 Livraison progressive\n"
            "⏱️ Delai maximum : 24h\n\n"
            "Avant de payer, envoie le lien du compte TikTok a booster."
        )
    if product["id"] == "insta_views":
        return (
            f"🚀 {name}\n\n"
            "💶 Tarif : 0.60€\n"
            "📦 Livraison progressive\n"
            "⏱️ Delai maximum : 24h\n\n"
            "Envoie le lien du post ou de la video Instagram concernee avant le paiement."
        )
    if product["id"] == "insta_boost":
        return (
            f"🚀 {name}\n\n"
            "💶 Tarif : 2€\n"
            "📦 Livraison progressive\n"
            "⏱️ Delai maximum : 24h\n\n"
            "Envoie le lien du compte Instagram a booster avant le paiement."
        )
    return ""


async def show_boost_intro(query, product_id):
    product = get_product(product_id)
    if not product or not product.get("active", True):
        await edit_or_reply(
            query.message,
            "🚀 Boost reseaux\n\n🚧 Cette option est temporairement indisponible pour le moment.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Retour", callback_data="cat:boosts")]]),
        )
        return
    product = dict(product)
    product["id"] = product_id
    if product.get("subcategory") == "discord":
        lines = [f"🚀 {product['name']}", f"💰 Prix : {fmt_price(float(product['price']))}", "🔗 Livraison manuelle via lien / acces apres validation."]
        rows = [
            [InlineKeyboardButton("🛒 Ajouter au panier", callback_data=f"product:add:{product_id}")],
            [InlineKeyboardButton("⬅️ Retour", callback_data="boostsubcat:discord")],
        ]
        await edit_or_reply(query.message, "\n".join(lines), reply_markup=InlineKeyboardMarkup(rows))
        return
    await edit_or_reply(
        query.message,
        boost_intro_text(product),
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("🚀 Demarrer la commande", callback_data=f"boost:start:{product_id}")],
                [InlineKeyboardButton("⬅️ Retour", callback_data=f"boostsubcat:{product.get('subcategory', 'tiktok')}")],
            ]
        ),
    )


async def show_fastfood_subcategory(query, subcategory):
    rows = []
    emoji = "🍔" if subcategory == "mcdo" else "🍗"
    brand = "McDo" if subcategory == "mcdo" else "KFC"
    for product_id, product in product_rows("fastfood", subcategory=subcategory):
        short_name = product["name"].replace(f"{brand} ", "")
        rows.append([InlineKeyboardButton(f"{emoji} {short_name} - {fmt_price(float(product['price']))}", callback_data=f"product:view:{product_id}")])
    if not rows:
        await edit_or_reply(
            query.message,
            f"{FASTFOOD_SUBCATEGORY_NAMES.get(subcategory, 'Fast Food')}\n\n🚧 Cette categorie est en travaux pour le moment.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Retour", callback_data="cat:fastfood")]]),
        )
        return
    rows.append([InlineKeyboardButton("📦 Voir mon panier", callback_data="menu:cart")])
    rows.append([InlineKeyboardButton("🏠 Menu principal", callback_data="menu:start")])
    await edit_or_reply(
        query.message,
        f"{FASTFOOD_SUBCATEGORY_NAMES.get(subcategory, 'Fast Food')}\n\n💡 Clique pour ajouter au panier !",
        reply_markup=InlineKeyboardMarkup(rows),
    )


async def show_product(query, product_id):
    product = get_product(product_id)
    if not product or not product.get("active", True):
        await edit_or_reply(query.message, "Produit indisponible.")
        return
    if product.get("category") == "boosts":
        await show_boost_intro(query, product_id)
        return
    if product_id == "spotify_premium":
        await show_spotify_intro(query)
        return
    lines = [f"✨ {product['name']}", f"💰 Prix : {fmt_price(float(product['price']))}"]
    if product["type"] == "manual":
        if product.get("category") == "subscriptions":
            lines.append("🎧 Offre disponible")
        else:
            lines.append("🍔 Selection disponible")
    else:
        lines.append(f"📦 Stock : {stock_count(product_id)}")
    back_callback = f"cat:{product['category']}"
    if product.get("category") == "fastfood" and product.get("subcategory"):
        back_callback = f"subcat:{product['subcategory']}"
    rows = [
        [InlineKeyboardButton("🛒 Ajouter au panier", callback_data=f"product:add:{product_id}")],
        [InlineKeyboardButton("⬅️ Retour", callback_data=back_callback)],
    ]
    await edit_or_reply(query.message, "\n".join(lines), reply_markup=InlineKeyboardMarkup(rows))


async def notify_admin_ubereats_request(context, order_id):
    order = DATA["orders"][order_id]
    text = (
        f"🛵 Nouvelle demande Uber Eats {order_id}\n\n"
        f"👤 Client : {admin_client_header(order['user_id'])}\n"
        f"📍 Adresse : {order.get('ubereats_address', 'Non renseignee')}\n"
        f"💶 Total commande client : {fmt_price(float(order.get('ubereats_total', 0)))}\n"
        f"📌 Statut : {STATUS_NAMES.get(order['status'], order['status'])}\n\n"
        "Fixe maintenant le montant a regler par le client."
    )
    markup = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("💶 Fixer le montant", callback_data=f"admin:uberquote:{order_id}")],
            [InlineKeyboardButton("❌ Annuler", callback_data=f"admin:cancel:{order_id}")],
        ]
    )
    await context.bot.send_photo(ADMIN_ID, photo=order["request_file_id"], caption=text, reply_markup=markup)


async def notify_admin_osint_request(context, order_id):
    order = DATA["orders"][order_id]
    text = (
        f"🕵️ Nouvelle demande OSINT {order_id}\n\n"
        f"👤 Client : {admin_client_header(order['user_id'])}\n"
        f"📌 Statut : {STATUS_NAMES.get(order['status'], order['status'])}\n\n"
        "Demande recue :\n"
        f"{escape(order.get('osint_request', 'Aucune information'))}"
    )
    markup = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("💶 Fixer le montant", callback_data=f"admin:osintquote:{order_id}")],
            [InlineKeyboardButton("❌ Annuler", callback_data=f"admin:cancel:{order_id}")],
        ]
    )
    await context.bot.send_message(ADMIN_ID, text, reply_markup=markup, parse_mode="HTML")


async def notify_admin(context, order_id):
    order = DATA["orders"][order_id]
    text = (
        f"📦 Nouvelle preuve pour commande {order_id}\n\n"
        f"👤 Client : {admin_client_header(order['user_id'])}\n"
        f"💰 Total : {fmt_price(float(order['total']))}\n"
        f"📌 Statut : {STATUS_NAMES[order['status']]}\n\n"
        f"{order_lines(order)}"
    )
    markup = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✅ Valider", callback_data=f"admin:approve:{order_id}")],
            [InlineKeyboardButton("✏️ Modifier", callback_data=f"admin:modify:{order_id}")],
            [InlineKeyboardButton("❌ Annuler", callback_data=f"admin:cancel:{order_id}")],
        ]
    )
    if order.get("proof_file_id") and order["proof_file_id"] != "PAID_BY_BALANCE":
        await context.bot.send_photo(ADMIN_ID, photo=order["proof_file_id"], caption=text, reply_markup=markup)
    else:
        await context.bot.send_message(
            ADMIN_ID,
            text + "\n\n💼 Paiement effectue via le solde du client.",
            reply_markup=markup,
        )


async def notify_admin_deposit(context, deposit_id):
    deposit = DATA["deposits"][deposit_id]
    text = (
        f"💰 Nouvelle preuve de depot {deposit_id}\n\n"
        f"👤 Client : {admin_client_header(deposit['user_id'])}\n"
        f"💵 Montant : {fmt_price(float(deposit['amount']))}\n\n"
        "Valide ce depot pour crediter le solde du client."
    )
    markup = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✅ Valider le depot", callback_data=f"admin:depositapprove:{deposit_id}")],
            [InlineKeyboardButton("❌ Refuser le depot", callback_data=f"admin:depositcancel:{deposit_id}")],
        ]
    )
    await context.bot.send_photo(ADMIN_ID, photo=deposit["proof_file_id"], caption=text, reply_markup=markup)


async def approve_order(query, context, order_id):
    order = DATA["orders"].get(order_id)
    if not order:
        await query.message.reply_text("Commande introuvable.")
        return
    if order["status"] != "proof_received":
        await query.message.reply_text("Cette commande n est pas en attente de validation.")
        return
    current_delivery_order = active_delivery_order_id(ADMIN_ID)
    if current_delivery_order and str(current_delivery_order) != str(order_id):
        await query.message.reply_text(
            f"⛔ Acces refuse.\n\nTermine d'abord la commande {current_delivery_order} avant de valider une autre commande."
        )
        return
    if order.get("order_kind") == "ubereats":
        order["status"] = "awaiting_delivery"
        ensure_user(ADMIN_ID)["admin_state"] = {"action": "uber_link", "order_id": order_id}
        save_data()
        await context.bot.send_message(
            order["user_id"],
            "✅ Paiement valide.\n\n🛵 Ta commande Uber Eats est en preparation. On t'envoie le lien de suivi tres vite.",
        )
        await query.message.reply_text("✅ Commande validee. Envoie maintenant le lien de suivi Uber Eats.")
        return
    if order.get("order_kind") == "osint":
        order["status"] = "awaiting_delivery"
        order["result_buffer"] = order.get("result_buffer") or []
        ensure_user(ADMIN_ID)["admin_state"] = {"action": "osint_result", "order_id": order_id}
        save_data()
        await context.bot.send_message(
            order["user_id"],
            "✅ Paiement valide.\n\n🕵️ Ta recherche OSINT est en cours de finalisation. On t'envoie le resultat tres vite.",
        )
        await query.message.reply_text(
            "✅ Commande validee.\n\nEnvoie maintenant le resultat OSINT.\n"
            "Tu peux envoyer plusieurs messages, photos ou fichiers, puis finaliser a la fin.",
            reply_markup=osint_delivery_menu(order_id),
        )
        return
    if order.get("order_kind") == "spotify":
        order["status"] = "awaiting_delivery"
        ensure_user(ADMIN_ID)["admin_state"] = {"action": "spotify_result", "order_id": order_id}
        save_data()
        await context.bot.send_message(
            order["user_id"],
            "✅ Paiement valide.\n\n🎧 Ta commande Spotify Premium est en cours de mise en service.\n⚡ Cela prend souvent 5 a 10 minutes, mais cela peut parfois aller jusqu'a 24h.\n🆘 En cas de souci, cree un ticket SAV depuis l'accueil.",
        )
        await query.message.reply_text(
            "✅ Commande validee.\n\nEnvoie maintenant soit le compte cree, soit le message de mise en service Spotify.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔎 Ouvrir la commande", callback_data=f"admin:order:{order_id}")]]),
        )
        return
    if order.get("order_kind") == "boost":
        order["status"] = "awaiting_delivery"
        ensure_user(ADMIN_ID)["admin_state"] = {"action": "boost_result", "order_id": order_id}
        save_data()
        await context.bot.send_message(
            order["user_id"],
            "✅ Paiement valide.\n\n🚀 Ton boost est lance ou en cours de lancement.\n📦 Livraison progressive\n⏱️ Delai maximum : 24h.",
        )
        await query.message.reply_text(
            "✅ Commande validee.\n\nEnvoie maintenant le message final ou les infos de lancement a transmettre au client.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔎 Ouvrir la commande", callback_data=f"admin:order:{order_id}")]]),
        )
        return
    sent, missing = deliver_stock(order_id)
    if sent:
        await context.bot.send_message(order["user_id"], "✅ Paiement valide.\n\n🔑 Voici tes cles :\n\n" + "\n".join(sent))
    if missing:
        await query.message.reply_text("Cles manquantes : " + ", ".join(missing))
    if has_manual_items(order):
        order["status"] = "awaiting_delivery"
        order["manual_delivery_queue"] = manual_order_items(order)
        order["manual_delivery_sent"] = []
        current_delivery_order = active_delivery_order_id(ADMIN_ID)
        if not current_delivery_order:
            ensure_user(ADMIN_ID)["admin_state"] = {"action": "deliver", "order_id": order_id}
        save_data()
        next_product = current_manual_delivery(order)
        next_label = next_product["name"] if next_product else "la prochaine livraison"
        await context.bot.send_message(
            order["user_id"],
            "✅ Paiement valide.\n\n😉 Ta commande est en preparation, on te l'envoie tres vite.",
        )
        if current_delivery_order and str(current_delivery_order) != str(order_id):
            await query.message.reply_text(
                f"✅ Commande validee.\n\nUne autre livraison est deja en cours sur la commande {current_delivery_order}.\nCelle-ci reste en attente : {next_label}."
            )
        else:
            await query.message.reply_text(f"✅ Commande validee. Envoie maintenant la livraison manuelle : {next_label}.")
    else:
        order["status"] = "delivered"
        save_data()
        await context.bot.send_message(
            order["user_id"],
            "✅ Paiement valide.\n\n🎉 Ta commande a bien ete livree. Merci pour ta confiance.",
        )
        await query.message.reply_text("✅ Commande livree.")


async def show_admin_orders(query):
    rows = []
    for order_id, order in sorted(DATA["orders"].items(), key=lambda row: int(row[0]), reverse=True):
        if order["status"] in {"quote_pending", "awaiting_proof", "proof_received", "awaiting_delivery"}:
            rows.append([InlineKeyboardButton(f"Commande {order_id} - {STATUS_NAMES[order['status']]}", callback_data=f"admin:order:{order_id}")])
    rows.append([InlineKeyboardButton("Retour", callback_data="admin:home")])
    await edit_or_reply(query.message, "Commandes en attente", reply_markup=InlineKeyboardMarkup(rows))


async def show_admin_order(query, order_id):
    order = DATA["orders"].get(order_id)
    if not order:
        await edit_or_reply(query.message, "Commande introuvable.")
        return
    lines = [
        f"Commande {order_id}",
        f"Client : {admin_client_header(order['user_id'])}",
        f"Statut : {STATUS_NAMES.get(order['status'], order['status'])}",
        f"Total : {fmt_price(float(order['total']))}",
        "",
        "Selection :",
        admin_order_item_lines(order),
    ]
    if order.get("order_kind") == "ubereats":
        lines.extend(
            [
                "",
                "Infos Uber Eats :",
                f"Adresse : {order.get('ubereats_address', 'Non renseignee')}",
                f"Total client : {fmt_price(float(order.get('ubereats_total', 0)))}",
            ]
        )
    if order.get("order_kind") == "osint":
        lines.extend(
            [
                "",
                "Demande OSINT :",
                order.get("osint_request", "Aucune information"),
            ]
        )
        if order.get("osint_source_order_id"):
            lines.append(f"Recherche source : {order.get('osint_source_order_id')}")
        if order.get("status") == "awaiting_delivery":
            lines.extend(["", f"Brouillon resultat : {osint_buffer_count(order)} element(s)"])
    if order.get("order_kind") == "spotify":
        lines.extend(
            [
                "",
                "Infos Spotify :",
                f"Mode : {order.get('spotify_details', {}).get('mode_label', 'Non renseigne')}",
            ]
        )
        if order.get("spotify_mode") == "keep":
            lines.extend(
                [
                    f"Email : {order.get('spotify_details', {}).get('email', 'Non renseigne')}",
                    f"Pseudo : {order.get('spotify_details', {}).get('username', 'Non renseigne')}",
                    f"Mot de passe : {order.get('spotify_details', {}).get('password', 'Non renseigne')}",
                ]
            )
    if order.get("order_kind") == "boost":
        lines.extend(
            [
                "",
                "Infos boost :",
                order.get("boost_details", "Aucune information"),
            ]
        )
    current_delivery = current_manual_delivery(order)
    if current_delivery:
        lines.extend(["", f"Livraison en cours : {current_delivery['name']}"])
    rows = []
    if order["status"] == "quote_pending" and order.get("order_kind") == "ubereats":
        rows.append([InlineKeyboardButton("Fixer le montant", callback_data=f"admin:uberquote:{order_id}")])
        rows.append([InlineKeyboardButton("Annuler", callback_data=f"admin:cancel:{order_id}")])
    if order["status"] == "quote_pending" and order.get("order_kind") == "osint":
        rows.append([InlineKeyboardButton("Fixer le montant", callback_data=f"admin:osintquote:{order_id}")])
        rows.append([InlineKeyboardButton("Annuler", callback_data=f"admin:cancel:{order_id}")])
    if order["status"] == "proof_received":
        rows.append([InlineKeyboardButton("Valider", callback_data=f"admin:approve:{order_id}")])
        if order.get("order_kind") not in {"ubereats", "osint"}:
            rows.append([InlineKeyboardButton("Modifier", callback_data=f"admin:modify:{order_id}")])
        rows.append([InlineKeyboardButton("Annuler", callback_data=f"admin:cancel:{order_id}")])
    if order["status"] == "awaiting_delivery":
        label = (
            "Envoyer le lien de suivi"
            if order.get("order_kind") == "ubereats"
            else "Envoyer le resultat"
            if order.get("order_kind") == "osint"
            else "Envoyer l'acces Spotify"
            if order.get("order_kind") == "spotify"
            else "Envoyer le suivi"
            if order.get("order_kind") == "boost"
            else "Preparer la livraison"
        )
        rows.append([InlineKeyboardButton(label, callback_data=f"admin:deliver:{order_id}")])
    rows.append([InlineKeyboardButton("Retour", callback_data="admin:orders")])
    await edit_or_reply(query.message, "\n".join(lines), reply_markup=InlineKeyboardMarkup(rows))


async def show_order_modify_menu(query, order_id):
    order = DATA["orders"].get(order_id)
    if not order:
        await edit_or_reply(query.message, "Commande introuvable.", reply_markup=admin_menu())
        return
    lines = [
        f"✏️ Modifier commande {order_id}",
        "",
        "Selection actuelle :",
        admin_order_item_lines(order),
        "",
        "Choisis une ligne a retirer.",
        "La difference sera recréditee sur le solde du client.",
    ]
    rows = removable_order_buttons(order_id, order)
    rows.append([InlineKeyboardButton("⬅️ Retour", callback_data=f"admin:order:{order_id}")])
    await edit_or_reply(query.message, "\n".join(lines), reply_markup=InlineKeyboardMarkup(rows))


async def show_admin_products(query):
    rows = [
        [InlineKeyboardButton("Uber Eats", callback_data="admin:products:ubereats")],
        [InlineKeyboardButton("Recherche OSINT", callback_data="admin:products:osint")],
        [InlineKeyboardButton("Fast Food", callback_data="admin:products:fastfood")],
        [InlineKeyboardButton("Abonnements", callback_data="admin:products:subscriptions")],
        [InlineKeyboardButton("Cartes cadeaux", callback_data="admin:products:giftcards")],
        [InlineKeyboardButton("Boost reseaux", callback_data="admin:products:boosts")],
        [InlineKeyboardButton("Rfunds", callback_data="admin:products:refunds")],
        [InlineKeyboardButton("Retour", callback_data="admin:home")],
    ]
    await edit_or_reply(query.message, "Gestion des produits", reply_markup=InlineKeyboardMarkup(rows))


async def show_admin_product_list(query, category):
    rows = []
    for product_id, product in product_rows(category, include_inactive=True):
        state = "ON" if product.get("active", True) else "OFF"
        rows.append([InlineKeyboardButton(f"{product['name']} [{state}]", callback_data=f"admin:product:{product_id}")])
    if category == "ubereats" and not rows:
        product = ubereats_product()
        if product:
            state = "ON" if product.get("active", True) else "OFF"
            rows.append([InlineKeyboardButton(f"{product['name']} [{state}]", callback_data="admin:product:ubereats_offer")])
    if category == "osint" and not rows:
        product = osint_product()
        if product:
            state = "ON" if product.get("active", True) else "OFF"
            rows.append([InlineKeyboardButton(f"{product['name']} [{state}]", callback_data="admin:product:osint_offer")])
    rows.append([InlineKeyboardButton("Retour", callback_data="admin:products")])
    await edit_or_reply(query.message, f"Produits {CATEGORY_NAMES.get(category, category)}", reply_markup=InlineKeyboardMarkup(rows))


async def show_admin_product(query, product_id):
    product = get_product(product_id)
    if not product:
        await edit_or_reply(query.message, "Produit introuvable.")
        return
    lines = [
        product["name"],
        f"Prix : {fmt_price(float(product['price']))}",
        f"Type : {product['type']}",
        f"Statut : {'actif' if product.get('active', True) else 'desactive'}",
    ]
    if product["type"] == "stock":
        lines.append(f"Stock : {stock_count(product_id)}")
    rows = [
        [InlineKeyboardButton("Activer / desactiver", callback_data=f"admin:toggle:{product_id}")],
        [InlineKeyboardButton("Changer nom / tranche", callback_data=f"admin:setname:{product_id}")],
        [InlineKeyboardButton("Changer prix", callback_data=f"admin:setprice:{product_id}")],
        [InlineKeyboardButton("Retour", callback_data=f"admin:products:{product['category']}")],
    ]
    await edit_or_reply(query.message, "\n".join(lines), reply_markup=InlineKeyboardMarkup(rows))


async def show_admin_stock(query):
    rows = []
    for product_id, product in sorted(DATA["products"].items(), key=lambda row: row[1]["name"].lower()):
        if product["type"] != "stock":
            continue
        rows.append([InlineKeyboardButton(f"{product['name']} ({stock_count(product_id)})", callback_data=f"admin:stockitem:{product_id}")])
    rows.append([InlineKeyboardButton("Retour", callback_data="admin:home")])
    await edit_or_reply(query.message, "Gestion du stock", reply_markup=InlineKeyboardMarkup(rows))


async def show_stock_item(query, product_id):
    product = get_product(product_id)
    rows = [
        [InlineKeyboardButton("Ajouter des cles", callback_data=f"admin:addkeys:{product_id}")],
        [InlineKeyboardButton("Voir 10 cles", callback_data=f"admin:viewkeys:{product_id}")],
        [InlineKeyboardButton("Retour", callback_data="admin:stock")],
    ]
    await edit_or_reply(query.message, f"{product['name']}\nPrix : {fmt_price(float(product['price']))}\nStock : {stock_count(product_id)}", reply_markup=InlineKeyboardMarkup(rows))


async def show_stats(query):
    total_orders = len(DATA["orders"])
    delivered = sum(1 for order in DATA["orders"].values() if order["status"] == "delivered")
    waiting = sum(1 for order in DATA["orders"].values() if order["status"] in {"awaiting_proof", "proof_received", "awaiting_delivery"})
    text = f"Stats Shop2Tech\nClients : {len(DATA['users'])}\nCommandes : {total_orders}\nLivrees : {delivered}\nEn attente : {waiting}"
    await edit_or_reply(query.message, text, reply_markup=admin_menu())


async def show_admin_clients(query):
    rows = []
    client_ids = [int(user_id) for user_id in DATA["users"].keys() if client_has_activity(user_id)]
    client_ids.sort(reverse=True)
    for target_id in client_ids[:40]:
        rows.append([InlineKeyboardButton(admin_client_header(target_id), callback_data=f"admin:client:{target_id}")])
    rows.append([InlineKeyboardButton("⬅️ Retour", callback_data="admin:home")])
    await edit_or_reply(query.message, "👤 Clients\n\nChoisis un client pour ouvrir sa fiche complete.", reply_markup=InlineKeyboardMarkup(rows))


async def show_admin_client(query, target_id):
    user_data = ensure_user(int(target_id))
    transactions = all_client_transactions(int(target_id), limit=30)
    orders_count = sum(1 for order in DATA["orders"].values() if str(order.get("user_id")) == str(target_id))
    deposits_count = sum(1 for deposit in DATA["deposits"].values() if str(deposit.get("user_id")) == str(target_id))
    label = client_label(int(target_id))
    lines = [
        "👤 Fiche client",
        "",
        f"Pseudo : {escape(label)}",
        f"ID : {target_id}",
        f"Solde actuel : {fmt_price(float(user_data.get('balance', 0.0)))}",
        f"Commandes : {orders_count}",
        f"Depots : {deposits_count}",
    ]
    if transactions:
        lines.extend(["", "💳 Historique :", *[f"- {escape(entry)}" for entry in transactions]])
    else:
        lines.extend(["", "💳 Aucun historique disponible pour le moment."])
    await edit_or_reply(
        query.message,
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Retour", callback_data="admin:clients")]]),
    )


async def show_admin_tickets(query, status=None, category_filter=None):
    rows = []
    if status is None:
        await edit_or_reply(query.message, "🎫 Gestion tickets\n\nChoisis la section que tu veux afficher.", reply_markup=admin_ticket_sections_menu())
        return

    source = tickets_by_status_and_category(status, category_filter) if category_filter else tickets_by_status(status)
    for ticket_id, ticket in source[:20]:
        rows.append(
            [
                InlineKeyboardButton(
                    f"{ticket_status_badge(ticket['status'])} {ticket['category'].upper()} - Ticket {ticket_id} - client {ticket['user_id']}",
                    callback_data=f"admin:ticket:{ticket_id}",
                )
            ]
        )
    rows.append([InlineKeyboardButton("⬅️ Retour", callback_data="admin:tickets")])
    section_name = TICKET_STATUS_NAMES.get(status, status)
    text = f"🎫 Tickets {section_name.lower()}" if rows[:-1] else f"🎫 Aucun ticket {section_name.lower()} pour le moment."
    await edit_or_reply(query.message, text, reply_markup=InlineKeyboardMarkup(rows))


async def show_admin_ticket(query, ticket_id):
    ticket = DATA["tickets"].get(ticket_id)
    if not ticket:
        await edit_or_reply(query.message, "Ticket introuvable.", reply_markup=admin_menu())
        return
    limited_view = is_support_admin(query.from_user.id) and not is_owner(query.from_user.id)
    client_balance, recent_transactions = client_recent_transactions(ticket["user_id"])
    history = ticket["messages"][-5:]
    lines = [
        f"🎫 Ticket {ticket_id}",
        f"👤 Client : {ticket['user_id']}",
        f"🔗 Pseudo : {escape(ticket.get('username') or 'Aucun')}",
        f"🗂️ Type : {ticket['category'].upper()}",
        f"📌 Statut : {ticket_status_badge(ticket['status'])} {TICKET_STATUS_NAMES.get(ticket['status'], ticket['status'])}",
        "",
        f"📝 Motif : {escape(ticket['reason'])}",
    ]
    if ticket.get("details"):
        details = ticket["details"]
        lines.append("")
        lines.append("📋 Infos client :")
        for label, value in details.items():
            if limited_view and label.lower() in {"moyen de paiement", "nom / prenom paiement"}:
                continue
            lines.append(f"- {label} : {escape(str(value))}")
        lines.append(f"- Solde client : {fmt_price(client_balance)}")
    else:
        lines.append("")
        lines.append("📋 Infos client :")
        lines.append(f"- Solde client : {fmt_price(client_balance)}")
    if recent_transactions:
        lines.append("")
        lines.append("💳 Dernieres transactions :")
        for entry in recent_transactions:
            lines.append(f"- {escape(entry)}")
    if history:
        lines.append("")
        lines.append("💬 Derniers messages :")
        for msg in history:
            prefix = "Admin" if msg["from"] == "admin" else "Client"
            lines.append(f"- {prefix} : {escape(msg['text'])}")
    rows = []
    if ticket["status"] == "pending":
        rows.append([InlineKeyboardButton("🟢 Prendre en charge", callback_data=f"admin:tickettake:{ticket_id}")])
        rows.append([InlineKeyboardButton("✅ Fermer le ticket", callback_data=f"admin:ticketclose:{ticket_id}")])
    elif ticket["status"] == "open":
        rows.append([InlineKeyboardButton("💬 Répondre", callback_data=f"admin:ticketreply:{ticket_id}")])
        rows.append([InlineKeyboardButton("🟠 Mettre en attente", callback_data=f"admin:ticketpending:{ticket_id}")])
        rows.append([InlineKeyboardButton("✅ Fermer le ticket", callback_data=f"admin:ticketclose:{ticket_id}")])
    else:
        rows.append([InlineKeyboardButton("🗑️ Supprimer le ticket", callback_data=f"admin:ticketdelete:{ticket_id}")])
    rows.append([InlineKeyboardButton("⬅️ Retour", callback_data="admin:tickets")])
    await edit_or_reply(query.message, "\n".join(lines), reply_markup=InlineKeyboardMarkup(rows))


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_data = sync_user_profile(query.from_user)
    if expire_pending_order(user_data):
        await edit_or_reply(query.message, "⌛ Le delai est depasse. La commande a ete annulee automatiquement et le panier a ete reinitialise.", reply_markup=main_menu(user_id))
        return
    data = query.data

    if data == "menu:start":
        await welcome(query.message, query.from_user)
        return
    if data == "menu:shop":
        if not shop_is_open():
            await show_shop_closed(query.message, user_id)
            return
        await edit_or_reply(query.message, "🛍️ Choisis une categorie.", reply_markup=categories_menu())
        return
    if data == "menu:cart":
        await show_cart(query.message, user_id)
        return
    if data == "menu:orders":
        await show_orders(query.message, user_id)
        return
    if data == "deposit:home":
        balance = fmt_price(float(user_data["balance"]))
        await edit_or_reply(
            query.message,
            f"💰 Depot\n\n💼 Solde actuel : {balance}\n\nChoisis le montant a deposer.",
            reply_markup=deposit_amounts_menu(),
        )
        return
    if data == "deposit:custom":
        user_data["state"] = {"action": "custom_deposit_amount"}
        save_data()
        await edit_or_reply(
            query.message,
            "💰 Depot personnalise\n\nEnvoie maintenant le montant souhaite.\nExemple : 25",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Annuler", callback_data="menu:start")]]),
        )
        return
    if data.startswith("deposit:amount:"):
        amount = float(data.split(":")[2])
        deposit_id = create_deposit(user_id, amount)
        text = (
            f"💰 Depot {fmt_price(amount)}\n\n"
            "Choisis maintenant le moyen de paiement.\n"
            "Le delai de 8 minutes commence des maintenant."
        )
        await edit_or_reply(query.message, text, reply_markup=payment_methods_menu())
        return
    if data.startswith("ticket:reply:"):
        ticket_id = data.split(":")[2]
        ticket = DATA["tickets"].get(ticket_id)
        if not ticket or ticket["status"] == "closed":
            await edit_or_reply(query.message, "❌ Ce ticket n'est plus disponible.", reply_markup=main_menu(user_id))
            return
        user_data["state"] = {"action": "ticket_reply", "ticket_id": ticket_id}
        save_data()
        await edit_or_reply(
            query.message,
            f"💬 Reponse au ticket {ticket_id}\n\nEcris maintenant ton message pour poursuivre l'echange.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Retour", callback_data="menu:start")]]),
        )
        return
    if data == "ticket:new":
        await edit_or_reply(
            query.message,
            "🆘 Ticket report\n\nChoisis d'abord le type de demande.",
            reply_markup=ticket_category_menu(),
        )
        return
    if data.startswith("ticket:type:"):
        ticket_type = data.split(":")[2]
        if ticket_type == "sav":
            user_data["state"] = {"action": "sav_full_name", "category": ticket_type, "details": {}}
            save_data()
            await edit_or_reply(
                query.message,
                "🛠️ Ticket SAV\n\nIndique d'abord ton nom et prenom.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Annuler", callback_data="menu:start")]]),
            )
        else:
            user_data["state"] = {"action": "new_ticket", "category": ticket_type}
            save_data()
            await edit_or_reply(
                query.message,
                "❓ Ticket Question\n\nExplique clairement ta demande en un seul message.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Annuler", callback_data="menu:start")]]),
            )
        return
    if data.startswith("cat:"):
        category = data.split(":", 1)[1]
        if not shop_is_open():
            await show_shop_closed(query.message, user_id)
            return
        if category == "ubereats":
            await show_ubereats_intro(query)
            return
        if category == "osint":
            await show_osint_intro(query)
            return
        if category == "subscriptions" and get_product("spotify_premium") and get_product("spotify_premium").get("active", True):
            await show_category(query, category)
            return
        if category == "fastfood":
            await edit_or_reply(query.message, "🍔 Fast Food\n\nChoisis maintenant une enseigne.", reply_markup=fastfood_menu())
        elif category == "boosts":
            await edit_or_reply(query.message, "🚀 Boost reseaux\n\nChoisis maintenant une plateforme.", reply_markup=boosts_menu())
        else:
            await show_category(query, category)
        return
    if data == "ubereats:start":
        user_data["state"] = {"action": "ubereats_address"}
        save_data()
        await edit_or_reply(
            query.message,
            "🛵 Uber Eats -50%\n\n📍 Envoie maintenant l'adresse complete de livraison en un seul message.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Annuler", callback_data="menu:start")]]),
        )
        return
    if data == "osint:start":
        user_data["state"] = {"action": "osint_request"}
        save_data()
        await edit_or_reply(
            query.message,
            "🕵️ Recherche OSINT\n\nEnvoie ta demande en un seul message en indiquant un maximum d'informations.\n\nExemple :\n- Nom / prenom\n- Nom de naissance\n- Pseudo\n- Telephone\n- Email\n- Adresse IP\n- Plaque / VIN\n- Telegram / Facebook\n- Localisation\n- IBAN / BIC\n- Infos FiveM / GTA RP\n\nPlus ta demande est complete, mieux c'est.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Annuler", callback_data="menu:start")]]),
        )
        return
    if data.startswith("osint:deepen:"):
        source_order_id = data.split(":")[2]
        source_order = DATA["orders"].get(source_order_id)
        if not source_order or source_order.get("order_kind") != "osint" or int(source_order.get("user_id", 0)) != int(user_id):
            await edit_or_reply(query.message, "❌ Cette recherche n'est plus disponible.", reply_markup=main_menu(user_id))
            return
        user_data["state"] = {"action": "osint_deepen", "source_order_id": source_order_id}
        save_data()
        await edit_or_reply(
            query.message,
            (
                "🔎 Approfondir la recherche\n\n"
                "Explique maintenant ce que tu veux approfondir ou verifier en plus.\n\n"
                "💰 Prix fixe : 2€"
            ),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Annuler", callback_data="menu:start")]]),
        )
        return
    if data.startswith("spotify:start:"):
        mode = data.split(":")[2]
        if mode == "keep":
            user_data["state"] = {"action": "spotify_email", "mode": mode, "details": {}}
            save_data()
            await edit_or_reply(
                query.message,
                "🎧 Spotify Premium\n\nEnvoie maintenant l'email de ton compte Spotify personnel.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Annuler", callback_data="cat:subscriptions")]]),
            )
            return
        order_id = create_spotify_order(user_id, "new", {"mode_label": "Nouveau compte"})
        user_data["awaiting_order_id"] = order_id
        save_data()
        await edit_or_reply(
            query.message,
            (
                f"🎧 Spotify Premium - commande {order_id}\n\n"
                f"💰 Total a regler : {fmt_price(float(get_product('spotify_premium')['price']))}\n\n"
                "✨ Choisis le moyen de paiement qui t'arrange.\n"
                "Le delai commencera au moment ou tu selectionnes ton moyen de paiement.\n\n"
                "⚡ Mise en service souvent en 5 a 10 minutes, mais cela peut prendre jusqu'a 24h."
            ),
            reply_markup=checkout_methods_menu(float(user_data["balance"]), float(get_product("spotify_premium")["price"])),
        )
        return
    if data.startswith("boost:start:"):
        product_id = data.split(":")[2]
        product = get_product(product_id)
        if not product or not product.get("active", True):
            await edit_or_reply(query.message, "🚧 Cette option est temporairement indisponible.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Retour", callback_data="cat:boosts")]]))
            return
        user_data["state"] = {"action": "boost_details", "product_id": product_id}
        save_data()
        prompt = "Envoie maintenant le lien du compte, du post, de la video ou les infos utiles selon ton besoin."
        if product_id == "tiktok_boost":
            prompt = "Envoie maintenant le lien de la video TikTok concernee."
        elif product_id == "tiktok_followers":
            prompt = "Envoie maintenant le lien du compte TikTok a booster."
        elif product_id == "insta_views":
            prompt = "Envoie maintenant le lien du post ou de la video Instagram concernee."
        elif product_id == "insta_boost":
            prompt = "Envoie maintenant le lien du compte Instagram a booster."
        await edit_or_reply(
            query.message,
            f"🚀 {product['name']}\n\n{prompt}\n\n📦 Livraison progressive\n⏱️ Delai maximum : 24h",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Annuler", callback_data=f"boostsubcat:{product.get('subcategory', 'tiktok')}")]]),
        )
        return
    if data.startswith("subcat:"):
        subcategory = data.split(":", 1)[1]
        if not shop_is_open():
            await show_shop_closed(query.message, user_id)
            return
        if subcategory in FASTFOOD_SUBCATEGORY_NAMES:
            await show_fastfood_subcategory(query, subcategory)
        return
    if data.startswith("boostsubcat:"):
        subcategory = data.split(":", 1)[1]
        if not shop_is_open():
            await show_shop_closed(query.message, user_id)
            return
        if subcategory in BOOST_SUBCATEGORY_NAMES:
            await show_boost_subcategory(query, subcategory)
        return
    if data.startswith("soon:"):
        await edit_or_reply(query.message, "🌮 Cette categorie arrive bientot.", reply_markup=fastfood_menu())
        return
    if data.startswith("product:view:"):
        if not shop_is_open():
            await show_shop_closed(query.message, user_id)
            return
        product_id = data.split(":", 2)[2]
        product = get_product(product_id)
        if product and product["category"] == "fastfood" and product.get("subcategory"):
            lines = [f"✨ {product['name']}", f"💰 Prix : {fmt_price(float(product['price']))}", "🍔 Selection disponible"]
            rows = [
                [InlineKeyboardButton("🛒 Ajouter au panier", callback_data=f"product:add:{product_id}")],
                [InlineKeyboardButton("⬅️ Retour", callback_data=f"subcat:{product['subcategory']}")],
            ]
            await edit_or_reply(query.message, "\n".join(lines), reply_markup=InlineKeyboardMarkup(rows))
            return
        await show_product(query, product_id)
        return
    if data.startswith("product:add:"):
        if not shop_is_open():
            await show_shop_closed(query.message, user_id)
            return
        product_id = data.split(":", 2)[2]
        product = get_product(product_id)
        if product and product.get("active", True) and product.get("subcategory") and product["category"] in {"fastfood", "boosts"}:
            user_data["cart"].append(product_id)
            save_data()
            total = fmt_price(cart_total(user_data["cart"]))
            continue_callback = f"subcat:{product['subcategory']}" if product["category"] == "fastfood" else f"boostsubcat:{product['subcategory']}"
            rows = [
                [InlineKeyboardButton("💳 Payer maintenant", callback_data="cart:pay")],
                [InlineKeyboardButton("📦 Voir mon panier", callback_data="menu:cart")],
                [InlineKeyboardButton("🛒 Continuer mes achats", callback_data=continue_callback)],
            ]
            await edit_or_reply(
                query.message,
                f"✨ {product['name']} a bien ete ajoute a ton panier.\n\n📦 Articles : {len(user_data['cart'])}\n💰 Total actuel : {total}",
                reply_markup=InlineKeyboardMarkup(rows),
            )
            return
    if data.startswith("product:add:"):
        product_id = data.split(":", 2)[2]
        product = get_product(product_id)
        if not product or not product.get("active", True):
            await edit_or_reply(query.message, "Ce produit n'est pas disponible pour le moment.")
            return
        user_data["cart"].append(product_id)
        save_data()
        total = fmt_price(cart_total(user_data["cart"]))
        continue_callback = f"cat:{product['category']}"
        if product.get("category") == "boosts" and product.get("subcategory"):
            continue_callback = f"boostsubcat:{product['subcategory']}"
        rows = [
            [InlineKeyboardButton("💳 Payer maintenant", callback_data="cart:pay")],
            [InlineKeyboardButton("📦 Voir mon panier", callback_data="menu:cart")],
            [InlineKeyboardButton("🛒 Continuer mes achats", callback_data=continue_callback)],
        ]
        await edit_or_reply(
            query.message,
            f"✨ {product['name']} a bien ete ajoute a ton panier.\n\n📦 Articles : {len(user_data['cart'])}\n💰 Total actuel : {total}",
            reply_markup=InlineKeyboardMarkup(rows),
        )
        return
    if data.startswith("cart:remove:"):
        index = int(data.split(":")[2])
        if 0 <= index < len(user_data["cart"]):
            product_id = user_data["cart"].pop(index)
            save_data()
            product = get_product(product_id)
            await show_cart(query.message, user_id)
        return
    if data == "cart:clear":
        user_data["cart"] = []
        save_data()
        await edit_or_reply(query.message, "🗑️ Panier vide.", reply_markup=main_menu(user_id))
        return
    if data == "cart:pay":
        if not shop_is_open():
            await show_shop_closed(query.message, user_id)
            return
        if not user_data["cart"]:
            await edit_or_reply(query.message, "🛒 Ton panier est vide.")
            return
        total = fmt_price(cart_total(user_data["cart"]))
        text = (
            "💳 Paiement\n\n"
            f"💰 Total a regler : {total}\n\n"
            "✨ Choisis le moyen de paiement qui t'arrange.\n"
            "Le delai commencera au moment ou tu selectionnes ton moyen de paiement.\n\n"
            "⏳ Tu auras ensuite 8 minutes pour finaliser."
        )
        await edit_or_reply(query.message, text, reply_markup=checkout_methods_menu(float(user_data["balance"]), cart_total(user_data["cart"])))
        return
    if data.startswith("pay:method:"):
        method = data.split(":")[2]
        if method != "balance" and not shop_is_open() and not user_data.get("awaiting_deposit_id"):
            await show_shop_closed(query.message, user_id)
            return
        if method == "balance":
            if user_data.get("awaiting_order_id") and user_data["awaiting_order_id"] in DATA["orders"]:
                order_id = user_data["awaiting_order_id"]
                order = DATA["orders"][order_id]
                total = float(order["total"])
            else:
                total = cart_total(user_data["cart"])
            if float(user_data["balance"]) < total:
                await edit_or_reply(query.message, "❌ Solde insuffisant pour regler cette commande.", reply_markup=main_menu(user_id))
                return
            if not user_data.get("awaiting_order_id"):
                order_id = create_order(user_id)
                order = DATA["orders"][order_id]
            user_data["balance"] = round(float(user_data["balance"]) - total, 2)
            user_data["awaiting_order_id"] = None
            order["status"] = "proof_received"
            order["proof_file_id"] = "PAID_BY_BALANCE"
            order["expires_at"] = None
            order["payment_method"] = "balance"
            log_balance_event(user_id, -total, "Paiement par solde", f"order:{order_id}", "balance")
            save_data()
            await edit_or_reply(
                query.message,
                f"✅ Paiement par solde confirme.\n\n💼 Nouveau solde : {fmt_price(float(user_data['balance']))}",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Retour a l'accueil", callback_data="menu:start")]]),
            )
            await notify_admin(context, order_id)
            return
        if not user_data["cart"] and not user_data.get("awaiting_order_id"):
            if not user_data.get("awaiting_deposit_id"):
                await edit_or_reply(query.message, "🛒 Ton panier est vide.", reply_markup=main_menu(user_id))
                return
        if user_data.get("awaiting_deposit_id") and user_data["awaiting_deposit_id"] in DATA["deposits"]:
            deposit = DATA["deposits"][user_data["awaiting_deposit_id"]]
            deposit["payment_method"] = method
            deposit["expires_at"] = int(time()) + (8 * 60)
            save_data()
            total = fmt_price(float(deposit["amount"]))
        elif user_data.get("awaiting_order_id") and user_data["awaiting_order_id"] in DATA["orders"]:
            order_id = user_data["awaiting_order_id"]
            order = DATA["orders"][order_id]
            order["payment_method"] = method
            order["expires_at"] = int(time()) + (8 * 60)
            save_data()
            total = fmt_price(float(order["total"]))
        else:
            if not user_data["cart"]:
                await edit_or_reply(query.message, "🛒 Ton panier est vide.", reply_markup=main_menu(user_id))
                return
            order_id = create_order(user_id)
            order = DATA["orders"][order_id]
            order["payment_method"] = method
            save_data()
            total = fmt_price(float(order["total"]))
        method_text = {
            "paypal": (
                "💙 PayPal",
                f"<a href=\"{PAYPAL_LINK}\">👉 Ouvrir le lien PayPal</a>\n\n⚠️ <b>AMIS / PROCHES</b>\n⚠️ <b>NE RIEN METTRE EN NOTE</b>"
            ),
            "applepay": (
                " Apple Pay",
                f"<a href=\"{LEETCHI_LINK}\">👉 Ouvrir le lien Leetchi</a>\n\n"
                "1. Clique sur <b>Participer</b>\n"
                "2. Mets le <b>montant exact</b> de la participation\n"
                "3. Remplis les <b>informations personnelles</b>\n"
                "4. Mets une <b>date de naissance majeure</b>\n"
                "5. Regle avec <b>Apple Pay</b> si disponible, sinon par carte\n"
                "6. Envoie ensuite un <b>screen complet</b> de la validation"
            ),
            "googlepay": (
                "🅖 Google Pay",
                f"<a href=\"{LEETCHI_LINK}\">👉 Ouvrir le lien Leetchi</a>\n\n"
                "1. Clique sur <b>Participer</b>\n"
                "2. Mets le <b>montant exact</b> de la participation\n"
                "3. Remplis les <b>informations personnelles</b>\n"
                "4. Mets une <b>date de naissance majeure</b>\n"
                "5. Regle avec <b>Google Pay</b> si disponible, sinon par carte\n"
                "6. Envoie ensuite un <b>screen complet</b> de la validation"
            ),
            "bitcoin": (
                "₿ Bitcoin",
                "Copie bien l'adresse ci-dessous :\n<code>bc1q0mwntue4rkz6rygcc40y2lwx0mc6y8clj6svhw</code>"
            ),
            "solana": (
                "◎ Solana",
                "Copie bien l'adresse ci-dessous :\n<code>89zWXgADYNeYz9H46kgokLYyA7CxAbAbxNKrtUBsr3dh</code>"
            ),
            "ethereum": (
                "◆ Ethereum",
                "Copie bien l'adresse ci-dessous :\n<code>0xf776906e1A254f9043C0994346c446fe0569F6b2</code>"
            ),
        }
        title, value = method_text[method]
        text = (
            f"✨ {title}\n\n"
            f"💰 Montant : {total}\n\n"
            f"{value}\n\n"
            "✅ Quand c'est regle, clique sur <b>J'ai paye</b> puis envoie ta preuve.\n"
            "⏳ Tu as 8 minutes !"
        )
        await edit_or_reply(query.message, text, reply_markup=payment_detail_menu())
        return
    if data == "pay:confirm":
        if user_data.get("awaiting_deposit_id") and user_data["awaiting_deposit_id"] in DATA["deposits"]:
            await edit_or_reply(
                query.message,
                "✅ Paiement indique.\n\n📸 Envoie maintenant ta preuve de depot ici.\n⏳ Le delai de 8 minutes est deja en cours.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Annuler le depot", callback_data="pay:cancel")]]),
            )
            return
        if not (user_data.get("awaiting_order_id") and user_data["awaiting_order_id"] in DATA["orders"]):
            await edit_or_reply(query.message, "🛒 Ton panier est vide.", reply_markup=main_menu(user_id))
            return
        await edit_or_reply(
            query.message,
            "✅ Paiement indique.\n\n📸 Envoie maintenant ta preuve de paiement ici.\n⏳ Le delai de 8 minutes est deja en cours.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Annuler la commande", callback_data="pay:cancel")]]),
        )
        return
    if data == "pay:cancel":
        deposit_id = user_data.get("awaiting_deposit_id")
        if deposit_id and deposit_id in DATA["deposits"] and DATA["deposits"][deposit_id]["status"] == "awaiting_proof":
            DATA["deposits"].pop(deposit_id, None)
            user_data["awaiting_deposit_id"] = None
            save_data()
            await edit_or_reply(query.message, "❌ Depot annule.", reply_markup=main_menu(user_id))
            return
        order_id = user_data.get("awaiting_order_id")
        if order_id and order_id in DATA["orders"] and DATA["orders"][order_id]["status"] == "awaiting_proof":
            order = DATA["orders"].pop(order_id)
            user_data["cart"] = order["items"][:]
            user_data["awaiting_order_id"] = None
            save_data()
        await edit_or_reply(query.message, "❌ Commande annulee.\n\nSi tu as besoin d'aide, tu peux creer un ticket directement.", reply_markup=cancelled_order_menu())
        return

    if not is_admin(user_id):
        return

    if data == "admin:home":
        menu = admin_menu() if is_owner(user_id) else support_admin_menu()
        await edit_or_reply(query.message, "🛠️ Panel admin", reply_markup=menu)
        return
    if data == "admin:clients":
        if not is_owner(user_id):
            return
        await show_admin_clients(query)
        return
    if data.startswith("admin:client:"):
        if not is_owner(user_id):
            return
        await show_admin_client(query, data.split(":")[2])
        return
    if data == "admin:ticketsupport":
        if not is_support_admin(user_id) and not is_owner(user_id):
            return
        await show_admin_tickets(query, "pending", "question")
        return
    if data == "admin:tickets":
        if not is_owner(user_id):
            await show_admin_tickets(query, "pending", "question")
            return
        await show_admin_tickets(query)
        return
    if data.startswith("admin:tickets:"):
        status = data.split(":")[2]
        if is_owner(user_id):
            await show_admin_tickets(query, status)
        else:
            await show_admin_tickets(query, status, "question")
        return
    if data.startswith("admin:ticket:"):
        ticket = DATA["tickets"].get(data.split(":")[2])
        if not ticket:
            await edit_or_reply(query.message, "Ticket introuvable.", reply_markup=admin_menu() if is_owner(user_id) else support_admin_menu())
            return
        if is_support_admin(user_id) and ticket.get("category") != "question":
            await edit_or_reply(query.message, "⛔ Ce ticket n'est pas accessible avec ce role.", reply_markup=support_admin_menu())
            return
        await show_admin_ticket(query, data.split(":")[2])
        return
    if data.startswith("admin:ticketreply:"):
        ticket_id = data.split(":")[2]
        user_data["admin_state"] = {"action": "ticket_reply", "ticket_id": ticket_id}
        ticket = DATA["tickets"].get(ticket_id)
        if ticket and not can_manage_ticket(user_id, ticket):
            await edit_or_reply(query.message, "⛔ Ce ticket n'est pas accessible avec ce role.", reply_markup=support_admin_menu())
            return
        if ticket:
            ticket["status"] = "open"
        save_data()
        await edit_or_reply(query.message, f"💬 Reponse au ticket {ticket_id}\n\nEnvoie maintenant ton message.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Retour", callback_data=f"admin:ticket:{ticket_id}")]]))
        return
    if data.startswith("admin:ticketpending:"):
        ticket_id = data.split(":")[2]
        ticket = DATA["tickets"].get(ticket_id)
        if ticket and not can_manage_ticket(user_id, ticket):
            await edit_or_reply(query.message, "⛔ Ce ticket n'est pas accessible avec ce role.", reply_markup=support_admin_menu())
            return
        if ticket:
            ticket["status"] = "pending"
            save_data()
            await context.bot.send_message(
                ticket["user_id"],
                f"🟠 Ton ticket {ticket_id} est actuellement en attente de traitement.",
            )
        await edit_or_reply(query.message, f"🟠 Ticket {ticket_id} mis en attente.", reply_markup=admin_menu() if is_owner(user_id) else support_admin_menu())
        return
    if data.startswith("admin:tickettake:"):
        ticket_id = data.split(":")[2]
        ticket = DATA["tickets"].get(ticket_id)
        if ticket and not can_manage_ticket(user_id, ticket):
            await edit_or_reply(query.message, "⛔ Ce ticket n'est pas accessible avec ce role.", reply_markup=support_admin_menu())
            return
        if ticket:
            ticket["status"] = "open"
            save_data()
            staff_tag = f"@{query.from_user.username}" if query.from_user.username else "un membre du staff"
            await context.bot.send_message(
                ticket["user_id"],
                f"🟢 Ton ticket {ticket_id} a ete pris en charge par {staff_tag}.\n\nVous pouvez maintenant echanger directement ici.",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("💬 Repondre au ticket", callback_data=f"ticket:reply:{ticket_id}")],
                        [InlineKeyboardButton("🏠 Retour a l'accueil", callback_data="menu:start")],
                    ]
                ),
            )
        await edit_or_reply(
            query.message,
            f"🟢 Ticket {ticket_id} pris en charge.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("💬 Répondre", callback_data=f"admin:ticketreply:{ticket_id}")],
                    [InlineKeyboardButton("📋 Voir les informations", callback_data=f"admin:ticket:{ticket_id}")],
                    [InlineKeyboardButton("🏠 Accueil", callback_data="admin:home")],
                ]
            ),
        )
        return
    if data.startswith("admin:ticketclose:"):
        ticket_id = data.split(":")[2]
        ticket = DATA["tickets"].get(ticket_id)
        if ticket and not can_manage_ticket(user_id, ticket):
            await edit_or_reply(query.message, "⛔ Ce ticket n'est pas accessible avec ce role.", reply_markup=support_admin_menu())
            return
        if ticket:
            ticket["status"] = "closed"
            save_data()
            await context.bot.send_message(
                ticket["user_id"],
                f"✅ Ton ticket {ticket_id} a ete traite et ferme.\n\nAppuie sur Start pour afficher le menu.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Start", callback_data="menu:start")]]),
            )
        await edit_or_reply(query.message, f"✅ Ticket {ticket_id} ferme.", reply_markup=admin_menu() if is_owner(user_id) else support_admin_menu())
        return
    if data.startswith("admin:ticketdelete:"):
        ticket_id = data.split(":")[2]
        if ticket_id in DATA["tickets"]:
            DATA["tickets"].pop(ticket_id, None)
            save_data()
        await edit_or_reply(query.message, f"🗑️ Ticket {ticket_id} supprime definitivement.", reply_markup=admin_ticket_sections_menu())
        return
    if not is_owner(user_id):
        if data == "admin:shoptoggle":
            DATA["shop_open"] = not shop_is_open()
            save_data()
            status_text = (
                "🟢 Boutique ouverte\n\n✨ Le shop est de nouveau en ligne."
                if shop_is_open()
                else "🔴 Boutique fermee\n\n✨ Le shop est actuellement hors ligne.\nLes clients verront un message propre et pourront toujours creer un ticket."
            )
            await edit_or_reply(query.message, status_text, reply_markup=support_admin_menu())
        return
    if data == "admin:clients":
        await show_admin_clients(query)
        return
    if data.startswith("admin:client:"):
        await show_admin_client(query, data.split(":")[2])
        return
    if data == "admin:products":
        await show_admin_products(query)
        return
    if data == "admin:staff":
        await edit_or_reply(query.message, "👥 Gestion des admins support", reply_markup=admin_staff_menu())
        return
    if data == "admin:staff:add":
        user_data["admin_state"] = {"action": "staff_add"}
        save_data()
        await edit_or_reply(
            query.message,
            "👥 Ajouter un admin support\n\nEnvoie maintenant son ID Telegram.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Retour", callback_data="admin:staff")]]),
        )
        return
    if data.startswith("admin:staff:remove:"):
        target_id = data.split(":")[3]
        DATA["support_admins"] = [value for value in DATA.get("support_admins", []) if str(value) != str(target_id)]
        save_data()
        await edit_or_reply(query.message, f"✅ Admin support retire : {target_id}", reply_markup=admin_staff_menu())
        return
    if data == "admin:shoptoggle":
        DATA["shop_open"] = not shop_is_open()
        save_data()
        status_text = (
            "🟢 Boutique ouverte\n\n✨ Le shop est de nouveau en ligne."
            if shop_is_open()
            else "🔴 Boutique fermee\n\n✨ Le shop est actuellement hors ligne.\nLes clients verront un message propre et pourront toujours creer un ticket."
        )
        await edit_or_reply(query.message, status_text, reply_markup=admin_menu())
        return
    if data.startswith("admin:products:"):
        await show_admin_product_list(query, data.split(":")[2])
        return
    if data.startswith("admin:uberquote:"):
        order_id = data.split(":")[2]
        order = DATA["orders"].get(order_id)
        if not order or order.get("order_kind") != "ubereats":
            await edit_or_reply(query.message, "Commande Uber Eats introuvable.", reply_markup=admin_menu())
            return
        user_data["admin_state"] = {"action": "uber_quote", "order_id": order_id}
        save_data()
        await edit_or_reply(
            query.message,
            f"🛵 Uber Eats {order_id}\n\nEnvoie maintenant le montant exact a regler par le client.\nExemple : 18.50",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Retour", callback_data=f"admin:order:{order_id}")]]),
        )
        return
    if data.startswith("admin:osintquote:"):
        order_id = data.split(":")[2]
        order = DATA["orders"].get(order_id)
        if not order or order.get("order_kind") != "osint":
            await edit_or_reply(query.message, "Demande OSINT introuvable.", reply_markup=admin_menu())
            return
        user_data["admin_state"] = {"action": "osint_quote", "order_id": order_id}
        save_data()
        await edit_or_reply(
            query.message,
            f"🕵️ Recherche OSINT {order_id}\n\nEnvoie maintenant le montant exact a regler par le client.\nExemple : 8.50",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Retour", callback_data=f"admin:order:{order_id}")]]),
        )
        return
    if data.startswith("admin:product:"):
        await show_admin_product(query, data.split(":")[2])
        return
    if data.startswith("admin:toggle:"):
        product = get_product(data.split(":")[2])
        if product:
            product["active"] = not product.get("active", True)
            save_data()
            await edit_or_reply(query.message, f"{product['name']} -> {'actif' if product['active'] else 'desactive'}")
        return
    if data.startswith("admin:setprice:"):
        product_id = data.split(":")[2]
        user_data["admin_state"] = {"action": "setprice", "product_id": product_id}
        save_data()
        await edit_or_reply(query.message, "💰 Envoie le nouveau prix. Exemple : 5.5")
        return
    if data.startswith("admin:setname:"):
        product_id = data.split(":")[2]
        user_data["admin_state"] = {"action": "setname", "product_id": product_id}
        save_data()
        await edit_or_reply(query.message, "✏️ Envoie maintenant le nouveau nom ou la nouvelle tranche.\nExemple : McDo 250-274 pts")
        return
    if data == "admin:addbalance":
        await edit_or_reply(
            query.message,
            "💼 Gestion manuelle du solde\n\nChoisis l'action a faire.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("➕ Ajouter", callback_data="admin:addbalance:add")],
                    [InlineKeyboardButton("➖ Retirer", callback_data="admin:addbalance:remove")],
                    [InlineKeyboardButton("⬅️ Retour", callback_data="admin:home")],
                ]
            ),
        )
        return
    if data.startswith("admin:addbalance:"):
        mode = data.split(":")[2]
        user_data["admin_state"] = {"action": "addbalance", "mode": mode}
        save_data()
        label = "ajout" if mode == "add" else "retrait"
        await edit_or_reply(
            query.message,
            f"💼 Solde manuel\n\nMode : {label}\nEnvoie maintenant : ID montant\nExemple : 8567294409 15",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Retour", callback_data="admin:home")]]),
        )
        return
    if data == "admin:orders":
        await show_admin_orders(query)
        return
    if data.startswith("admin:modify:"):
        target_order = DATA["orders"].get(data.split(":")[2])
        if target_order and target_order.get("order_kind") == "ubereats":
            await edit_or_reply(query.message, "Cette commande Uber Eats n'est pas modifiable ligne par ligne.", reply_markup=admin_menu())
            return
        await show_order_modify_menu(query, data.split(":")[2])
        return
    if data.startswith("admin:modifyremove:"):
        _, _, order_id, index_text = data.split(":")
        order = DATA["orders"].get(order_id)
        if not order:
            await edit_or_reply(query.message, "Commande introuvable.", reply_markup=admin_menu())
            return
        try:
            index = int(index_text)
        except ValueError:
            await edit_or_reply(query.message, "Ligne invalide.", reply_markup=admin_menu())
            return
        if index < 0 or index >= len(order["items"]):
            await edit_or_reply(query.message, "Ligne introuvable.", reply_markup=admin_menu())
            return
        removed_product_id = order["items"].pop(index)
        removed_product = get_product(removed_product_id)
        refund_amount = float(removed_product["price"]) if removed_product else 0.0
        order["total"] = round(cart_total(order["items"]), 2)
        if removed_product_id in order.get("manual_delivery_queue", []):
            order["manual_delivery_queue"].remove(removed_product_id)
        client_user = ensure_user(order["user_id"])
        if refund_amount > 0:
            client_user["balance"] = round(float(client_user["balance"]) + refund_amount, 2)
            log_balance_event(order["user_id"], refund_amount, "Remboursement commande modifiee", f"order:{order_id}")
        if not order["items"]:
            order["status"] = "cancelled"
        save_data()
        removed_name = removed_product["name"] if removed_product else "Produit inconnu"
        if not order["items"]:
            await context.bot.send_message(
                order["user_id"],
                f"❌ Ta commande {order_id} a ete annulee apres modification.\n\n💼 {fmt_price(refund_amount)} ont ete recrédités sur ton solde.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Retour a l'accueil", callback_data="menu:start")]]),
            )
            await edit_or_reply(
                query.message,
                f"✅ {removed_name} retire de la commande.\n\nLa commande est maintenant vide et a ete annulee.\nRemboursement : {fmt_price(refund_amount)}",
                reply_markup=admin_menu(),
            )
            return
        await context.bot.send_message(
            order["user_id"],
            f"✏️ Ta commande {order_id} a ete modifiee.\n\nArticle retire : {removed_name}\n💼 Remboursement credite sur ton solde : {fmt_price(refund_amount)}\n💰 Nouveau total de la commande : {fmt_price(float(order['total']))}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Retour a l'accueil", callback_data="menu:start")]]),
        )
        await edit_or_reply(
            query.message,
            f"✅ {removed_name} retire de la commande.\n\nRemboursement credite : {fmt_price(refund_amount)}\nNouveau total : {fmt_price(float(order['total']))}",
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("🔄 Continuer la modification", callback_data=f"admin:modify:{order_id}")],
                    [InlineKeyboardButton("🔎 Retour a la commande", callback_data=f"admin:order:{order_id}")],
                    [InlineKeyboardButton("🏠 Accueil", callback_data="admin:home")],
                ]
            ),
        )
        return
    if data.startswith("admin:depositapprove:"):
        deposit_id = data.split(":")[2]
        deposit = DATA["deposits"].get(deposit_id)
        if deposit:
            deposit["status"] = "approved"
            credited_user = ensure_user(deposit["user_id"])
            credited_user["balance"] = round(float(credited_user["balance"]) + float(deposit["amount"]), 2)
            log_balance_event(deposit["user_id"], float(deposit["amount"]), "Depot valide", f"deposit:{deposit_id}", deposit.get("payment_method"))
            if credited_user.get("awaiting_deposit_id") == deposit_id:
                credited_user["awaiting_deposit_id"] = None
            save_data()
            await context.bot.send_message(
                deposit["user_id"],
                f"✅ Ton depot de {fmt_price(float(deposit['amount']))} a ete valide.\n\n💼 Nouveau solde : {fmt_price(float(credited_user['balance']))}",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Retour a l'accueil", callback_data="menu:start")]]),
            )
        await edit_or_reply(query.message, f"✅ Depot {deposit_id} valide.", reply_markup=admin_menu())
        return
    if data.startswith("admin:depositcancel:"):
        deposit_id = data.split(":")[2]
        deposit = DATA["deposits"].get(deposit_id)
        if deposit:
            deposit["status"] = "cancelled"
            deposit_user = ensure_user(deposit["user_id"])
            if deposit_user.get("awaiting_deposit_id") == deposit_id:
                deposit_user["awaiting_deposit_id"] = None
            save_data()
            await context.bot.send_message(
                deposit["user_id"],
                "❌ Ton depot a ete refuse.\n\nSi besoin, tu peux creer un ticket depuis l'accueil.",
            )
        await edit_or_reply(query.message, f"❌ Depot {deposit_id} refuse.", reply_markup=admin_menu())
        return
    if data.startswith("admin:order:"):
        await show_admin_order(query, data.split(":")[2])
        return
    if data.startswith("admin:approve:"):
        await approve_order(query, context, data.split(":")[2])
        return
    if data.startswith("admin:osintclear:"):
        order_id = data.split(":")[2]
        order = DATA["orders"].get(order_id)
        if not order or order.get("order_kind") != "osint":
            await edit_or_reply(query.message, "Commande introuvable.", reply_markup=admin_menu())
            return
        if order.get("status") != "awaiting_delivery":
            ensure_user(user_id)["admin_state"] = None
            save_data()
            await edit_or_reply(query.message, "Cette commande OSINT n'est plus en cours d'envoi.", reply_markup=admin_menu())
            return
        order["result_buffer"] = []
        ensure_user(user_id)["admin_state"] = {"action": "osint_result", "order_id": order_id}
        save_data()
        await edit_or_reply(
            query.message,
            f"🗑️ Brouillon OSINT vide.\n\nCommande {order_id}\n\nTu peux maintenant renvoyer autant de messages, photos ou fichiers que tu veux, puis finaliser a la fin.",
            reply_markup=osint_delivery_menu(order_id),
        )
        return
    if data.startswith("admin:osintfinish:"):
        order_id = data.split(":")[2]
        order = DATA["orders"].get(order_id)
        if not order or order.get("order_kind") != "osint":
            await edit_or_reply(query.message, "Commande introuvable.", reply_markup=admin_menu())
            return
        if order.get("status") != "awaiting_delivery":
            ensure_user(user_id)["admin_state"] = None
            save_data()
            await edit_or_reply(query.message, "Cette commande OSINT est deja terminee.", reply_markup=admin_menu())
            return
        if not order.get("result_buffer"):
            await edit_or_reply(
                query.message,
                f"❌ Aucun element n'est encore ajoute au brouillon pour la commande {order_id}.",
                reply_markup=osint_delivery_menu(order_id),
            )
            return
        await flush_osint_result_buffer(context, order_id)
        order["status"] = "delivered"
        order["result_buffer"] = []
        ensure_user(user_id)["admin_state"] = None
        save_data()
        await edit_or_reply(query.message, "✅ Resultat OSINT envoye au client.", reply_markup=admin_menu())
        return
    if data.startswith("admin:cancel:"):
        order = DATA["orders"].get(data.split(":")[2])
        if order:
            order["status"] = "cancelled"
            client_data = ensure_user(order["user_id"])
            if client_data.get("awaiting_order_id") == data.split(":")[2]:
                client_data["awaiting_order_id"] = None
            save_data()
            await context.bot.send_message(
                order["user_id"],
                "❌ La commande a ete annulee.\n\nSi tu as besoin d'aide, cree un ticket depuis l'accueil avec le bouton Report / ticket.",
            )
            await edit_or_reply(query.message, "Commande annulee.", reply_markup=admin_menu())
        return
    if data.startswith("admin:deliver:"):
        order_id = data.split(":")[2]
        current_delivery_order = active_delivery_order_id(user_id)
        if current_delivery_order and str(current_delivery_order) != str(order_id):
            await edit_or_reply(
                query.message,
                f"⛔ Une livraison est deja en cours sur la commande {current_delivery_order}.\n\nTermine-la d'abord avant d'en ouvrir une autre.",
                reply_markup=admin_menu() if is_owner(user_id) else support_admin_menu(),
            )
            return
        order = DATA["orders"].get(order_id)
        if order and order.get("order_kind") == "ubereats":
            user_data["admin_state"] = {"action": "uber_link", "order_id": order_id}
            save_data()
            await edit_or_reply(
                query.message,
                f"🛵 Livraison Uber Eats\n\nCommande {order_id}\n\nEnvoie maintenant le lien de suivi a transmettre au client.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Retour", callback_data=f"admin:order:{order_id}")]]),
            )
            return
        if order and order.get("order_kind") == "osint":
            user_data["admin_state"] = {"action": "osint_result", "order_id": order_id}
            save_data()
            await edit_or_reply(
                query.message,
                f"🕵️ Resultat OSINT\n\nCommande {order_id}\n\n"
                "Tu peux envoyer plusieurs messages, photos ou fichiers.\n"
                "Quand tout est pret, clique sur finaliser pour tout transmettre au client.",
                reply_markup=osint_delivery_menu(order_id),
            )
            return
        if order and order.get("order_kind") == "spotify":
            user_data["admin_state"] = {"action": "spotify_result", "order_id": order_id}
            save_data()
            await edit_or_reply(
                query.message,
                f"🎧 Livraison Spotify\n\nCommande {order_id}\n\nEnvoie maintenant soit les identifiants du compte cree, soit le message de mise en service a transmettre au client.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Retour", callback_data=f"admin:order:{order_id}")]]),
            )
            return
        if order and order.get("order_kind") == "boost":
            user_data["admin_state"] = {"action": "boost_result", "order_id": order_id}
            save_data()
            await edit_or_reply(
                query.message,
                f"🚀 Livraison boost\n\nCommande {order_id}\n\nEnvoie maintenant le message final, le lien ou les informations a transmettre au client.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Retour", callback_data=f"admin:order:{order_id}")]]),
            )
            return
        user_data["admin_state"] = {"action": "deliver", "order_id": order_id}
        save_data()
        hint = fastfood_order_hint(order) if order else "Commande"
        details = order_lines(order) if order else "- Commande introuvable"
        current_product = current_manual_delivery(order) if order else None
        current_label = current_product["name"] if current_product else "Aucune livraison restante"
        await edit_or_reply(
            query.message,
            f"📤 Livraison manuelle\n\n{hint} {order_id}\n\nA envoyer maintenant : {current_label}\n\n{details}\n\nTu peux envoyer une photo ou un texte.\nAjoute le numero de telephone ou les infos utiles dans la legende si besoin.",
        )
        return
    if data == "admin:stock":
        await show_admin_stock(query)
        return
    if data.startswith("admin:stockitem:"):
        await show_stock_item(query, data.split(":")[2])
        return
    if data.startswith("admin:addkeys:"):
        user_data["admin_state"] = {"action": "addkeys", "product_id": data.split(":")[2]}
        save_data()
        await edit_or_reply(query.message, "🔑 Envoie une ou plusieurs cles. Une cle par ligne.")
        return
    if data.startswith("admin:viewkeys:"):
        keys = DATA["stock"].get(data.split(":")[2], [])
        await edit_or_reply(query.message, "\n".join(keys[:10]) if keys else "Aucune cle en stock.")
        return
    if data == "admin:stats":
        await show_stats(query)


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = sync_user_profile(update.effective_user)
    photo = update.message.photo[-1].file_id

    user_state = user_data.get("state") or {}
    if user_state.get("action") == "ubereats_screen":
        order_id = create_ubereats_order(
            user_id,
            user_state.get("address", ""),
            user_state.get("order_total", 0.0),
            photo,
        )
        user_data["state"] = None
        save_data()
        await update.message.reply_text(
            f"✅ Demande Uber Eats {order_id} bien recue.\n\nOn analyse ta commande et on t'envoie ensuite le montant exact a regler.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Retour a l'accueil", callback_data="menu:start")]]),
        )
        await notify_admin_ubereats_request(context, order_id)
        return

    admin_state = user_data.get("admin_state") or {}
    if is_admin(user_id) and admin_state.get("action") == "osint_result":
        order_id = admin_state["order_id"]
        order = DATA["orders"].get(order_id)
        if not order or order.get("status") != "awaiting_delivery":
            user_data["admin_state"] = None
            save_data()
            await update.message.reply_text("❌ Cette commande OSINT n'est plus en cours d'envoi.")
            return
        append_osint_result_chunk(
            order,
            {
                "type": "photo",
                "file_id": photo,
                "caption": (update.message.caption or "").strip(),
            },
        )
        return
    if is_admin(user_id) and admin_state.get("action") == "boost_result":
        order_id = admin_state["order_id"]
        order = DATA["orders"].get(order_id)
        if not order or order.get("status") != "awaiting_delivery":
            user_data["admin_state"] = None
            save_data()
            await update.message.reply_text("❌ Cette commande boost n'est plus en cours d'envoi.")
            return
        caption = (update.message.caption or "").strip() or f"🚀 Mise a jour pour ta commande {fastfood_order_hint(order)}"
        await context.bot.send_photo(
            order["user_id"],
            photo=photo,
            caption=f"{caption}\n\n📦 Livraison progressive\n⏱️ Delai maximum : 24h",
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("🏠 Retour a l'accueil", callback_data="menu:start")],
                    [InlineKeyboardButton("🆘 Creer un ticket", callback_data="ticket:new")],
                ]
            ),
        )
        order["status"] = "delivered"
        user_data["admin_state"] = None
        save_data()
        await update.message.reply_text("✅ Suivi boost envoye au client.")
        return
    if is_admin(user_id) and admin_state.get("action") == "deliver":
        order_id = admin_state["order_id"]
        order = DATA["orders"].get(order_id)
        if order:
            current_product = current_manual_delivery(order)
            extra_text = (update.message.caption or "").strip()
            caption = (
                "🎉 Bon appetit !\n\n"
                "⏱️ Ta commande est garantie 15 minutes en cas de probleme.\n\n"
                "⚠️ En cas de souci :\n"
                "• preuve video obligatoire\n"
                "• nom de la ville / du restaurant\n\n"
                "🆘 Aide : cree un ticket report depuis l'accueil"
            )
            if extra_text:
                caption = f"{extra_text}\n\n{caption}"
            await context.bot.send_photo(
                order["user_id"],
                photo=photo,
                caption=caption,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("🏠 Retour a l'accueil", callback_data="menu:start")],
                        [InlineKeyboardButton("🆘 Creer un ticket", callback_data="ticket:new")],
                    ]
                ),
            )
            if order.get("manual_delivery_queue"):
                sent_product_id = order["manual_delivery_queue"].pop(0)
                order.setdefault("manual_delivery_sent", []).append(sent_product_id)
            next_product = current_manual_delivery(order)
            if next_product:
                order["status"] = "awaiting_delivery"
                user_data["admin_state"] = {"action": "deliver", "order_id": order_id}
                save_data()
                current_name = current_product["name"] if current_product else "cet article"
                await update.message.reply_text(f"✅ Livraison envoyee pour {current_name}.\n\nEnvoie maintenant : {next_product['name']}.")
                return
            order["status"] = "delivered"
            user_data["admin_state"] = None
            save_data()
            await update.message.reply_text("✅ Livraison envoyee au client.")
        return

    if expire_pending_deposit(user_data):
        await update.message.reply_text("⌛ Le delai du depot est depasse. Le depot a ete annule automatiquement.")
        return
    deposit_id = user_data.get("awaiting_deposit_id")
    if deposit_id:
        deposit = DATA["deposits"].get(deposit_id)
        if deposit and deposit["status"] == "awaiting_proof":
            deposit["proof_file_id"] = photo
            deposit["status"] = "proof_received"
            deposit["expires_at"] = None
            user_data["awaiting_deposit_id"] = None
            save_data()
            await update.message.reply_text("✅ Preuve de depot bien recue. Elle vient d'etre transmise a l'admin.")
            await notify_admin_deposit(context, deposit_id)
            return

    if expire_pending_order(user_data):
        await update.message.reply_text("⌛ Le delai est depasse. La commande a ete annulee automatiquement.")
        return
    order_id = user_data.get("awaiting_order_id")
    if not order_id:
        await update.message.reply_text("❌ Aucune commande en attente de preuve.")
        return
    order = DATA["orders"].get(order_id)
    if not order or order["status"] != "awaiting_proof":
        await update.message.reply_text("❌ Cette commande n attend plus de preuve.")
        return
    order["proof_file_id"] = photo
    order["status"] = "proof_received"
    order["expires_at"] = None
    user_data["awaiting_order_id"] = None
    save_data()
    await update.message.reply_text("✅ Preuve bien recue. Elle vient d'etre transmise a l'admin.")
    await notify_admin(context, order_id)


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = sync_user_profile(update.effective_user)
    admin_state = user_data.get("admin_state") or {}
    document = update.message.document

    if is_admin(user_id) and admin_state.get("action") == "osint_result":
        order_id = admin_state["order_id"]
        order = DATA["orders"].get(order_id)
        if not order or order.get("status") != "awaiting_delivery":
            user_data["admin_state"] = None
            save_data()
            await update.message.reply_text("❌ Cette commande OSINT n'est plus en cours d'envoi.")
            return
        append_osint_result_chunk(
            order,
            {
                "type": "document",
                "file_id": document.file_id,
                "caption": (update.message.caption or "").strip(),
                "file_name": document.file_name,
            },
        )
        return
    if is_admin(user_id) and admin_state.get("action") == "boost_result":
        order_id = admin_state["order_id"]
        order = DATA["orders"].get(order_id)
        if not order or order.get("status") != "awaiting_delivery":
            user_data["admin_state"] = None
            save_data()
            await update.message.reply_text("❌ Cette commande boost n'est plus en cours d'envoi.")
            return
        caption = (update.message.caption or "").strip() or f"🚀 Mise a jour pour ta commande {fastfood_order_hint(order)}"
        await context.bot.send_document(
            order["user_id"],
            document=document.file_id,
            caption=f"{caption}\n\n📦 Livraison progressive\n⏱️ Delai maximum : 24h",
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("🏠 Retour a l'accueil", callback_data="menu:start")],
                    [InlineKeyboardButton("🆘 Creer un ticket", callback_data="ticket:new")],
                ]
            ),
        )
        order["status"] = "delivered"
        user_data["admin_state"] = None
        save_data()
        await update.message.reply_text("✅ Suivi boost envoye au client.")
        return

    await update.message.reply_text("👉 Utilise /start pour ouvrir la boutique.")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    user_id = update.effective_user.id
    user_data = sync_user_profile(update.effective_user)
    text = update.message.text.strip()
    if text.startswith("/"):
        return

    user_state = user_data.get("state") or {}
    if user_state.get("action") == "ubereats_address":
        user_state["address"] = text
        user_state["action"] = "ubereats_total"
        user_data["state"] = user_state
        save_data()
        await update.message.reply_text(
            "💶 Envoie maintenant le prix total final de la commande Uber Eats.\n\nLe montant doit etre compris entre 20€ et 23€.\nExemple : 21.90"
        )
        return
    if user_state.get("action") == "ubereats_total":
        try:
            amount = float(text.replace(",", "."))
        except ValueError:
            await update.message.reply_text("❌ Montant invalide. Exemple : 18.90")
            return
        if amount < 20 or amount > 23:
            await update.message.reply_text("❌ Montant refuse.\n\nReessaie avec une commande comprise entre 20€ et 23€.")
            return
        user_state["order_total"] = amount
        user_state["action"] = "ubereats_screen"
        user_data["state"] = user_state
        save_data()
        await update.message.reply_text(
            "📸 Envoie maintenant un screen du recapitulatif complet de la commande Uber Eats avec son prix final bien visible."
        )
        return
    if user_state.get("action") == "osint_request":
        order_id = create_osint_order(user_id, text)
        user_data["state"] = None
        save_data()
        await update.message.reply_text(
            f"✅ Demande OSINT {order_id} bien recue.\n\nElle a ete envoyee a l'admin et reste en attente de prix.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Retour a l'accueil", callback_data="menu:start")]]),
        )
        await notify_admin_osint_request(context, order_id)
        return
    if user_state.get("action") == "osint_deepen":
        source_order_id = user_state.get("source_order_id")
        order_id = create_osint_order(user_id, f"Approfondissement de la recherche {source_order_id}\n\n{text}")
        order = DATA["orders"].get(order_id)
        if order:
            order["total"] = 2.0
            order["status"] = "awaiting_proof"
            order["expires_at"] = None
            order["osint_source_order_id"] = source_order_id
        user_data["state"] = None
        user_data["awaiting_order_id"] = order_id
        save_data()
        await update.message.reply_text(
            (
                f"🔎 Approfondissement OSINT - commande {order_id}\n\n"
                "💰 Total a regler : 2€\n\n"
                "✨ Choisis le moyen de paiement qui t'arrange.\n"
                "Le delai commencera au moment ou tu selectionnes ton moyen de paiement.\n\n"
                "⏳ Tu auras ensuite 8 minutes pour finaliser."
            ),
            reply_markup=checkout_methods_menu(float(user_data["balance"]), 2.0),
        )
        return
    if user_state.get("action") == "spotify_email":
        user_state["details"]["email"] = text
        user_state["action"] = "spotify_username"
        user_data["state"] = user_state
        save_data()
        await update.message.reply_text("👤 Envoie maintenant le pseudo / nom du compte Spotify.")
        return
    if user_state.get("action") == "spotify_username":
        user_state["details"]["username"] = text
        user_state["action"] = "spotify_password"
        user_data["state"] = user_state
        save_data()
        await update.message.reply_text("🔒 Envoie maintenant le mot de passe de ton compte Spotify.")
        return
    if user_state.get("action") == "spotify_password":
        user_state["details"]["password"] = text
        details = {
            "mode_label": "Compte personnel",
            "email": user_state["details"].get("email", ""),
            "username": user_state["details"].get("username", ""),
            "password": user_state["details"].get("password", ""),
        }
        order_id = create_spotify_order(user_id, "keep", details)
        user_data["state"] = None
        user_data["awaiting_order_id"] = order_id
        save_data()
        await update.message.reply_text(
            (
                f"🎧 Spotify Premium - commande {order_id}\n\n"
                f"💰 Total a regler : {fmt_price(float(get_product('spotify_premium')['price']))}\n\n"
                "✨ Choisis le moyen de paiement qui t'arrange.\n"
                "Le delai commencera au moment ou tu selectionnes ton moyen de paiement.\n\n"
                "⚡ Mise en service souvent en 5 a 10 minutes, mais cela peut prendre jusqu'a 24h."
            ),
            reply_markup=checkout_methods_menu(float(user_data["balance"]), float(get_product("spotify_premium")["price"])),
        )
        return
    if user_state.get("action") == "boost_details":
        product_id = user_state.get("product_id")
        product = get_product(product_id)
        if not product or not product.get("active", True):
            user_data["state"] = None
            save_data()
            await update.message.reply_text("🚧 Cette option n'est plus disponible pour le moment.")
            return
        order_id = create_boost_order(user_id, product_id, text)
        user_data["state"] = None
        user_data["awaiting_order_id"] = order_id
        save_data()
        await update.message.reply_text(
            (
                f"🚀 {product['name']} - commande {order_id}\n\n"
                f"💰 Total a regler : {fmt_price(float(product['price']))}\n\n"
                "✨ Choisis le moyen de paiement qui t'arrange.\n"
                "Le delai commencera au moment ou tu selectionnes ton moyen de paiement.\n\n"
                "📦 Livraison progressive\n"
                "⏱️ Delai maximum : 24h"
            ),
            reply_markup=checkout_methods_menu(float(user_data["balance"]), float(product["price"])),
        )
        return
    if user_state.get("action") == "custom_deposit_amount":
        try:
            amount = float(text.replace(",", "."))
        except ValueError:
            await update.message.reply_text("❌ Montant invalide. Exemple : 25")
            return
        if amount <= 0:
            await update.message.reply_text("❌ Le montant doit etre superieur a 0.")
            return
        user_data["state"] = None
        create_deposit(user_id, amount)
        await update.message.reply_text(
            f"💰 Depot {fmt_price(amount)}\n\nChoisis maintenant le moyen de paiement.\n⏳ Le delai de 8 minutes commence des maintenant.",
            reply_markup=payment_methods_menu(),
        )
        return
    if user_state.get("action") == "sav_full_name":
        user_state["details"]["nom_prenom"] = text
        user_state["action"] = "sav_payment_method"
        user_data["state"] = user_state
        save_data()
        await update.message.reply_text("💳 Indique maintenant le moyen de paiement utilise. Exemple : PayPal, Bitcoin, Solana, Ethereum.")
        return

    if user_state.get("action") == "sav_payment_method":
        user_state["details"]["moyen_paiement"] = text
        user_state["action"] = "sav_payment_name"
        user_data["state"] = user_state
        save_data()
        await update.message.reply_text("🧾 Indique maintenant le nom / prenom utilise pour ce paiement.")
        return

    if user_state.get("action") == "sav_payment_name":
        user_state["details"]["identite_paiement"] = text
        user_state["action"] = "sav_reason"
        user_data["state"] = user_state
        save_data()
        await update.message.reply_text("📝 Explique maintenant clairement ton souci SAV en un seul message.")
        return

    if user_state.get("action") == "sav_reason":
        username = f"@{update.effective_user.username}" if update.effective_user.username else "Aucun"
        telegram_name = " ".join(part for part in [update.effective_user.first_name, update.effective_user.last_name] if part) or "Aucun"
        ticket_id = create_ticket(
            user_id,
            username,
            "sav",
            text,
            details={
                "ID client": user_id,
                "Pseudo": username,
                "Nom Telegram": telegram_name,
                "Nom / prenom": user_state["details"].get("nom_prenom", ""),
                "Moyen de paiement": user_state["details"].get("moyen_paiement", ""),
                "Nom / prenom paiement": user_state["details"].get("identite_paiement", ""),
                "IP": "Non disponible via Telegram bot",
                "Licence Telegram": "Non disponible via Telegram bot",
            },
        )
        DATA["tickets"][ticket_id]["messages"].append({"from": "client", "text": text})
        user_data["state"] = None
        save_data()
        await update.message.reply_text(
            f"✅ Ticket SAV {ticket_id} cree.\n\nIl est maintenant en attente de prise en charge.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Retour a l'accueil", callback_data="menu:start")]]),
        )
        await context.bot.send_message(
            ADMIN_ID,
            f"🎫 Nouveau ticket {ticket_id}\n👤 Client : {user_id}\n🗂️ Type : SAV\n🔗 Pseudo : {username}\n\n📝 Motif : {text}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Ouvrir le ticket", callback_data=f"admin:ticket:{ticket_id}")]]),
        )
        return

    if user_state.get("action") == "new_ticket":
        username = f"@{update.effective_user.username}" if update.effective_user.username else "Aucun"
        telegram_name = " ".join(part for part in [update.effective_user.first_name, update.effective_user.last_name] if part) or "Aucun"
        ticket_id = create_ticket(
            user_id,
            username,
            user_state.get("category", "question"),
            text,
            details={
                "ID client": user_id,
                "Pseudo": username,
                "Nom Telegram": telegram_name,
                "IP": "Non disponible via Telegram bot",
                "Licence Telegram": "Non disponible via Telegram bot",
            },
        )
        DATA["tickets"][ticket_id]["messages"].append({"from": "client", "text": text})
        user_data["state"] = None
        save_data()
        await update.message.reply_text(
            f"✅ Ticket {ticket_id} cree.\n\nIl est maintenant en attente de prise en charge.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Retour a l'accueil", callback_data="menu:start")]]),
        )
        await context.bot.send_message(
            ADMIN_ID,
            f"🎫 Nouveau ticket {ticket_id}\n👤 Client : {user_id}\n🗂️ Type : {DATA['tickets'][ticket_id]['category'].upper()}\n🔗 Pseudo : {username}\n\n📝 Motif : {text}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Ouvrir le ticket", callback_data=f"admin:ticket:{ticket_id}")]]),
        )
        if DATA["tickets"][ticket_id]["category"] == "question":
            await notify_support_admins(
                context,
                f"🎫 Nouveau ticket {ticket_id}\n👤 Client : {user_id}\n🔗 Pseudo : {username}\n🗂️ Type : QUESTION\n\n📝 Motif : {text}",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Ouvrir le ticket", callback_data=f"admin:ticket:{ticket_id}")]]),
            )
        return

    if user_state.get("action") == "ticket_reply":
        ticket = DATA["tickets"].get(user_state["ticket_id"])
        if not ticket or ticket["status"] == "closed":
            user_data["state"] = None
            save_data()
            await update.message.reply_text("❌ Ce ticket n'est plus disponible.")
            return
        ticket["messages"].append({"from": "client", "text": text})
        ticket["status"] = "open"
        user_data["state"] = None
        save_data()
        await update.message.reply_text("✅ Ta reponse a bien ete ajoutee au ticket.")
        await context.bot.send_message(
            ADMIN_ID,
            f"💬 Nouvelle reponse sur le ticket {user_state['ticket_id']}\n👤 Client : {user_id}\n\n{text}",
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("💬 Repondre au ticket", callback_data=f"admin:ticketreply:{user_state['ticket_id']}")],
                    [InlineKeyboardButton("🔎 Ouvrir le ticket", callback_data=f"admin:ticket:{user_state['ticket_id']}")],
                    [InlineKeyboardButton("🎫 Gestion tickets", callback_data="admin:tickets")],
                ]
            ),
        )
        if ticket.get("category") == "question":
            username = f"@{update.effective_user.username}" if update.effective_user.username else "Aucun"
            await notify_support_admins(
                context,
                f"💬 Nouvelle reponse sur le ticket {user_state['ticket_id']}\n👤 Client : {user_id}\n🔗 Pseudo : {username}\n\n{text}",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("💬 Repondre au ticket", callback_data=f"admin:ticketreply:{user_state['ticket_id']}")],
                        [InlineKeyboardButton("🔎 Ouvrir le ticket", callback_data=f"admin:ticket:{user_state['ticket_id']}")],
                        [InlineKeyboardButton("🎫 Tickets support", callback_data="admin:ticketsupport")],
                    ]
                ),
            )
        return

    if is_admin(user_id) and user_data.get("admin_state"):
        admin_state = user_data["admin_state"]
        if admin_state["action"] == "uber_quote":
            order = DATA["orders"].get(admin_state["order_id"])
            if not order or order.get("order_kind") != "ubereats":
                user_data["admin_state"] = None
                save_data()
                await update.message.reply_text("❌ Commande Uber Eats introuvable.")
                return
            try:
                quote_amount = float(text.replace(",", "."))
            except ValueError:
                await update.message.reply_text("❌ Montant invalide. Exemple : 18.50")
                return
            if quote_amount <= 0:
                await update.message.reply_text("❌ Le montant doit etre superieur a 0.")
                return
            order["total"] = round(quote_amount, 2)
            order["status"] = "awaiting_proof"
            order["expires_at"] = None
            user_data["admin_state"] = None
            client_data = ensure_user(order["user_id"])
            client_data["awaiting_order_id"] = admin_state["order_id"]
            save_data()
            await context.bot.send_message(
                order["user_id"],
                (
                    f"🛵 Commande Uber Eats {admin_state['order_id']}\n\n"
                    f"💰 Total a regler : {fmt_price(float(order['total']))}\n\n"
                    "✨ Choisis le moyen de paiement qui t'arrange.\n"
                    "Le delai commencera au moment ou tu selectionnes ton moyen de paiement.\n\n"
                    "⏳ Tu auras ensuite 8 minutes pour finaliser."
                ),
                reply_markup=checkout_methods_menu(float(client_data["balance"]), float(order["total"])),
            )
            await update.message.reply_text(
                f"✅ Montant envoye au client pour la commande {admin_state['order_id']} : {fmt_price(float(order['total']))}",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔎 Ouvrir la commande", callback_data=f"admin:order:{admin_state['order_id']}")]]),
            )
            return
        if admin_state["action"] == "osint_quote":
            order = DATA["orders"].get(admin_state["order_id"])
            if not order or order.get("order_kind") != "osint":
                user_data["admin_state"] = None
                save_data()
                await update.message.reply_text("❌ Demande OSINT introuvable.")
                return
            try:
                quote_amount = float(text.replace(",", "."))
            except ValueError:
                await update.message.reply_text("❌ Montant invalide. Exemple : 8.50")
                return
            if quote_amount <= 0:
                await update.message.reply_text("❌ Le montant doit etre superieur a 0.")
                return
            order["total"] = round(quote_amount, 2)
            order["status"] = "awaiting_proof"
            order["expires_at"] = None
            user_data["admin_state"] = None
            client_data = ensure_user(order["user_id"])
            client_data["awaiting_order_id"] = admin_state["order_id"]
            save_data()
            await context.bot.send_message(
                order["user_id"],
                (
                    f"🕵️ Recherche OSINT {admin_state['order_id']}\n\n"
                    f"💰 Total a regler : {fmt_price(float(order['total']))}\n\n"
                    "✨ Choisis le moyen de paiement qui t'arrange.\n"
                    "Le delai commencera au moment ou tu selectionnes ton moyen de paiement.\n\n"
                    "⏳ Tu auras ensuite 8 minutes pour finaliser."
                ),
                reply_markup=checkout_methods_menu(float(client_data["balance"]), float(order["total"])),
            )
            await update.message.reply_text(
                f"✅ Montant envoye au client pour la demande {admin_state['order_id']} : {fmt_price(float(order['total']))}",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔎 Ouvrir la commande", callback_data=f"admin:order:{admin_state['order_id']}")]]),
            )
            return
        if admin_state["action"] == "setprice":
            product = get_product(admin_state["product_id"])
            try:
                product["price"] = float(text.replace(",", "."))
            except ValueError:
                await update.message.reply_text("❌ Prix invalide. Exemple : 5.5")
                return
            user_data["admin_state"] = None
            save_data()
            await update.message.reply_text(f"✅ Prix change pour {product['name']}.")
            return
        if admin_state["action"] == "setname":
            product = get_product(admin_state["product_id"])
            if not product:
                user_data["admin_state"] = None
                save_data()
                await update.message.reply_text("❌ Produit introuvable.")
                return
            product["name"] = text
            user_data["admin_state"] = None
            save_data()
            await update.message.reply_text(f"✅ Nom mis a jour : {product['name']}.")
            return
        if admin_state["action"] == "staff_add":
            target_id = text.strip()
            if not target_id.isdigit():
                await update.message.reply_text("❌ ID invalide.")
                return
            if str(target_id) == str(ADMIN_ID):
                await update.message.reply_text("❌ Cet ID correspond deja au proprietaire du bot.")
                return
            support_admins = {str(value) for value in DATA.get("support_admins", [])}
            support_admins.add(str(target_id))
            DATA["support_admins"] = sorted(support_admins, key=int)
            user_data["admin_state"] = None
            save_data()
            await update.message.reply_text(
                f"✅ Admin support ajoute : {target_id}",
                reply_markup=admin_staff_menu(),
            )
            try:
                await context.bot.send_message(
                    int(target_id),
                    "🛠️ Tu as ete ajoute comme admin support.\n\nTu peux gerer les tickets support et le ON/OFF de la boutique.",
                    reply_markup=support_admin_menu(),
                )
            except Exception:
                pass
            return
        if admin_state["action"] == "addbalance":
            parts = text.replace(",", ".").split()
            if len(parts) != 2:
                await update.message.reply_text("❌ Format invalide. Utilise : ID montant")
                return
            target_id, amount_text = parts
            if not target_id.isdigit():
                await update.message.reply_text("❌ ID invalide.")
                return
            try:
                amount = float(amount_text)
            except ValueError:
                await update.message.reply_text("❌ Montant invalide.")
                return
            if amount <= 0:
                await update.message.reply_text("❌ Le montant doit etre superieur a 0.")
                return
            target_user = ensure_user(int(target_id))
            mode = admin_state.get("mode", "add")
            current_balance = float(target_user["balance"])
            if mode == "remove" and amount > current_balance:
                await update.message.reply_text(
                    f"❌ Solde insuffisant.\n\nSolde actuel de {target_id} : {fmt_price(current_balance)}"
                )
                return
            if mode == "remove":
                target_user["balance"] = round(current_balance - amount, 2)
            else:
                target_user["balance"] = round(current_balance + amount, 2)
            delta = amount if mode != "remove" else -amount
            reason = "Ajout manuel admin" if mode != "remove" else "Retrait manuel admin"
            log_balance_event(int(target_id), delta, reason, f"admin:{user_id}")
            user_data["admin_state"] = None
            save_data()
            action_text = "ajoute(s)" if mode != "remove" else "retire(s)"
            await update.message.reply_text(
                f"✅ {fmt_price(amount)} {action_text} au solde de {target_id}.\n\nNouveau solde : {fmt_price(float(target_user['balance']))}",
                reply_markup=admin_menu(),
            )
            try:
                client_text = (
                    f"💼 Ton solde a ete credite manuellement de {fmt_price(amount)}.\n\nNouveau solde : {fmt_price(float(target_user['balance']))}"
                    if mode != "remove"
                    else f"💼 {fmt_price(amount)} ont ete retires manuellement de ton solde.\n\nNouveau solde : {fmt_price(float(target_user['balance']))}"
                )
                await context.bot.send_message(
                    int(target_id),
                    client_text,
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Retour a l'accueil", callback_data="menu:start")]]),
                )
            except Exception:
                pass
            return
        if admin_state["action"] == "addkeys":
            values = [line.strip() for line in text.splitlines() if line.strip()]
            DATA["stock"].setdefault(admin_state["product_id"], []).extend(values)
            user_data["admin_state"] = None
            save_data()
            await update.message.reply_text(f"✅ {len(values)} cle(s) ajoutee(s).")
            return
        if admin_state["action"] == "deliver":
            order = DATA["orders"].get(admin_state["order_id"])
            if order:
                current_product = current_manual_delivery(order)
                delivery_text = (
                    "🎉 Voici ta commande.\n\n"
                    f"{text}\n\n"
                    "⏱️ Garantie 15 minutes en cas de probleme.\n"
                    "🎥 Preuve video obligatoire si souci.\n"
                    "📍 Pense a bien garder le numero / les infos utiles de la commande.\n"
                    "🆘 Aide : cree un ticket report depuis l'accueil"
                )
                await context.bot.send_message(
                    order["user_id"],
                    delivery_text,
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [InlineKeyboardButton("🏠 Retour a l'accueil", callback_data="menu:start")],
                            [InlineKeyboardButton("🆘 Creer un ticket", callback_data="ticket:new")],
                        ]
                    ),
                )
                if order.get("manual_delivery_queue"):
                    sent_product_id = order["manual_delivery_queue"].pop(0)
                    order.setdefault("manual_delivery_sent", []).append(sent_product_id)
                next_product = current_manual_delivery(order)
                if next_product:
                    order["status"] = "awaiting_delivery"
                    user_data["admin_state"] = {"action": "deliver", "order_id": admin_state["order_id"]}
                    save_data()
                    current_name = current_product["name"] if current_product else "cet article"
                    await update.message.reply_text(f"✅ Livraison texte envoyee pour {current_name}.\n\nEnvoie maintenant : {next_product['name']}.")
                    return
                order["status"] = "delivered"
                user_data["admin_state"] = None
                save_data()
                await update.message.reply_text("✅ Livraison texte envoyee au client.")
            return
        if admin_state["action"] == "uber_link":
            order = DATA["orders"].get(admin_state["order_id"])
            if not order:
                user_data["admin_state"] = None
                save_data()
                await update.message.reply_text("❌ Commande introuvable.")
                return
            await context.bot.send_message(
                order["user_id"],
                (
                    "🛵 Ta commande Uber Eats est bien lancee.\n\n"
                    f"🔗 Lien de suivi : {text}\n\n"
                    "📲 Garde bien ce lien pour suivre la livraison.\n"
                    "🆘 Si besoin, tu peux toujours creer un ticket depuis l'accueil."
                ),
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("🏠 Retour a l'accueil", callback_data="menu:start")],
                        [InlineKeyboardButton("🆘 Creer un ticket", callback_data="ticket:new")],
                    ]
                ),
            )
            order["status"] = "delivered"
            user_data["admin_state"] = None
            save_data()
            await update.message.reply_text("✅ Lien de suivi Uber Eats envoye au client.")
            return
        if admin_state["action"] == "spotify_result":
            order = DATA["orders"].get(admin_state["order_id"])
            if not order or order.get("status") != "awaiting_delivery":
                user_data["admin_state"] = None
                save_data()
                await update.message.reply_text("❌ Cette commande Spotify n'est plus en cours d'envoi.")
                return
            await context.bot.send_message(
                order["user_id"],
                (
                    "🎧 Spotify Premium\n\n"
                    f"{text}\n\n"
                    "⚡ La plupart des mises a niveau sont effectuees en 5 a 10 minutes,\n"
                    "mais cela peut parfois prendre jusqu'a 24h.\n"
                    "🆘 En cas de souci, cree un ticket SAV depuis l'accueil."
                ),
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("🏠 Retour a l'accueil", callback_data="menu:start")],
                        [InlineKeyboardButton("🆘 Creer un ticket", callback_data="ticket:new")],
                    ]
                ),
            )
            order["status"] = "delivered"
            user_data["admin_state"] = None
            save_data()
            await update.message.reply_text("✅ Acces Spotify envoye au client.")
            return
        if admin_state["action"] == "boost_result":
            order = DATA["orders"].get(admin_state["order_id"])
            if not order or order.get("status") != "awaiting_delivery":
                user_data["admin_state"] = None
                save_data()
                await update.message.reply_text("❌ Cette commande boost n'est plus en cours d'envoi.")
                return
            await context.bot.send_message(
                order["user_id"],
                (
                    f"🚀 Mise a jour pour ta commande {fastfood_order_hint(order)}\n\n"
                    f"{text}\n\n"
                    "📦 Livraison progressive\n"
                    "⏱️ Delai maximum : 24h\n\n"
                    "🆘 Si besoin, tu peux creer un ticket depuis l'accueil."
                ),
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("🏠 Retour a l'accueil", callback_data="menu:start")],
                        [InlineKeyboardButton("🆘 Creer un ticket", callback_data="ticket:new")],
                    ]
                ),
            )
            order["status"] = "delivered"
            user_data["admin_state"] = None
            save_data()
            await update.message.reply_text("✅ Suivi boost envoye au client.")
            return
        if admin_state["action"] == "osint_result":
            order = DATA["orders"].get(admin_state["order_id"])
            if not order or order.get("status") != "awaiting_delivery":
                user_data["admin_state"] = None
                save_data()
                await update.message.reply_text("❌ Cette commande OSINT n'est plus en cours d'envoi.")
                return
            append_osint_result_chunk(
                order,
                {
                    "type": "text",
                    "text": text,
                },
            )
            return
        if admin_state["action"] == "ticket_reply":
            ticket = DATA["tickets"].get(admin_state["ticket_id"])
            if not ticket:
                user_data["admin_state"] = None
                save_data()
                await update.message.reply_text("❌ Ticket introuvable.")
                return
            ticket["messages"].append({"from": "admin", "text": text})
            ticket["status"] = "open"
            user_data["admin_state"] = None
            save_data()
            await context.bot.send_message(
                ticket["user_id"],
                f"💬 Reponse a ton ticket {admin_state['ticket_id']} :\n\n{text}",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💬 Repondre au ticket", callback_data=f"ticket:reply:{admin_state['ticket_id']}")]]),
            )
            await update.message.reply_text(
                f"✅ Reponse envoyee pour le ticket {admin_state['ticket_id']}.",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("🔎 Ouvrir le ticket", callback_data=f"admin:ticket:{admin_state['ticket_id']}")],
                        [InlineKeyboardButton("🟠 Mettre en attente", callback_data=f"admin:ticketpending:{admin_state['ticket_id']}")],
                        [InlineKeyboardButton("✅ Fermer le ticket", callback_data=f"admin:ticketclose:{admin_state['ticket_id']}")],
                        [InlineKeyboardButton("🏠 Accueil", callback_data="admin:home")],
                    ]
                ),
            )
            return

    await update.message.reply_text("👉 Utilise /start pour ouvrir la boutique.")


def main():
    if TOKEN == "PUT_YOUR_BOT_TOKEN_HERE":
        raise RuntimeError("Configure BOT_TOKEN avant de lancer le bot.")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_command))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    logging.info("Bot lance")
    app.run_polling()


if __name__ == "__main__":
    main()
