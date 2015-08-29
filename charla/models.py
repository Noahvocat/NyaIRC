"""Data Models"""


from time import time
from operator import attrgetter
from socket import socket, error as SocketError


from bidict import bidict

from circuits.protocols.irc import joinprefix

from redisco.models import Model
from redisco.models import Attribute, BooleanField, DateTimeField
from redisco.models import IntegerField, ListField, ReferenceField


class SocketField(Attribute):

    cache = bidict()

    def typecast_for_read(self, value):
        return self.cache.get(int(value), None)

    def typecast_for_storage(self, value):
        if value is None:
            return None

        try:
            fd = value.fileno()
            self.cache[fd] = value
            return fd
        except SocketError:
            try:
                fd = self.cache[:value]
                self.cache[fd] = value
                return fd
            except KeyError:
                return None

    def value_type(self):
        return socket

    def acceptable_types(self):
        return self.value_type()


class User(Model):

    sock = SocketField(required=True)
    host = Attribute(default="")
    port = IntegerField(default=0)

    nick = Attribute(default=None)
    away = Attribute(default=None)
    modes = Attribute(default="")

    channels = ListField("Channel")
    userinfo = ReferenceField("UserInfo")

    registered = BooleanField(default=False)
    lastmessage = IntegerField(default=None)
    signon = DateTimeField(auto_now_add=True)

    def __repr__(self):
        attrs = self.attributes_dict.copy()
        attrs["channels"] = map(attrgetter("name"), attrs["channels"])

        key = self.__class__.__name__ if self.is_new() else self.key()

        return "<{0} {1}>".format(key, attrs)

    @property
    def oper(self):
        return "o" in self.modes

    @property
    def visible(self):
        return not self.invisible

    @property
    def invisible(self):
        return "i" in self.modes

    @property
    def prefix(self):
        userinfo = self.userinfo
        if userinfo is None:
            return
        return joinprefix(*self.source)

    @property
    def source(self):
        userinfo = self.userinfo
        if userinfo is None:
            return
        return self.nick, userinfo.user, userinfo.host

    class Meta:
        indices = ("id", "sock", "nick",)


class UserInfo(Model):

    user = Attribute(default=None)
    host = Attribute(default=None)
    server = Attribute(default=None)
    name = Attribute(default=None)

    def __nonzero__(self):
        return all(x is not None for x in (self.user, self.host, self.name))


class Channel(Model):

    name = Attribute(required=True, unique=True)
    users = ListField("User")
    modes = Attribute(default="")
    operators = ListField("User")
    voiced = ListField("User")

    _topic = Attribute(default=None)
    _topic_setter = Attribute(default=None)
    _topic_timestamp = IntegerField(default=None)

    def __repr__(self):
        attrs = self.attributes_dict.copy()
        attrs["users"] = map(attrgetter("nick"), attrs["users"])

        if not self.is_new():
            return "<%s %s>" % (self.key(), attrs)

        return "<%s %s>" % (self.__class__.__name__, attrs)

    @property
    def topic(self):
        return self._topic, self._topic_setter, self._topic_timestamp

    @topic.setter
    def topic(self, (topic, setter)):
        self._topic = topic
        self._topic_setter = setter
        self._topic_timestamp = int(time())
        self.save()

    @property
    def type(self):
        return self.name[0]

    @property
    def userprefixes(self):
        def prefix(user):
            if user in self.operators:
                return "@{0}".format(user.nick)
            if user in self.voiced:
                return "+{0}".format(user.nick)
            return user.nick

        return map(prefix, sorted(self.users, key=prefix))

    class Meta:
        indices = ("id", "name",)
