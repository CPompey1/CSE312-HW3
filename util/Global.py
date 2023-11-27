from util.Database import Database
from util.ChatSockets import ChatSockets
DB = Database('ChatMessages','localhost',27017)
CHATSOCKETS = ChatSockets()