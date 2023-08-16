import slixmpp
from slixmpp.exceptions import IqError, IqTimeout

# Class wiht al the XMPP functions
class Client(slixmpp.ClientXMPP):
    def __init__(self, jid, password):
        slixmpp.ClientXMPP.__init__(self, jid, password)

        self.use_aiodns = False

        self.just_registered = False

        self.just_logged_in = False

        # Event listeners
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("register", self.register)
        self.add_event_handler("message", self.get_message)
        self.add_event_handler("chatstate_composing", self.receive_notification)

    async def start(self, event):
        self.send_presence()
        await self.get_roster()

        if self.just_registered:
            print("Account successfully created! You're now logged in.")
            self.just_registered = False  # Reset this flag

        # Check if user has just logged in
        elif self.just_logged_in:  # add this block
            print("Successfully logged in!")
            self.just_logged_in = False  # Reset this flag

        # Menu after logging in or creating account
        menu = """
        1. Log Out
        2. Delete Account
        3. Show contacts and status
        4. Contact Details
        5. Add Contact
        6. Send Private Message
        7. Join Group
        8. Send Group Message
        9. Define Presence
        10. Send File
        11. Chat Answers
        """

        # Loop for menu options
        show = True
        while show:
            print("*" * 50)
            print("Bienvenido ", self.jid)
            print(menu)
            print("*" * 50)

            choose = input("Choose an option: ")

            # Functions for every option
            if choose == "1":
                print("Log Out")
                self.disconnect()
                show = False
                return
            elif choose == "2":
                print("Delete Account")
                show = False
                self.delete_account()
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
                print("Send File")
                await self.send_file()
                print("File Sent")
            elif choose == "11":
                print("Chat Answers")
            else:
                print("Invalid Option")

            await self.get_roster()

    # Function to delete an account from the server
    def delete_account(self):
        try:
            self.register_plugin("xep_0030")  # Service Discovery
            self.register_plugin("xep_0004")  # Data forms
            self.register_plugin("xep_0066")  # Out-of-band Data
            self.register_plugin("xep_0077")  # In-band Registration
            reg = self.plugin["xep_0077"]
            reg.unregister()
            print("Account Deleted Successfully!")
        except IqError as e:
            print("Could not delete account:", e.iq["error"]["text"])
        except IqTimeout:
            print("Request timed out")

    # Function to join a group chat
    def join_group(self):
        room_jid = input(
            "Enter the JID of the group you want to join (e.g. room@server.tld): "
        )
        nick = input("Enter the nickname you want to use in the group: ")
        self.plugin["xep_0045"].join_muc(room_jid, nick)

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
        jid_to_show = input(
            "Enter the JID of the contact whose details you want to see: "
        )

        if jid_to_show in self.client_roster:
            contact = self.client_roster[jid_to_show]
            print("JID:", jid_to_show)
            print("Subscription:", contact["subscription"])
            for group in contact["groups"]:
                print("Group:", group)
            online_status = "Online" if contact["online"] else "Offline"
            print("Status:", online_status)
        else:
            print("No such contact in roster.")

    # Function to show every contact and group
    def show_contacts(self):
        for jid, contact in self.client_roster.items():
            if contact["subscription"] in ["both", "to"]:
                online_status = "Online" if contact["online"] else "Offline"
                print(f"{jid} - {online_status}")

    # Function to add a contact
    def add_contact(self):
        jid_to_add = input("Enter the JID of the contact you want to add: ")
        self.send_presence_subscription(pto=jid_to_add)

    # Function to change the presence
    def change_presence(self):
        show = input("Enter your status (chat, away, xa, dnd, available): ")
        status = input("Enter a status message (optional): ")
        self.send_presence(pshow=show, pstatus=status)

    # Function when you receive a message
    def get_message(self, message):
        if message["type"] in ("chat", "normal"):
            print("{} says: {}".format(message["from"], message["body"]))

    # Function to send notification while typing a message
    def send_notification(self, recipient, state):
        chatstate = slixmpp.plugins.xep_0085.ChatStateProtocol(self)
        chatstate.send_chat_state(recipient, state)

    # Function when you receive a notification
    def receive_notification(self, chatstate):
        print("{} is {}".format(chatstate["from"], chatstate["chatstate"]))

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
