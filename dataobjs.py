from PyQt4 import QtGui, QtCore
from datetime import *
import re
import random

from generic import PesterIcon
from parsetools import timeDifference, convertTags, lexMessage, parseRegexpFunctions
from mispeller import mispeller

_groupre = re.compile(r"\\([0-9]+)")
_upperre = re.compile(r"upper\(([\w<>\\]+)\)")
_lowerre = re.compile(r"lower\(([\w<>\\]+)\)")
_scramblere = re.compile(r"scramble\(([\w<>\\]+)\)")
_reversere = re.compile(r"reverse\(([\w<>\\]+)\)")

class Mood(object):
    moods = ["chummy", "rancorous", "offline", "pleasant", "distraught",
             "pranky", "smooth", "ecstatic", "relaxed", "discontent",
             "devious", "sleek", "detestful", "mirthful", "manipulative",
             "vigorous", "perky", "acceptant", "protective", "mystified",
             "amazed", "insolent", "bemused" ]
    moodcats = ["chums", "trolls", "other"]
    revmoodcats = {'discontent': 'trolls', 'insolent': 'chums', 'rancorous': 'chums', 'sleek': 'trolls', 'bemused': 'chums', 'mystified': 'chums', 'pranky': 'chums', 'distraught': 'chums', 'offline': 'chums', 'chummy': 'chums', 'protective': 'other', 'vigorous': 'trolls', 'ecstatic': 'trolls', 'relaxed': 'trolls', 'pleasant': 'chums', 'manipulative': 'trolls', 'detestful': 'trolls', 'smooth': 'chums', 'mirthful': 'trolls', 'acceptant': 'trolls', 'perky': 'trolls', 'devious': 'trolls', 'amazed': 'chums'}

    def __init__(self, mood):
        if type(mood) is int:
            self.mood = mood
        else:
            self.mood = self.moods.index(mood)
    def value(self):
        return self.mood
    def name(self):
        try:
            name = self.moods[self.mood]
        except IndexError:
            name = "chummy"
        return name
    def icon(self, theme):
        try:
            f = theme["main/chums/moods"][self.name()]["icon"]
        except KeyError:
            return PesterIcon(theme["main/chums/moods/chummy/icon"])
        return PesterIcon(f)


class pesterQuirk(object):
    def __init__(self, quirk):
        if type(quirk) != dict:
            raise ValueError("Quirks must be given a dictionary")
        self.quirk = quirk
        self.type = self.quirk["type"]
        if "on" not in self.quirk:
            self.quirk["on"] = True
        self.on = self.quirk["on"]
    def apply(self, string, first=False, last=False):
        if not self.on:
            return string
        elif self.type == "prefix":
            return self.quirk["value"] + string
        elif self.type == "suffix":
            return string + self.quirk["value"]
        elif self.type == "replace":
            return string.replace(self.quirk["from"], self.quirk["to"])
        elif self.type == "regexp":
            fr = self.quirk["from"]
            if not first and len(fr) > 0 and fr[0] == "^":
                return string
            if not last and len(fr) > 0 and fr[len(fr)-1] == "$":
                return string
            to = self.quirk["to"]
            pt = parseRegexpFunctions(to)
            return re.sub(fr, pt.expand, string)
        elif self.type == "random":
            if len(self.quirk["randomlist"]) == 0:
                return string
            fr = self.quirk["from"]
            if not first and len(fr) > 0 and fr[0] == "^":
                return string
            if not last and len(fr) > 0 and fr[len(fr)-1] == "$":
                return string
            def randomrep(mo):
                choice = random.choice(self.quirk["randomlist"])
                pt = parseRegexpFunctions(choice)
                return pt.expand(mo)
            return re.sub(self.quirk["from"], randomrep, string)
        elif self.type == "spelling":
            percentage = self.quirk["percentage"]/100.0
            words = string.split(" ")
            newl = []
            for w in words:
                p = random.random()
                if p < percentage:
                    newl.append(mispeller(w))
                else:
                    newl.append(w)
            return " ".join(newl)

    def __str__(self):
        if self.type == "prefix":
            return "BEGIN WITH: %s" % (self.quirk["value"])
        elif self.type == "suffix":
            return "END WITH: %s" % (self.quirk["value"])
        elif self.type == "replace":
            return "REPLACE %s WITH %s" % (self.quirk["from"], self.quirk["to"])
        elif self.type == "regexp":
            return "REGEXP: %s REPLACED WITH %s" % (self.quirk["from"], self.quirk["to"])
        elif self.type == "random":
            return "REGEXP: %s RANDOMLY REPLACED WITH %s" % (self.quirk["from"], [str(r) for r in self.quirk["randomlist"]])
        elif self.type == "spelling":
            return "MISPELLER: %d%%" % (self.quirk["percentage"])

