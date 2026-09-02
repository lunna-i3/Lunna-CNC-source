import src.commands as commands
from src.utils import reload
COMMANDS = {
        "clear": {
            "def": commands.clear,
            "needs": ["sock"]
        },

        "exit": {
            "def": commands.exit,
            "needs": ["sock", "user"]
        },

        "echo": {
            "def": commands.echo,
            "needs": ["sock", "receive", "user"]
        },

        "history": {
            "def": commands.history,
            "needs": ["sock", "user"]
        },

        "debug": {
            "def": commands.debug,
            "needs": ["sock", "command"],
            "permissions": ["admin"]
        },

        "users": {
            "def": commands.user_manager,
            "needs": ["sock", "receive", "command", 'user'],
            "permissions": ['admin']
        },

        "reload": {
            "def": reload,
            "needs": ["sock", "user"],
            "permissions": ['admin']
        },

        "check-host": {
            "def": commands.check_host,
            "needs": ["sock", "user", "command"]
        },

        "ongoing": {
            "def": commands.ongoing,
            "needs": ["sock", "user"]
        }
    }