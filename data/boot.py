def login():
    global CURRENT_USER
    while True:
        print("\nWelcome to PyShellOS!")
        username = input("Username: ").strip()
        if username not in USERS:
            print("User not found!")
            continue

        if USERS[username]["password"] is not None:
            password = input("Password: ")
            if password != USERS[username]["password"]:
                print("Invalid password!")