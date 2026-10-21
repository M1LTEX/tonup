# Ton Up — стартовий Telegram Mini App
Демо з кейсами, Plinko, апгрейдером, «Коровкою», інвентарем і SQLite. Ігри використовують тільки тестові монети — не реальні Telegram Stars.

## Windows 10
1. Розпакуй архів і відкрий термінал у папці.
2. Скопіюй `.env.example` у `.env`, впиши токен від @BotFather і HTTPS-адресу вебзастосунку.
3. `py -m venv .venv`
4. `.venv\\Scripts\\activate`
5. `pip install -r requirements.txt`
6. В одному терміналі: `uvicorn server:app --host 0.0.0.0 --port 8000`
7. В іншому: `python bot.py`

Для Telegram Mini App потрібна публічна HTTPS-адреса. Це прототип: перед публічним запуском потрібні валідація Telegram initData, захист адмінки та перевірка безпеки.
