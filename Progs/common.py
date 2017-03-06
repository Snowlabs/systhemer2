
class ConfigElement(object):
    parent = None

class Rule(ConfigElement):
    def __init__(self, rule, keys):
        self.rule = rule
        self.keys = keys

class Section(ConfigElement):
    def __init__(self, name, startchar, rules, endchar):
        self.name = name
        self.startchar = startchar
        self.rules = rules
        self.endchar = endchar
        for rule in self.rules:
            rule.parent = self

    def __iter__(self):
        return self

    def __next__(self):
        pass
