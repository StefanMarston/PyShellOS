This is a basic information about this virtual operating system.

It runs on Python3.

If you want to run it follow these steps:

--Linux--
```shell
cd /home/USERNAME/Downloads/PyShellOS
python3 main.py
```
--MacOS--
```shell
cd ~/Downloads/PyShellOS/
python3 main.py
```
--Windows--
```shell
cd C:\Downloads\PyShellOS\
py main.py
```

Verion PyShellOS-01.02-Beta or newer support live updates means you don't have to manually update the files!

to update your system use:

```shell
sudo settings
sudo password: (password)
choose option 4
choose option 1
and wait
```

New to 1.3.1-Alpha

The setup has been changed. to apply for alpha please go to settings -> update -> beta features and activate it!
Inside the new setup I have added: 
- Color shenes. Your text will be now changed based on yojr preferences.
- Different application boreders. There's now basic, double, pointed.
- Different Langiages: French, German, Russian, English, Spanish.

Basic command usage:

# Filesystem #

```shell
-> cd <dir>               - move to a directory.
-> ls [-l] {-a}           - List all the content in the given direcotry.
-> pwd                    - Print working Directory.
-> tree {-a}              - Print all directories and files in a tree view.
-> find <pattern>         - Find a file/directory using a pattern.
-> grep <pattern> <file>  - Search in files.
-> rm <name> [-f]         - Remove a file.
-> mkdir <dir>            - Create a new directory.
-> touch <file>           - Create a new File.
-> wc <file>              - Count lines/words/characters.
-> cp <src> <dst>         - Copy a file.
-> mv <src> <dst>         - Move a file.
-> cat <file> [-n]        - Show file content.
```

# User and root Usage #

```shell
-> whoami                 - Show current user.
-> adduser                - Add a user [root required].
-> su                     - Switch to a user [root required]
-> users                  - Show all system users.
-> logout                 - Logout of the current user.
-> own <file>             - Own a file for the current user.
-> disown <file>          - Remove File ownership of the current user.
```

# More #

```shell
-> sudo [command]         - Execute a command with root previleges.
-> settings               - Enter settings application [root required].
-> security               - Enter security application [root required].
-> neofetch               - Enter Neofetch application.
-> help                   - Show all commands.
-> date                   - Show current date/time.
-> clear                  - clear all previous commands.
-> exit                   - Forcequit OS.
-> reboot                 - Reboot the Virtual OS.
```

# Advanced #

```shell
[sudo] nano <file>
```
```Python
Instructions: Enter      |   Command   |         :sv         |        :sn          |      :clear      |         :del         |
These cmds on a new line |    Output   |    save and exit    | exit without saving | clear whole file | delete previous line |
 ```


# planned stuff #
```shell
-> update                 - (grabs main.py) from https://github.com/StefanMArston/PyShellOS/ and replaces the old one.
```


# Settings #
Be sure to KNOW how to use the settings as you could accidentally wipe all Data!

```shell
┌Settings Shell Application─────────────────────
│
│ Currently logged in as user: Stefan with permission: user
│
├   1. User Settings
├   2. General
├   3. System
├   4. Update PyShellOS
│
├   5. Return to shell
│
└─────────────────────────────────────────────────
```

USER SETTINGS

```shell
┌User Settings──────────────────────────────────
|
│ Currently logged in as user: Stefan
│
├   1. Change Username
├   2. Change Password
├   3. Add User
├   4. Remove User
│
├   5. Back
│
└───────────────────────────────────────────────
```

SYSTEM SETTINGS

```shell
┌System Settings────────────────────────────────
│
├   1. Reset PyShellOS
├   2. Restart PyShellOS
├   3. Bulk Remove All Users
├   4. Show security Info
│
├   5. Back
│
└───────────────────────────────────────────────
```

SYSTEM INFORMATIONS (example)

```shell
┌System Info────────────────────────────────────
│            OS: PyShellOS-01.02-Beta
│        MainOS: Linux-6.11.0-26-generic
│  Architecture: x86_64
│        Python: 3.12.3
│         Shell: PyshellOS-Terminal
│        Python: Py3 - Python3 - Py3.1Rls
│     Publisher: Stefan Kilber
│          Help: https://github.com/StefanMarston/PyShellOS
│
├   1. User Settings
├   2. General
├   3. Return
│
└───────────────────────────────────────────────
```

UPDATE SETTINGS

```shell
┌Update Settings────────────────────────────────
│
├    Current Version: PyShellOS-01.02-Beta
├   1. Update version
│
├   2. Back
│
└───────────────────────────────────────────────

```
