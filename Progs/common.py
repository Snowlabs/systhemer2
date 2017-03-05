

class Rule(object):
    def __init__(self, rule, keys):
        self.rule = rule
        self.keys = keys

class Section(object):
    def __init__(self, name, startchar, rules, endchar):
        self.name = name
        self.startchar = startchar
        self.rules = rules
        self.endchar = endchar

    def __iter__(self):
        return self

    def __next__(self):
        pass
