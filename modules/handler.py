from datetime import datetime
import json
import traceback

from tornado import websocket

from helpers import get_unread
from logger import log
from models.action import Action
from models.forum import Forum
from models.mod import Mod
from shared import *
from models.user import User

class SocketHandler(websocket.WebSocketHandler):
    def check_origin(self, origin):
        # Origin URLs do not have a trailing slash.
        setattr(self, 'origin', origin + '/')
        return True

    def open(self):
        # Do nothing. The handler will
        # be added to the list if it receives
        # a proper handshake.
        #
        # Eventually though, we want to be able
        # to verify sending domains.
        pass

    def handshake(self, user, key, mod_key):
        # Only one handshake per connection.
        if hasattr(self, 'user'):
            return

        # Check for disabled boards.
        board = Forum.from_key_and_bpath(user['board_key'], user['bpath'])

        # Returning without sending an access key
        # basically cripples the front-end script
        # since access keys are required to send
        # messages.
        if board is None:
            return

        if board.enabled == False or board.real_location != self.origin:
            return

        name = user['name']
        user = User.create_from(user)

        user.name = name
        user.save()

        # if the above passes this is a handshake
        setattr(self, 'user', user)

        conn_mutex.acquire()
        connections.append((self.user.toKey(), self))
        conn_mutex.release()

        # Send API key.

        handshake = Action(
            event='handshake',
            details=self.user.access_key,
            source=self.user.access_key,
            receiver=self.user.access_key
        )

        self.push_action(handshake, self.user.access_key, 0)

    def push_action(self, action, key, mod_key):
        if not self.user or not self.user.validate_key(key):
            return

        if not Mod.key_exists(mod_key):
            log('Attempted to use invalid modification key:', mod_key)
            return

        forum = Forum.from_key(self.user.board_key)

        mod_keys = forum.mod_keys.split('\r\n')

        if str(mod_key) not in mod_keys:
            log('Attempted to use invalid modification key:', mod_key)
            return

        action = Action.create_from(action)
        receiver = User.from_access_key(action.receiver)

        # Check for cross-board requests
        if self.user.board_key != receiver.board_key:
            log('Attempted to send cross-board request:', self.user.board_key, receiver.board_key)
            return

        if action.timestamp > datetime.utcnow():
            store_queue.put(action)
        else:
            action_queue.put(action)

    def get_unread(self, user, key, mod_key):
        if hasattr(self, 'unread_done'):
            return

        setattr(self, 'unread_done', True)

        for action in get_unread(self.user):
            # action
            self.push_action(action, self.user.access_key, 0)

    def on_message(self, message):
        try:
            log('Received:', message)

            message = json.loads(message)

            # A dict of message handlers.
            handlers = {
                'handshake': self.handshake,
                'get_unread': self.get_unread,
                'action': self.push_action
            }

            handler = handlers[message['type']]
            mod_key = message['mod_key'] if 'mod_key' in message else None

            # 0 is reserved for system use.
            if mod_key == '0' and message['type'] == 'action':
                return

            handler(message['data'], message['key'], mod_key)
        except:
            # any of the above causing an error
            # means something wrong happened
            # and we should ignore. log the error
            # anyway in case.
            log('An unknown error occurred:', traceback.format_exc())

    def on_close(self):
        if 'user' in self.__dict__:
            conn_mutex.acquire()
            connections.remove((self.toKey(), self))
            conn_mutex.release()

            log('Disconnected from user:', self.toKey())

    def toKey(self):
        return self.user.toKey()
