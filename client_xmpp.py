import slixmpp
from slixmpp.exceptions import IqError, IqTimeout
import base64
import logging
logging.basicConfig(level=logging.DEBUG)


# Class with all the XMPP functions
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
        elif self.just_logged_in:
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
        [11] Chat Answers (Get automated responses)

        Type the number corresponding to your choice and hit Enter.
        """.format(self.jid)

        # Loop for menu options
        while True:
            print("*" * 60)
            print(menu)
            print("*" * 60)

            choose = input("Your choice: ")

            # Functions for every option
            if choose == "1":
                print("Log Out")
                self.disconnect()
                return
            elif choose == "2":
                print("Delete Account")
                self.async_delete_account()
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
                self.send_file()
                print("File Sent")
            elif choose == "11":
                print("Chat Answers")
            else:
                print("Invalid Option")

            self.get_roster()

    # Function to delete an account from the server
    def async_delete_account(self):
        try:
            if input("Are you sure you want to delete? [yes/no]: ") == "yes":
                self.register_plugin("xep_0077")  # In-band Registration

                resp = self.Iq()
                resp["type"] = "set"
                resp["from"] = self.boundjid.user
                resp["register"]["remove"] = True

                resp.send()
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

    # Función para enviar notificación mientras se escribe un mensaje privado
    def send_typing_notification(self, recipient):
        self.send_notification(recipient, 'composing')

    # Función para enviar notificación mientras se escribe en un grupo
    def send_group_typing_notification(self, room_jid):
        self.send_notification(room_jid, 'composing', mtype="groupchat")
        

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
        username = input('Write the username (user@alumchat.xyz): ')

        contact = self.client_roster[username]
        print('*' * 50)
        if contact['name']:
            print('Nombre: ', contact['name'], '\n')
        print('Username: ', username, '\n')
        connections = self.client_roster.presence(username)

        if not connections:
            print('Estado: Offline')
        else:
            for client, status in connections.items():
                print('Estado: ', status['status'])

        print('*' * 50)

    # Function to show every contact and group
        # Simplified function to show every contact and their presence
    def show_contacts(self):
        groups = self.client_roster.groups()
        
        for group in groups:
            print('*' * 50)
            for username in groups[group]:
                if username != self.jid:
                    print('usuario: ', username)
                    
                    connections = self.client_roster.presence(username)
                    if not connections:
                        print('estado: Offline')
                    else:
                        for _, status in connections.items():
                            print('estado: ', status.get('show', 'Available') or 'Available') 
                    print('\n')
        print('*' * 50)




    # Function to add a contact
    def add_contact(self):
        jid_to_add = input("Enter the JID of the contact you want to add: ")
        self.send_presence_subscription(pto=jid_to_add)

    # Function to change the presence
    def change_presence(self, show=None):
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


    # Función de envío de archivos
    async def send_file(self):
        recipient = input("Enter the recipient's JID: ")
        filename = input("¿Que archivo deseas mandar? ")
        with open(filename, "rb") as img_file:
            message = base64.b64encode(img_file.read()).decode('utf-8')
        self.send_message(mto=recipient, mbody=message, mtype="chat")
        print("¡Archivo enviado exitosamente!")

    def send_notification(self, recipient, chatstate, mtype="chat"):
        """
        Send a chat state notification.
        
        Args:
        - recipient: The JID of the recipient.
        - chatstate: The chat state string (e.g., "composing", "paused").
        - mtype: The message type, either "chat" or "groupchat".
        """
        msg = self.Message()
        msg["to"] = recipient
        msg["type"] = mtype
        msg["chatstate"] = chatstate
        msg.send()


    # Función para recepción de archivos
    def get_message(self, message):
        if message["type"] in ("chat", "normal"):
            body = message["body"]
            if len(body) > 3000:
                received = body.encode('utf-8')
                received = base64.decodebytes(received)
                with open("recibido.png", "wb") as fh:
                    fh.write(received)
            else:
                print("{} says: {}".format(message["from"], message["body"]))

    # Función actualizada para recibir notificación mientras alguien escribe
    def receive_notification(self, chatstate):
        notification_type = str(chatstate["chatstate"])
        if notification_type == "composing":
            if "groupchat" in chatstate["type"]:
                print(f"{chatstate['from']} in group {chatstate['to']} is typing...")
            else:
                print(f"{chatstate['from']} is typing...")

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