class pesterQuirks(object):
    def __init__(self, quirklist):
        self.quirklist = []
        for q in quirklist:
            self.addQuirk(q)
    def plainList(self):
        return [q.quirk for q in self.quirklist]
    def addQuirk(self, q):
        if type(q) == dict:
            self.quirklist.append(pesterQuirk(q))
        elif type(q) == pesterQuirk:
            self.quirklist.append(q)
    def apply(self, lexed, first=False, last=False):
        prefix = [q for q in self.quirklist if q.type=='prefix']
        suffix = [q for q in self.quirklist if q.type=='suffix']

        newlist = []
        for (i, o) in enumerate(lexed):
            if type(o) not in [str, unicode]:
                if i == 0:
                    string = " "
                    for p in prefix:
                        string += p.apply(string)
                    newlist.append(string)
                newlist.append(o)
                continue
            lastStr = (i == len(lexed)-1)
            string = o
            for q in self.quirklist:
                if q.type != 'prefix' and q.type != 'suffix':
                    if q.type == 'regexp' or q.type == 'random':
                        string = q.apply(string, first=(i==0), last=lastStr)
                    else:
                        string = q.apply(string)
            if i == 0:
                if len(prefix) >= 1:
                    myprefix = random.choice(prefix)
                    string = myprefix.apply(string)
            if lastStr:
                if len(suffix) >= 1:
                    mysuffix = random.choice(suffix)
                    string = mysuffix.apply(string)
            newlist.append(string)

        final = []
        for n in newlist:
            if type(n) in [str, unicode]:
                final.extend(lexMessage(n))
            else:
                final.append(n)
        return final

    def __iter__(self):
        for q in self.quirklist:
            yield q

