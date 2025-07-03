# licensed @2025 Stefan Kilber - PyCharm Professional - PyShellOS-1.1-Beta

import json
import time
from datetime import datetime
import random
import shutil
import platform
import urllib.request
import os
import sys
import threading
import time
from itertools import repeat
from os import CLONE_VM
from random import choice

import json
import os

def get_current_language_from_virtual_fs():
    fs_path = "data/filesystem.json"
    lang_data_path = "data/languages.json"

    if not os.path.exists(fs_path):
        raise FileNotFoundError("filesystem.json nicht gefunden")

    with open(fs_path, "r", encoding="utf-8") as f:
        fs = json.load(f)

    try:
        # Sprache als string direkt
        lang_code = fs["/"]["lib-usr"]["current_language"]
        if not isinstance(lang_code, str):
            raise ValueError("Sprache muss ein String sein (z. B. 'en', 'de')")
    except Exception as e:
        raise ValueError(f"Fehler beim Lesen der Sprache aus filesystem.json: {e}")

    if not os.path.exists(lang_data_path):
        raise FileNotFoundError("languages.json nicht gefunden")

    with open(lang_data_path, "r", encoding="utf-8") as f:
        all_languages = json.load(f)

    if lang_code not in all_languages:
        raise ValueError(f"Sprache '{lang_code}' nicht in languages.json gefunden")

    return all_languages[lang_code]




CURRENT_THEME_COLOR = "\033[1;32m"
THEMES = {
    "green": "\033[1;32m",
    "yellow": "\033[1;93m",
    "red": "\033[1;91m",
    "blue": "\033[1;94m",
    "magenta": "\033[1;95m",
    "cyan": "\033[1;96m",
    "white": "\033[1;97m",
    "grey": "\033[1;90m"
}

THEME_SYMBOLS = {
    "ROUNDED_INFO": "├",
    "ROUNDED_LINE": "─",
    "ROUNDED_TOP": "╭",
    "ROUNDED_SIDE": "│",
    "ROUNDED_BOTTOM": "╰",

    "THIN_INFO": "├",
    "THIN_LINE": "─",
    "THIN_TOP": "┌",
    "THIN_SIDE": "│",
    "THIN_BOTTOM": "└",

    "THICK_INFO": "┣",
    "THICK_LINE": "━",
    "THICK_TOP": "┏",
    "THICK_SIDE": "┃",
    "THICK_BOTTOM": "┗",

    "DOUBLE_INFO": "╠",
    "DOUBLE_LINE": "═",
    "DOUBLE_TOP": "╔",
    "DOUBLE_SIDE": "║",
    "DOUBLE_BOTTOM": "╚"
}

if os.path.exists("data/filesystem.json"):
    with open("data/filesystem.json", "r") as f:
        fs = json.load(f)
    try:
        saved_theme = fs["/"]["lib-usr"]["current_theme"]
        CURRENT_THEME_COLOR = saved_theme
    except (KeyError, TypeError):
        pass
else:
    fs = {
        "/": {
            "lib-usr": {
                "current_theme": CURRENT_THEME_COLOR
            }
        }
    }


FILESYSTEM_PATH = "data/filesystem.json"

with open("data/filesystem.json", "r") as f:
    fs = json.load(f)

libusr = fs["/"]["lib-usr"]
theme_id = libusr.get("current_theme_id", "1")
theme = libusr.get("themes", {}).get(theme_id)

if not theme:
    raise ValueError(f"Theme ID {theme_id} not found in /lib-usr/themes")

CURRENT_LINE_THEME   = THEME_SYMBOLS.get(theme.get("LINE"))
CURRENT_TOP_THEME    = THEME_SYMBOLS.get(theme.get("TOP"))
CURRENT_SIDE_THEME   = THEME_SYMBOLS.get(theme.get("SIDE"))
CURRENT_BOTTOM_THEME = THEME_SYMBOLS.get(theme.get("BOTTOM"))
CURRENT_INFO_THEME   = THEME_SYMBOLS.get(theme.get("INFO"))


def load_current_theme(fs):
    theme_id = fs["/"]["lib-usr"].get("current_theme_id", "1")
    theme_def = fs["/"]["lib-usr"]["themes"].get(theme_id)
    return {
        "LINE": THEME_SYMBOLS[theme_def["LINE"]],
        "TOP": THEME_SYMBOLS[theme_def["TOP"]],
        "SIDE": THEME_SYMBOLS[theme_def["SIDE"]],
        "BOTTOM": THEME_SYMBOLS[theme_def["BOTTOM"]]
    }

def save_filesystem(fs):
    with open(FILESYSTEM_PATH, "w") as f:
        json.dump(fs, f, indent=2)

ENCODE_MAP = {
    "!": "heK", "?": "Evt", ".": "Wpa", "1": "gr", "2": "0w", "3": "s7", "4": "92j", "@": "qJs", "&": "Zbg", "-": "mMg", "a": "0b", "A": "0B", "b": "ab", "B": "AB", "c": "Bd", "5": "a0", "6": "64", "7": "362", "8": "he", "9": "s", "0": "b", "C": "BD", "d": "cE", "D": "CE", "e": "df", "E": "DF", "f": "eg", "F": "EG", "g": "fh", "G": "FH", "h": "gi", "H": "GI", "i": "hj", "I": "HJ", "j": "ik", "J": "IK", "r": "qs", "R": "QS", "s": "rt", "S": "RT", "t": "su", "T": "SU", "u": "tv", "U": "TV", "v": "uw", "V": "UW", "w": "vx", "W": "VX", "x": "wy", "X": "WY", "y": "xz", "Y": "XZ",  "k": "jl", "K": "JL", "l": "km", "L": "KM", "m": "ln", "M": "LN", "n": "mo", "N": "MO", "o": "np", "O": "NP", "p": "oq", "P": "OQ", "q": "pr", "Q": "PR", "z": "yA", "Z": "YA",
}

def encode_password_custom(password):
    result = ""
    for char in password:
        result += ENCODE_MAP.get(char, char)
    return result


DECODE_MAP = {v: k for k, v in ENCODE_MAP.items()}

def decode_password_custom(encoded):
    decoded = ""
    i = 0
    while i < len(encoded):
        match = None
        for length in sorted({len(k) for k in DECODE_MAP}, reverse=True):
            part = encoded[i:i+length]
            if part in DECODE_MAP:
                decoded += DECODE_MAP[part]
                i += length
                match = True
                break
        if not match:
            decoded += encoded[i]
            i += 1
    return decoded



def autosave_fs(interval=10):
    while True:
        time.sleep(interval)
        with open("data/filesystem.json", "w") as f:
            json.dump(fs, f, indent=4)


threading.Thread(target=autosave_fs, daemon=True).start()


def update_main_py_and_restart():
    main_url = "https://raw.githubusercontent.com/StefanMarston/PyShellOS/main/main.py"
    fs_url = "https://raw.githubusercontent.com/StefanMarston/PyShellOS/main/data/filesystem.json"
    local_path = os.path.abspath(sys.argv[0])
    fs_path = os.path.join(os.path.dirname(local_path), "data", "filesystem.json")


    print("[ ✓ ] fetching update...")
    time.sleep(random.randint(1, 3))  # Etwas kürzer, sonst nervt es beim Testen


    # main.py herunterladen und ersetzen
    urllib.request.urlretrieve(main_url, local_path)
    print("[ ✓ ] System was updated.")


    # filesystem.json mit Erhalt von .userdata aktualisieren
    def merge_filesystem_userdata(fs_url, fs_path):
        # Bestehende userdata laden
        if os.path.exists(fs_path):
            with open(fs_path, "r") as f:
                local_fs = json.load(f)
            local_userdata = local_fs.get("/", {}).get(".etc", {}).get(".userdata", {})
        else:
            local_userdata = {}


        # Neue Datei von GitHub laden
        with urllib.request.urlopen(fs_url) as response:
            new_fs = json.load(response)


        # userdata mergen
        if "/" in new_fs and ".etc" in new_fs["/"]:
            new_fs["/"][".etc"][".userdata"] = local_userdata
        else:
            print("[ ! ]: New filesystem.json is corrupted!")


        # Neue Version speichern
        os.makedirs(os.path.dirname(fs_path), exist_ok=True)
        with open(fs_path, "w") as f:
            json.dump(new_fs, f, indent=4)
        print("[ ✓ ] filesystem.json was updated.")


    merge_filesystem_userdata(fs_url, fs_path)


    print("[ ✓ ] Update successful. Rebooting...")
    time.sleep(2)
    os.execv(sys.executable, [sys.executable] + sys.argv)



# Add these global variables at the top of the file
# Initialize with only root user
CURRENT_USER = None  # Will be set during first boot or login
USERS = {
    "root": {"password": "root"}
}


# === Load virtual filesystem ===
with open("data/filesystem.json", "r") as f:
    fs = json.load(f)


cwd = ["/"]  # current working directory as list
USER = "user"
LOGGED_IN = True
CLIPBOARD = None


# Add this after the other global variables (CURRENT_USER, USERS, etc.)
# but before any function definitions


# Initialize empty commands dictionary
commands = {}


# Security variables
SUDO_ATTEMPT_COUNTER = 0
SUDO_LOCKED_UNTIL = 0


def get_dir(path_list):
    d = fs["/"]
    for p in path_list[1:]:
        d = d.get(p, {})
    return d


def repair():
    global CURRENT_THEME_COLOR
    while True:
        print(CURRENT_TOP_THEME + CURRENT_THEME_COLOR + "\033[1m" + "Repair PyShellOS" + "\033[0m" + CURRENT_LINE_THEME * 30)
        print(CURRENT_INFO_THEME + CURRENT_THEME_COLOR + "  Repair PyShellOS" + "\033[0m")
        print(CURRENT_SIDE_THEME)
        choice = input(CURRENT_INFO_THEME + "   Select option (1-2): ").strip()


        if choice == "1":
            update_main_py_and_restart()
        elif choice == "2":
            break
        else:
            print("Invalid option")


