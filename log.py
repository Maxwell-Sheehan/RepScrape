# log.py
import datetime

def log(message):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("app.log", "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {message}\n")
    print(message)
