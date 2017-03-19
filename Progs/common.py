import logging
logger = logging.getLogger('Systhemer.Progs.common')
Settings = None


class ConfigElement(object):
    parent = None
    tree = None

    def build_hierarchy_tree(self):
        """generate hierarchy tree for Rule object"""

        assert isinstance(self.parent, ConfigElement) or self.parent is None
        self.tree = [e for e in self.parent.get_tree()] if self.parent else []
        self.tree.append(self)
        logger.log(Settings.VDEBUG, 'tree generated: %s', self.tree)
        return self.tree

    def get_tree(self, force_rebuild=False):
        """generate hierarchy tree if needed and return it"""
        if self.tree:
            logger.debug('hierarchy tree already exists...')
            if force_rebuild:
                logger.debug('force_rebuild was true, '
                             'rebuilding hierarchy tree...')
                return self.build_hierarchy_tree()
            return self.tree
        else:
            logger.debug('initializing hierarchy tree...')
            return self.build_hierarchy_tree()


class RuleTree(ConfigElement):
    def __init__(self, *args):
        self.logger = logger
        self.leaves = None
        self.rules = args
        for r in self.rules:
            r.parent = self

    def __iter__(self):
        return iter(self.rules)

    def __getitem__(self, key):
        return self.rules[key]

    def _get_leaves(self, section_obj):
        out = []
        for ro in section_obj:
            if isinstance(ro, Section):
                out.extend(self._get_leaves(ro))
            elif isinstance(ro, Rule):
                out.append(ro)
            # invalid type
            else:
                self.logger.critical('Member or descendant of self.config'
                                     ' has invalid type: \'%s\'',
                                     ro.__class__)
                exit(1)
        return out

    def build_leaves_list(self):
        self.leaves = self._get_leaves(self)
        self.logger.log(Settings.VDEBUG, 'leaves list generated: %s',
                        self.leaves)
        return self.leaves

    def get_leaves(self, force_rebuild=False):
        """generate leaves array if needed and return it"""
        if self.leaves:
            self.logger.debug('leaves array already exists...')
            if force_rebuild:
                self.logger.debug('force_rebuild was true, '
                                  'rebuilding leaves array...')
                return self.build_leaves_list()
            return self.leaves
        else:
            self.logger.debug('initializing leaves array...')
            return self.build_leaves_list()


class Rule(ConfigElement):
    def __init__(self, rule, keys):
        self.rule = rule
        self.keys = keys


class Section(ConfigElement):
    def __init__(self, name, startchar, endchar, *rules,
                 separator=r'[ \t\n]*'):
        self.name = name
        self.startchar = startchar
        self.rules = rules
        self.endchar = endchar
        self.separator = separator
        for rule in self.rules:
            rule.parent = self

    def __iter__(self):
        return iter(self.rules)

    def __getitem__(self, key):
        return self.rules[key]
