import os
import subprocess
import smtplib
import time
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# =====================================================================
# ШАГ 0. УМНЫЙ ХАРДКОД-ХАК ДЛЯ ПУТЕЙ К ФАЙЛАМ
# =====================================================================
# Скрипт сам определяет папку, в которой он лежит, и привязывается к ней
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

EMAILS_FILE = os.path.join(BASE_DIR, "emails_new.txt")
HISTORY_FILE = os.path.join(BASE_DIR, "sent_history.txt")

RESUME_NAME_ONLY = "Matskevich_Resume_work&travel_2027.pdf"
RESUME_FILE_PATH = os.path.join(BASE_DIR, RESUME_NAME_ONLY)

# =====================================================================
# НАСТРОЙКИ ПОЧТЫ И ОГРАНИЧЕНИЙ
# =====================================================================
SENDER_EMAIL = "alexmatskevich2000en@gmail.com"        # Ваш Gmail
SENDER_PASSWORD = "opmaymzowoelcymf"                  # Пароль приложения
SUBJECT = "Application for Seasonal Positions (July - Sept 2027) - Resume"
DAILY_LIMIT = 40                                      # Лимит писем за один запуск
DELAY_SECONDS = 50.0                                  # Пауза в 20 секунд

# Текст письма для Алекса (доступность: июль - сентябрь)
html_text = """
<html>
 <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333333;">
  <p>Dear Hiring Team,</p>
  
  <p>I hope this email finds you well.</p>
  
  <p>I am writing to express my strong interest in seasonal employment opportunities at your company for the upcoming season. I am a hardworking, adaptable, and team-oriented candidate, eager to contribute to delivering an exceptional experience for your guests and members.</p>
  
  <p>My full resume with detailed information regarding my background, skills, and previous experience is attached to this email. I am fully available to work from <b>[Start Month Year]</b> through <b>[End Month Year]</b>.</p>
  
  <p>Thank you for your time and consideration. I would welcome the opportunity to discuss how my profile and enthusiasm align with your team's needs.</p>
  
  <p>Best regards,<br>
  <b>Alex Matskevich</b><br>
  <i>J-1 Visa Applicant</i></p>
</body>
</html>
"""

# 1. Автоматическая очистка терминала современным способом
subprocess.run('cls' if os.name == 'nt' else 'clear', shell=True)

print("🤖 БОТ-РАССЫЛЬЩИК ЗАПУЩЕН И ГОТОВ К РАБОТЕ 🚀")

# ШАГ 1. ЗАГРУЗКА ИСТОРИИ (Умное чтение логов прошлых дней)
already_sent = set()
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r", encoding="utf-8") as h_file:
        for line in h_file:
            if "|" in line:
                parts = line.split("|")
                email_from_history = parts[1].strip()  # Извлекаем email из лога
                already_sent.add(email_from_history)

# ШАГ 2. ПРОВЕРКА НАЛИЧИЯ ФАЙЛОВ
if not os.path.exists(EMAILS_FILE):
    print(f"❌ Ошибка: Файл базы не найден по пути: {EMAILS_FILE}")
    exit()

if not os.path.exists(RESUME_FILE_PATH):
    print(f"❌ Ошибка: Файл резюме не найден по пути: {RESUME_FILE_PATH}")
    exit()

# ШАГ 3. ПОДКЛЮЧЕНИЕ К СЕРВЕРУ GOOGLE
print("🔗 Подключение к SMTP-серверу Google...")
try:
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(SENDER_EMAIL, SENDER_PASSWORD)
    print("🔑 Успешная авторизация в Gmail!")
except Exception as e:
    print(f"❌ Ошибка подключения: {e}")
    exit()

# Бортовой счетчик отправленных писем за сессию
sent_counter = 0

print("🚀 Начинаем безопасную отправку по списку чистых адресов...")

# ШАГ 4. ЦИКЛ РАССЫЛКИ С КОНТРОЛЕМ ЛИМИТА И ДУБЛИКАТОВ
with open(EMAILS_FILE, "r", encoding="utf-8") as file:
    for line in file:
        
        # СТРОГИЙ ЛИМИТ: Останавливаемся ровно на 50 письмах
        if sent_counter >= DAILY_LIMIT:
            print(f"\n🛑 Достигнут строгий лимит в {DAILY_LIMIT} писем за этот запуск! Бот завершает сессию.")
            break

        receiver_email = line.strip().lower()
        
        # Пропускаем пустые строки
        if not receiver_email or "@" not in receiver_email:
            continue

        # ПРОВЕРКА ПО ИСТОРИИ: Если этой почте уже отправляли резюме — бот её пропускает
        if receiver_email in already_sent:
            print(f"⏭️ Пропуск {receiver_email}: письмо уже отправлялось ранее.")
            continue

        print(f"\n📧 [{sent_counter + 1}/{DAILY_LIMIT}] Готовим письмо для: {receiver_email}")

        try:
            # Собираем письмо (MIME)
            msg = MIMEMultipart()
            msg["From"] = SENDER_EMAIL
            msg["To"] = receiver_email
            msg["Subject"] = SUBJECT
            msg.attach(MIMEText(html_text, "html", "utf-8"))

            # Пакуем файл резюме по полному авто-пути
            file_data = open(RESUME_FILE_PATH, "rb")
            attachment = MIMEBase("application", "octet-stream")
            attachment.set_payload(file_data.read())
            file_data.close()
            encoders.encode_base64(attachment)
            attachment.add_header("Content-Disposition", f"attachment; filename={RESUME_NAME_ONLY}")
            msg.attach(attachment)

            # Отправляем на сервер Google
            server.send_message(msg)
            print(f"🚀 Успешно отправлено на: {receiver_email}")

            # Увеличиваем счетчик отправленных
            sent_counter += 1

            # ЗАПИСЬ В ЖУРНАЛ ИСТОРИИ НА ДИСК (создается автоматически)
            current_time = datetime.now().strftime("%d-%m-%Y %H:%M")
            log_line = f"{current_time} | {receiver_email} | SUCCESS | {RESUME_NAME_ONLY}\n"
            with open(HISTORY_FILE, "a", encoding="utf-8") as h_file:
                h_file.write(log_line)

            # Безопасная пауза в 20 секунд
            print(f"⏳ Ждем {DELAY_SECONDS} секунд перед следующим письмом...")
            time.sleep(DELAY_SECONDS)

        except Exception as e:
            print(f"❌ Ошибка отправки на {receiver_email}: {e}")
            current_time = datetime.now().strftime("%d-%m-%Y %H:%M")
            log_line = f"{current_time} | {receiver_email} | FAILED ({e}) | {RESUME_NAME_ONLY}\n"
            with open(HISTORY_FILE, "a", encoding="utf-8") as h_file:
                h_file.write(log_line)

# Отключаемся от почты
server.quit()
print(f"\n🎉 Рассылка завершена. Всего отправлено писем за этот запуск: {sent_counter}")
