from util.Database import Database
from util.ChatSockets import ChatSockets
from threading import Lock
DB = Database('ChatMessages','localhost',27017)
CHATSOCKETS = ChatSockets()
MUTEX = Lock()