def set_dir_value(path_list, value):
    """Set a value in the virtual filesystem at the specified path."""
    d = fs["/"]
    for p in path_list[1:-1]:
        d = d.get(p, {})
    d[path_list[-1]] = value


def has_permission(path_name):
    """Check if user has permission to access a file/directory."""
    global CURRENT_USER
    # Root can access everything
    if CURRENT_USER == "root" or is_sudo_active():
        return True


    # Check for home directory access
    if path_name.startswith('.') and path_name != f".{CURRENT_USER}":
        return False


    return True


# Update is_sudo_active function
def is_sudo_active():
    """Check if we
    """
    global SUDO_MODE
    return SUDO_MODE


SUDO_MODE = False  # Global variable to track sudo status


def sudo(args):
    """Execute command with root privileges."""
    if len(args) < 1:
        print("sudo: Missing command")
        return


    # Check if sudo is temporarily locked
    global SUDO_ATTEMPT_COUNTER, SUDO_LOCKED_UNTIL
    current_time = time.time()


    if current_time < SUDO_LOCKED_UNTIL:
        remaining_time = int(SUDO_LOCKED_UNTIL - current_time)
        print(f"sudo: Authentication locked for {remaining_time} more seconds due to too many failed attempts")
        return


    # Reset lock if it has expired
    if current_time > SUDO_LOCKED_UNTIL and SUDO_ATTEMPT_COUNTER >= 3:
        SUDO_ATTEMPT_COUNTER = 0


    try:
        stored_password = get_dir(["/", ".root"])[".sudopswd"]
    except:
        print("sudo: Cannot access sudo password file")
        return


    input_password = input("[sudo] password for user: ")
    if input_password != stored_password:
        SUDO_ATTEMPT_COUNTER += 1
        attempts_left = 3 - SUDO_ATTEMPT_COUNTER


        if SUDO_ATTEMPT_COUNTER >= 3:
            # Lock sudo for 60 seconds after 3 failed attempts
            SUDO_LOCKED_UNTIL = current_time + 60
            print(f"sudo: Authentication failed - too many attempts. Locked for 60 seconds.")
        else:
            print(f"sudo: Incorrect password. {attempts_left} attempt{'s' if attempts_left > 1 else ''} remaining.")
        return


    # Reset counter on successful authentication
    SUDO_ATTEMPT_COUNTER = 0


    global SUDO_MODE
    SUDO_MODE = True  # Enable sudo mode


    cmd = args[0]


    # Special handling for 'su' command
    if cmd == "su":
        if len(args) < 2:
            print("sudo su: Missing username")
            SUDO_MODE = False
            return
        username = args[1]
        global CURRENT_USER
        CURRENT_USER = username
        print(f"Switched to user: {username}")
        SUDO_MODE = False
        return


    # Handle other commands
    if cmd in commands:
        try:
            commands[cmd](args[1:])
        finally:
            SUDO_MODE = False  # Disable sudo mode after command execution
    else:
        SUDO_MODE = False  # Disable sudo mode if command not found
        print(f"sudo: command '{cmd}' not found")


def ls(args):
    """List directory contents with optional flags."""
    d = get_dir(cwd)
    show_all = "-a" in args or is_sudo_active()

    # Filter items based on permissions
    visible_items = {k: v for k, v in d.items()
                    if show_all or has_permission(k)}

    if not args or (len(args) == 1 and "-a" in args):
        print("  ".join(visible_items.keys()))
        return


    if "-l" in args:  # detailed listing
        for item in visible_items.keys():
            type_marker = "d" if isinstance(d[item], dict) else "f"
            size = len(str(d[item])) if isinstance(d[item], str) else 0
            ownership = "root" if item.startswith('.') else "user"
            print(f"{type_marker}  {ownership:6s}  {size:4d} bytes  {item}")


def cd(args):
    global cwd
    if len(args) < 1:
        print("cd: Not a directory!")
        return
    target = args[0]


    if target == "~" or target == "/":
        cwd = ["/"]
        return
    elif target == "..":
        if len(cwd) > 1:
            cwd.pop()
    elif target in get_dir(cwd):
        if not has_permission(target):
            print(f"cd: Permission denied: '{target}'")
            return
        if isinstance(get_dir(cwd)[target], dict):
            cwd.append(target)
        else:
            print("cd: Not a target directory:", target)
    else:
        print("cd: Couldn't find directory:", target)


def cat(args):
    if len(args) < 1:
        print("cat: Nothing to show")
        return
    name = args[0]
    d = get_dir(cwd)


    if not has_permission(name):
        print(f"cat: Permission denied: '{name}'")
        return


    if name in d and isinstance(d[name], str):
        if "-n" in args:  # show line numbers
            for i, line in enumerate(d[name].split('\n'), 1):
                print(f"{i:4d}  {line}")
        else:
            print(d[name])
    else:
        print("cat: Couldn't find file:", name)


def echo(args):
    """Echo text and optionally write to file."""
    if len(args) < 1:
        return


    text = " ".join(args)
    redirect_idx = -1


    if ">" in args:
        redirect_idx = args.index(">")
        text = " ".join(args[:redirect_idx])


    if redirect_idx != -1 and len(args) > redirect_idx + 1:
        filename = args[redirect_idx + 1]
        if not filename.endswith('.txt'):
            print("echo: Only .txt files are supported")
            return
        d = get_dir(cwd)
        d[filename] = text
    else:
        print(text)


def pwd(args):
    """Print working directory."""
    path = "/" if len(cwd) == 1 else "/" + "/".join(cwd[1:])
    print(path)


def date(args):
    """Show current date and time."""
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


# Update get_current_username function
def get_current_username():
    """Get the current username"""
    global CURRENT_USER
    return CURRENT_USER


def whoami(args):
    """Show current user."""
    print(get_current_username())


def clear(args):
    """Clear screen."""
    print("\n" * 50)


def cp(args):
    """Copy file to another location."""
    if len(args) < 2:
        print("cp: Missing source or destination")
        return

    source, dest = args[0], args[1]
    d = get_dir(cwd)

    if source not in d:
        print(f"cp: Cannot copy '{source}': No such file")
        return

    if not isinstance(d[source], str):
        print("cp: Can only copy files")
        return

    d[dest] = d[source]


def mv(args):
    """Move/rename file."""
    if len(args) < 2:
        print("mv: Missing source or destination")
        return


def grep(args):
    """Search for pattern in file."""
    if len(args) < 2:
        print("grep: Missing pattern or file")
        return

    pattern, filename = args[0], args[1]
    d = get_dir(cwd)

    if filename not in d or not isinstance(d[filename], str):
        print(f"grep: Cannot read '{filename}'")
        return

    for line in d[filename].split('\n'):
        if pattern in line:
            print(line)


def wc(args):
    """Count lines, words, and characters in file."""
    if len(args) < 1:
        print("wc: Missing file")
        return

    filename = args[0]
    d = get_dir(cwd)

    if filename not in d or not isinstance(d[filename], str):
        print(f"wc: Cannot read '{filename}'")
        return

    content = d[filename]
    lines = content.count('\n') + 1
    words = len(content.split())
    chars = len(content)
    print(f"{lines:4d} {words:4d} {chars:4d} {filename}")


def df(args):
    """Show filesystem usage."""
    total_size = 1000000  # simulate 1MB total size
    used = sum(len(str(v)) for v in get_dir(["/"]).values())
    free = total_size - used
    print(f"Filesystem Size: {total_size} bytes")
    print(f"Used: {used} bytes")
    print(f"Free: {free} bytes")
    print(f"Use%: {(used / total_size) * 100:.1f}%")


def tree(args, prefix=""):
    """Show directory structure in tree format."""
    d = get_dir(cwd)
    items = list(d.items())

    for i, (name, content) in enumerate(items):
        is_last = i == len(items) - 1
        print(f"{prefix}{'└── ' if is_last else '├── '}{name}")
        if isinstance(content, dict):
            new_prefix = prefix + ('    ' if is_last else '│   ')
            cwd.append(name)
            tree(args, new_prefix)
            cwd.pop()


def find(args):
    """Find files by name pattern."""
    if len(args) < 1:
        print("find: Missing pattern")
        return

    pattern = args[0]

    def search_dir(d, path=""):
        for name, content in d.items():
            current_path = f"{path}/{name}"
            if pattern in name:
                print(current_path)
            if isinstance(content, dict):
                search_dir(content, current_path)

    search_dir(get_dir(["/"]))


def touch(args):
    if len(args) < 1:
        print("touch: Missing file name")
        return
    filename = args[0]
    if not filename.endswith('.txt'):
        print("touch: Only .txt files are supported")
        return
    d = get_dir(cwd)
    if filename in d:
        print(f"touch: Cannot create file '{filename}': Already exists")
        return
    d[filename] = ""


def mkdir(args):
    if len(args) < 1:
        print("mkdir: Missing directory name")
        return
    dirname = args[0]
    d = get_dir(cwd)
    if dirname in d:
        print(f"mkdir: Cannot create directory '{dirname}': Already exists")
        return
    d[dirname] = {}


def rm(args):
    if len(args) < 1:
        print("rm: Missing file/directory name")
        return

    force = "-f" in args
    if "-f" in args:
        args.remove("-f")

    name = args[0]
    d = get_dir(cwd)

    if name not in d:
        if not force:
            print(f"rm: Cannot remove '{name}': No such file or directory")
        return

    if isinstance(d[name], dict) and not force:
        confirm = input(f"rm: Remove directory '{name}'? (y/N): ")
        if confirm.lower() != 'y':
            return

    del d[name]

def own(args):
    """Take ownership of a file/directory (remove dot prefix)."""
    if len(args) < 1:
        print("own: Missing file/directory name")
        return

    name = args[0]
    d = get_dir(cwd)

    if not name.startswith('.'):
        print(f"own: '{name}' is already owned by user")
        return

    if name not in d:
        print(f"own: Cannot find '{name}'")
        return

    # Only normal users can own files (remove dot)
    if is_sudo_active():
        print("own: Root user cannot own files")
        return

    new_name = name[1:]  # Remove the dot
    d[new_name] = d[name]
    del d[name]
    print(f"Successfully owned '{name}' as '{new_name}'")

