import asyncio
import json
import os
import random
import logging
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

# Токен вашего бота-управляющего (создайте у @BotFather)
MASTER_BOT_TOKEN = "8762511961:AAHTd2Khe6bmN0GtZqyAH8KVIpXn2SYUslY"  # ЗАМЕНИТЕ НА РЕАЛЬНЫЙ ТОКЕН

# API данные (общие для всех сессий)
API_ID = 35800959
API_HASH = '708e7d0bc3572355bcaf68562cc068f1'

TARGET_BOT = "@minonshoprobot"

# Задержки между ответами (сек)
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

# ================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==================
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
        self.current_round: Dict[str, dict] = {}
        self.won_this_round: Dict[str, bool] = {}
        self.is_running = False
        self.spam_tasks: Dict[str, asyncio.Task] = {}
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
            if phone in self.spam_tasks:
                self.spam_tasks[phone].cancel()
                del self.spam_tasks[phone]
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
        """Проверяет работоспособность сессии"""
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
        for task in self.spam_tasks.values():
            task.cancel()
        self.spam_tasks.clear()
        for client in self.clients.values():
            await client.disconnect()
        self.clients.clear()

# ================== ОСНОВНОЙ БОТ ==================
class BotHunter:
    def __init__(self):
        self.session_mgr = SessionManager()
        self.master_bot: Optional[TelegramClient] = None
        self.target_entity = None
    
    async def start(self):
        """Запуск бота-управляющего"""
        self.master_bot = TelegramClient("master_bot", API_ID, API_HASH)
        await self.master_bot.start(bot_token=MASTER_BOT_TOKEN)
        
        # Регистрируем обработчики команд
        @self.master_bot.on(events.NewMessage(pattern='/start'))
        async def start_cmd(event):
            if not is_admin(event.sender_id):
                await event.reply("❌ У вас нет доступа к этому боту.")
                return
            
            keyboard = [
                [Button.inline("➕ Добавить сессию", b"add_session")],
                [Button.inline("📋 Список сессий", b"list_sessions")],
                [Button.inline("🔍 Проверить сессии", b"check_sessions")],
                [Button.inline("▶️ Запустить всех", b"start_all")],
                [Button.inline("⏹️ Остановить всех", b"stop_all")],
                [Button.inline("👥 Управление админами", b"manage_admins")]
            ]
            await event.reply(
                "🤖 **Бот для автоматического выигрыша аккаунтов**\n\n"
                f"📊 Активных сессий: {len(self.session_mgr.get_active_phones())}\n"
                f"🎯 Целевой бот: {TARGET_BOT}\n\n"
                "Выберите действие:",
                buttons=keyboard,
                parse_mode='markdown'
            )
        
        @self.master_bot.on(events.CallbackQuery)
        async def callback_handler(event):
            if not is_admin(event.sender_id):
                await event.answer("Нет доступа", alert=True)
                return
            
            data = event.data.decode()
            
            if data == "add_session":
                await event.answer()
                await event.edit(
                    "📱 **Добавление сессии**\n\n"
                    "Отправьте номер телефона в формате:\n`+79991234567`",
                    parse_mode='markdown'
                )
                # Сохраняем состояние
                async with self.master_bot.conversation(event.sender_id, timeout=60) as conv:
                    try:
                        msg = await conv.get_response()
                        phone = msg.text.strip()
                        if phone.startswith('+') and phone[1:].isdigit():
                            if self.session_mgr.add_session(phone):
                                await conv.send_message(f"✅ Сессия {phone} добавлена!\n\nТеперь нужно авторизоваться.\nОтправьте код подтверждения из Telegram:")
                                
                                # Получаем клиент и запрашиваем код
                                client = TelegramClient(os.path.join(SESSIONS_DIR, f"session_{phone.replace('+', '')}"), API_ID, API_HASH)
                                await client.connect()
                                await client.send_code_request(phone)
                                
                                code_msg = await conv.get_response()
                                code = code_msg.text.strip()
                                
                                try:
                                    await client.sign_in(phone, code)
                                    await conv.send_message(f"✅ Сессия {phone} успешно авторизована!")
                                except errors.SessionPasswordNeededError:
                                    await conv.send_message("🔐 Требуется пароль двухфакторной аутентификации. Введите пароль:")
                                    password_msg = await conv.get_response()
                                    await client.sign_in(password=password_msg.text.strip())
                                    await conv.send_message(f"✅ Сессия {phone} успешно авторизована!")
                                
                                await client.disconnect()
                                await self.show_main_menu(event, "✅ Сессия добавлена и авторизована!")
                            else:
                                await conv.send_message(f"❌ Сессия {phone} уже существует")
                        else:
                            await conv.send_message("❌ Неверный формат номера. Используйте формат: +79991234567")
                    except asyncio.TimeoutError:
                        await event.edit("⏰ Время вышло. Попробуйте снова.")
            
            elif data == "list_sessions":
                await event.answer()
                phones = self.session_mgr.get_all_phones()
                if not phones:
                    await event.edit("📭 Нет добавленных сессий")
                    await asyncio.sleep(2)
                    await self.show_main_menu(event)
                    return
                
                text = "📱 **Список сессий:**\n\n"
                for phone in phones:
                    active = "✅" if self.session_mgr.sessions[phone].get('active', True) else "❌"
                    text += f"{active} `{phone}`\n"
                
                buttons = []
                for phone in phones:
                    buttons.append([Button.inline(f"{phone}", f"session_{phone}")])
                buttons.append([Button.inline("🔙 Назад", b"back")])
                
                await event.edit(text, buttons=buttons, parse_mode='markdown')
            
            elif data.startswith("session_"):
                phone = data.replace("session_", "")
                session_data = self.session_mgr.sessions.get(phone, {})
                active = session_data.get('active', True)
                
                status = "🟢 Активна" if active else "🔴 Неактивна"
                text = f"📱 **Сессия:** `{phone}`\n"
                text += f"📊 Статус: {status}\n"
                text += f"📅 Добавлена: {session_data.get('added_at', 'Неизвестно')}\n"
                
                # Проверяем здоровье сессии
                health, health_msg = await self.session_mgr.check_session_health(phone)
                text += f"🔍 Состояние: {health_msg}\n"
                
                buttons = [
                    [Button.inline("🔄 Переключить активность", f"toggle_{phone}")],
                    [Button.inline("🗑️ Удалить", f"delete_{phone}")],
                    [Button.inline("🔙 Назад", b"list_sessions")]
                ]
                await event.edit(text, buttons=buttons, parse_mode='markdown')
            
            elif data.startswith("toggle_"):
                phone = data.replace("toggle_", "")
                self.session_mgr.toggle_session(phone)
                await event.answer("Статус изменен")
                # Возвращаемся к списку
                await self.show_sessions_list(event)
            
            elif data.startswith("delete_"):
                phone = data.replace("delete_", "")
                self.session_mgr.remove_session(phone)
                await event.answer("Сессия удалена")
                await self.show_sessions_list(event)
            
            elif data == "check_sessions":
                await event.answer("Проверяю...")
                phones = self.session_mgr.get_all_phones()
                if not phones:
                    await event.edit("📭 Нет сессий для проверки")
                    await asyncio.sleep(2)
                    await self.show_main_menu(event)
                    return
                
                text = "🔍 **Результаты проверки сессий:**\n\n"
                for phone in phones:
                    health, msg = await self.session_mgr.check_session_health(phone)
                    icon = "✅" if health else "❌"
                    text += f"{icon} `{phone}`: {msg}\n"
                
                await event.edit(text, buttons=[[Button.inline("🔙 Назад", b"back")]], parse_mode='markdown')
            
            elif data == "start_all":
                await event.answer("Запускаю...")
                await self.run_all_clients()
                await event.edit("🚀 Все активные сессии запущены и отслеживают задания!", buttons=[[Button.inline("🔙 Назад", b"back")]])
            
            elif data == "stop_all":
                await event.answer("Останавливаю...")
                await self.session_mgr.stop_all()
                await event.edit("⏹️ Все сессии остановлены.", buttons=[[Button.inline("🔙 Назад", b"back")]])
            
            elif data == "manage_admins":
                admins = load_admins()
                text = "👥 **Управление администраторами**\n\n"
                text += "Текущие админы:\n"
                for admin in admins:
                    text += f"• `{admin}`\n"
                text += "\nДоступные команды:\n/add_admin <id>\n/remove_admin <id>"
                
                await event.edit(text, buttons=[[Button.inline("🔙 Назад", b"back")]], parse_mode='markdown')
            
            elif data == "back":
                await self.show_main_menu(event)
        
        # Обработка текстовых команд для админов
        @self.master_bot.on(events.NewMessage)
        async def admin_commands(event):
            if not is_admin(event.sender_id):
                return
            
            text = event.message.text
            if text.startswith('/add_admin '):
                try:
                    admin_id = int(text.split()[1])
                    if add_admin(admin_id):
                        await event.reply(f"✅ Админ {admin_id} добавлен")
                    else:
                        await event.reply(f"❌ Админ {admin_id} уже существует")
                except:
                    await event.reply("❌ Используйте: /add_admin <id>")
            
            elif text.startswith('/remove_admin '):
                try:
                    admin_id = int(text.split()[1])
                    if remove_admin(admin_id):
                        await event.reply(f"✅ Админ {admin_id} удален")
                    else:
                        await event.reply(f"❌ Админ {admin_id} не найден")
                except:
                    await event.reply("❌ Используйте: /remove_admin <id>")
    
    async def show_main_menu(self, event, message=None):
        keyboard = [
            [Button.inline("➕ Добавить сессию", b"add_session")],
            [Button.inline("📋 Список сессий", b"list_sessions")],
            [Button.inline("🔍 Проверить сессии", b"check_sessions")],
            [Button.inline("▶️ Запустить всех", b"start_all")],
            [Button.inline("⏹️ Остановить всех", b"stop_all")],
            [Button.inline("👥 Управление админами", b"manage_admins")]
        ]
        
        msg = message or (
            "🤖 **Бот для автоматического выигрыша аккаунтов**\n\n"
            f"📊 Активных сессий: {len(self.session_mgr.get_active_phones())}\n"
            f"🎯 Целевой бот: {TARGET_BOT}\n\n"
            "Выберите действие:"
        )
        
        await event.edit(msg, buttons=keyboard, parse_mode='markdown')
    
    async def show_sessions_list(self, event):
        phones = self.session_mgr.get_all_phones()
        if not phones:
            await event.edit("📭 Нет добавленных сессий")
            await asyncio.sleep(2)
            await self.show_main_menu(event)
            return
        
        text = "📱 **Список сессий:**\n\n"
        for phone in phones:
            active = "✅" if self.session_mgr.sessions[phone].get('active', True) else "❌"
            text += f"{active} `{phone}`\n"
        
        buttons = []
        for phone in phones:
            buttons.append([Button.inline(f"{phone}", f"session_{phone}")])
        buttons.append([Button.inline("🔙 Назад", b"back")])
        
        await event.edit(text, buttons=buttons, parse_mode='markdown')
    
    async def run_all_clients(self):
        """Запускаем всех активных клиентов"""
        self.session_mgr.is_running = True
        phones = self.session_mgr.get_active_phones()
        
        for phone in phones:
            client = await self.session_mgr.get_client(phone)
            if client:
                @client.on(events.NewMessage(chats=TARGET_BOT))
                async def handler(event, p=phone):
                    await self.handle_message(p, event.message)
                
                logging.info(f"Клиент {phone} запущен")
    
    async def handle_message(self, phone: str, message: Message):
        """Обработка входящего сообщения от целевого бота"""
        text = message.text or ""
        
        # Если пришёл ZIP-файл (выигрыш)
        if message.document and message.document.mime_type == "application/zip":
            await self.save_zip(phone, message)
            return
        
        # Распознаём задание
        task_type = self.parse_task(text)
        if not task_type:
            return
        
        # Если этот аккаунт уже выиграл в текущем раунде – не спамим
        if self.session_mgr.won_this_round.get(phone, False):
            return
        
        # Запускаем спам для этого аккаунта
        if phone not in self.session_mgr.spam_tasks or self.session_mgr.spam_tasks[phone].done():
            self.session_mgr.spam_tasks[phone] = asyncio.create_task(self.spam_answers(phone, task_type))
    
    def parse_task(self, text: str) -> Optional[str]:
        """Определяем тип задания"""
        if "Гео разыгрываемого аккаунта" in text or ("Гео" in text and "аккаунта" in text):
            return "geo"
        elif "Число от 1 до 200" in text:
            return "number"
        return None
    
    async def spam_answers(self, phone: str, task_type: str):
        """Цикл отправки ответов"""
        client = await self.session_mgr.get_client(phone)
        if not client:
            return
        
        target = await client.get_entity(TARGET_BOT)
        
        if task_type == "geo":
            answers = all_territories
        else:
            # Сначала цифрами, потом словами
            answers = [str(i) for i in range(1, 201)] + [number_to_words_ru(i) for i in range(1, 201)]
        
        index = 0
        while self.session_mgr.is_running and not self.session_mgr.won_this_round.get(phone, False):
            if index >= len(answers):
                index = 0
            
            answer = answers[index]
            try:
                await client.send_message(target, str(answer))
                await asyncio.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
                index += 1
            except errors.FloodWaitError as e:
                await asyncio.sleep(e.seconds)
            except Exception as e:
                print(f"[{phone}] Ошибка: {e}")
                break
        
        if phone in self.session_mgr.spam_tasks:
            del self.session_mgr.spam_tasks[phone]
    
    async def save_zip(self, phone: str, message: Message):
        """Сохраняем ZIP и отправляем мастеру"""
        try:
            file_path = await message.download_media(file=os.path.join(DOWNLOADS_DIR, f"{phone}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"))
            
            # Отправляем мастеру
            if self.master_bot:
                await self.master_bot.send_file(MASTER_BOT_TOKEN, file_path, caption=f"🎉 **ВЫИГРЫШ!**\nОт: `{phone}`", parse_mode='markdown')
            
            # Помечаем, что этот аккаунт выиграл
            self.session_mgr.won_this_round[phone] = True
            
            # Останавливаем спам
            if phone in self.session_mgr.spam_tasks:
                self.session_mgr.spam_tasks[phone].cancel()
                del self.session_mgr.spam_tasks[phone]
        except Exception as e:
            print(f"Ошибка сохранения ZIP: {e}")
    
    async def stop(self):
        """Остановка всех клиентов"""
        await self.session_mgr.stop_all()
        if self.master_bot:
            await self.master_bot.disconnect()

# ================== ЗАПУСК ==================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    hunter = BotHunter()
    await hunter.start()
    
    # Добавляем первого админа (вас) через файл, без input()
    admins = load_admins()
    if not admins:
        print("\n" + "="*50)
        print("ПЕРВЫЙ ЗАПУСК!")
        print("Ваш Telegram ID нужно добавить вручную.")
        print("Узнать ID можно у @userinfobot")
        print("После этого отредактируйте файл admins.json")
        print("Добавьте ваш ID в формате: [123456789]")
        print("="*50)
        print("\n✅ Бот запущен! Но без админов.")
        print("Добавьте себя в админы через файл admins.json")
    
    print("\n✅ Бот запущен!")
    print("Откройте Telegram и отправьте /start вашему боту")
    print("Нажмите Ctrl+C для остановки\n")
    
    try:
        await hunter.master_bot.run_until_disconnected()
    except KeyboardInterrupt:
        await hunter.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Программа остановлена")