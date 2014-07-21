# -*- test-case-name: tests.test_talkbackbot -*-

import re
from twisted.internet import protocol
from twisted.python import log
from twisted.words.protocols import irc


class TalkBackBot(irc.IRCClient):
    def connectionMade(self):
        """Called when a connection is made."""
        self.nickname = self.factory.nickname
        self.realname = self.factory.realname
        self.password = self.factory.password
        irc.IRCClient.connectionMade(self)
        log.msg("connectionMade")

    def connectionLost(self, reason):
        """Called when a connection is lost."""
        irc.IRCClient.connectionLost(self, reason)
        log.msg("connectionLost {!r}".format(reason))

    # callbacks for events

    def signedOn(self):
        """Called when bot has successfully signed on to server."""
        log.msg("Signed on")
        if self.nickname != self.factory.nickname:
            log.msg('Your nickname was already occupied, actual nickname is '
                    '"{}".'.format(self.nickname))
        where = self.factory.channel + " " + self.factory.password
        log.msg("where: %s" % where)
        self.join(where)

    def joined(self, channel):
        """Called when the bot joins the channel."""
        log.msg("[{nick} has joined {channel}]"
                .format(nick=self.nickname, channel=self.factory.channel,))

    def privmsg(self, user, channel, msg):
        """Called when the bot receives a message."""
        sendTo = None
        prefix = ''
        senderNick = user.split('!', 1)[0]
        if channel == self.nickname:
            # /MSG back
            sendTo = senderNick
        elif msg.startswith(self.nickname):
            # Reply back on the channel
            sendTo = channel
            prefix = senderNick + ' the most relevant answer is:\n'
        else:
            msg = msg.lower()
            for trigger in self.factory.triggers:
                if trigger in msg:
                    sendTo = channel
                    prefix = senderNick + ' the most relevant answer is:\n'
                    break

        if sendTo:
            question = msg.replace("howdoi ", "")
            answer = self.factory.adapter.ask(question)
            self.msg(sendTo, prefix + answer)
            log.msg(
                "sent message to {receiver}, triggered by {sender}:\n\t{answer}"
                .format(receiver=sendTo, sender=senderNick, answer=answer)
            )


class TalkBackBotFactory(protocol.ClientFactory):
    protocol = TalkBackBot

    def __init__(self, channel, nickname, realname, password, adapter, triggers):
        """Initialize the bot factory with our settings."""
        self.channel = channel
        self.nickname = nickname
        self.realname = realname
        self.password = password
        self.adapter = adapter
        self.triggers = triggers