def disown(args):
    """Remove ownership of a file/directory (add dot prefix)."""
    if len(args) < 1:
        print("disown: Missing file/directory name")
        return

    name = args[0]
    d = get_dir(cwd)

    if name.startswith('.'):
        print(f"disown: '{name}' is already owned by root")
        return

    if name not in d:
        print(f"disown: Cannot find '{name}'")
        return

    # Only normal users can disown their files
    if is_sudo_active():
        print("disown: Root user cannot disown files")
        return

    new_name = f".{name}"
    d[new_name] = d[name]
    del d[name]
    print(f"Successfully disowned '{name}' as '{new_name}'")

def su(args):
    """Switch user command - only accessible through sudo"""
    print("su: Permission denied (use 'sudo su username' instead)")
    return

def adduser(args):
    """Add a new user (requires sudo)"""
    if not is_sudo_active():
        print("adduser: Permission denied (requires sudo)")
        return

    if len(args) < 1:
        print("adduser: Missing username")
        return

    username = args[0]

    if username in USERS:
        print(f"adduser: User '{username}' already exists")
        return

    password = input("Enter new password: ")
    confirm = input("Retype new password: ")

    if password != confirm:
        print("adduser: Passwords do not match")
        return

    # Add user to USERS dictionary
    USERS[username] = {"password": encode_password_custom(password)}

    # Create user directory structure in .etc/.userdata
    userdata_path = get_dir(["/", ".etc", ".userdata"])
    userdata_path[f".{username}"] = {
        ".username": username,
        ".password": encode_password_custom(password)
    }

    # Handle home directory creation
    home_path = get_dir(["/", "home"])

    # First time: rename default user directory to make it hidden
    if "user" in home_path:
        user_content = home_path["user"]
        home_path[".User"] = user_content  # Changed to .User to match the default user name
        del home_path["user"]

    # Create new user's home directory (hidden)
    home_path[f".{username}"] = {
        "welcome.txt": f"Welcome {username} to PyShellOS!"
    }

    print(f"adduser: User '{username}' created successfully")
    print(f"Home directory created at /home/.{username}/")

def sudo_su(args):
    """Sudo implementation of su command"""
    global CURRENT_USER

    if len(args) < 1:
        print("sudo su: Missing username")
        return

    username = args[0]

    if username not in USERS:
        print(f"sudo su: User '{username}' does not exist")
        return

    CURRENT_USER = username
    print(f"Switched to user: {username}")

def help_cmd(args):
    print("Available commands:")
    print("  ls [-l]    - List directory contents")
    print("  cd <dir>   - Change directory (cd ~ for home)")
    print("  pwd        - Print working directory")
    print("  cat [-n] <file> - Show file contents")
    print("  echo [text] [> file] - Echo text or write to file")
    print("  mkdir <dir>- Create directory")
    print("  touch <file>- Create file")
    print("  rm [-f] <name> - Remove file/directory")
    print("  cp <src> <dst> - Copy file")
    print("  mv <src> <dst> - Move/rename file")
    print("  grep <pattern> <file> - Search in file")
    print("  wc <file>  - Count lines/words/chars")
    print("  tree       - Show directory tree")
    print("  find <pattern> - Find files")
    print("  date       - Show date/time")
    print("  whoami     - Show current user")
    print("  clear      - Clear screen")
    print("  df         - Show filesystem usage")
    print("  sudo <cmd> - Run as superuser (3 attempts limit)")
    print("  su <user>  - Switch user")
    print("  adduser <user> - Add a new user (sudo required)")
    print("  help       - Show this help")
    print("  exit       - Exit shell")
    print("  own <file>  - Take ownership of a file (remove dot prefix)")
    print("  disown <file> - Remove ownership of a file (add dot prefix)")
    print("  settings    - Open settings application")
    print("  nano <file> - Text editor")
    print("  logout     - Logout current user")
    print("  reboot     - Restart the system")
    print("  users      - Show all users (sudo required)")
    print("  security   - Show security features (sudo required)")
    print("  neofetch   - Show system information")

    if len(args) > 0 and args[0] == "security":
        print("\nSecurity Features:")
        print("  - Login attempts are limited to 3 tries before temporary lockout")
        print("  - Sudo privileges require password and are also limited to 3 attempts")
        print("  - Hidden files (prefixed with '.') are only accessible to their owners")
        print("  - System files are protected from unauthorized access")


def shell():
    lang = get_current_language_from_virtual_fs()
    global CURRENT_THEME_COLOR, CURRENT_USER
    print(lang["help_info"])

    while LOGGED_IN:
        current_user = get_current_username()
        path = "/" if len(cwd) == 1 else "/" + "/".join(cwd[1:])
        print( CURRENT_THEME_COLOR + f"╔═({current_user}@pyos)═[{path}]")
        prompt = "╚═" + "\033[0m$"
        try:
            cmd_input = input(prompt).strip()
            if not cmd_input:
                continue
            parts = cmd_input.split()
            cmd, args = parts[0], parts[1:]

            if cmd == "exit":
                print("Shutting down!")
                break
            elif cmd in commands:
                commands[cmd](args)
            else:
                print(lang["help_info_error_main"] + f"{cmd}" + lang["help_info_error"])
        except KeyboardInterrupt:
            print("\nUse 'exit' to shutdown system")
        except Exception as e:
            print(f"Error: {str(e)}")

# Also update the settings function to reflect changes immediately
def parse_path(path):
    """Convert a path string to a path list."""
    if path.startswith('/'):
        parts = [p for p in path.split('/') if p]
        return ["/"] + parts
    else:
        return cwd + [p for p in path.split('/') if p]

def nano(args):
    """Simple text editor."""
    if len(args) < 1:
        print("nano: Missing filename")
        return

    filename = args[0]
    path_parts = parse_path(filename)
    filename = path_parts[-1]
    directory = path_parts[:-1]

    if not filename.endswith('.txt'):
        print("nano: Only .txt files are supported")
        return

    try:
        d = get_dir(directory)

        # Check permissions
        if not has_permission(filename):
            print(f"nano: Permission denied: '{filename}'")
            return

        if filename in d and not isinstance(d[filename], str):
            print(f"nano: '{filename}' is not a text file")
            return

        # Show current content or empty string for new files
        content = d.get(filename, "")

        # Show instructions
        print("┌Nano text Editor─┬────────┬─────────────┬─────────────────┬────────────┬───────────────────┐")
        print("│  Instructions:  │ Enter  │     :sv     │      :sn        │   :clear   │       :del        │")
        print("│                 │ Output │ save & exit │ exit w/o saving │ clear file │ del previous line │")
        print("│                 └────────┴─────────────┴─────────────────┴────────────┴───────────────────┘")
        print(f"└Current content of {filename}:")

        if content:
            print(content)

        # Edit mode
        lines = []
        if content:
            lines = content.split('\n')

        while True:
            try:
                line = input()
                if line == ':sv':
                    # Save and exit
                    new_content = '\n'.join(lines)
                    d[filename] = new_content
                    print(f"File '{filename}' saved")
                    break
                elif line == ':sn':
                    # Exit without saving
                    confirm = input("Exit without saving? (y/N): ")
                    if confirm.lower() == 'y':
                        break
                    continue
                elif line == ':clear':
                    # Clear all text
                    lines = []
                    print("All text cleared")
                    continue
                elif line == ':del':
                    # Delete last line
                    if lines:
                        removed = lines.pop()
                        print(f"Removed line: {removed}")
                    else:
                        print("No lines to remove")
                    continue
                lines.append(line)
            except KeyboardInterrupt:
                # Handle Ctrl+C
                print("\nUse ':sn' to exit or ':sy' to save and exit")
                continue
            except EOFError:
                # Handle Ctrl+D
                break

    except Exception as e:
        print(f"nano: Error accessing file: {str(e)}")

def login():
    """Handle user login process."""
    global CURRENT_USER, LOGGED_IN

    # Initialize login attempt counters
    login_attempts = {}
    max_attempts = 3
    lockout_time = 60  # seconds

    while True:
        print("\nWelcome to PyShellOS!")
        username = input("Username: ").strip()

        # Check if username exists
        if username not in USERS:
            print("User not found!")
            continue

        # Check if this user is locked out
        if username in login_attempts and 'locked_until' in login_attempts[username]:
            current_time = time.time()
            if current_time < login_attempts[username]['locked_until']:
                remaining_time = int(login_attempts[username]['locked_until'] - current_time)
                print(f"User locked. Try again in {remaining_time} seconds.")
                time.sleep(1)  # Small delay to prevent rapid retries
                continue
            else:
                # Reset attempts if lockout period is over
                if username in login_attempts:
                    login_attempts[username] = {'attempts': 0}


        # Initialize attempt counter for this user if not already done
        if username not in login_attempts:
            login_attempts[username] = {'attempts': 0}

        password = input("Password: ").strip()
        if password != decode_password_custom(USERS[username]["password"]):
            # Increment failed attempts
            login_attempts[username]['attempts'] += 1
            attempts_left = max_attempts - login_attempts[username]['attempts']

            if login_attempts[username]['attempts'] >= max_attempts:
                # Lock the account
                login_attempts[username]['locked_until'] = time.time() + lockout_time
                print(f"Too many failed attempts. User locked for {lockout_time} seconds.")
            else:
                print(f"Incorrect password! {attempts_left} attempt{'s' if attempts_left > 1 else ''} remaining.")
            continue

        # Reset attempt counter on successful login
        if username in login_attempts:
            login_attempts[username] = {'attempts': 0}

        CURRENT_USER = username
        LOGGED_IN = True
        print(f"\nLogged in as {username}")
        break

def logout(args):
    """Logout current user and show login prompt."""
    global CURRENT_USER, LOGGED_IN
    if len(args) > 0:
        print("logout: too many arguments")
        return

    print(f"Logging out user: {CURRENT_USER}")
    CURRENT_USER = None
    LOGGED_IN = False
    login()

