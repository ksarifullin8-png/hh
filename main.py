import asyncio
import json
import os
import random
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from telethon import TelegramClient, errors, events
from telethon.tl.custom import Message, Button

# ================== НАСТРОЙКИ ==================
SESSIONS_DIR = "sessions"
DOWNLOADS_DIR = "downloads"
CONFIG_FILE = "sessions_config.json"
ADMINS_FILE = "admins.json"

os.makedirs(SESSIONS_DIR, exist_ok=True)
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

MASTER_BOT_TOKEN = "8762511961:AAHTd2Khe6bmN0GtZqyAH8KVIpXn2SYUslY"
API_ID = 35800959
API_HASH = '708e7d0bc3572355bcaf68562cc068f1'
TARGET_BOT = "@minonshoprobot"

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

def save_admins(admins: List[int]):
    with open(ADMINS_FILE, 'w') as f:
        json.dump(admins, f)

def is_admin(user_id: int) -> bool:
    return user_id in load_admins()

def add_admin(user_id: int) -> bool:
    admins = load_admins()
    if user_id not in admins:
        admins.append(user_id)
        save_admins(admins)
        return True
    return False

def remove_admin(user_id: int) -> bool:
    admins = load_admins()
    if user_id in admins:
        admins.remove(user_id)
        save_admins(admins)
        return True
    return False

