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
=== Settings Shell Application ===

Currently logged in as e user

1. User Settings            - All settings for users (change password, username, add/remove users)
2. System Settings          - All settings for the system (reboot/Reset/bulk clear users)
3. Exit Settings            - Go back to normal Shell commands.

Select option (1-3):
```
```shell
=== User Settings ===

Currently logged in as e

1. Change Username         - Change the username of CURRENT user
2. Change Password         - Change the password of CURRENT user
3. Add User                - Add a user
4. Remove User             - Remove the CURRENT user
5. Back                    - Go back to normal app

Select option (1-5): 
```
```shell
=== System Settings ===

1. Reset PyShellOS         - Resets ALL data!
2. Restart PyShellOS       - Reboots the system
3. Bulk Remove All Users   - Removes all users (excluding root)
4. Back                    - Go back to normal app

Select option (1-4):
```
