# CNC source, feel free to modify whatever u want

# Version 2.0.0

import socket, random, base64, requests, threading, time, string, os, json, hashlib, paramiko, traceback
import pyotp, qrcode, qrcode.console_scripts, pyfiglet # for captchas and 2FA
from datetime import datetime
from src.utils import *
from src.core import *
from src.env import env
from src.database import init_db

DB_PATH = env['core']['db_path']

def run_server(port):
    HOST = '0.0.0.0'
    PORT = int(port)
    sockx = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockx.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sockx.bind((HOST, PORT))
    sockx.listen(100)
    print(f"[{c.GREEN}Server{c.R}] Started successfully.")
    while True:
        sock, addr = sockx.accept()
        threading.Thread(target=core.login, args=(sock, addr), daemon=True).start()

# - - - - - -
# - - - - - -
# end
# - - - - - -
# - - - - - -

if __name__ == "__main__":
    if os.path.exists('Settings/config.json') and os.path.exists('Settings/funnel.json'):
        print(f'[{c.GREEN}Server{c.R}] Configs, funnels and logins exist.')
        if not os.path.exists(DB_PATH):
            print(f'[{c.YELLOW}Server{c.R}] Database not found, creating!')
            init_db()
        print(f'[{c.GREEN}Server{c.R}] Loading configs...')
        reload()
        run_server(env['cnc'].get('port'))
    else:
        print(f'[{c.RED}Fatal{c.R}] You don\'t have the main settings files(Settings/[config.json, funnel.json], {DB_PATH}).')
