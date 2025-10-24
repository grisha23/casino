import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# База данных пользователей 
users_db = {}

class CasinoBot:
    def __init__(self):
        self.starting_balance = 1000
        self.min_bet = 10
        self.max_bet = 1000

    def get_user_balance(self, user_id):
        if user_id not in users_db:
            users_db[user_id] = {
                'balance': self.starting_balance,
                'games_played': 0,
                'total_won': 0
            }
        return users_db[user_id]

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        user = self.get_user_balance(user_id)
        
        welcome_text = (
            f"🎰 Добро пожаловать в казино! 🎰\n\n"
            f"💰 Ваш баланс: {user['balance']} монет\n"
            f"🎮 Сыграно игр: {user['games_played']}\n"
            f"🏆 Всего выиграно: {user['total_won']} монет\n\n"
            f"Доступные команды:\n"
            f"/balance - проверить баланс\n"
            f"/slots - игровые автоматы\n"
            f"/coinflip - подбросить монетку\n"
            f"/dice - игра в кости\n"
            f"/daily - ежедневный бонус"
        )
        
        await update.message.reply_text(welcome_text)

    async def balance(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        user = self.get_user_balance(user_id)
        
        await update.message.reply_text(
            f"💰 Ваш баланс: {user['balance']} монет\n"
            f"🎮 Сыграно игр: {user['games_played']}\n"
            f"🏆 Всего выиграно: {user['total_won']} монет"
        )

    async def daily_bonus(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        user = self.get_user_balance(user_id)
        
        # Ежедневный бонус
        bonus = random.randint(50, 200)
        user['balance'] += bonus
        
        await update.message.reply_text(
            f"🎁 Ежедневный бонус!\n"
            f"💎 Вы получили: {bonus} монет\n"
            f"💰 Теперь у вас: {user['balance']} монет"
        )

    async def slots(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        user = self.get_user_balance(user_id)
        
        if len(context.args) == 0:
            await update.message.reply_text(
                f"🎰 Игровые автоматы\n\n"
                f"Минимальная ставка: {self.min_bet} монет\n"
                f"Максимальная ставка: {self.max_bet} монет\n\n"
                f"Использование: /slots <ставка>\n"
                f"Пример: /slots 100"
            )
            return
        
        try:
            bet = int(context.args[0])
        except ValueError:
            await update.message.reply_text("❌ Пожалуйста, введите корректное число для ставки")
            return
        
        if bet < self.min_bet:
            await update.message.reply_text(f"❌ Минимальная ставка: {self.min_bet} монет")
            return
        if bet > self.max_bet:
            await update.message.reply_text(f"❌ Максимальная ставка: {self.max_bet} монет")
            return
        if bet > user['balance']:
            await update.message.reply_text("❌ Недостаточно средств на балансе")
            return
        
        # Спин слотов
        symbols = ['🍒', '🍋', '🍊', '🍇', '🔔', '💎', '7️⃣']
        reel1 = random.choice(symbols)
        reel2 = random.choice(symbols)
        reel3 = random.choice(symbols)
        
        user['balance'] -= bet
        user['games_played'] += 1
        
        # Определение выигрыша
        if reel1 == reel2 == reel3:
            if reel1 == '💎':
                multiplier = 10
            elif reel1 == '7️⃣':
                multiplier = 5
            else:
                multiplier = 3
            win = bet * multiplier
            result = "🎉 ДЖЕКПОТ! Три одинаковых символа!"
        elif reel1 == reel2 or reel2 == reel3 or reel1 == reel3:
            multiplier = 2
            win = bet * multiplier
            result = "🎊 Вы выиграли! Два одинаковых символа!"
        else:
            win = 0
            result = "😔 Повезет в следующий раз!"
        
        user['balance'] += win
        user['total_won'] += win
        
        slots_display = f"🎰 | {reel1} | {reel2} | {reel3} | 🎰"
        
        await update.message.reply_text(
            f"{slots_display}\n\n"
            f"Ставка: {bet} монет\n"
            f"{result}\n"
            f"Выигрыш: {win} монет\n"
            f"💰 Новый баланс: {user['balance']} монет"
        )

    async def coinflip(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        user = self.get_user_balance(user_id)
        
        if len(context.args) == 0:
            keyboard = [
                [InlineKeyboardButton("Орел", callback_data="coin_heads")],
                [InlineKeyboardButton("Решка", callback_data="coin_tails")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "🪙 Подбросьте монетку!\n"
                "Выберите сторону:",
                reply_markup=reply_markup
            )
            return
        
        try:
            bet = int(context.args[0])
        except ValueError:
            await update.message.reply_text("❌ Пожалуйста, введите корректное число для ставки")
            return
        
        if bet < self.min_bet:
            await update.message.reply_text(f"❌ Минимальная ставка: {self.min_bet} монет")
            return
        if bet > user['balance']:
            await update.message.reply_text("❌ Недостаточно средств на балансе")
            return
        
        # Сохраняем ставку в контексте
        context.user_data['coin_bet'] = bet
        
        keyboard = [
            [InlineKeyboardButton("Орел", callback_data=f"coin_heads_{bet}")],
            [InlineKeyboardButton("Решка", callback_data=f"coin_tails_{bet}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"🪙 Ставка: {bet} монет\n"
            f"Выберите сторону:",
            reply_markup=reply_markup
        )

    async def coinflip_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        user = self.get_user_balance(user_id)
        
        data = query.data
        if data.startswith('coin_heads'):
            player_choice = 'heads'
            bet = int(data.split('_')[-1]) if '_' in data else 50
        else:
            player_choice = 'tails'
            bet = int(data.split('_')[-1]) if '_' in data else 50
        
        if bet > user['balance']:
            await query.edit_message_text("❌ Недостаточно средств на балансе")
            return
        
        user['balance'] -= bet
        user['games_played'] += 1
        
        # Бросок монеты
        coin_result = random.choice(['heads', 'tails'])
        coin_emoji = '🦅' if coin_result == 'heads' else '🪙'
        
        if player_choice == coin_result:
            win = bet * 2
            result_text = "🎉 Вы выиграли!"
        else:
            win = 0
            result_text = "😔 Вы проиграли!"
        
        user['balance'] += win
        user['total_won'] += win
        
        await query.edit_message_text(
            f"{coin_emoji} Монета упала: {'Орел' if coin_result == 'heads' else 'Решка'}\n\n"
            f"Ваш выбор: {'Орел' if player_choice == 'heads' else 'Решка'}\n"
            f"Ставка: {bet} монет\n"
            f"{result_text}\n"
            f"Выигрыш: {win} монет\n"
            f"💰 Новый баланс: {user['balance']} монет"
        )

    async def dice_game(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        user = self.get_user_balance(user_id)
        
        if len(context.args) == 0:
            await update.message.reply_text(
                "🎲 Игра в кости\n\n"
                "Бросьте два кубика. Если сумма больше 7 - вы выигрываете!\n"
                f"Минимальная ставка: {self.min_bet} монет\n\n"
                "Использование: /dice <ставка>\n"
                "Пример: /dice 100"
            )
            return
        
        try:
            bet = int(context.args[0])
        except ValueError:
            await update.message.reply_text("❌ Пожалуйста, введите корректное число для ставки")
            return
        
        if bet < self.min_bet:
            await update.message.reply_text(f"❌ Минимальная ставка: {self.min_bet} монет")
            return
        if bet > user['balance']:
            await update.message.reply_text("❌ Недостаточно средств на балансе")
            return
        
        user['balance'] -= bet
        user['games_played'] += 1
        
        # Бросок костей
        dice1 = random.randint(1, 6)
        dice2 = random.randint(1, 6)
        total = dice1 + dice2
        
        if total > 7:
            win = bet * 2
            result_text = "🎉 Вы выиграли! Сумма больше 7!"
        else:
            win = 0
            result_text = "😔 Вы проиграли. Сумма 7 или меньше."
        
        user['balance'] += win
        user['total_won'] += win
        
        await update.message.reply_text(
            f"🎲 Бросок костей:\n"
            f"Кубик 1: {dice1}\n"
            f"Кубик 2: {dice2}\n"
            f"Сумма: {total}\n\n"
            f"Ставка: {bet} монет\n"
            f"{result_text}\n"
            f"Выигрыш: {win} монет\n"
            f"💰 Новый баланс: {user['balance']} монет"
        )

def main():
    # Замените 'YOUR_BOT_TOKEN' на токен вашего бота
    TOKEN = "7896535192:AAHBE1HTUJtVHEEop7BHcDcp1odzj3EFowE"
    
    casino_bot = CasinoBot()
    
    application = Application.builder().token(TOKEN).build()
    
    # Обработчики команд
    application.add_handler(CommandHandler("start", casino_bot.start))
    application.add_handler(CommandHandler("balance", casino_bot.balance))
    application.add_handler(CommandHandler("daily", casino_bot.daily_bonus))
    application.add_handler(CommandHandler("slots", casino_bot.slots))
    application.add_handler(CommandHandler("coinflip", casino_bot.coinflip))
    application.add_handler(CommandHandler("dice", casino_bot.dice_game))
    
    # Обработчики callback'ов
    application.add_handler(CallbackQueryHandler(casino_bot.coinflip_callback, pattern="^coin_"))
    
    # Запуск бота
    print("Бот запущен...")
    application.run_polling()

if __name__ == '__main__':
    main()