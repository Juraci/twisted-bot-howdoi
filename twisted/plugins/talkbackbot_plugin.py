from ConfigParser import ConfigParser

from twisted.application.service import IServiceMaker, Service
from twisted.internet.endpoints import clientFromString
from twisted.plugin import IPlugin
from twisted.python import usage, log
from zope.interface import implementer

from talkback.bot import TalkBackBotFactory
from talkback.adapter import Adapter


class Options(usage.Options):
    optParameters = [
        ['config', 'c', 'settings.ini', 'Configuration file.'],
    ]


class TalkBackBotService(Service):
    _bot = None

    def __init__(self, endpoint, channel, nickname, realname, password, triggers):
        self._endpoint = endpoint
        self._channel = channel
        self._nickname = nickname
        self._realname = realname
        self._password = password
        self._triggers = triggers

    def startService(self):
        """Construct a client & connect to server."""
        from twisted.internet import reactor

        def connected(bot):
            self._bot = bot

        def failure(err):
            log.err(err, _why='Could not connect to specified server.')
            reactor.stop()

        adapter = Adapter()
        client = clientFromString(reactor, self._endpoint)
        factory = TalkBackBotFactory(
            self._channel,
            self._nickname,
            self._realname,
            self._password,
            adapter,
            self._triggers,
        )

        return client.connect(factory).addCallbacks(connected, failure)

    def stopService(self):
        """Disconnect."""
        if self._bot and self._bot.transport.connected:
            self._bot.transport.loseConnection()


@implementer(IServiceMaker, IPlugin)
class BotServiceMaker(object):
    tapname = "twsrs"
    description = "IRC bot that provides answers for programming questions"
    options = Options
    options = Options

    def makeService(self, options):
        """Construct the talkbackbot service."""
        config = ConfigParser()
        config.read([options['config']])
        triggers = [
            trigger.strip()
            for trigger
            in config.get('talkback', 'triggers').split('\n')
            if trigger.strip()
        ]

        return TalkBackBotService(
            endpoint=config.get('irc', 'endpoint'),
            channel=config.get('irc', 'channel'),
            nickname=config.get('irc', 'nickname'),
            realname=config.get('irc', 'realname'),
            password=config.get('irc', 'password'),
            triggers=triggers,
        )

# Now construct an object which *provides* the relevant interfaces
# The name of this variable is irrelevant, as long as there is *some*
# name bound to a provider of IPlugin and IServiceMaker.

serviceMaker = BotServiceMaker()
