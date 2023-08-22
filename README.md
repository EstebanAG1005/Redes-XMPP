
# XMPP Chat Client

This project is an XMPP chat client built using the `slixmpp` library. It offers functionalities for user registration, chat sessions, and various XMPP protocol interactions.

## Features:

### Client Features:
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

## Usage

It is recommended to use a python version lower than 3.9

py -3.9 menu_functions.py

## Dependencies:

- aioconsole==0.5.0
- aiodns==3.0.0
- aiohttp==3.7.4.post0
- slixmpp==1.7.1
- async-timeout==3.0.1
