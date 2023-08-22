import slixmpp
from slixmpp.exceptions import IqError, IqTimeout
import logging
import threading
import aioconsole
import sys
import base64
import os
import time



# Class wiht al the XMPP functions
class Client(slixmpp.ClientXMPP):
    def __init__(self, jid, password):
        slixmpp.ClientXMPP.__init__(self, jid, password)

        self.wait_for_input = True

        self.use_aiodns = False

        self.just_registered = False

        self.is_listening = False

        
        

        # Event listeners
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("register", self.register)
        self.add_event_handler("chatstate_composing", self.receive_notification)
        self.add_event_handler("presence_subscribe", self.subscription_request)  # Add this line to handle subscription requests
        self.add_event_handler("message", self.get_message)



    def setup_logging(self, level):
        logging.basicConfig(level=level)
        logging.getLogger('slixmpp').setLevel(level)


    async def start(self, event):

        
        self.send_presence()
        await self.get_roster()

        self.setup_logging(logging.CRITICAL)


        if self.just_registered:
            print("Account successfully created! You're now logged in.")
            self.just_registered = False  # Reset this flag
        

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
        [11] Create Group (Create a new chat group)

        Type the number corresponding to your choice and hit Enter.
        """.format(self.jid)

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
            elif choose == "2":
                print("Delete Account")
                show = False
                await self.delete_account()
                print("Account Deleted")
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
                recipient = input("Enter the recipient's JID: ")
                await self.user_input(recipient)
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
                print("Create Group")
                self.create_group()
            else:
                print("Invalid Option")

            await self.get_roster()

    # Function to delete an account from the server
    async def delete_account(self):
        try:
            if input("Are you sure you want to delete? [yes/no]: ") == "yes":
                self.register_plugin("xep_0077") # In-band Registration

                resp = self.Iq()
                resp["type"] = "set"
                resp["from"] = self.boundjid.user
                resp["register"]["remove"] = True

                await resp.send()
                logging.info("Account deleted successfully.")
                sys.exit()  # Termina el programa.
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

    # Function to send a message to a group
    def send_group_message(self):
        room_jid = input("Enter the JID of the group you want to send a message to: ")

        # Este método simplemente espera a que el usuario escriba un mensaje y luego lo envía.
        def send_loop():
            while True:
                msg_body = input("Escribe <<volver>> si deseas regresar al menu \n Mensaje... ")
                if msg_body.lower() == "volver":
                    break
                else:
                    self.send_message(mto=room_jid, mbody=msg_body, mtype="groupchat")

        # Aquí creamos un hilo que se encargará de esperar y enviar mensajes.
        send_thread = threading.Thread(target=send_loop)
        send_thread.start()

        # Esperamos a que el hilo termine (es decir, cuando el usuario escribe "volver").
        send_thread.join()


    def message_callback(self, msg):
        if msg['type'] == 'groupchat':
            print(f"[{msg['from'].resource}] {msg['body']}")
        elif msg['type'] != 'groupchat':
            print(f"Received a message of type {msg['type']} from {msg['from']}: {msg['body']}")



    async def user_input(self, recipient):
        while True:
            msg_body = await aioconsole.ainput("Escribe <<volver>> si deseas regresar al menu \n Mensaje... ")
            if msg_body.lower() == "volver":
                break
            else:
                self.send_message(mto=recipient, mbody=msg_body, mtype="chat")
                print(f"[You] {msg_body}")


    def private_message(self):
        recipient = input("Enter the recipient's JID: ")
        while True:
            msg_body = input("Escribe <<volver>> si deseas regresar al menu \n Mensaje... ")
            if msg_body.lower() == "volver":
                break
            else:
                self.send_message(mto=recipient, mbody=msg_body, mtype="chat")
                print(f"[You] {msg_body}")


    # Function to show the detail from a specific contact
    def show_contact_details(self):
        # Pedir al usuario que ingrese el JID del contacto que desea ver
        target_jid = input("Enter the JID of the contact whose details you want to see: ")

        groups = self.client_roster.groups()

        found = False
        for group in groups:
            for username in groups[group]:
                if username == target_jid:
                    found = True
                    connections = self.client_roster.presence(username)
                    if not connections:
                        status = 'Offline'
                    else:
                        primary_status = list(connections.values())[0]
                        status = primary_status.get('show')
                        # Check if status is None or an empty string, then set to 'Available'.
                        if not status:
                            status = 'Available'
                        # Capitalize the first letter.
                        status = status.capitalize()
                    print(f"JID: {username}\nStatus: {status}")

        if not found:
            print(f"No contact found with JID: {target_jid}")

    # Function to show every contact and group
    def show_contacts(self):
        groups = self.client_roster.groups()

        for group in groups:
            for username in groups[group]:
                if username != self.jid:
                    connections = self.client_roster.presence(username)
                    if not connections:
                        display_status = 'Offline'
                    else:
                        primary_status = list(connections.values())[0]
                        show = primary_status.get('show')
                        custom_status = primary_status.get('status')
                        # Check if show is None or an empty string, then set to 'Available'.
                        if not show:
                            show = 'Available'
                        # Capitalize the first letter.
                        show = show.capitalize()
                        # Build the display status string.
                        display_status = f"{show}" if not custom_status else f"{show} ({custom_status})"

                    print(f"{username}: {display_status}")





    # Function to add a contact
    def add_contact(self):
        jid_to_add = input("Enter the JID of the contact you want to add: ")
        self.send_presence_subscription(pto=jid_to_add)
        print(f"Sent a contact request to {jid_to_add}. Awaiting their response...")
    

    def subscription_request(self, presence):
        from_jid = presence["from"]
        print(f"Received a contact request from {from_jid}.\nDo you want to accept? [yes/no]: ", end="")
        
        response = input()
        if response == "yes":
            # If the user wants to accept the subscription request
            self.send_presence(pto=from_jid, ptype="subscribed")
            self.send_presence(pto=from_jid, ptype="subscribe")  # Also send a subscription request back
            print(f"You are now connected with {from_jid}.")
        else:
            # If the user wants to reject the subscription request
            self.send_presence(pto=from_jid, ptype="unsubscribed")
            print(f"Declined the contact request from {from_jid}.")

    # Function to change the presence
    def change_presence(self, show=None):
        """Change user presence based on the value of show."""
        
        # Get the presence 'show' value
        if not show:
            show = input("show: [chat, away, xa, dnd, custom] ")

        # Define the status based on the 'show' value
        statuses = {
            "chat": "Available",
            "away": "Unavailable",
            "xa": "Bye",
            "dnd": "Do not Disturb"
        }

        if show == "custom":
            # Ask for the status message; keep 'show' as one of the standard states.
            status = input("status: ")
            show = "chat"  # Default to 'chat' or any other appropriate value.
        else:
            status = statuses.get(show, "Available")
        
        # Attempt to send the presence
        try:
            self.send_presence(pshow=show, pstatus=status)
            logging.info("Presence setted.")
        except IqError:
            logging.error("Something went wrong.")
        except IqTimeout:
            logging.error("No response from server.")
    
    async def send_file(self):
        recipient = input("Enter the recipient's JID: ")
        filename = input("¿Qué archivo deseas mandar? ")
        file_extension = os.path.splitext(filename)[1]

        # Codificar el archivo según su extensión.
        with open(filename, "rb") as file:
            encoded_content = base64.b64encode(file.read()).decode('utf-8')
            if file_extension == ".txt":
                message_body = "FILE:TXT:" + encoded_content
            elif file_extension in [".png", ".jpg", ".jpeg"]:
                message_body = "FILE:IMG:" + encoded_content
            else:
                print("Tipo de archivo no soportado.")
                return

        self.send_message(mto=recipient, mbody=message_body, mtype="chat")
        print("¡Archivo enviado exitosamente!")

    # Function when you receive a message
    def get_message(self, message):
        if message["type"] in ("chat", "normal"):
            body = message["body"]
            
            # Obtener el tiempo actual para crear un nombre de archivo único.
            timestamp = int(time.time())
            
            if body.startswith("FILE:TXT:"):
                encoded_content = body.replace("FILE:TXT:", "").encode('utf-8')
                decoded_content = base64.decodebytes(encoded_content)
                
                file_name = f"recibido_{timestamp}.txt"
                with open(file_name, "w", encoding="utf-8") as txt_file:
                    txt_file.write(decoded_content.decode('utf-8'))
                print(f"Archivo TXT recibido y guardado como {file_name}")

            elif body.startswith("FILE:IMG:"):
                encoded_content = body.replace("FILE:IMG:", "").encode('utf-8')
                decoded_content = base64.decodebytes(encoded_content)
                
                # Aquí solo estoy guardando como .png para simplificar, pero podrías mejorar esto.
                file_name = f"recibido_{timestamp}.png"
                with open(file_name, "wb") as img_file:
                    img_file.write(decoded_content)
                print(f"Imagen recibida y guardada como {file_name}")

            else:
                print("{} dice: {}".format(message["from"], body))

        elif message['type'] == 'groupchat':
            print(f"[{message['from'].resource}] {message['body']}")
        else:
            print(f"Received a message of type {message['type']} from {message['from']}: {message['body']}")




    
    def create_group(self):
        room_jid = input("Enter the JID of the group you want to create (e.g. room@server.tld): ")
        nick = input("Enter the nickname you want to use as the group admin: ")
        public = input("Do you want the group to be public? (yes/no): ").strip().lower()

        # Default value is private (0)
        is_public = 1 if public == 'yes' else 0
        
        # Join the group to create it.
        self.plugin["xep_0045"].join_muc(room_jid, nick)

        # Setting the room config
        self.plugin["xep_0045"].set_room_config(room_jid, {"muc#roomconfig_persistentroom": 1, 
                                                        "muc#roomconfig_publicroom": is_public})
        
        print(f"Group {room_jid} created successfully!")




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
