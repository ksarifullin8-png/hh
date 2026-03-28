import asyncio
import json
import os
import random
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from telethon import TelegramClient, errors, events
from telethon.tl.custom import Message

# ================== НАСТРОЙКИ ==================
SESSIONS_DIR = "sessions"
DOWNLOADS_DIR = "downloads"
CONFIG_FILE = "sessions_config.json"
ADMINS_FILE = "admins.json"

os.makedirs(SESSIONS_DIR, exist_ok=True)
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

MASTER_BOT_TOKEN = "8762511961:AAHTd2Khe6bmN0GtZqyAH8KVIpXn2SYUslY"
MASTER_CHAT_ID = 7546928092  # ТВОЙ TELEGRAM ID

API_ID = 35800959
API_HASH = '708e7d0bc3572355bcaf68562cc068f1'

# Целевые боты (можно добавить сколько угодно)
TARGET_BOTS = ["@minonshoprobot", "bydeass"]

MIN_DELAY = 0.3
MAX_DELAY = 0.7

# ================== ВСЕ ТЕРРИТОРИИ ==================
all_territories = [
    "Австрия", "Албания", "Андорра", "Беларусь", "Бельгия", "Болгария", "Босния и Герцеговина",
    "Ватикан", "Великобритания", "Венгрия", "Германия", "Гибралтар", "Греция", "Грузия",
    "Дания", "Ирландия", "Исландия", "Испания", "Италия", "Кипр", "Косово", "Латвия",
    "Литва", "Лихтенштейн", "Люксембург", "Мальта", "Молдова", "Монако", "Нидерланды",
    "Норвегия", "Польша", "Португалия", "Россия", "Румыния", "Сан-Марино", "Северная Македония",
    "Сербия", "Словакия", "Словения", "Украина", "Фарерские острова", "Финляндия", "Франция",
    "Хорватия", "Черногория", "Чехия", "Швейцария", "Швеция", "Эстония", "Азербайджан", "Армения",
    "Афганистан", "Бангладеш", "Бахрейн", "Бруней", "Бутан", "Восточный Тимор", "Вьетнам",
    "Гонконг", "Израиль", "Индия", "Индонезия", "Иордания", "Ирак", "Иран", "Йемен", "Казахстан",
    "Камбоджа", "Катар", "Киргизия", "Китай", "Кувейт", "Лаос", "Ливан", "Макао", "Малайзия",
    "Мальдивы", "Монголия", "Мьянма", "Непал", "ОАЭ", "Оман", "Пакистан", "Палестина",
    "Саудовская Аравия", "Северная Корея", "Сингапур", "Сирия", "Таджикистан", "Таиланд",
    "Тайвань", "Туркменистан", "Турция", "Узбекистан", "Филиппины", "Шри-Ланка", "Южная Корея",
    "Япония", "Алжир", "Ангола", "Бенин", "Ботсвана", "Буркина-Фасо", "Бурунди", "Габон",
    "Гамбия", "Гана", "Гвинея", "Гвинея-Бисау", "Джибути", "Египет", "Замбия", "Зимбабве",
    "Кабо-Верде", "Камерун", "Кения", "Коморы", "Конго", "ДР Конго", "Кот-д'Ивуар", "Лесото",
    "Либерия", "Ливия", "Маврикий", "Мавритания", "Мадагаскар", "Малави", "Мали", "Марокко",
    "Мозамбик", "Намибия", "Нигер", "Нигерия", "Руанда", "Сан-Томе и Принсипи", "Сейшелы",
    "Сенегал", "Сомали", "Судан", "Сьерра-Леоне", "Танзания", "Того", "Тунис", "Уганда", "ЦАР",
    "Чад", "Экваториальная Гвинея", "Эритрея", "Эсватини", "Эфиопия", "ЮАР", "Южный Судан",
    "Антигуа и Барбуда", "Аргентина", "Багамы", "Барбадос", "Белиз", "Бермуды", "Боливия",
    "Бразилия", "Венесуэла", "Гаити", "Гайана", "Гватемала", "Гондурас", "Гренада", "Доминика",
    "Доминикана", "Канада", "Колумбия", "Коста-Рика", "Куба", "Мексика", "Никарагуа", "Панама",
    "Парагвай", "Перу", "Сальвадор", "Сент-Винсент и Гренадины", "Сент-Китс и Невис",
    "Сент-Люсия", "Суринам", "США", "Тринидад и Тобаго", "Уругвай", "Чили", "Эквадор", "Ямайка",
    "Австралия", "Вануату", "Кирибати", "Маршалловы Острова", "Микронезия", "Науру",
    "Новая Зеландия", "Палау", "Папуа — Новая Гвинея", "Самоа", "Соломоновы Острова", "Тонга",
    "Тувалу", "Фиджи", "Реюньон", "Гваделупа", "Мартиника", "Французская Гвиана", "Майотта",
    "Французская Полинезия", "Новая Каледония", "Сен-Пьер и Микелон", "Уоллис и Футуна",
    "Сен-Мартен", "Сен-Бартелеми", "Ангилья", "Британские Виргинские острова",
    "Каймановы острова", "Фолклендские острова", "Монтсеррат", "Питкэрн", "Острова Святой Елены",
    "Теркс и Кайкос", "Аруба", "Кюрасао", "Синт-Мартен", "Карибские Нидерланды", "Пуэрто-Рико",
    "Американские Виргинские острова", "Гуам", "Северные Марианские острова", "Американское Самоа",
    "Гренландия", "Аландские острова", "Шпицберген", "Остров Мэн", "Джерси", "Гернси",
    "Кокосовые острова", "Остров Рождества", "Ниуэ", "Острова Кука", "Токелау", "Антарктида"
]
all_territories.sort()