def reboot(args):
    global CURRENT_THEME_COLOR
    """Reboot the system."""
    global CURRENT_USER, LOGGED_IN, fs, USERS, cwd

    print("System is rebooting...")
    time.sleep(1)

    # Reset current session
    CURRENT_USER = None
    LOGGED_IN = False
    cwd = ["/"]

    print("Booting PyShellOS...")
    time.sleep(1)

    # Check if this is a post-reset boot
    is_first_boot = check_first_boot()
    if is_first_boot:
        print("\nDetected first boot!")
        first_boot_setup()
    else:
        load_users()
        login()

    print(CURRENT_THEME_COLOR + "PyShellOS is ready!" + "\033[0m")
    print("Type 'help' for command list")

# Update settings function to use reboot after reset
def settings(args):
    global CURRENT_THEME_COLOR, THEME_SYMBOLS
    lang = get_current_language_from_virtual_fs()
    """Terminal-based settings application."""
    if not is_sudo_active():
        print("Settings can only be accessed with sudo privileges")
        return

    while True:
        current_user = get_current_username()
        print(CURRENT_TOP_THEME + CURRENT_THEME_COLOR + "\033[1m" + lang["settings"] + "\033[0m" + CURRENT_LINE_THEME * 21)
        print(CURRENT_SIDE_THEME)
        print(CURRENT_SIDE_THEME + lang["current_user_wording"] + CURRENT_THEME_COLOR + f"{current_user} " + "\033[0m" + lang["with_permission_wording"] + CURRENT_THEME_COLOR + f"{'system' if current_user == 'root' or 'none' == current_user == "None" else 'user'}" + "\033[0m")
        print(CURRENT_SIDE_THEME)
        print(CURRENT_INFO_THEME + "   " + CURRENT_THEME_COLOR + "1. " + lang["user_settings_option"] + "\033[0m")
        print(CURRENT_INFO_THEME + "   " + CURRENT_THEME_COLOR + "2. " + lang["general_settings_option"] + "\033[0m")
        print(CURRENT_INFO_THEME + "   " + CURRENT_THEME_COLOR + "3. " + lang["system_settings_option"] + "\033[0m")
        print(CURRENT_INFO_THEME + "   " + CURRENT_THEME_COLOR + "4. " + lang["update_settings_option"] + "\033[0m")
        print(CURRENT_INFO_THEME + "   " + CURRENT_THEME_COLOR + "5. " + lang["customize_settings_option"] + "\033[0m")
        print(CURRENT_SIDE_THEME)
        print(CURRENT_INFO_THEME + "   " + CURRENT_THEME_COLOR + "6. " + lang["return_shell_settings_option"] + "\033[0m")
        print(CURRENT_SIDE_THEME)
        print(CURRENT_BOTTOM_THEME + CURRENT_LINE_THEME * 49)

        choice = input(lang["option_6"]).strip()

        if choice == "1":
            user_settings()
        elif choice == "2":
            system_settings()
        elif choice == "3":
            system_info()
        elif choice == "4":
            update_settings()
        elif choice == "5":
            CustomizeSettings()
        elif choice == "6":
            print(lang["exit_settings"])
            break
        else:
            print(lang["Invalid_option"])

def CustomizeSettings():
    lang = get_current_language_from_virtual_fs()
    global CURRENT_THEME_COLOR
    while True:
        print(CURRENT_TOP_THEME + CURRENT_THEME_COLOR + "\033[1m" + lang["settings"] + "\033[0m" + CURRENT_LINE_THEME * 21)
        print(CURRENT_SIDE_THEME)
        print(CURRENT_INFO_THEME + CURRENT_THEME_COLOR +   " 1." + lang["change_system_color_settings"] + "\033[0m")
        print(CURRENT_INFO_THEME + CURRENT_THEME_COLOR +   " 2." + lang["change_app_style_settings"] + "\033[0m")
        print(CURRENT_SIDE_THEME)
        print(CURRENT_INFO_THEME + "   " + CURRENT_THEME_COLOR + " 3. " + lang["return_to_settings"] + "\033[0m")
        print(CURRENT_BOTTOM_THEME + CURRENT_LINE_THEME * 49)
        choice = input(lang["option_2"]).strip()

        if choice == "1":
            print(CURRENT_TOP_THEME + CURRENT_THEME_COLOR + "\033[1m" + lang["settings"] + "\033[0m" + CURRENT_LINE_THEME * 21)
            print(CURRENT_SIDE_THEME)
            print(CURRENT_INFO_THEME + CURRENT_THEME_COLOR + lang["green_color_custom_settings"] + "\033[0m")
            print(CURRENT_INFO_THEME + CURRENT_THEME_COLOR + lang["blue_color_custom_settings" + "\033[0m"])
            print(CURRENT_INFO_THEME + CURRENT_THEME_COLOR + lang["red_color_custom_settings"] + "\033[0m")
            print(CURRENT_INFO_THEME + CURRENT_THEME_COLOR + lang["yellow_color_custom_settings"] + "\033[0m")
            print(CURRENT_INFO_THEME + CURRENT_THEME_COLOR + lang["magenta_color_custom_settings"] + "\033[0m")
            print(CURRENT_INFO_THEME + CURRENT_THEME_COLOR + lang["cyan_color_custom_settings"] + "\033[0m")
            print(CURRENT_INFO_THEME + CURRENT_THEME_COLOR + lang["white_color_custom_settings"] + "\033[0m")
            print(CURRENT_INFO_THEME + CURRENT_THEME_COLOR + lang["grey_color_custom_settings"] + "\033[0m")
            print(CURRENT_BOTTOM_THEME + CURRENT_LINE_THEME * 49)

            theme_input = input(CURRENT_INFO_THEME + "   " + CURRENT_THEME_COLOR + lang["change_theme_input_custom_settings"] + "\033[0m").strip().lower()
            if theme_input in THEMES:
                CURRENT_THEME_COLOR = THEMES[theme_input]
                print(CURRENT_SIDE_THEME + lang["theme_success_custom_settings"] + CURRENT_THEME_COLOR + f"{theme_input}." + "\033[0m")
                if "/" not in fs:
                    fs["/"] = {}
                if "lib-usr" not in fs["/"]:
                    fs["/"]["lib-usr"] = {}
                fs["/"]["lib-usr"]["current_theme"] = CURRENT_THEME_COLOR
                with open("data/filesystem.json", "w") as f:
                    json.dump(fs, f, indent=4)
            else:
                print("\033[1;91m" + CURRENT_SIDE_THEME + lang["theme_error_custom_settings_unknown"] + "\033[0m")
            break

        elif choice == "2":
            print(
                CURRENT_TOP_THEME + CURRENT_THEME_COLOR + "\033[1m" + lang["apps_settings_wording"] + "\033[0m" + CURRENT_LINE_THEME * 23)
            print(CURRENT_SIDE_THEME)
            print(CURRENT_INFO_THEME + CURRENT_THEME_COLOR + "  1.     " + lang["apps_settings_rounded_boarders_wording"] + "\033[0m")
            print(CURRENT_INFO_THEME + " ╭" + "─" * 10)
            print(CURRENT_INFO_THEME + " │")
            print(CURRENT_INFO_THEME + " ├" + CURRENT_THEME_COLOR + lang["apps_settings_description_wording"] + "\033[0m")
            print(CURRENT_INFO_THEME + " ╰" + "─" * 10)
            print(CURRENT_SIDE_THEME)
            print(CURRENT_INFO_THEME + CURRENT_THEME_COLOR + "  2.       " + lang["apps_settings_thin_boarders_wording"] +"\033[0m")
            print(CURRENT_INFO_THEME + " ┌" + "─" * 10)
            print(CURRENT_INFO_THEME + " │")
            print(CURRENT_INFO_THEME + " ├" + CURRENT_THEME_COLOR + lang["apps_settings_description_wording"] + "\033[0m")
            print(CURRENT_INFO_THEME + " └" + "─" * 10)
            print(CURRENT_SIDE_THEME)
            print(CURRENT_INFO_THEME + CURRENT_THEME_COLOR + "  3.      " + lang["apps_settings_thick_boarders_wording"] + "\033[0m")
            print(CURRENT_INFO_THEME + " ┏" + "━" * 10)
            print(CURRENT_INFO_THEME + " ┃")
            print(CURRENT_INFO_THEME + " ┣" + CURRENT_THEME_COLOR + lang["apps_settings_description_wording"] + "\033[0m")
            print(CURRENT_INFO_THEME + " ┗" + "━" * 10)
            print(CURRENT_SIDE_THEME)
            print(CURRENT_INFO_THEME + CURRENT_THEME_COLOR + "  4. " + lang["apps_settings_double_boarders_wording"] + "\033[0m")
            print(CURRENT_INFO_THEME + " ╔" + "═" * 10)
            print(CURRENT_INFO_THEME + " ║")
            print(CURRENT_INFO_THEME + " ╠" + CURRENT_THEME_COLOR + lang["apps_settings_description_wording"] + "\033[0m")
            print(CURRENT_INFO_THEME + " ╚" + "═" * 10)
            print(CURRENT_SIDE_THEME)
            print(CURRENT_INFO_THEME + CURRENT_THEME_COLOR + "  5. " + lang["return_to_settings"] + "\033[0m")
            print(CURRENT_BOTTOM_THEME + CURRENT_LINE_THEME * 49)
            choice = input(lang["option_5"]).strip()

            if choice == "5":
                break
            elif choice in ("1", "2", "3", "4"):
                fs["/"]["lib-usr"]["current_theme_id"] = choice
                save_filesystem(fs)
                load_current_theme(fs)
                print(lang["accepted_request_token"] + f"{choice}." + lang["reboot_request_changes"])
                break
            else:
                print("\033[91m" + lang["invalid_option"] + "\033[0m")


