
# XMPP Chat Client

This project is an XMPP chat client built using the `slixmpp` library. It offers functionalities for user registration, chat sessions, and various XMPP protocol interactions.

## Features:

### Client Features:
1. Initialize the client with JID and password.
2. Set up logging for the client.
3. Start the XMPP session.
4. Delete an XMPP account.
5. Join an XMPP group.
6. Send a group message.
7. Continuous message sending loop.
8. Callback for received messages.
9. Get user input during a session.
10. Send private messages.
11. Display contact details.
12. Display a list of contacts.
13. Add a new contact.
14. Handle subscription requests.
15. Change online presence (e.g., online, away).
16. Send files.
17. Receive and handle messages.
18. Create a group.
19. Send notifications (e.g., typing).
20. Receive and handle notifications (e.g., another user typing).
21. Register a new user.

### Utility Features:
1. Initiate registration for a new user.
2. Initiate a chat session for a user.

## Installation:

1. Clone the repository:
```bash
git clone <repository_url>
```
2. Navigate to the project directory:
```bash
cd <project_directory>
```
3. Install the required packages:
```bash
pip install -r requirements.txt
```

## Dependencies:

- aioconsole==0.5.0
- aiodns==3.0.0
- aiohttp==3.7.4.post0
- slixmpp==1.7.1
- async-timeout==3.0.1