# ================== МЕНЕДЖЕР СЕССИЙ ==================
class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, dict] = {}
        self.clients: Dict[str, TelegramClient] = {}
        self.is_running = False
        self.current_round_active = False
        self.current_round_phone = None
        self.current_task_type = None
        self.current_spam_task = None
        self.current_stage = None  # 'digits' or 'words' for number task
        self.load_sessions()
    
    def load_sessions(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                self.sessions = json.load(f)
        else:
            self.sessions = {}
    
    def save_sessions(self):
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.sessions, f, ensure_ascii=False, indent=2)
    
    def add_session(self, phone: str):
        if phone not in self.sessions:
            self.sessions[phone] = {
                'phone': phone,
                'active': True,
                'added_at': datetime.now().isoformat()
            }
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
    
    def toggle_session(self, phone: str) -> bool:
        if phone in self.sessions:
            self.sessions[phone]['active'] = not self.sessions[phone].get('active', True)
            self.save_sessions()
            return True
        return False
    
    def get_active_phones(self) -> List[str]:
        return [p for p, cfg in self.sessions.items() if cfg.get('active', True)]
    
    def get_all_phones(self) -> List[str]:
        return list(self.sessions.keys())
    
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
            print(f"Ошибка авторизации {phone}: {e}")
        return None
    
    async def check_session_health(self, phone: str) -> Tuple[bool, str]:
        try:
            client = await self.get_client(phone)
            if not client:
                return False, "Не авторизован"
            me = await client.get_me()
            if me:
                return True, f"OK: {me.first_name or me.username}"
            return False, "Не удалось получить информацию"
        except Exception as e:
            return False, f"Ошибка: {str(e)[:50]}"
    
    async def stop_all(self):
        self.is_running = False
        self.current_round_active = False
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
        self.current_round_winner = None
    
    async def start(self):
        self.master_bot = TelegramClient("master_bot", API_ID, API_HASH)
        await self.master_bot.start(bot_token=MASTER_BOT_TOKEN)
        
        # ========== КОМАНДЫ ==========
        @self.master_bot.on(events.NewMessage(pattern='/add_phone (.+)'))
        async def add_phone_cmd(event):
            if not is_admin(event.sender_id):
                return
            phone = event.pattern_match.group(1).strip()
            if not phone.startswith('+') or not phone[1:].isdigit():
                await event.reply("❌ Неверный формат. Используйте: +79991234567")
                return
            if self.session_mgr.add_session(phone):
                await event.reply(f"✅ Сессия {phone} добавлена!\n\nТеперь авторизуйте её командой:\n`/auth {phone}`")
            else:
                await event.reply(f"❌ Сессия {phone} уже существует")
        
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
                await event.reply(f"📱 Код отправлен на {phone}\n`/verify {phone} <код>`")
            except Exception as e:
                await event.reply(f"❌ Ошибка: {e}")
        
        @self.master_bot.on(events.NewMessage(pattern='/verify (.+) (.+)'))
        async def verify_cmd(event):
            if not is_admin(event.sender_id):
                return
            phone, code = event.pattern_match.groups()
            if phone not in self.pending_auth:
                await event.reply(f"❌ Сначала `/auth {phone}`")
                return
            client = self.pending_auth[phone]
            try:
                await client.sign_in(phone, code)
                await event.reply(f"✅ Сессия {phone} авторизована!")
                self.session_mgr.clients[phone] = client
                del self.pending_auth[phone]
            except errors.SessionPasswordNeededError:
                await event.reply(f"🔐 Требуется 2FA\n`/2fa {phone} <пароль>`")
            except Exception as e:
                await event.reply(f"❌ {e}")
        
        @self.master_bot.on(events.NewMessage(pattern='/2fa (.+) (.+)'))
        async def twofa_cmd(event):
            if not is_admin(event.sender_id):
                return
            phone, password = event.pattern_match.groups()
            if phone not in self.pending_auth:
                await event.reply(f"❌ Сначала `/auth {phone}`")
                return
            client = self.pending_auth[phone]
            try:
                await client.sign_in(password=password)
                await event.reply(f"✅ Сессия {phone} авторизована!")
                self.session_mgr.clients[phone] = client
                del self.pending_auth[phone]
            except Exception as e:
                await event.reply(f"❌ {e}")
        
        @self.master_bot.on(events.NewMessage(pattern='/start'))
        async def start_cmd(event):
            if not is_admin(event.sender_id):
                await event.reply("❌ Нет доступа")
                return
            await event.reply(
                "🤖 **Бот для выигрыша аккаунтов**\n\n"
                f"📊 Активных сессий: {len(self.session_mgr.get_active_phones())}\n"
                f"🎯 Целевой бот: {TARGET_BOT}\n\n"
                "**Команды:**\n"
                "/add_phone +79991234567 - добавить\n"
                "/auth +79991234567 - авторизовать\n"
                "/verify +79991234567 код - код\n"
                "/2fa +79991234567 пароль - 2FA\n"
                "/list - список сессий\n"
                "/check - проверить\n"
                "/start_all - запустить\n"
                "/stop_all - остановить\n"
                "/toggle +79991234567 - вкл/выкл\n"
                "/remove +79991234567 - удалить\n\n"
                "📌 **Логика:**\n"
                "• Гео → спам территориями\n"
                "• Числа → сначала цифрами, если не выиграл → словами",
                parse_mode='markdown'
            )
        
        @self.master_bot.on(events.NewMessage(pattern='/list'))
        async def list_cmd(event):
            if not is_admin(event.sender_id):
                return
            phones = self.session_mgr.get_all_phones()
            if not phones:
                await event.reply("📭 Нет сессий")
                return
            text = "📱 **Список сессий:**\n\n"
            for phone in phones:
                active = "✅" if self.session_mgr.sessions[phone].get('active', True) else "❌"
                text += f"{active} `{phone}`\n"
            await event.reply(text, parse_mode='markdown')
        
        @self.master_bot.on(events.NewMessage(pattern='/check'))
        async def check_cmd(event):
            if not is_admin(event.sender_id):
                return
            await event.reply("🔍 Проверяю...")
            phones = self.session_mgr.get_all_phones()
            if not phones:
                await event.reply("📭 Нет сессий")
                return
            text = "🔍 **Результаты:**\n\n"
            for phone in phones:
                health, msg = await self.session_mgr.check_session_health(phone)
                icon = "✅" if health else "❌"
                text += f"{icon} `{phone}`: {msg}\n"
            await event.reply(text, parse_mode='markdown')
        
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
        
        @self.master_bot.on(events.NewMessage(pattern='/toggle (.+)'))
        async def toggle_cmd(event):
            if not is_admin(event.sender_id):
                return
            phone = event.pattern_match.group(1).strip()
            if self.session_mgr.toggle_session(phone):
                status = "активирована" if self.session_mgr.sessions[phone].get('active', True) else "деактивирована"
                await event.reply(f"✅ {phone} {status}")
            else:
                await event.reply(f"❌ {phone} не найдена")
        
        @self.master_bot.on(events.NewMessage(pattern='/remove (.+)'))
        async def remove_cmd(event):
            if not is_admin(event.sender_id):
                return
            phone = event.pattern_match.group(1).strip()
            if self.session_mgr.remove_session(phone):
                await event.reply(f"✅ {phone} удалена")
            else:
                await event.reply(f"❌ {phone} не найдена")
        
        @self.master_bot.on(events.NewMessage(pattern='/add_admin (.+)'))
        async def add_admin_cmd(event):
            if not is_admin(event.sender_id):
                return
            try:
                admin_id = int(event.pattern_match.group(1))
                if add_admin(admin_id):
                    await event.reply(f"✅ Админ {admin_id} добавлен")
                else:
                    await event.reply(f"❌ Уже существует")
            except:
                await event.reply("❌ /add_admin 123456789")
        
        @self.master_bot.on(events.NewMessage(pattern='/remove_admin (.+)'))
        async def remove_admin_cmd(event):
            if not is_admin(event.sender_id):
                return
            try:
                admin_id = int(event.pattern_match.group(1))
                if remove_admin(admin_id):
                    await event.reply(f"✅ Админ {admin_id} удален")
                else:
                    await event.reply(f"❌ Не найден")
            except:
                await event.reply("❌ /remove_admin 123456789")
        
        await self.setup_message_handlers()
    
    async def setup_message_handlers(self):
        phones = self.session_mgr.get_active_phones()
        for phone in phones:
            client = await self.session_mgr.get_client(phone)
            if client:
                @client.on(events.NewMessage(chats=TARGET_BOT))
                async def handler(event, p=phone):
                    await self.handle_target_message(p, event.message)
                print(f"✅ {phone}: обработчик установлен")
    
    async def run_round_robin(self):
        self.session_mgr.is_running = True
        
        while self.session_mgr.is_running:
            active_phones = self.session_mgr.get_active_phones()
            if not active_phones:
                await self.send_admin("⚠️ Нет активных сессий")
                break
            
            for phone in active_phones:
                if not self.session_mgr.is_running:
                    break
                
                await self.send_admin(f"🔄 **{phone}** ожидает конкурс...")
                
                self.session_mgr.current_round_active = False
                self.session_mgr.current_round_phone = phone
                self.session_mgr.current_task_type = None
                self.session_mgr.current_stage = None
                self.current_round_winner = None
                
                while self.session_mgr.is_running:
                    if self.session_mgr.current_round_active and self.session_mgr.current_round_phone == phone:
                        await self.send_admin(f"🚀 **{phone}**: Конкурс начался! Тип: {self.session_mgr.current_task_type}")
                        
                        self.session_mgr.current_spam_task = asyncio.create_task(
                            self.spam_answers(phone, self.session_mgr.current_task_type)
                        )
                        
                        while self.session_mgr.is_running and self.session_mgr.current_round_active:
                            await asyncio.sleep(1)
                        
                        if self.current_round_winner == phone:
                            await self.send_admin(f"✅ **{phone}** ВЫИГРАЛ! Перехожу к следующему")
                        else:
                            await self.send_admin(f"⚠️ **{phone}** не выиграл")
                        
                        break
                    
                    await asyncio.sleep(1)
                
                await asyncio.sleep(3)
    
    async def handle_target_message(self, phone: str, message: Message):
        text = message.text or ""
        
        # ZIP = выигрыш
        if message.document and message.document.mime_type == "application/zip":
            await self.save_zip(phone, message)
            return
        
        # Завершение конкурса
        if "РАЗДАЧА ЗАВЕРШЕНА" in text or "Победитель" in text:
            if self.session_mgr.current_round_active:
                await self.send_admin(f"🏆 Конкурс завершен!")
                self.session_mgr.current_round_active = False
                if self.session_mgr.current_spam_task:
                    self.session_mgr.current_spam_task.cancel()
            return
        
        # Начало конкурса
        task_type = self.parse_task(text)
        if task_type:
            if not self.session_mgr.current_round_active and self.session_mgr.current_round_phone == phone:
                self.session_mgr.current_task_type = task_type
                self.session_mgr.current_round_active = True
                await self.send_admin(
                    f"🎯 **НОВЫЙ КОНКУРС!**\n"
                    f"📱 Аккаунт: {phone}\n"
                    f"📝 Задание: {task_type}\n"
                    f"🚀 Начинаю спам..."
                )
    
    def parse_task(self, text: str) -> Optional[str]:
        if "Гео разыгрываемого аккаунта" in text or ("Гео" in text and "аккаунта" in text):
            return "geo"
        if "Число от 1 до" in text or "Число" in text:
            return "number"
        return None
    
    async def spam_answers(self, phone: str, task_type: str):
        client = await self.session_mgr.get_client(phone)
        if not client:
            await self.send_admin(f"❌ {phone}: не удалось получить клиент")
            self.session_mgr.current_round_active = False
            return
        
        target = await client.get_entity(TARGET_BOT)
        
        if task_type == "geo":
            answers = all_territories
            await self.send_admin(f"📤 {phone}: Спам {len(answers)} территорий")
            await self._send_answers(client, target, answers, phone)
        
        else:  # number
            # Этап 1: цифры
            digits = [str(i) for i in range(1, 201)]
            await self.send_admin(f"📤 {phone}: Этап 1 - спам цифрами (1-200)")
            
            won = await self._send_answers(client, target, digits, phone)
            
            # Если не выиграл на цифрах, переходим к словам
            if not won and self.session_mgr.current_round_active:
                words = [number_to_words_ru(i) for i in range(1, 201)]
                await self.send_admin(f"📤 {phone}: Этап 2 - спам словами")
                await self._send_answers(client, target, words, phone)
        
        await self.send_admin(f"⏹️ {phone}: Спам завершен")
    
    async def _send_answers(self, client, target, answers: list, phone: str) -> bool:
        """Отправляет ответы, возвращает True если выиграл"""
        index = 0
        count = 0
        
        while self.session_mgr.is_running and self.session_mgr.current_round_active:
            if index >= len(answers):
                index = 0
            
            answer = answers[index]
            try:
                await client.send_message(target, str(answer))
                count += 1
                
                if count % 50 == 0:
                    await self.send_admin(f"📊 {phone}: Отправлено {count} сообщений")
                
                await asyncio.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
                index += 1
                
                # Если выиграли, выходим
                if not self.session_mgr.current_round_active:
                    return True
                    
            except errors.FloodWaitError as e:
                await self.send_admin(f"⚠️ {phone}: Flood wait {e.seconds} сек")
                await asyncio.sleep(e.seconds)
            except Exception as e:
                await self.send_admin(f"❌ {phone}: {e}")
                break
        
        return False
    
    async def save_zip(self, phone: str, message: Message):
        try:
            file_path = await message.download_media(file=os.path.join(DOWNLOADS_DIR, f"{phone}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"))
            
            await self.send_admin(
                f"🎉🎉🎉 **ВЫИГРЫШ!** 🎉🎉🎉\n"
                f"📱 Аккаунт: {phone}\n"
                f"📁 Файл: {os.path.basename(file_path)}"
            )
            
            if self.master_bot:
                await self.master_bot.send_file(MASTER_BOT_TOKEN, file_path, 
                    caption=f"🎉 **ВЫИГРЫШ!**\nОт: `{phone}`")
            
            self.current_round_winner = phone
            self.session_mgr.current_round_active = False
            
            if self.session_mgr.current_spam_task:
                self.session_mgr.current_spam_task.cancel()
                
        except Exception as e:
            await self.send_admin(f"❌ Ошибка: {e}")
    
    async def send_admin(self, text: str):
        if self.master_bot:
            try:
                await self.master_bot.send_message(MASTER_BOT_TOKEN, text, parse_mode='markdown')
            except:
                print(text)
    
    async def stop(self):
        await self.session_mgr.stop_all()
        if self.master_bot:
            await self.master_bot.disconnect()

# ================== ЗАПУСК ==================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    hunter = BotHunter()
    await hunter.start()
    
    admins = load_admins()
    if not admins:
        print("\n" + "="*50)
        print("ПЕРВЫЙ ЗАПУСК!")
        print("Добавьте ваш Telegram ID в файл admins.json")
        print("Формат: [123456789]")
        print("="*50)
    
    print("\n✅ Бот запущен!")
    print("Отправьте /start вашему боту")
    print("\n🚀 Запуск: /start_all")
    print("Нажмите Ctrl+C для остановки\n")
    
    try:
        await hunter.master_bot.run_until_disconnected()
    except KeyboardInterrupt:
        await hunter.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Остановлено")