def system_info():
    lang = get_current_language_from_virtual_fs()
    global CURRENT_THEME_COLOR
    while True:
        print(CURRENT_TOP_THEME + CURRENT_THEME_COLOR + "\033[1m" + lang["system_info"] + "\033[0m" + CURRENT_LINE_THEME * 37)
        print(CURRENT_SIDE_THEME + CURRENT_THEME_COLOR + "             OS: PyShellOS-01.02-Beta"+"\033[0m")
        print(CURRENT_SIDE_THEME + CURRENT_THEME_COLOR + f"        MainOS: {platform.system()}-{platform.release()}"+"\033[0m")
        print(CURRENT_SIDE_THEME + CURRENT_THEME_COLOR + f"  Architecture: {platform.machine()}"+"\033[0m")
        print(CURRENT_SIDE_THEME + CURRENT_THEME_COLOR + f"        Python: {platform.python_version()}"+"\033[0m")
        print(CURRENT_SIDE_THEME + CURRENT_THEME_COLOR + "          Shell: PyshellOS-Terminal"+"\033[0m")
        print(CURRENT_SIDE_THEME + CURRENT_THEME_COLOR + "        Version: PyShellOS-3.1.Beta - The Customization Update"+"\033[0m")
        print(CURRENT_SIDE_THEME + CURRENT_THEME_COLOR + "         Python: Py3 - Python3 - Py3.1Rls"+"\033[0m")
        print(CURRENT_SIDE_THEME + CURRENT_THEME_COLOR + "      Publisher: Stefan Kilber"+"\033[0m")
        print(CURRENT_SIDE_THEME + CURRENT_THEME_COLOR + "           Help: https://github.com/StefanMarston/PyShellOS"+"\033[0m")
        print(CURRENT_SIDE_THEME)
        print(CURRENT_INFO_THEME + "   " + CURRENT_THEME_COLOR + "1. " + lang["user_settings"] + "\033[0m")
        print(CURRENT_INFO_THEME + "   " + CURRENT_THEME_COLOR + lang["general_settings_option"] + "\033[0m")
        print(CURRENT_INFO_THEME + "   " + CURRENT_THEME_COLOR + lang["return_to_settings"] + "\033[0m")
        print(CURRENT_SIDE_THEME)
        print(CURRENT_BOTTOM_THEME + CURRENT_LINE_THEME * 49)
        choice = input(lang["option_3"]).strip()

        if choice == "1":
            user_settings()
        elif choice == "2":
            system_settings()
        elif choice == "3":
            break
        else:
            print(lang["invalid_option"])

def user_settings():
    lang = get_current_language_from_virtual_fs()
    global CURRENT_THEME_COLOR
    """Handle user-related settings."""
    while True:
        current_user = get_current_username()
        print(CURRENT_TOP_THEME + CURRENT_THEME_COLOR + "\033[1m" + lang["user_settings"] + "\033[0m" + CURRENT_LINE_THEME * 34)
        print(CURRENT_SIDE_THEME)
        print(CURRENT_SIDE_THEME + lang["current_user_wording"] + CURRENT_THEME_COLOR + f"{current_user}" + "\033[0m")
        print(CURRENT_SIDE_THEME)
        print(CURRENT_INFO_THEME + "   " + CURRENT_THEME_COLOR + "1. " + lang["change_user_name"] + "\033[0m")
        print(CURRENT_INFO_THEME + "   " + CURRENT_THEME_COLOR + "2. " + lang["change_user_pass"] + "\033[0m")
        print(CURRENT_INFO_THEME + "   " + CURRENT_THEME_COLOR + "3. " + lang["change_user_auth"] + "\033[0m")
        print(CURRENT_INFO_THEME + "   " + CURRENT_THEME_COLOR + "4. " + lang["change_user_rmff"] + "\033[0m")
        print(CURRENT_SIDE_THEME)
        print(CURRENT_INFO_THEME + "   " + CURRENT_THEME_COLOR + "5. " + lang["return_to_settings"] + "\033[0m")
        print(CURRENT_SIDE_THEME)
        print(CURRENT_BOTTOM_THEME + CURRENT_LINE_THEME * 49)

        choice = input(lang["option_5"]).strip()

        if choice == "1":
            new_username = input(lang["change_user_name_input"]).strip()
            if new_username:
                if new_username in USERS:
                    print(lang["change_user_name_input_error_exist"])
                else:
                    USERS[new_username] = USERS[current_user]
                    del USERS[current_user]
                    global CURRENT_USER
                    CURRENT_USER = new_username
                    print(lang["change_user_name_input_success"])
            else:
                print(lang["change_user_name_input_error_empty"])

        elif choice == "2":
            new_password = input(lang["change_user_pass_input"]).strip()
            confirm_password = input(lang["change_user_pass_input_confirmation"]).strip()
            if not new_password:
                print(lang["change_user_pass_input_error_empty"])
            elif new_password != confirm_password:
                print(lang["change_user_pass_input_error_match"])
            else:
                USERS[current_user]["password"] = new_password
                print(lang["change_user_pass_input_success"])

        elif choice == "3":
            username = input(lang["change_user_name_input"]).strip()
            if username in USERS:
                print(lang["change_user_name_input_error_exist"])
            else:
                password = input(lang["password_enter"]).strip()
                confirm = input(lang["change_user_pass_input_confirmation"]).strip()
                if password != confirm:
                    print(lang["change_user_pass_input_error_match"])
                else:
                    USERS[username] = {"password": password}
                    print(lang["user_wording"] + f" {username}" + lang["created_successfully_wording"])

        elif choice == "4":
            username = input(lang["user_remove_option"]).strip()
            if username == "root":
                print(lang["user_remove_option_input_error_root"])
            elif username not in USERS:
                print(lang["user_remove_option_input_error_exist_false"])
            else:
                confirm = input(lang["user_remove_option_input_acceptance_request_token"] + f" {username}?" + lang["yes_no_request"]).strip().lower()
                if confirm == 'y':
                    del USERS[username]
                    print(lang["user_wording"] + f" {username}" + lang["user_remove_option_input_success"] )

        elif choice == "5":
            break
        else:
            print(lang["invalid_option"])

def update_settings():
    lang = get_current_language_from_virtual_fs()
    global CURRENT_THEME_COLOR
    while True:
        print("┌" + CURRENT_THEME_COLOR + "\033[1m" + lang["system_settings"] + "\033[0m" + "────────────────────────────────")
        print("│")
        print("├    " + lang["current_version_info_table"] + "PyShellOS-01.02-Beta")
        print("├   " + CURRENT_THEME_COLOR + "1. " + lang["update_version"] + "\033[0m")
        print("│")
        print("├   " + CURRENT_THEME_COLOR + "2. " + lang["return_to_settings"] + "\033[0m")
        print("│")
        print(CURRENT_BOTTOM_THEME + CURRENT_LINE_THEME * 49)

        choice = input(lang["option_2"]).strip()

        if choice == "1":
            update_main_py_and_restart()

        elif choice == "2":
            break
        else:
            print(lang["invalid_option"])


