import slixmpp
from slixmpp.exceptions import IqError, IqTimeout

# Class wiht al the XMPP functions
class Client(slixmpp.ClientXMPP):
    def __init__(self, jid, password):
        slixmpp.ClientXMPP.__init__(self, jid, password)

        self.use_aiodns = False

        self.just_registered = False

        # Event listeners
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("register", self.register)
        self.add_event_handler("message", self.get_message)
        self.add_event_handler("chatstate_composing", self.receive_notification)

    async def start(self, event):
        # Get contacts and setting status after loging in
        self.send_presence()
        await self.get_roster()

        if self.just_registered:
            print("You can now login using the created account.")
            self.disconnect()
        return

        # Menu after logging in or creating account
        menu = """
        1. Log Out
        2. Delete Account
        3. Show contacts
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
            elif choose == "2":
                print("Delete Account")
                show = False
                self.delete_account()
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
        print("Function not yet implemented.")

    # Function to join a group chat
    def join_group(self):
        print("Function not yet implemented.")

    # Function to send a message to a group
    def send_group_message(self):
        print("Function not yet implemented.")

    # Function to send a private message
    def private_message(self):
        print("Function not yet implemented.")

    # Function to show the detail from a specific contact
    def show_contact_details(self):
        print("Function not yet implemented.")

    # Function to show every contact and group
    def show_contacts(self):
        print("Function not yet implemented.")

    # Function to add a contact
    def add_contact(self):
        print("Function not yet implemented.")

    # Function to change the presence
    def change_presence(self):
        print("Function not yet implemented.")

    # Function when you receive a message
    def get_message(self, message):
        print("Function not yet implemented.")

    # Function to send notification while typing a message
    def send_notification(self, recipient, state):
        print("Function not yet implemented.")

    # Function when you receive a notification
    def receive_notification(self, chatstate):
        print("Function not yet implemented.")

    # Function to register a new account to the server from the client menu
    async def register(self, iq):
        responce = self.Iq()
        responce["type"] = "set"
        responce["register"]["username"] = self.boundjid.user
        responce["register"]["password"] = self.password

        try:
            await responce.send()
            print("Account created")
            self.disconnect()
            self.just_registered = True
        except IqError as e:
            print("Could not register account")
            self.disconnect()
        except IqTimeout:
            print("No response from server")
            self.disconnect()
