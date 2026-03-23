from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.ext import MessageHandler, filters

TOKEN = "8612591465:AAEffMxCTf0wc9DkXzwbcG_K6ngEwnq2kfk"
ADMIN_ID = 8567294409

users = {}

products = {
    "50-74": 3,
    "75-99": 4.5,
    "100-124": 6,
    "125-149": 7,
    "150-174": 8,
    "175-199": 9,
    "200-224": 10,
    "225-249": 14,
    "250-274": 15,
    "275-299": 16
}

# stock simple (comme avant)
stock = {key: [] for key in products}

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    username = f"@{user.username}" if user.username else user.first_name

    if user_id not in users:
        users[user_id] = {"solde": 0, "panier": []}

    keyboard = [
        [InlineKeyboardButton("🛒 Boutique", callback_data="shop")],
        [InlineKeyboardButton("💰 Solde", callback_data="balance")],
        [InlineKeyboardButton("📦 Panier", callback_data="cart")]
    ]

    with open("logo.png", "rb") as photo:
        await update.message.reply_photo(
            photo=photo,
            caption=f"""🔥 Bienvenue sur O'Market !

👋 Salut {username}

🆔 ID : {user_id}
💰 Solde : {users[user_id]['solde']}€

⚡ Propulsé par Shop2Tech""",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# ================= BUTTON =================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if user_id not in users:
        users[user_id] = {"solde": 0, "panier": []}

    # SHOP
    if query.data == "shop":
        keyboard = [
            [InlineKeyboardButton("🍔 Fast Food", callback_data="fastfood")],
            [InlineKeyboardButton("🏠 Retour", callback_data="start")]
        ]
        await query.message.reply_text("🛒 Choisis une catégorie :", reply_markup=InlineKeyboardMarkup(keyboard))

    # FASTFOOD
    elif query.data == "fastfood":
        keyboard = [
            [InlineKeyboardButton("🍔 McDo", callback_data="mcdo")],
            [InlineKeyboardButton("⬅️ Retour", callback_data="shop")]
        ]
        await query.message.reply_text("🍔 Fast Food :", reply_markup=InlineKeyboardMarkup(keyboard))

    # MCDO
    elif query.data == "mcdo":
        keyboard = []
        for pts, price in products.items():
            keyboard.append([
                InlineKeyboardButton(f"{pts} pts - {price}€ (📦 {len(stock[pts])})", callback_data=f"add_{pts}")
            ])

        keyboard.append([
            InlineKeyboardButton("🛒 Voir mon panier", callback_data="cart"),
            InlineKeyboardButton("🏠 Menu principal", callback_data="start")
        ])

        await query.message.reply_text("🍔 McDo :", reply_markup=InlineKeyboardMarkup(keyboard))

    # ADD PANIER
    elif query.data.startswith("add_"):
        prod = query.data.replace("add_", "")
        prix = products[prod]

        if len(stock[prod]) <= 0:
            await query.message.reply_text("❌ Rupture de stock")
            return

        users[user_id]["panier"].append((prod, prix))

        await query.message.reply_text("✅ Ajouté au panier")

    # PANIER
    elif query.data == "cart":
        panier = users[user_id]["panier"]

        if not panier:
            await query.message.reply_text("🛒 Panier vide")
            return

        text = "🛒 Panier :\n\n"
        total = 0

        for i, (p, prix) in enumerate(panier, 1):
            text += f"{i}. {p} - {prix}€\n"
            total += prix

        text += f"\n💰 Total : {total}€"

        keyboard = [
            [InlineKeyboardButton("💳 Payer", callback_data="pay")],
            [InlineKeyboardButton("⬅️ Retour", callback_data="fastfood")]
        ]

        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    # PAIEMENT
    elif query.data == "pay":
        panier = users[user_id]["panier"]

        total = sum(p[1] for p in panier)

        await query.message.reply_text(
            f"""💳 Paiement

💰 Total : {total}€

👉 https://www.paypal.me/crz843026

⚠️ AMIS / PROCHES
❌ PAS DE NOTE""",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📨 J'ai payé", callback_data="paid")]
            ])
        )

    # JAI PAYÉ
    elif query.data == "paid":
        users[user_id]["attente_preuve"] = True
        await query.message.reply_text("📸 Envoie ta preuve")

    # MENU PRINCIPAL FIX
    elif query.data == "start":
        user = query.from_user
        username = f"@{user.username}" if user.username else user.first_name

        keyboard = [
            [InlineKeyboardButton("🛒 Boutique", callback_data="shop")],
            [InlineKeyboardButton("💰 Solde", callback_data="balance")],
            [InlineKeyboardButton("📦 Panier", callback_data="cart")]
        ]

        with open("logo.png", "rb") as photo:
            await query.message.reply_photo(
                photo=photo,
                caption=f"""🔥 Bienvenue sur O'Market !

👋 Salut {username}

🆔 ID : {user.id}
💰 Solde : {users[user.id]['solde']}€

⚡ Propulsé par Shop2Tech""",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

    # VALIDATION ADMIN
    elif query.data.startswith("valider_"):
        if query.from_user.id != ADMIN_ID:
            return

        uid = int(query.data.split("_")[1])

        panier = users[uid]["panier"]

        for prod, prix in panier:
            if stock[prod]:
                code = stock[prod].pop(0)
                await context.bot.send_message(uid, f"🎁 Code {prod} : {code}")

        users[uid]["panier"] = []

        await query.message.reply_text(f"✅ Commande validée {uid}")

# ================= PHOTO =================
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not users.get(user_id, {}).get("attente_preuve"):
        return

    photo = update.message.photo[-1].file_id
    panier = users[user_id]["panier"]

    details = ""
    total = 0

    for p, prix in panier:
        details += f"{p} - {prix}€\n"
        total += prix

    await context.bot.send_photo(
        ADMIN_ID,
        photo=photo,
        caption=f"""📦 Commande

ID : {user_id}

{details}

💰 {total}€""",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(f"✅ Valider {user_id}", callback_data=f"valider_{user_id}")]
        ])
    )

    users[user_id]["attente_preuve"] = False
    await update.message.reply_text("✅ Envoyé à l'admin")

# ================= ADDCODE =================
async def addcode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if len(context.args) < 3:
        await update.message.reply_text("❌ /addcode mcdo 75-99 CODE")
        return

    prod = context.args[1]
    code = context.args[2]

    if prod not in stock:
        await update.message.reply_text("❌ Produit invalide")
        return

    stock[prod].append(code)

    await update.message.reply_text(f"✅ Ajouté {prod}")

# ================= RUN =================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("addcode", addcode))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.PHOTO, photo_handler))

print("🔥 BOT LANCÉ")
app.run_polling()