def system_settings():
    global CURRENT_THEME_COLOR,  CURRENT_APP_THEME
    lang = get_current_language_from_virtual_fs()
    """Handle system-related settings."""
    while True:
        print("┌" + CURRENT_THEME_COLOR + "\033[1m" + lang["system_settings"] + "\033[0m" + "────────────────────────────────")
        print("│")
        print("├   " + CURRENT_THEME_COLOR + "1. " + lang["system_settings_reset_option"] + "\033[0m" + "\033[0m")
        print("├   " + CURRENT_THEME_COLOR + "2. " + lang["system_settings_restart_option"] + "\033[0m" + "\033[0m")
        print("├   " + CURRENT_THEME_COLOR + "3. " + lang["system_settings_bulk_remove_option"] + "\033[0m" + "\033[0m")
        print("├   " + CURRENT_THEME_COLOR + "4. " + lang["system_settings_show_security_option"] + "\033[0m" + "\033[0m")
        print("├   " + CURRENT_THEME_COLOR + "5. " + lang["system_settings_show_theme_option"] + "\033[0m" + "\033[0m")
        print("│")
        print("├   " + CURRENT_THEME_COLOR + "6. " + lang["return_to_settings"] + "\033[0m")
        print("│")
        print(CURRENT_BOTTOM_THEME + CURRENT_LINE_THEME * 49)

        choice = input("\nSelect option (1-5): ").strip()

        if choice == "1":
            confirm = input("Are you sure you want to reset PyShellOS? This will erase all data! (type 'RESET' to confirm): ")
            if confirm == "RESET":
                print("\n[ " + f"\033[1;32m" + "✓ " + "\033[0m" + "] Initializing system...")
                time.sleep(random.randint(1, 2))
                print("[ " + f"\033[1;32m" + "✓ " + "\033[0m" + "] Mounting /Kernel")
                time.sleep(random.randint(1, 3))
                print("[ " + f"\033[1;32m" + "✓ " + "\033[0m" + "] Mounting /Boot")
                time.sleep(random.randint(1, 2))
                print("[ " + f"\033[1;32m" + "✓ " + "\033[0m" + "] Mounting /Home")
                time.sleep(random.randint(1, 1))
                print("[ " + f"\033[1;32m" + "✓ " + "\033[0m" + "] Extracting Kernel Level Files...")
                time.sleep(random.randint(1, 3))
                print("[ " + f"\033[1;32m" + "✓ " + "\033[0m" + "] Initializing Storage...")
                time.sleep(random.randint(1, 2))
                print("[ " + f"\033[1;32m" + "✓ " + "\033[0m" + "] Mounting /dev...")
                time.sleep(0.1)
                print("[ " + f"\033[1;32m" + "✓ " + "\033[0m" + "] Mounting /proc...")
                time.sleep(0.1)
                print("[ " + f"\033[1;32m" + "✓ " + "\033[0m" + "] Mounting /sys...")
                time.sleep(0.1)
                print("[ " + f"\033[1;32m" + "✓ " + "\033[0m" + "] Mounting /run...")
                time.sleep(0.1)
                print("[ " + f"\033[1;32m" + "✓ " + "\033[0m" + "] Mounting /home...")
                time.sleep(0.1)
                print("[ " + f"\033[1;32m" + "✓ " + "\033[0m" + "] Mounting /tmp...")
                time.sleep(0.1)
                print("[ " + f"\033[1;32m" + "✓ " + "\033[0m" + "] Mounting /etc...")
                time.sleep(0.4)
                print("[ " + f"\033[1;32m" + "✓ " + "\033[0m" + "] Mounting /var...")
                time.sleep(0.1)
                print("[ " + f"\033[1;32m" + "✓ " + "\033[0m" + "] Mounting /opt...")
                time.sleep(0.1)
                print("[ " + f"\033[1;32m" + "✓ " + "\033[0m" + "] Logging in as root...")
                time.sleep(random.randint(1, 3))
                print("[ " + f"\033[1;32m" + "✓ " + "\033[0m" + "] root executing /etc/..init/boot.py...")
                time.sleep(random.randint(1, 1))
                print("[ " + f"\033[1;32m" + "✓ " + "\033[0m" + "] root executing /Kernel/main/kernel.py...")
                time.sleep(0.1)
                print("[ " + f"\033[1;32m" + "✓ " + "\033[0m" + "] root disowning /Kernel...")
                time.sleep(random.randint(1, 1))
                print("[ " + f"\033[1;32m" + "✓ " + "\033[0m" + "] root disowning /Boot...")
                time.sleep(random.randint(1, 2))
                print("[ " + f"\033[1;32m" + "✓ " + "\033[0m" + "] Identifying Data")
                time.sleep(random.randint(1, 3))
                print("[ " + f"\033[1;32m" + "✓ " + "\033[0m" + "] Loading Archives")
                time.sleep(random.randint(1, 3))
                print("[ " + f"\033[1;32m" + "✓ " + "\033[0m" + "] Validating kernel Signature")
                time.sleep(random.randint(1, 3))
                global fs, USERS
                fs = {"/": {
        "trash": {},
        "bin": {
            "x11": {},
            ".[": {},
            ".7z": {},
            ".7zA": {},
            ".7zR": {},
            ".aConnect.txt": "cnct",
            ".add2line.txt": "x0010"
        },
        ".bin-usr": {},
        "boot": {
            ".efi": {
                "EFI": {
                    ".BOOT": {
                        ".bootx65.efi": {},
                        ".fbx64.efi": {},
                        ".mmx64.efi": {}
                    },
                    "PyShellOS": {
                        ".BOOTX64.CSV": {},
                        ".grub.cfg": {},
                        ".grub64.efi": {},
                        ".mmx64.efi": {},
                        ".shimx64.efi": {}
                    }
                }
            },
            ".kernel": {
                ".irq": {
                    ".0.txt": "false",
                    ".1.txt": "true"
                },
                "vmcoreinfo.txt": "vmcoreinfo // 0x0000000102612000 1024",
                "crashhandler.txt": "917616"
            },
            ".grub": {
                "fonts": {
                    "unicode.txt": "aAbBcCdDeEfFgGhHiIjJkKlLmMnNoOpPqQrRsStTuUvVwWxXyYzZ1234567890!\u00a7$%&/()=?`*'_:;,.-#+\u00b4"
                },
                "..locale": {
                    "HIDDEN_DATA": {},
                    "HIDDEN_DATAx": {}
                }
            },
            ".config-1.1-1.2-genericK.txt": "hidden data"
        },
        "cdrom": {},
        "dev": {
            "block": {},
            "bugrps": {},
            "..bus": {},
            "..char": {},
            ".console.txt": {},
            ".core.txt": {},
            ".full.txt": {},
            ".hpet,txt": {}
        },
        ".etc": {
            ".userdata": {
            }
        },
        "lib": {},
        "home": {
        },
        "lib-usr": {},
        "lib64": {},
        "media": {},
        "mnt": {},
        "opt": {},
        "proc": {
            "1": {},
            "2": {},
            "3": {},
            "4": {},
            "5": {},
            "6": {},
            "7": {},
            "8": {},
            "9": {},
            "10": {},
            "11": {},
            "12": {},
            "13": {},
            "14": {},
            "15": {},
            "16": {},
            "17": {},
            "18": {},
            "19": {},
            "20": {},
            "21": {},
            "22": {},
            "23": {},
            "24": {},
            "25": {},
            "26": {},
            "27": {},
            "28": {},
            "29": {},
            "30": {},
            "31": {},
            "32": {},
            "33": {},
            "34": {},
            "35": {},
            "36": {},
            "37": {},
            "38": {},
            "39": {},
            "40": {},
            "41": {},
            "42": {},
            "43": {},
            "44": {},
            "45": {},
            "46": {},
            "47": {},
            "48": {},
            "49": {},
            "50": {},
            "51": {},
            "52": {},
            "53": {},
            "54": {},
            "55": {},
            "56": {},
            "57": {},
            "58": {},
            "59": {},
            "60": {},
            "61": {},
            "62": {},
            "63": {},
            "64": {},
            "65": {},
            "66": {},
            "67": {},
            "69": {},
            "70": {},
            "71": {},
            "72": {},
            "73": {},
            "74": {},
            "75": {},
            "76": {},
            "77": {},
            "78": {},
            "79": {},
            "80": {},
            "81": {},
            "82": {},
            "83": {},
            "84": {},
            "85": {},
            "86": {}
        },
        ".root": {
            ".critical": "0x0000000102612000 1024",
            ".sudopswd": "root"
        },
        "run": {},
        "sbin": {},
        "sbin-usr": {},
        "snap": {},
        "lndk": {
            "Downloaded": {}
        },
        "srv": {},
        ".sys": {
            ".block": {},
            ".dev": {},
            ".fs": {},
            ".firmware": {},
            "PyShellOS-License": {
                "PyShellOS-License.txt": "Owned by Stefan Kilber @2025",
                "PyShellM.txt": "Owned by Stefan Kilber @2025"
            },
            "tmp": {},
            "usr": {},
            ".var": {},
            ".debug.txt": "0x0000000102612000 1024",
            ".snap.txt": "0x0000000102612000 10240x0000000102612000 10240x0000000102612000 10240x0000000102612000 10240x0000000102612000 10240x0000000102612000 1024"
        },
        "q.txt": "e",
        ".e.txt": ""
    }
}

                USERS = {"root": {"password": "root"}}
                print("OS reset complete!")
                print("System will now reboot...")
                reboot([])  # Reboot the system after reset
                return
            else:
                print("Reset cancelled")

        elif choice == "2":
            confirm = input("Are you sure you want to restart PyShellOS? (y/N): ").strip().lower()
            if confirm == 'y':
                print("Restarting PyShellOS...")
                reboot([])
                return

        elif choice == "3":
            confirm = input("Are you sure you want to remove all non-root users? (type 'REMOVE' to confirm): ")
            if confirm == "REMOVE":
                users_to_remove = [user for user in USERS if user != "root"]
                for user in users_to_remove:
                    del USERS[user]
                print("All non-root users have been removed!")
            else:
                print("Operation cancelled")
        elif choice == "4":
                print("Security Status:")
                print("")
                print(f"  - Current sudo timeout: 60 seconds after 3 failed attempts")
                print(f"  - Current login timeout: 60 seconds after 3 failed attempts")
                print(f"  - Sudo attempts since last reset: {SUDO_ATTEMPT_COUNTER}/3")
                print("")

        elif choice == "5":
            break
        else:
            print("Invalid option")

def move_cursor_up(n=1):
    sys.stdout.write(f"\033[{n}A")
def clear_line():
    sys.stdout.write("\033[2K\r")
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")
def first_boot_setup():
    lang = get_current_language_from_virtual_fs()
    global CURRENT_THEME_COLOR
    greetings = ["Hallo", "Hello", "bonjour", "привет", "こんにちは", "안녕하세요", "مرحبا", "Benvenuto"]
    for word in greetings:
        for i in range(1, len(word) + 1):
            partical = word[:i]
            clear_screen()
            print(CURRENT_TOP_THEME + CURRENT_LINE_THEME + CURRENT_THEME_COLOR + lang["first_boot_setup"] + "\033[0m" + CURRENT_LINE_THEME * 33)
            print(CURRENT_SIDE_THEME)
            print(CURRENT_INFO_THEME + CURRENT_THEME_COLOR + f"{partical}\033[0m")
            print(CURRENT_SIDE_THEME)
            print(CURRENT_INFO_THEME + CURRENT_THEME_COLOR + lang["continue"] + "\033[0m")
            print(CURRENT_SIDE_THEME)
            print(CURRENT_BOTTOM_THEME + CURRENT_LINE_THEME * 49)

            time.sleep(0.5)
        time.sleep(0.5)
    input()
    clear_screen()
    first_boot_setup_3()

def set_language_in_virtual_fs_setting(lang_code):
    fs_path = "data/filesystem.json"

    with open(fs_path, "r", encoding="utf-8") as f:
        fs = json.load(f)

    if "/" not in fs or "lib-usr" not in fs["/"]:
        raise ValueError("Directory /lib-usr is missing. FATAL ERROR as ALL config files are missing!.")

    fs["/"]["lib-usr"]["current_language"] = lang_code

    with open(fs_path, "w", encoding="utf-8") as f:
        json.dump(fs, f, indent=2, ensure_ascii=False)

def first_boot_setup_3():
    lang = get_current_language_from_virtual_fs()
    global CURRENT_THEME_COLOR
    print(CURRENT_TOP_THEME + CURRENT_LINE_THEME + CURRENT_THEME_COLOR + lang["first_boot_setup"] + "\033[0m" + CURRENT_LINE_THEME * 33)
    print(CURRENT_SIDE_THEME)
    print(CURRENT_INFO_THEME + CURRENT_THEME_COLOR + "Select your Language." + "\033[0m")
    print(CURRENT_SIDE_THEME)
    print(CURRENT_INFO_THEME + CURRENT_THEME_COLOR + "1. English" + "\033[0m")
    print(CURRENT_INFO_THEME + CURRENT_THEME_COLOR + "2. Deutsch" + "\033[0m")
    print(CURRENT_INFO_THEME + CURRENT_THEME_COLOR + "3. Русский" + "\033[0m")
    print(CURRENT_INFO_THEME + CURRENT_THEME_COLOR + "4. Español" + "\033[0m")
    print(CURRENT_SIDE_THEME)
    print(CURRENT_BOTTOM_THEME + CURRENT_LINE_THEME * 49)
    choice = input("\nSelect option (1-4): ").strip()
    lang_map = {
        "1": "en",
        "english": "en",
        "2": "de",
        "deutsch": "de",
        "3": "ru",
        "Русский": "ru",
        "4": "es",
        "Español": "es"
    }
    if choice in lang_map:
        set_language_in_virtual_fs_setting(lang_map[choice])
        first_boot_setup_4()
    else:
        print("Error: Not supported language! You can request it on GitHub.")
        first_boot_setup_3()

