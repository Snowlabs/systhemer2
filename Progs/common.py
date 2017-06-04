"""General utilities and common global variables.
"""


import logging
logger = logging.getLogger('Systhemer.Progs.common')
Settings = None


class utils(object):
    """Namespace for basic utilities.
    """
    @staticmethod
    def get_home_dir():
        """Get home directory for the user.
        """
        from os.path import expanduser
        return expanduser('~')

    @staticmethod
    def get_setting(setting, default=None, critical=True, msg=None):
        """Get a setting from self.Settings.
        NOTE: probably should get moved to common module..."""
        value = getattr(Settings, setting, None)
        if value is None:
            msg = msg if msg is not None else \
                  'Setting \'%s\' not set!' % setting
            if critical:
                logger.critical(msg)
                exit(1)
            else:
                logger.error(msg + ' Returning \'None\'.', setting)
                return default
        return value

    @staticmethod
    def is_excluded(exclude_rule, check_range):
        """ Check if the given range is within the exclude rule.

        :param tuple exclude_rule: (depth, startpos, endpos)
        :param tuple check_range:  (startpos, endpos)

        :return:
            * **1** if range is completely in the exclude range

            * **2** if range is partially in the exclude range

            * **0** if range is not at all in the exclude range
        """
        # avoid nonsense (start > end) = nonsense
        if check_range[0] > check_range[1]:
            logger = logging.getLogger('Systhemer.common.utils')
            logger.critical('Range makes no sense!'
                            ' Startpos is bigger than endpos!')
            exit(1)

        exclude_range = range(exclude_rule[1], exclude_rule[2]+1)

        # if range is completely within the exclude range
        if (check_range[0] in exclude_range) and \
           (check_range[1] in exclude_range):
            return 1

        # if range is partially within the exclude range
        if (check_range[0] in exclude_range) or \
           (check_range[1] in exclude_range):
            return 2

        # if range is not in the exclude range at all
        return 0