class PesterProfile(object):
    def __init__(self, handle, color=None, mood=Mood("offline"), group=None, chumdb=None):
        self.handle = handle
        if color is None:
            if chumdb:
                color = chumdb.getColor(handle, QtGui.QColor("black"))
            else:
                color = QtGui.QColor("black")
        self.color = color
        self.mood = mood
        if group is None:
            if chumdb:
                group = chumdb.getGroup(handle, "Chums")
            else:
                group = "Chums"
        self.group = group
    def initials(self, time=None):
        handle = self.handle
        caps = [l for l in handle if l.isupper()]
        if not caps:
            caps = [""]
        initials = (handle[0]+caps[0]).upper()
        if hasattr(self, 'time') and time:
            if self.time > time:
                return "F"+initials
            elif self.time < time:
                return "P"+initials
            else:
                return "C"+initials
        else:
            return (handle[0]+caps[0]).upper()
    def colorhtml(self):
        if self.color:
            return self.color.name()
        else:
            return "#000000"
    def colorcmd(self):
        if self.color:
            (r, g, b, a) = self.color.getRgb()
            return "%d,%d,%d" % (r,g,b)
        else:
            return "0,0,0"
    def plaindict(self):
        return (self.handle, {"handle": self.handle,
                              "mood": self.mood.name(),
                              "color": unicode(self.color.name()),
                              "group": unicode(self.group)})
    def blocked(self, config):
        return self.handle in config.getBlocklist()

    def memsg(self, syscolor, lexmsg, time=None):
        suffix = lexmsg[0].suffix
        msg = convertTags(lexmsg[1:], "text")
        uppersuffix = suffix.upper()
        if time is not None:
            handle = "%s %s" % (time.temporal, self.handle)
            initials = time.pcf+self.initials()+time.number+uppersuffix
        else:
            handle = self.handle
            initials = self.initials()+uppersuffix
        return "<c=%s>-- %s%s <c=%s>[%s]</c> %s --</c>" % (syscolor.name(), handle, suffix, self.colorhtml(), initials, msg)
    def pestermsg(self, otherchum, syscolor, verb):
        return "<c=%s>-- %s <c=%s>[%s]</c> %s %s <c=%s>[%s]</c> at %s --</c>" % (syscolor.name(), self.handle, self.colorhtml(), self.initials(), verb, otherchum.handle, otherchum.colorhtml(), otherchum.initials(), datetime.now().strftime("%H:%M"))
    def moodmsg(self, mood, syscolor, theme):
        return "<c=%s>-- %s <c=%s>[%s]</c> changed their mood to %s <img src='%s' /> --</c>" % (syscolor.name(), self.handle, self.colorhtml(), self.initials(), mood.name().upper(), theme["main/chums/moods"][mood.name()]["icon"])
    def idlemsg(self, syscolor, verb):
        return "<c=%s>-- %s <c=%s>[%s]</c> %s --" % (syscolor.name(), self.handle, self.colorhtml(), self.initials(), verb)
    def memoclosemsg(self, syscolor, timeGrammar, verb):
        return "<c=%s><c=%s>%s%s%s</c> %s.</c>" % (syscolor.name(), self.colorhtml(), timeGrammar.pcf, self.initials(), timeGrammar.number, verb)
    def memoopenmsg(self, syscolor, td, timeGrammar, verb, channel):
        (temporal, pcf, when) = (timeGrammar.temporal, timeGrammar.pcf, timeGrammar.when)
        timetext = timeDifference(td)
        initials = pcf+self.initials()
        return "<c=%s><c=%s>%s</c> %s %s %s.</c>" % \
            (syscolor.name(), self.colorhtml(), initials, timetext, verb, channel[1:].upper().replace("_", " "))
    def memobanmsg(self, opchum, opgrammar, syscolor, timeGrammar):
        initials = timeGrammar.pcf+self.initials()+timeGrammar.number
        opinit = opgrammar.pcf+opchum.initials()+opgrammar.number
        return "<c=%s>%s</c> banned <c=%s>%s</c> from responding to memo." % \
            (opchum.colorhtml(), opinit, self.colorhtml(), initials)
    def memojoinmsg(self, syscolor, td, timeGrammar, verb):
        (temporal, pcf, when) = (timeGrammar.temporal, timeGrammar.pcf, timeGrammar.when)
        timetext = timeDifference(td)
        initials = pcf+self.initials()+timeGrammar.number
        return "<c=%s><c=%s>%s %s [%s]</c> %s %s." % \
            (syscolor.name(), self.colorhtml(), temporal, self.handle,
             initials, timetext, verb)
    def memoopmsg(self, opchum, opgrammar, syscolor):
        opinit = opgrammar.pcf+opchum.initials()+opgrammar.number
        return "<c=%s>%s</c> made <c=%s>%s</c> an OP." % \
            (opchum.colorhtml(), opinit, self.colorhtml(), self.initials())
    def memodeopmsg(self, opchum, opgrammar, syscolor):
        opinit = opgrammar.pcf+opchum.initials()+opgrammar.number
        return "<c=%s>%s</c> took away <c=%s>%s</c>'s OP powers." % \
            (opchum.colorhtml(), opinit, self.colorhtml(), self.initials())
    def memovoicemsg(self, opchum, opgrammar, syscolor):
        opinit = opgrammar.pcf+opchum.initials()+opgrammar.number
        return "<c=%s>%s</c> gave <c=%s>%s</c> voice." % \
            (opchum.colorhtml(), opinit, self.colorhtml(), self.initials())
    def memodevoicemsg(self, opchum, opgrammar, syscolor):
        opinit = opgrammar.pcf+opchum.initials()+opgrammar.number
        return "<c=%s>%s</c> took away <c=%s>%s</c>'s voice." % \
            (opchum.colorhtml(), opinit, self.colorhtml(), self.initials())

    @staticmethod
    def checkLength(handle):
        return len(handle) <= 256
    @staticmethod
    def checkValid(handle):
        caps = [l for l in handle if l.isupper()]
        if len(caps) != 1 or handle[0].isupper():
            return False
        if re.search("[^A-Za-z0-9]", handle) is not None:
            return False
        return True

class PesterHistory(object):
    def __init__(self):
        self.history = []
        self.current = 0
        self.saved = None
    def next(self, text):
        if self.current == 0:
            return None
        if self.current == len(self.history):
            self.save(text)
        self.current -= 1
        text = self.history[self.current]
        return text
    def prev(self):
        self.current += 1
        if self.current >= len(self.history):
            self.current = len(self.history)
            return self.retrieve()
        return self.history[self.current]
    def reset(self):
        self.current = len(self.history)
        self.saved = None
    def save(self, text):
        self.saved = text
    def retrieve(self):
        return self.saved
    def add(self, text):
        if len(self.history) == 0 or text != self.history[len(self.history)-1]:
            self.history.append(text)
        self.reset()