def first_boot_setup_4():
    lang = get_current_language_from_virtual_fs()
    global CURRENT_THEME_COLOR
    print(CURRENT_TOP_THEME + CURRENT_THEME_COLOR + "\033[1m" + lang["settings"] + "\033[0m" + CURRENT_LINE_THEME * 21)
    print(CURRENT_SIDE_THEME)
    print(CURRENT_INFO_THEME + CURRENT_THEME_COLOR + lang["green_color_custom_settings"] + "\033[0m")
    print(CURRENT_INFO_THEME + CURRENT_THEME_COLOR + lang["blue_color_custom_settings"] + "\033[0m")
    print(CURRENT_INFO_THEME + CURRENT_THEME_COLOR + lang["red_color_custom_settings"] + "\033[0m")
    print(CURRENT_INFO_THEME + CURRENT_THEME_COLOR + lang["yellow_color_custom_settings"] + "\033[0m")
    print(CURRENT_INFO_THEME + CURRENT_THEME_COLOR + lang["magenta_color_custom_settings"] + "\033[0m")
    print(CURRENT_INFO_THEME + CURRENT_THEME_COLOR + lang["cyan_color_custom_settings"] + "\033[0m")
    print(CURRENT_INFO_THEME + CURRENT_THEME_COLOR + lang["white_color_custom_settings"] + "\033[0m")
    print(CURRENT_INFO_THEME + CURRENT_THEME_COLOR + lang["grey_color_custom_settings"] + "\033[0m")
    print(CURRENT_BOTTOM_THEME + CURRENT_LINE_THEME * 49)

    theme_input = input(CURRENT_INFO_THEME + "   " + CURRENT_THEME_COLOR + lang[
        "change_theme_input_custom_settings"] + "\033[0m").strip().lower()
    if theme_input in THEMES:
        CURRENT_THEME_COLOR = THEMES[theme_input]
        print(CURRENT_SIDE_THEME + lang["theme_success_custom_settings"] + CURRENT_THEME_COLOR + f"{theme_input}." + "\033[0m")
        first_boot_setup_2()
        if "/" not in fs:
            fs["/"] = {}
        if "lib-usr" not in fs["/"]:
            fs["/"]["lib-usr"] = {}
        fs["/"]["lib-usr"]["current_theme"] = CURRENT_THEME_COLOR
        with open("data/filesystem.json", "w") as f:
            json.dump(fs, f, indent=4)
    else:
        print("\033[1;91m" + CURRENT_SIDE_THEME + lang["theme_error_custom_settings_unknown"] + "\033[0m")
        first_boot_setup_4()

def first_boot_setup_2():
    lang = get_current_language_from_virtual_fs()
    print(CURRENT_TOP_THEME + CURRENT_LINE_THEME + CURRENT_THEME_COLOR + lang["first_boot_setup"] + "\033[0m" + CURRENT_LINE_THEME * 33)
    print(CURRENT_SIDE_THEME)
    print(CURRENT_INFO_THEME + CURRENT_THEME_COLOR + "  1." + lang["create_acc"] + "\033[0m")
    print(CURRENT_INFO_THEME + CURRENT_THEME_COLOR + "  2." + lang["temp_acc"] + "\033[0m")
    print(CURRENT_SIDE_THEME)
    print(CURRENT_BOTTOM_THEME + CURRENT_LINE_THEME * 49)
    choice = input(CURRENT_SIDE_THEME + CURRENT_THEME_COLOR + lang["option_2"] + "\033[0m").strip()

    global USERS
    USERS = {
        "root": {"password": "root"}
    }

    if choice == "1":
        while True:
            username = input(CURRENT_INFO_THEME + CURRENT_THEME_COLOR + lang["username_enter"] + "\033[0m").strip()
            if not username:
                print(CURRENT_INFO_THEME + "\033[91m" + lang["username_error_empty"] + "\033[0m")
                continue
            if username.lower() == 'root':
                print(CURRENT_INFO_THEME + "\033[91m" + lang["username_error_root"] + "\033[0m")
                continue
            if not username.isalnum():
                print(CURRENT_INFO_THEME + "\033[91m" + "Username must contain only letters and numbers" + "\033[0m")
                continue
            break

        while True:
            password = input(CURRENT_INFO_THEME + CURRENT_THEME_COLOR + lang["password_enter"] + "\033[0m").strip()
            if not password:
                print(CURRENT_INFO_THEME + "\033[91m" + lang["password_error_empty"] + "\033[0m")
                continue
            confirm_password = input(CURRENT_INFO_THEME + CURRENT_THEME_COLOR + "Confirm password: " + "\033[0m").strip()
            if password != confirm_password:
                print(CURRENT_INFO_THEME + "\033[91m" + lang["password_error_match"] + "\033[0m")
                continue
            break

            # Add new user
        # Encode password before storing
        encoded_pw = encode_password_custom(password)

        # Add new user with encoded password
        USERS[username] = {"password": encoded_pw}

        # Update .etc structure
        fs["/"][".etc"][".userdata"] = {
            f".{username}": {
                ".username": username,
                ".password": encoded_pw
            }
        }

        # Create home directory structure
        fs["/"]["home"] = {
            username: {
                "Documents": {},
                "Downloads": {},
                "Desktop": {},
                "welcome.txt": f"Welcome to PyShellOS, {username}!\nThis is your home directory."
            }
        }

        print(CURRENT_SIDE_THEME + lang["user_success"])
        print(CURRENT_INFO_THEME + lang["username_word"] +  f" {username}")
        print(CURRENT_SIDE_THEME)

        # Set current user
        global CURRENT_USER
        CURRENT_USER = username

        # Persist to disk
        with open("data/filesystem.json", "w") as f:
            json.dump(fs, f, indent=4)

        return username

    elif choice == "2":
        USERS["temp_user"] = {"password": "root"}
        print(CURRENT_SIDE_THEME + lang["temp_success"])
        print(CURRENT_SIDE_THEME + lang["temp_tip_1"])
        print(CURRENT_SIDE_THEME + lang["temp_tip_2"])


def check_first_boot():
    """Check if this is the first time the system is running."""
    try:
        # Check if any non-root users exist in .userdata
        userdata = fs["/"][".etc"][".userdata"]
        user_count = len([k for k in userdata.keys() if k != ".root"])
        return user_count == 0
    except:
        return True

# Load these AFTER the first boot check
def load_users():
    """Load users from filesystem."""
    try:
        userdata = get_dir(["/", ".etc", ".userdata"])
        for user_entry in userdata:
            if user_entry.startswith('.') and user_entry != '.root':
                username = userdata[user_entry].get('.username')
                password = userdata[user_entry].get('.password')
                if username and password:
                    USERS[username] = {"password": password}
    except:
        pass

# more infos
def users(args):
    """Show all users on the system."""
    if not is_sudo_active():
        print("users: Permission denied (requires sudo)")
        return
    
    print("\nSystem Users:")
    print("-" * 30)
    print(f"{'Username':<20} {'Type'}")
    print("-" * 30)
    
    # First show root user
    print(f"{'root':<20} {'system'}")


    # Then show other users
    for username in USERS:
        if username != "root":
            print(f"{username:<20} {'user'}")


def neofetch(args=None):
    now = datetime.now()

    total, used, free = shutil.disk_usage("/")


    """Show system information."""
    print("\n=== PyShellOS System Information ===")
    print("\nSystem Information:")
    print(fr" /$$$$$$$              - OS: PyShellOS-01-01-Beta")
    print(fr" | $$__  $$            - OS: {platform.system()} {platform.release()}")
    print(fr" | $$  \ $$ /$$   /$$  - Architecture: {platform.machine()}")
    print(fr" | $$$$$$$/| $$  | $$  - Python: {platform.python_version()}")
    print(fr" | $$____/ | $$  | $$  - Shell: PyShellOS-Terminal")
    print(fr" | $$      | $$  | $$  - Disk: {round(used / (1024 ** 3), 2)} GB used / {round(total / (1024 ** 3), 2)} GB total")
    print(fr" | $$      |  $$$$$$$  - Python: Py3")
    print(fr" |__/       \____  $$  - Shell: PyShellOS-Terminal")
    print(fr"             /$$  | $$")
    print(fr"            |  $$$$$$/")
    print(fr"             \______/")