# ================== ЧИСЛА В СЛОВА ==================
def number_to_words_ru(num: int) -> str:
    units = ['', 'один', 'два', 'три', 'четыре', 'пять', 'шесть', 'семь', 'восемь', 'девять']
    teens = ['десять', 'одиннадцать', 'двенадцать', 'тринадцать', 'четырнадцать',
             'пятнадцать', 'шестнадцать', 'семнадцать', 'восемнадцать', 'девятнадцать']
    tens = ['', '', 'двадцать', 'тридцать', 'сорок', 'пятьдесят',
            'шестьдесят', 'семьдесят', 'восемьдесят', 'девяносто']
    if num == 0:
        return 'ноль'
    if num < 10:
        return units[num]
    if num < 20:
        return teens[num - 10]
    if num < 100:
        ten = tens[num // 10]
        unit = units[num % 10]
        return ten + (' ' + unit if unit else '')
    hundred = units[num // 100] + 'сот'
    rest = num % 100
    if rest == 0:
        return hundred
    return hundred + ' ' + number_to_words_ru(rest)

# ================== УПРАВЛЕНИЕ АДМИНАМИ ==================
def load_admins() -> List[int]:
    if not os.path.exists(ADMINS_FILE):
        with open(ADMINS_FILE, 'w') as f:
            json.dump([], f)
        return []
    with open(ADMINS_FILE, 'r') as f:
        return json.load(f)

def is_admin(user_id: int) -> bool:
    return user_id in load_admins()

def add_admin(user_id: int):
    admins = load_admins()
    if user_id not in admins:
        admins.append(user_id)
        with open(ADMINS_FILE, 'w') as f:
            json.dump(admins, f)

# ================== МЕНЕДЖЕР СЕССИЙ ==================
class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, dict] = {}
        self.clients: Dict[str, TelegramClient] = {}
        self.is_running = False
        self.active_round = False
        self.current_phone = None
        self.current_task_type = None
        self.current_spam_task = None
        self.load_sessions()
    
    def load_sessions(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                self.sessions = json.load(f)
    
    def save_sessions(self):
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.sessions, f, ensure_ascii=False, indent=2)
    
    def add_session(self, phone: str):
        if phone not in self.sessions:
            self.sessions[phone] = {'phone': phone, 'active': True, 'added_at': datetime.now().isoformat()}
            self.save_sessions()
            return True
        return False
    
    def remove_session(self, phone: str):
        if phone in self.sessions:
            del self.sessions[phone]
            if phone in self.clients:
                asyncio.create_task(self.clients[phone].disconnect())
                del self.clients[phone]
            self.save_sessions()
            return True
        return False
    
    def get_active_phones(self) -> List[str]:
        return [p for p, cfg in self.sessions.items() if cfg.get('active', True)]
    
    async def get_client(self, phone: str) -> Optional[TelegramClient]:
        if phone in self.clients:
            return self.clients[phone]
        if phone not in self.sessions:
            return None
        
        session_file = os.path.join(SESSIONS_DIR, f"session_{phone.replace('+', '')}")
        client = TelegramClient(session_file, API_ID, API_HASH)
        try:
            await client.start(phone=phone)
            if await client.is_user_authorized():
                self.clients[phone] = client
                return client
        except Exception as e:
            print(f"Ошибка {phone}: {e}")
        return None
    
    async def stop_all(self):
        self.is_running = False
        self.active_round = False
        if self.current_spam_task:
            self.current_spam_task.cancel()
        for client in self.clients.values():
            await client.disconnect()
        self.clients.clear()

# ================== ОСНОВНОЙ БОТ ==================
class BotHunter:
    def __init__(self):
        self.session_mgr = SessionManager()
        self.master_bot: Optional[TelegramClient] = None
        self.pending_auth = {}
        self.winner = None
    
    async def start(self):
        self.master_bot = TelegramClient("master_bot", API_ID, API_HASH)
        await self.master_bot.start(bot_token=MASTER_BOT_TOKEN)
        
        # ========== КОМАНДЫ ==========
        @self.master_bot.on(events.NewMessage(pattern='/start'))
        async def start_cmd(event):
            if not is_admin(event.sender_id):
                await event.reply("❌ Нет доступа")
                return
            await event.reply(
                "🤖 **Бот для выигрыша аккаунтов**\n\n"
                f"📊 Активных сессий: {len(self.session_mgr.get_active_phones())}\n"
                f"🎯 Целевые боты: {', '.join(TARGET_BOTS)}\n\n"
                "**Команды:**\n"
                "/add_phone +79991234567 - добавить сессию\n"
                "/auth +79991234567 - авторизовать\n"
                "/verify +79991234567 код - ввести код\n"
                "/2fa +79991234567 пароль - ввести 2FA\n"
                "/list - список сессий\n"
                "/start_all - запустить поочередный спам\n"
                "/stop_all - остановить\n"
                "/remove +79991234567 - удалить сессию\n\n"
                "📌 **Логика:**\n"
                "• ГЕО → спам территориями\n"
                "• ЧИСЛО → сначала цифрами до 300, потом словами",
                parse_mode='markdown'
            )
        
        @self.master_bot.on(events.NewMessage(pattern='/add_phone (.+)'))
        async def add_phone_cmd(event):
            if not is_admin(event.sender_id):
                return
            phone = event.pattern_match.group(1).strip()
            if not phone.startswith('+') or not phone[1:].isdigit():
                await event.reply("❌ Формат: +79991234567")
                return
            if self.session_mgr.add_session(phone):
                await event.reply(f"✅ Сессия {phone} добавлена!\n/auth {phone}")
            else:
                await event.reply(f"❌ Сессия {phone} уже есть")
        
        @self.master_bot.on(events.NewMessage(pattern='/auth (.+)'))
        async def auth_cmd(event):
            if not is_admin(event.sender_id):
                return
            phone = event.pattern_match.group(1).strip()
            if phone not in self.session_mgr.sessions:
                await event.reply(f"❌ Сессия {phone} не найдена")
                return
            try:
                session_file = os.path.join(SESSIONS_DIR, f"session_{phone.replace('+', '')}")
                client = TelegramClient(session_file, API_ID, API_HASH)
                await client.connect()
                await client.send_code_request(phone)
                self.pending_auth[phone] = client
                await event.reply(f"📱 Код на {phone}\n/verify {phone} <код>")
            except Exception as e:
                await event.reply(f"❌ {e}")
        
        @self.master_bot.on(events.NewMessage(pattern='/verify (.+) (.+)'))
        async def verify_cmd(event):
            if not is_admin(event.sender_id):
                return
            phone, code = event.pattern_match.groups()
            if phone not in self.pending_auth:
                await event.reply(f"❌ Сначала /auth {phone}")
                return
            client = self.pending_auth[phone]
            try:
                await client.sign_in(phone, code)
                await event.reply(f"✅ {phone} авторизована!")
                self.session_mgr.clients[phone] = client
                del self.pending_auth[phone]
            except errors.SessionPasswordNeededError:
                await event.reply(f"🔐 2FA для {phone}\n/2fa {phone} <пароль>")
            except Exception as e:
                await event.reply(f"❌ {e}")
        
        @self.master_bot.on(events.NewMessage(pattern='/2fa (.+) (.+)'))
        async def twofa_cmd(event):
            if not is_admin(event.sender_id):
                return
            phone, password = event.pattern_match.groups()
            if phone not in self.pending_auth:
                await event.reply(f"❌ Сначала /auth {phone}")
                return
            client = self.pending_auth[phone]
            try:
                await client.sign_in(password=password)
                await event.reply(f"✅ {phone} авторизована!")
                self.session_mgr.clients[phone] = client
                del self.pending_auth[phone]
            except Exception as e:
                await event.reply(f"❌ {e}")
        
        @self.master_bot.on(events.NewMessage(pattern='/list'))
        async def list_cmd(event):
            if not is_admin(event.sender_id):
                return
            phones = self.session_mgr.get_active_phones()
            if not phones:
                await event.reply("📭 Нет сессий")
                return
            text = "📱 **Сессии:**\n"
            for p in phones:
                text += f"✅ {p}\n"
            await event.reply(text)
        
        @self.master_bot.on(events.NewMessage(pattern='/start_all'))
        async def start_all_cmd(event):
            if not is_admin(event.sender_id):
                return
            await event.reply("🔄 Запускаю...")
            asyncio.create_task(self.run_round_robin())
        
        @self.master_bot.on(events.NewMessage(pattern='/stop_all'))
        async def stop_all_cmd(event):
            if not is_admin(event.sender_id):
                return
            await event.reply("⏹️ Останавливаю...")
            await self.session_mgr.stop_all()
        
        @self.master_bot.on(events.NewMessage(pattern='/remove (.+)'))
        async def remove_cmd(event):
            if not is_admin(event.sender_id):
                return
            phone = event.pattern_match.group(1).strip()
            if self.session_mgr.remove_session(phone):
                await event.reply(f"✅ {phone} удалена")
            else:
                await event.reply(f"❌ {phone} не найдена")
        
        await self.setup_handlers()
    
    async def setup_handlers(self):
        for phone in self.session_mgr.get_active_phones():
            client = await self.session_mgr.get_client(phone)
            if client:
                for bot in TARGET_BOTS:
                    @client.on(events.NewMessage(chats=bot))
                    async def handler(event, p=phone):
                        await self.handle_message(p, event.message)
                print(f"✅ {phone}: слушает {', '.join(TARGET_BOTS)}")
    
    async def run_round_robin(self):
        self.session_mgr.is_running = True
        
        while self.session_mgr.is_running:
            phones = self.session_mgr.get_active_phones()
            if not phones:
                await self.send_msg("⚠️ Нет активных сессий")
                break
            
            for phone in phones:
                if not self.session_mgr.is_running:
                    break
                
                await self.send_msg(f"🔄 {phone} ожидает конкурс...")
                
                self.session_mgr.active_round = False
                self.session_mgr.current_phone = phone
                self.winner = None
                
                while self.session_mgr.is_running:
                    if self.session_mgr.active_round and self.session_mgr.current_phone == phone:
                        await self.send_msg(f"🚀 {phone}: {self.session_mgr.current_task_type} - СТАРТ!")
                        
                        self.session_mgr.current_spam_task = asyncio.create_task(
                            self.spam(phone, self.session_mgr.current_task_type)
                        )
                        
                        while self.session_mgr.is_running and self.session_mgr.active_round:
                            await asyncio.sleep(1)
                        
                        if self.winner == phone:
                            await self.send_msg(f"✅ {phone} ВЫИГРАЛ! Следующий...")
                        else:
                            await self.send_msg(f"⚠️ {phone} не выиграл")
                        break
                    
                    await asyncio.sleep(1)
                
                await asyncio.sleep(3)
    
    async def handle_message(self, phone: str, msg: Message):
        text = msg.text or ""
        
        # ZIP = выигрыш
        if msg.document and msg.document.mime_type == "application/zip":
            await self.save_zip(phone, msg)
            return
        
        # Конец конкурса
        if "РАЗДАЧА ЗАВЕРШЕНА" in text or "Победитель" in text:
            if self.session_mgr.active_round:
                await self.send_msg(f"🏆 Конкурс завершен!")
                self.session_mgr.active_round = False
                if self.session_mgr.current_spam_task:
                    self.session_mgr.current_spam_task.cancel()
            return
        
        # Начало конкурса
        task_type = None
        max_num = 200
        
        if "Гео" in text and "аккаунта" in text:
            task_type = "geo"
        elif "Число от" in text:
            task_type = "number"
            match = re.search(r'до (\d+)', text)
            if match:
                max_num = int(match.group(1))
        
        if task_type and not self.session_mgr.active_round and self.session_mgr.current_phone == phone:
            self.session_mgr.current_task_type = task_type
            self.session_mgr.active_round = True
            await self.send_msg(
                f"🎯 **НОВЫЙ КОНКУРС!**\n"
                f"📱 {phone}\n"
                f"📝 {task_type.upper()}\n"
                f"🔢 Макс: {max_num if task_type == 'number' else 'все гео'}"
            )
    
    async def spam(self, phone: str, task_type: str):
        client = await self.session_mgr.get_client(phone)
        if not client:
            await self.send_msg(f"❌ {phone}: нет клиента")
            self.session_mgr.active_round = False
            return
        
        # Получаем все целевые чаты
        targets = []
        for bot in TARGET_BOTS:
            try:
                targets.append(await client.get_entity(bot))
            except Exception as e:
                await self.send_msg(f"⚠️ {phone}: не могу получить {bot}")
        
        if not targets:
            return
        
        if task_type == "geo":
            await self.send_msg(f"📤 {phone}: Спам {len(all_territories)} гео")
            await self.send_answers(client, targets, all_territories, phone)
        
        else:  # number
            max_num = 200
            await self.send_msg(f"📤 {phone}: Этап 1 - цифры 1-{max_num}")
            
            digits = [str(i) for i in range(1, max_num + 1)]
            won = await self.send_answers(client, targets, digits, phone)
            
            if not won and self.session_mgr.active_round:
                await self.send_msg(f"📤 {phone}: Этап 2 - слова")
                words = [number_to_words_ru(i) for i in range(1, max_num + 1)]
                await self.send_answers(client, targets, words, phone)
        
        await self.send_msg(f"⏹️ {phone}: Спам завершен")
    
    async def send_answers(self, client, targets, answers: list, phone: str) -> bool:
        index = 0
        count = 0
        
        while self.session_mgr.is_running and self.session_mgr.active_round:
            if index >= len(answers):
                index = 0
            
            answer = answers[index]
            try:
                for target in targets:
                    await client.send_message(target, str(answer))
                count += 1
                
                if count % 50 == 0:
                    await self.send_msg(f"📊 {phone}: {count} сообщений")
                
                await asyncio.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
                index += 1
                
                if not self.session_mgr.active_round:
                    return True
                    
            except errors.FloodWaitError as e:
                await self.send_msg(f"⚠️ {phone}: Flood {e.seconds} сек")
                await asyncio.sleep(e.seconds)
            except Exception as e:
                await self.send_msg(f"❌ {phone}: {e}")
                break
        
        return False
    
    async def save_zip(self, phone: str, msg: Message):
        try:
            filename = f"{phone}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            file_path = await msg.download_media(file=os.path.join(DOWNLOADS_DIR, filename))
            
            await self.send_msg(f"🎉 **ВЫИГРЫШ!** {phone} - {filename}")
            
            if self.master_bot:
                await self.master_bot.send_file(MASTER_CHAT_ID, file_path, caption=f"🎉 ВЫИГРЫШ!\nОт: {phone}")
            
            self.winner = phone
            self.session_mgr.active_round = False
            
            if self.session_mgr.current_spam_task:
                self.session_mgr.current_spam_task.cancel()
                
        except Exception as e:
            await self.send_msg(f"❌ Ошибка ZIP: {e}")
    
    async def send_msg(self, text: str):
        if self.master_bot:
            try:
                await self.master_bot.send_message(MASTER_CHAT_ID, text, parse_mode='markdown')
            except:
                print(text)
    
    async def stop(self):
        await self.session_mgr.stop_all()
        if self.master_bot:
            await self.master_bot.disconnect()

# ================== ЗАПУСК ==================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def main():
    hunter = BotHunter()
    await hunter.start()
    
    # Добавляем админа
    if MASTER_CHAT_ID:
        add_admin(MASTER_CHAT_ID)
        print(f"✅ Админ {MASTER_CHAT_ID} добавлен")
    
    print("\n✅ БОТ ЗАПУЩЕН!")
    print(f"📱 Целевые боты: {', '.join(TARGET_BOTS)}")
    print("🚀 Команда для запуска: /start_all")
    print("Нажми Ctrl+C для остановки\n")
    
    try:
        await hunter.master_bot.run_until_disconnected()
    except KeyboardInterrupt:
        await hunter.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Остановлено")