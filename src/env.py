import time

env = {
    'core': {
        'server-key': 'server.key',
        'host-key': None,
        'db_path': 'Database/lunnaDB.db',
        'ssh-banner': 'SSH-2.0-LunnaSSHservice_2.0',
        'security-level': 0,
        'errors': {}
    },
    'users': {
        'clients': {},
        'roots': [],
        'vips': [],
        'user-command-history': {}
    }, 
    'cnc': {
        'uptime': time.time(),
        'blacklist': [],
        'commands': {},
        'aliases': {},
        'command-line': '',
        'default_banners': {},
        'fakebots': {},
        'MOTD': '',
        'name': '',
        'ongoing_color': '',
        'rate-limit-mc': '' # rate limit minimun time.
    },
    'funnel': {
        'prefix': '',
        'minimum_time': 0,
        'methods': {}
    },
    "blacklist": []
}