def info(args):
    if args is None:
        print("info: Usage: info --help")
        return
    elif args == "-h" or args == "--help":
        print("info: Usage: info [option]")
        print("info: Options:")
        print("info:  -h, --help: Show this help message")
        print("info:  -u, --users: Show all user commands")
        print("info:  -f, --info: Show system information")
        print("info:  -s, --services: Show all services")
        return
    elif args == "-u" or args == "--users":
        print("info: Show all users on the system:")
        print(CURRENT_SIDE_THEME + "┌User Commands" + CURRENT_LINE_THEME * 8 + "┬"+ CURRENT_LINE_THEME * 25)
        print(CURRENT_SIDE_THEME + "                " + "│")
        print(CURRENT_SIDE_THEME + "│ Show all user  " + "│")
        print(CURRENT_SIDE_THEME + "│ commands       " + "│")
        print(CURRENT_SIDE_THEME + "│                " + "│")
        print(CURRENT_SIDE_THEME + "│ -u = username  " + "│")
        print(CURRENT_SIDE_THEME + "│                " + "│")
        print(CURRENT_SIDE_THEME + "├ whoami         " + "│" + " Show current user")
        print(CURRENT_SIDE_THEME + "├ adduser -u     " + "│" + " Add an user")
        print(CURRENT_SIDE_THEME + "├ su -u          " + "│" + " Switch to a user")
        print(CURRENT_SIDE_THEME + "├ users          " + "│" + " Show all users")
        print(CURRENT_SIDE_THEME + "├ logout         " + "│" + " Logout of the current user")
        print(CURRENT_SIDE_THEME + "│                " + "│")
        print(CURRENT_BOTTOM_THEME + CURRENT_LINE_THEME * 21 + "┴" + CURRENT_LINE_THEME * 25)
        return

    elif args == "-f" or args == "--f" or args == "-file" or args == "--file" or args == "-filesystem" or args == "--filesystem" or args == "-fs" or args == "--fs":
        print("info: Show all users on the system:")
        print("┌Filesystem Commands" + CURRENT_LINE_THEME * 2 + "┬" + CURRENT_LINE_THEME * 25)
        print("│                " + "│")
        print("│ Show all file  " + "│")
        print("│ system-        " + "│")
        print("│ commands       " + "│")
        print("│                " + "│")
        print("│ -f = file      " + "│")
        print("│ -d = directory " + "│")
        print("│ -a = all       " + "│")
        print("│ -l = details   " + "│")
        print("│ -p = patterm   " + "│")
        print("│                " + "│")
        print("├ cd -d          " + "│" + " switch to a directory")
        print("├ ls -l -a       " + "│" + " List files in a directory")
        print("├ pwd            " + "│" + " print working directory")
        print("├ tree -a        " + "│" + " print a tree view of the filesystem")
        print("├ find -p        " + "│" + " find a file in the filesystem")
        print("├ grep -p -f     " + "│" + " find a directory in the filesystem")
        print("├ rm -f          " + "│" + " remove a file from the filesystem")
        print("├ mkdir -d       " + "│" + " make a directory")
        print("├ touch -f       " + "│" + " create a file in the filesystem")
        print("├ wc -f          " + "│" + " count the number of lines in a file")
        print("├ cp -f          " + "│" + " copy file (source/destination)")
        print("├ mv -f          " + "│" + " move file (source/destination)")
        print("├ cat -f         " + "│" + " show file content")
        print("│                " + "│")
        print("└─────────────────────┴─────────────────────────")
        return

    elif args == "-s" or args == "--services":
        print("info: Show all users on the system:")
        print("┌Filesystem Commands──┬───────────────────────────")
        print("│                " + "│")
        print("│ Show all app/  " + "│")
        print("│ service-       " + "│")
        print("│ commands       " + "│")
        print("│                " + "│")
        print("│                " + "│")
        print("├ sudo           " + "│" + " execute a command as root")
        print("├ settings       " + "│" + " enter settings application")
        print("├ neofetch       " + "│" + " show system information")
        print("├ help           " + "│" + " list all commands")
        print("├ date           " + "│" + " show current date")
        print("├ clear          " + "│" + " clear the terminal")
        print("├ exit           " + "│" + " exit the terminal")
        print("├ reboot         " + "│" + " reboot the system")
        print("│                " + "│")
        print("└─────────────────────┴─────────────────────────")
        return

    else:
        print("info: Invalid option")
    return
# Then at the bottom of the file, after all function definitions but before shell()
def init_commands():
    global commands
    commands.update({
        "ls": ls,
        "cd": cd,
        "pwd": pwd,
        "cat": cat,
        "echo": echo,
        "help": help_cmd,
        "mkdir": mkdir,
        "touch": touch,
        "rm": rm,
        "cp": cp,
        "mv": mv,
        "grep": grep,
        "wc": wc,
        "tree": tree,
        "find": find,
        "date": date,
        "whoami": whoami,
        "clear": clear,
        "df": df,
        "sudo": sudo,
        "own": own,
        "disown": disown,
        "su": su,
        "adduser": adduser,
        "nano": nano,
        "settings": settings,
        "logout": logout,
        "reboot": reboot,
        "users": users,
        "neofetch": neofetch,
        "info": info
    })




# Update the main block to use login()
if __name__ == "__main__":
    print("Booting PyShellOS...")
    time.sleep(1)
    print("\nPlease wait")
    time.sleep(0.2)
    print("Tip of the boot: If you see a `Access denied` error, try running `sudo [command]`")
    time.sleep(0.1)
    print("\n[ " + f"\033[1;32m" + "✓ " + "\033[0m" + "] Initializing system...")
    time.sleep(random.randint(1, 2))
    print("[ " + f"\033[1;32m" + "✓ " + "\033[0m" + "] Mounting /Kernel")
    time.sleep(random.randint(1, 3))
    print("[ " + f"\033[1;32m" + "✓ " + "\033[0m" + "] Mounting /Boot")
    time.sleep(random.randint(1, 2))
    print("[ " + f"\033[1;32m" + "✓ " + "\033[0m" + "] Mounting /Home")
    time.sleep(random.randint(1, 1))
    print("[ " + f"\033[1;32m" + "✓ " + "\033[0m" + "] Extracting Kernel Level Files...")
    time.sleep(random.randint(1, 3))
    print("[ " + f"\033[1;32m" + "✓ " + "\033[0m" + "] Initializing Storage...")
    time.sleep(random.randint(1, 2))
    print("[ " + f"\033[1;32m" + "✓ " + "\033[0m" + "] Mounting /dev...")
    time.sleep(0.1)
    print("[ " + f"\033[1;32m" + "✓ " + "\033[0m" + "] Mounting /proc...")
    time.sleep(0.1)
    print("[ " + f"\033[1;32m" + "✓ " + "\033[0m" + "] Mounting /sys...")
    time.sleep(0.1)
    print("[ " + f"\033[1;32m" + "✓ " + "\033[0m" + "] Mounting /run...")
    time.sleep(0.1)
    print("[ " + f"\033[1;32m" + "✓ " + "\033[0m" + "] Mounting /home...")
    time.sleep(0.1)
    print("[ " + f"\033[1;32m" + "✓ " + "\033[0m" + "] Mounting /tmp...")
    time.sleep(0.1)
    print("[ " + f"\033[1;32m" + "✓ " + "\033[0m" + "] Mounting /etc...")
    time.sleep(0.4)
    print("[ " + f"\033[1;32m" + "✓ " + "\033[0m" + "] Mounting /var...")
    time.sleep(0.1)
    print("[ " + f"\033[1;32m" + "✓ " + "\033[0m" + "] Mounting /opt...")
    time.sleep(0.1)
    print("[ " + f"\033[1;32m" + "✓ " + "\033[0m" + "] Logging in as root...")
    time.sleep(random.randint(1, 3))
    print("[ " + f"\033[1;32m" + "✓ " + "\033[0m" + "] root executing /etc/..init/boot.py...")
    time.sleep(random.randint(1, 1))
    print("[ " + f"\033[1;32m" + "✓ " + "\033[0m" + "] root executing /Kernel/main/kernel.py...")
    time.sleep(0.1)
    print("[ " + f"\033[1;32m" + "✓ " + "\033[0m" + "] root disowning /Kernel...")
    time.sleep(random.randint(1, 1))
    print("[ " + f"\033[1;32m" + "✓ " + "\033[0m" + "] root disowning /Boot...")
    time.sleep(random.randint(1, 2))
    print("[ " + f"\033[1;32m" + "✓ " + "\033[0m" + "] Identifying Data")
    time.sleep(random.randint(1, 3))
    print("[ " + f"\033[1;32m" + "✓ " + "\033[0m" + "] Loading Archives")
    time.sleep(random.randint(1, 3))
    print("[ " + f"\033[1;32m" + "✓ " + "\033[0m" + "] Validating kernel Signature")
    time.sleep(random.randint(1, 3))
    print("\n" * 50)


    is_first_boot = check_first_boot()
    if is_first_boot:
        print("\n[ " + f"\033[1;32m" + "✓ " + "\033[0m" + "] Detected first boot... This could take a moment...")
        time.sleep(0.3)
        print("\n[ " + f"\033[1;32m" + "✓ " + "\033[0m" + "] Please wait")
        time.sleep(0.5)
        print("\n" * 50)
        first_boot_setup()
    else:
        load_users()
        login()


    init_commands()
    print(CURRENT_SIDE_THEME + "\033[1;32m" + r" /$$$$$$$             /$$$$$$  /$$                 /$$ /$$  /$$$$$$   /$$$$$$" + "\033[0m")
    print(CURRENT_SIDE_THEME + "\033[1;32m" + r" | $$__  $$          /&&__  $$| $$                | $$| $$ /$$__  $$ /$$__  $$" + "\033[0m")
    print(CURRENT_SIDE_THEME + "\033[1;32m" + r" | $$  \ $$ /$$   /$$| $$  \__/| $$$$$$$   /$$$$$$ | $$| $$| $$  \ $$| $$  \__/" + "\033[0m")
    print(CURRENT_SIDE_THEME + "\033[1;32m" + r" | $$$$$$$/| $$  | $$|  $$$$$$ | $$__  $$ /$$__  $$| $$| $$| $$  | $$|  $$$$$$" + "\033[0m")
    print(CURRENT_SIDE_THEME + "\033[1;32m" + r" | $$____/ | $$  | $$ \____  $$| $$  \ $$| $$$$$$$$| $$| $$| $$  | $$ \____  $$" + "\033[0m")
    print(CURRENT_SIDE_THEME + "\033[1;32m" + r" | $$      | $$  | $$ /$$  \ $$| $$  | $$| $$_____/| $$| $$| $$  | $$ /$$  \ $$" + "\033[0m")
    print(CURRENT_SIDE_THEME + "\033[1;32m" + r" | $$      |  $$$$$$$|  $$$$$$/| $$  | $$|  $$$$$$$| $$| $$|  $$$$$$/|  $$$$$$/" + "\033[0m")
    print(CURRENT_SIDE_THEME + "\033[1;32m" + r" |__/       \____  $$ \______/ |__/  |__/ \_______/|__/|__/ \______/  \______/" + "\033[0m")
    print(CURRENT_SIDE_THEME + "\033[1;32m" + r"            /$$  | $$" + "\033[0m")
    print(CURRENT_SIDE_THEME + "\033[1;32m" + r"           |  $$$$$$/" + "\033[0m")
    print(CURRENT_SIDE_THEME + "\033[1;32m" + r"            \______/" + "\033[0m")
    print(CURRENT_BOTTOM_THEME + CURRENT_LINE_THEME * 49)
    shell()