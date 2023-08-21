from client_xmpp import Client
from getpass import getpass
import logging
logging.basicConfig(level=logging.DEBUG)


# Initialization routine for a new user registration
def initiate_registration(usr, pass_key):
    chat_client = Client(usr, pass_key)
    
    # Plugins to enhance XMPP functionality
    plugins = [
        "xep_0030",
        "xep_0004",
        "xep_0199",
        "xep_0066",
        "xep_0077",
        "xep_0071",
        "xep_0085",
        "xep_0128",
        "xep_0045",
        "xep_0363",
    ]
    
    for plugin in plugins:
        chat_client.register_plugin(plugin)

    chat_client["xep_0077"].force_registration = True

    chat_client.connect()
    chat_client.process()
    chat_client.disconnect()

# Routine to start chat session for a user
def initiate_session(usr_id, pass_key):
    chat_client = Client(usr_id, pass_key)
    
    # Plugins for XMPP session
    plugins = [
        "xep_0004",
        "xep_0030",
        "xep_0066",
        "xep_0071",
        "xep_0085",
        "xep_0128",
        "xep_0199",
        "xep_0045",
        "xep_0363",
    ]
    
    for plugin in plugins:
        chat_client.register_plugin(plugin)

    try:
        chat_client.connect()
        chat_client.process(forever=False)
        print("Successfully connected!")
    except Exception as e:
        print(f"Attempt failed due to {e}.")

    chat_client.disconnect()

# Stylish Menu Display
menu_display = """
╔════════════════════════════════╗
║ 1. Start Chat Session          ║
║ 2. Create New Account         ║
║ 3. Exit Application           ║
╚════════════════════════════════╝
"""

# Command loop to interact with the user
active = True

while active:
    print(menu_display)

    choice = input("Enter your choice: ")

    if choice == "1":  # Start Chat Session
        print("Starting Chat Session...")
        usr_name = input("Enter your username (example@alumchat.xyz): ")
        usr_password = getpass("Enter your password: ")
        initiate_session(usr_name, usr_password)
    elif choice == "2":  # Create New Account
        print("Registering New Account...")
        new_username = input("Choose a username (example@alumchat.xyz): ")
        new_password = getpass("Choose a password: ")
        initiate_registration(new_username, new_password)
    elif choice == "3":  # Exit the application
        active = False
        print("Goodbye!")
    else:  # Incorrect input
        print("Please enter a valid option!")
