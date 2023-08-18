import slixmpp
from slixmpp.exceptions import IqError, IqTimeout

# Class wiht al the XMPP functions
class Client(slixmpp.ClientXMPP):
    def __init__(self, jid, password):
        slixmpp.ClientXMPP.__init__(self, jid, password)

        self.add_event_handler("message_delivered", self.message_delivered)
        self.pending_messages = []
        self.use_aiodns = False
        self.just_registered = False
        self.just_logged_in = False
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("register", self.register)
        self.add_event_handler("message", self.get_message)
        self.add_event_handler("chatstate_composing", self.receive_notification)

    # Note: This method has been moved out of the __init__ method
    def message_delivered(self, msg_receipt):
        print(f"Message delivered to {self.recipient}")


    async def start(self, event):
        self.send_presence(self.show, self.stat)
        await self.get_roster()

         # Add a delivery receipt request
        self.send_message(mto=self.recipient, mbody=self.msg, mtype="chat",
                        request_receipt=True)

        if self.just_registered:
            print("Account successfully created! You're now logged in.")
            self.just_registered = False  # Reset this flag

        # Check if user has just logged in
        elif self.just_logged_in:  # add this block
            print("Successfully logged in!")
            self.just_logged_in = False  # Reset this flag

        # Menu after logging in or creating account
        menu = """
        📌 Welcome to XMPP Chat Client
        🖥 Logged in as: {}

        ➡️ Options:

        [1] Log Out (End your session)
        [2] Delete Account (Remove your account)
        [3] Show contacts (View online friends)
        [4] Contact Details (Info on a specific contact)
        [5] Add Contact (Add someone new)
        [6] Send Private Message (Chat one-on-one)
        [7] Join Group (Join a group chat)
        [8] Send Group Message (Chat in a group)
        [9] Define Presence (Set your status)
        [10] Send File (Share a document or picture)

        Type the number corresponding to your choice and hit Enter.
        """.format(self.jid)

        # Loop for menu options
        while self.pending_messages:
            from_jid, body = self.pending_messages.pop(0)
            print(f"\n{from_jid} says: {body}\n")

            print("*" * 60)
            print(menu)
            print("*" * 60)

            choose = input("Your choice: ")

            # Functions for every option
            if choose == "1":
                print("Log Out")
                self.disconnect()
                show = False
                return
            elif choose == "2":
                print("Delete Account")
                show = False
                await self.async_delete_account()
                print("Account Deleted")
                return
            elif choose == "3":
                print("Show Contacts")
                self.show_contacts()
            elif choose == "4":
                print("Contact Details")
                self.show_contact_details()
            elif choose == "5":
                print("Add Contact")
                self.add_contact()
            elif choose == "6":
                print("Send Private Message")
                self.private_message()
            elif choose == "7":
                print("Join Group")
                self.join_group()
            elif choose == "8":
                print("Send Group Message")
                self.send_group_message()
            elif choose == "9":
                print("Define Presence")
                self.change_presence()
            elif choose == "10":
                file_path = input("Enter the path to the file you want to send: ")
                if not file_path:
                    print("You must specify a file path.")
                    continue

                recipient = input("Enter the recipient's JID: ")
                await self.send_file(file_path, recipient)
                print("File Sent")
            else:
                print("Invalid Option")

            await self.get_roster()

    # Function to delete an account from the server
    async def async_delete_account(self):
        try:
            if input("Are you sure you want to delete? [yes/no]: ") == "yes":
                self.register_plugin("xep_0077") # In-band Registration

                resp = self.Iq()
                resp["type"] = "set"
                resp["from"] = self.boundjid.user
                resp["register"]["remove"] = True

                await resp.send()
                logging.info("Account deleted successfully.")
                self.logout()
        except IqError:
            logging.error("Something went wrong.")
        except IqTimeout:
            logging.error("No response from server.")




    # Function to join a group chat
    def join_group(self):
        room_jid = input(
            "Enter the JID of the group you want to join (e.g. room@server.tld): "
        )
        nick = input("Enter the nickname you want to use in the group: ")
        self.plugin["xep_0045"].join_muc(room_jid, nick)
        print(f"Joined group {room_jid} as {nick}")

    # Function to send a message to a group
    def send_group_message(self):
        room_jid = input("Enter the JID of the group you want to send a message to: ")
        msg_body = input("Enter your message: ")
        self.send_message(mto=room_jid, mbody=msg_body, mtype="groupchat")

    # Function to send a private message
    def private_message(self):
        recipient = input("Enter the recipient's JID: ")
        msg_body = input("Enter your message: ")
        self.send_message(mto=recipient, mbody=msg_body, mtype="chat")

    # Function to show the detail from a specific contact
    def show_contact_details(self):
        self.get_roster()
        contact_jid = input("Enter JID to see details: ")
        print("\n", contact_jid)
        
        connections = self.client_roster.presence(contact_jid)

        if not connections:
            print("No recent session for", contact_jid)
        else:
            for resource, presence_data in connections.items():
                show = presence_data.get('show', 'available')  # Default to 'available' if 'show' is not present
                status = presence_data.get('status', '')  # Presence message/status
                print(f"{resource} - Show: {show} - Status: {status}")



    def show_contact(self):
        # Show contact presence
        self.get_roster()

        contact_jid = input("JID: ")
        print("\n", contact_jid)
        connections = self.client_roster.presence(contact_jid)

        if connections == {}:
            print("No recent session")
        else:
            for device, presence in connections.items():
                print(device, " - ", presence["show"])


    # Function to add a contact
    def add_contact(self):
        jid_to_add = input("Enter the JID of the contact you want to add: ")
        self.send_presence_subscription(pto=jid_to_add)

    # Function to change the presence
    def presence(self, show=None):
        # Set presence messages
        if not show:
            show = input("show: [chat, away, xa, dnd, custom] ")

        if show not in ["chat", "away", "xa", "dnd", "custom"]:
            show = "chat"

        if show == "chat":
            status = "Available"
        elif show == "away":
            status = "Unavailable"
        elif show == "xa":
            status = "Bye"
        elif show == "dnd":
            status = "Do not Disturb"
        elif show == "custom":
            show = input("show: ")
            status = input("status: ")

        if show not in ["chat", "away", "xa", "dnd"]:
            show = "chat"
            status = "Available"

        try:
            self.send_presence(pshow=show, pstatus=status)
            logging.info("Presence setted.")
        except IqError:
            logging.error("Something went wrong.")
        except IqTimeout:
            logging.error("No response from server.")



    # Function when you receive a message
    def get_message(self, message):
        if message["type"] in ("chat", "normal"):
            self.pending_messages.append((message["from"], message["body"]))

    # Function to send notification while typing a message
    def send_notification(self, recipient, state):
        chatstate = slixmpp.plugins.xep_0085.ChatStateProtocol(self)
        chatstate.send_chat_state(recipient, state)

    def receive_notification(self, chatstate):
        notification_type = str(chatstate["chatstate"])
        if notification_type == "composing":
            print(f"\n{chatstate['from']} is typing...\n")

    # Function to register a new account to the server from the client menu
    async def register(self, iq):
        responce = self.Iq()
        responce["type"] = "set"
        responce["register"]["username"] = self.boundjid.user
        responce["register"]["password"] = self.password

        try:
            await responce.send()
            print("Account created")
            self.just_registered = True
        except IqError as e:
            print("Could not register account")
            self.disconnect()
        except IqTimeout:
            print("No response from server")
            self.disconnect()
