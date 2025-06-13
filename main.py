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
    """Navigate in virtual FS using current path."""
    d = fs["/"]
    for p in path_list[1:]:
        d = d.get(p, {})
    return d


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
    USERS[username] = {"password": password}

    # Create user directory structure in .etc/.userdata
    userdata_path = get_dir(["/", ".etc", ".userdata"])
    userdata_path[f".{username}"] = {
        ".username": username,
        ".password": password
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
    print("\033[1;32m" + "Welcome to Enhanced PyShellOS!" + "\033[0m")
    print("Type 'help' for command list")

    while LOGGED_IN:
        current_user = get_current_username()
        path = "/" if len(cwd) == 1 else "/" + "/".join(cwd[1:])
        prompt = f"\033[1;34m{current_user}@pyos\033[0m:\033[1;33m{path}\033[0m$ "
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
                print(f"command `{cmd}`: Not found. Try 'help' for available commands.")
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
                if line == ':sy':
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
                print(f"Account locked. Try again in {remaining_time} seconds.")
                time.sleep(1)  # Small delay to prevent rapid retries
                continue
            else:
                # Reset attempts if lockout period is over
                if username in login_attempts:
                    login_attempts[username] = {'attempts': 0}

        # Initialize attempt counter for this user if not already done
        if username not in login_attempts:
            login_attempts[username] = {'attempts': 0}

        password = input("Password: ")
        if password != USERS[username]["password"]:
            # Increment failed attempts
            login_attempts[username]['attempts'] += 1
            attempts_left = max_attempts - login_attempts[username]['attempts']

            if login_attempts[username]['attempts'] >= max_attempts:
                # Lock the account
                login_attempts[username]['locked_until'] = time.time() + lockout_time
                print(f"Too many failed attempts. Account locked for {lockout_time} seconds.")
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

    print("\033[1;32m" + "PyShellOS is ready!" + "\033[0m")
    print("Type 'help' for command list")

# Update settings function to use reboot after reset
def settings(args):
    """Terminal-based settings application."""
    if not is_sudo_active():
        print("Settings can only be accessed with sudo privileges")
        return

    while True:
        current_user = get_current_username()
        print("┌Settings Shell Application─────────────────────")
        print("│")
        print(f"│ Currently logged in as user:{current_user} with permission:{'system' if current_user == 'root' else 'user'}")
        print("│")
        print("├ 1. User Settings")
        print("├ 2. General")
        print("├ 3. System")
        print("├ 4. Update PyShellOS")
        print("│")
        print("├ 5. Return to shell")
        print("│")
        print("└─────────────────────────────────────────────────")

        choice = input("\nSelect option (1-3): ").strip()

        if choice == "1":
            user_settings()
        elif choice == "2":
            system_settings()
        elif choice == "3":
            system_info()
        elif choice == "4":
            update_settings()
        elif choice == "5":
            print("Exiting settings...")
            break
        else:
            print("Invalid option")

def system_info():
    while True:
        print("┌System Info────────────────────────────────────")
        print("│"+"\033[1;32m"+"            OS: PyShellOS-01.02-Beta"+"\033[0m")
        print(f"│"+"\033[1;32m"+"        MainOS: {platform.system()}-{platform.release()}"+"\033[0m")
        print(f"│"+"\033[1;32m"+"  Architecture: {platform.machine()}"+"\033[0m")
        print(f"│"+"\033[1;32m"+"        Python: {platform.python_version()}"+"\033[0m")
        print("│"+"\033[1;32m"+"         Shell: PyshellOS-Terminal"+"\033[0m")
        print("│"+"\033[1;32m"+"        Python: Py3 - Python3 - Py3.1Rls"+"\033[0m")
        print("│"+"\033[1;32m"+"     Publisher: Stefan Kilber"+"\033[0m")
        print("│"+"\033[1;32m"+"          Help: https://github.com/StefanMarston/PyShellOS"+"\033[0m")
        print("│")
        print("├ 1. User Settings")
        print("├ 2. General")
        print("├ 3. Return")
        print("│")
        print("└───────────────────────────────────────────────")
        choice = input("\nSelect option (1): ").strip()

        if choice == "1":
            user_settings()
        elif choice == "2":
            system_settings()
        elif choice == "3":
            break
        else:
            print("Invalid option")

def user_settings():
    """Handle user-related settings."""
    while True:
        current_user = get_current_username()
        print("┌User Settings──────────────────────────────────")
        print("|")
        print(f"│ Currently logged in as user: {current_user}")
        print("│")
        print("├ 1. Change Username")
        print("├ 2. Change Password")
        print("├ 3. Add User")
        print("├ 4. Remove User")
        print("│")
        print("├ 5. Back")
        print("│")
        print("└───────────────────────────────────────────────")

        choice = input("\nSelect option (1-5): ").strip()

        if choice == "1":
            new_username = input("Enter new username: ").strip()
            if new_username:
                if new_username in USERS:
                    print("Username already exists!")
                else:
                    USERS[new_username] = USERS[current_user]
                    del USERS[current_user]
                    global CURRENT_USER
                    CURRENT_USER = new_username
                    print("Username updated successfully!")
            else:
                print("Username cannot be empty")

        elif choice == "2":
            new_password = input("Enter new password: ").strip()
            confirm_password = input("Confirm new password: ").strip()
            if not new_password:
                print("Password cannot be empty")
            elif new_password != confirm_password:
                print("Passwords do not match")
            else:
                USERS[current_user]["password"] = new_password
                print("Password updated successfully!")

        elif choice == "3":
            username = input("Enter new username: ").strip()
            if username in USERS:
                print("User already exists!")
            else:
                password = input("Enter password: ").strip()
                confirm = input("Confirm password: ").strip()
                if password != confirm:
                    print("Passwords do not match!")
                else:
                    USERS[username] = {"password": password}
                    print(f"User {username} created successfully!")

        elif choice == "4":
            username = input("Enter username to remove: ").strip()
            if username == "root":
                print("Cannot remove root user!")
            elif username not in USERS:
                print("User does not exist!")
            else:
                confirm = input(f"Are you sure you want to remove user {username}? (y/N): ").strip().lower()
                if confirm == 'y':
                    del USERS[username]
                    print(f"User {username} removed successfully!")

        elif choice == "5":
            break
        else:
            print("Invalid option")

def update_settings():
    while True:
        print("┌Update Settings────────────────────────────────")
        print("│")
        print("├    Current Version: PyShellOS-01.02-Beta")
        print("├ 1. Update version")
        print("│")
        print("├ 2. Back")
        print("│")
        print("└───────────────────────────────────────────────")

        choice = input("\nSelect option (1-3): ").strip()

        if choice == "1":
            update_main_py_and_restart()

        elif choice == "2":
            break
        else:
            print("Invalid option")


def system_settings():
    """Handle system-related settings."""
    while True:
        print("┌System Settings────────────────────────────────")
        print("│")
        print("├ 1. Reset PyShellOS")
        print("├ 2. Restart PyShellOS")
        print("├ 3. Bulk Remove All Users")
        print("├ 4. Show security Info")
        print("│")
        print("├ 6. Back")
        print("│")
        print("└───────────────────────────────────────────────")

        choice = input("\nSelect option (1-4): ").strip()

        if choice == "1":
            confirm = input("Are you sure you want to reset PyShellOS? This will erase all data! (type 'RESET' to confirm): ")
            if confirm == "RESET":
                print("Resetting PyShellOS...")
                # Reset filesystem to initial state
                global fs, USERS
                fs = {"/": {
                    "bin": {},
                    "boot": {},
                    "home": {},
                    ".etc": {
                        ".userdata": {
                            ".root": {
                                ".username": "root",
                                ".password": "root"
                            }
                        }
                    },
                    ".root": {
                        ".sudopswd": "root"
                    }
                }}

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

def first_boot_setup():
    """Initial setup when running the system for the first time."""
    print("┌Welcome to PyShellOS First-Time Setup──────────")
    print("│Let's create your user account.")
    print("│")

    while True:
        username = input("│Enter username: ").strip()
        if not username:
            print("│Username cannot be empty")
            continue
        if username.lower() == 'root':
            print("│Cannot use 'root' as username")
            continue
        if not username.isalnum():
            print("│Username must contain only letters and numbers")
            continue
        break

    while True:
        password = input("│Enter password: ").strip()
        if not password:
            print("│Password cannot be empty")
            continue
        confirm_password = input("│Confirm password: ").strip()
        if password != confirm_password:
            print("│Passwords do not match")
            continue
        break

    # Clear existing users except root
    global USERS
    USERS = {
        "root": {"password": "root"}
    }

    # Add new user
    USERS[username] = {"password": password}

    # Update .etc structure
    fs["/"][".etc"][".userdata"] = {
        f".{username}": {
            ".username": username,
            ".password": password
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

    print("│User account created successfully!")
    print(f"│Username: {username}")
    print("│System initialization complete.")
    print("│The system will now start")
    print("│")

    # Persist to disk
    with open("data/filesystem.json", "w") as f:
        json.dump(fs, f, indent=4)

    # Set current user
    global CURRENT_USER
    CURRENT_USER = username

    return username

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
    print(f" /$$$$$$$              - OS: PyShellOS-01-01-Beta")
    print(f" | $$__  $$            - OS: {platform.system()} {platform.release()}")
    print(f" | $$  \ $$ /$$   /$$  - Architecture: {platform.machine()}")
    print(f" | $$$$$$$/| $$  | $$  - Python: {platform.python_version()}")
    print(f" | $$____/ | $$  | $$  - Shell: PyShellOS-Terminal")
    print(f" | $$      | $$  | $$  - Disk: {round(used / (1024 ** 3), 2)} GB used / {round(total / (1024 ** 3), 2)} GB total")
    print(f" | $$      |  $$$$$$$  - Python: Py3")
    print(f" |__/       \____  $$  - Shell: PyShellOS-Terminal")
    print(f"             /$$  | $$")
    print(f"            |  $$$$$$/")
    print(f"             \______/")

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
        "neofetch": neofetch
    })




# Update the main block to use login()
if __name__ == "__main__":
    print("Booting PyShellOS...")
    print("If you see a Syntax Error above the boot, ignore it!")
    time.sleep(1)
    print("\nPlease wait")
    time.sleep(0.2)
    print("Tip of the boot: If you see a `Access denied` error, try running `sudo [command]`")
    time.sleep(0.1)
    print("\n[ ✓ ] Initializing system...")
    time.sleep(random.randint(1, 2))
    print("[ ✓ ] Mounting /Kernel")
    time.sleep(random.randint(1, 3))
    print("[ ✓ ] Mounting /Boot")
    time.sleep(random.randint(1, 2))
    print("[ ✓ ] Mounting /Home")
    time.sleep(random.randint(1, 1))
    print("[ ✓ ] Extracting Kernel Level Files...")
    time.sleep(random.randint(1, 3))
    print("[ ✓ ] Initializing Storage...")
    time.sleep(random.randint(1, 2))
    print("[ ✓ ] Mounting /dev...")
    time.sleep(0.1)
    print("[ ✓ ] Mounting /proc...")
    time.sleep(0.1)
    print("[ ✓ ] Mounting /sys...")
    time.sleep(0.1)
    print("[ ✓ ] Mounting /run...")
    time.sleep(0.1)
    print("[ ✓ ] Mounting /home...")
    time.sleep(0.1)
    print("[ ✓ ] Mounting /tmp...")
    time.sleep(0.1)
    print("[ ✓ ] Mounting /etc...")
    time.sleep(0.4)
    print("[ ✓ ] Mounting /var...")
    time.sleep(0.1)
    print("[ ✓ ] Mounting /opt...")
    time.sleep(0.1)
    print("[ ✓ ] Logging in as root...")
    time.sleep(random.randint(1, 3))
    print("[ ✓ ] root executing /etc/..init/boot.py...")
    time.sleep(random.randint(1, 1))
    print("[ ✓ ] root executing /Kernel/main/kernel.py...")
    time.sleep(0.1)
    print("[ ✓ ] root disowning /Kernel...")
    time.sleep(random.randint(1, 1))
    print("[ ✓ ] root disowning /Boot...")
    time.sleep(random.randint(1, 2))
    print("[ ✓ ] Identifying Data")
    time.sleep(random.randint(1, 3))
    print("[ ✓ ] Loading Archives")
    time.sleep(random.randint(1, 3))
    print("[ ✓ ] Validating kernel Signature")
    time.sleep(random.randint(1, 3))
    print("\n" * 50)

    is_first_boot = check_first_boot()
    if is_first_boot:
        print("\n[ ✓ ] Detected first boot... This could take a moment...")
        time.sleep(0.3)
        print("\n[ ✓ ] Please wait")
        time.sleep(0.5)
        print("\n" * 50)
        first_boot_setup()
    else:
        load_users()
        login()
    init_commands()
    print(f"│" + "\033[1;32m" + " /$$$$$$$             /$$$$$$  /$$                 /$$ /$$  /$$$$$$   /$$$$$$" + "\033[0m")
    print(f"│" + "\033[1;32m" + " | $$__  $$          /&&__  $$| $$                | $$| $$ /$$__  $$ /$$__  $$" + "\033[0m")
    print(f"│" + "\033[1;32m" + " | $$  \ $$ /$$   /$$| $$  \__/| $$$$$$$   /$$$$$$ | $$| $$| $$  \ $$| $$  \__/" + "\033[0m")
    print(f"│" + "\033[1;32m" + " | $$$$$$$/| $$  | $$|  $$$$$$ | $$__  $$ /$$__  $$| $$| $$| $$  | $$|  $$$$$$" + "\033[0m")
    print(f"│" + "\033[1;32m" + " | $$____/ | $$  | $$ \____  $$| $$  \ $$| $$$$$$$$| $$| $$| $$  | $$ \____  $$" + "\033[0m")
    print(f"│" + "\033[1;32m" + " | $$      | $$  | $$ /$$  \ $$| $$  | $$| $$_____/| $$| $$| $$  | $$ /$$  \ $$" + "\033[0m")
    print(f"│" + "\033[1;32m" + " | $$      |  $$$$$$$|  $$$$$$/| $$  | $$|  $$$$$$$| $$| $$|  $$$$$$/|  $$$$$$/" + "\033[0m")
    print(f"│" + "\033[1;32m" + " |__/       \____  $$ \______/ |__/  |__/ \_______/|__/|__/ \______/  \______/" + "\033[0m")
    print(f"│" + "\033[1;32m" + "            /$$  | $$" + "\033[0m")
    print(f"│" + "\033[1;32m" + "           |  $$$$$$/" + "\033[0m")
    print(f"│" + "\033[1;32m" + "            \______/" + "\033[0m")
    print(f"└───────────────────────────────────────────────")
    shell()