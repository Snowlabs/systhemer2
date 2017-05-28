import logging


def setup_logger(Settings):
    log_props = Settings.log_props
    MAXLEN = log_props['MAXLEN']
    log_names = log_props['log_names']
    for l, n in log_names.items():
        logging.addLevelName(l, n)

    # TODO: automate this next chunk
    VDEBUG = log_names[Settings.VDEBUG]
    DEBUG = log_names[logging.DEBUG]
    INFO = log_names[logging.INFO]
    WARNING = log_names[logging.WARNING]
    ERROR = log_names[logging.ERROR]
    CRITICAL = log_names[logging.CRITICAL]

    fileHandler = logging.FileHandler('systhemer.log', mode='w')
    consHandler = logging.StreamHandler()
    fileFormatter = logging.Formatter(
        '%(levelname)-'+str(MAXLEN)+'s'
        ':%(name)-25s: '
        '%(message)s')

    # Color shortcuts
    llc = '%(line_log_color)s'
    mlc = llc + '%(message_log_color)s'
    lc = llc + '%(log_color)s'
    reset = '%(reset)s'

    if not Settings.no_colorlog:
        from colorlog import ColoredFormatter
        consFormatter = ColoredFormatter(
            lc+'%(levelname)-'+str(MAXLEN)+'s'+reset
            + llc+':%(name)-25s: '
            + mlc+'%(message)s'+reset,

            log_colors={
                VDEBUG:   'bold_cyan',
                DEBUG:    'bold_blue',
                INFO:     'green',
                WARNING:  'yellow',
                ERROR:    'red',
                CRITICAL: 'red,bg_white',
            },
            secondary_log_colors={
                'line': {
                    DEBUG:    'bg_black,bold_white'
                },
                'message': {
                    VDEBUG:   'cyan',
                    DEBUG:    'bold_blue',
                    ERROR:    'red',
                    CRITICAL: 'red'
                }
            })
    else:
        consFormatter = fileFormatter

    # highest verbosity for file logger
    fileHandler.setLevel(Settings.VDEBUG)
    consHandler.setLevel(Settings.verbosity)
    fileHandler.setFormatter(fileFormatter)
    consHandler.setFormatter(consFormatter)

    logger = logging.getLogger('Systhemer')
    logger.setLevel(Settings.VDEBUG)
    logger.addHandler(fileHandler)
    logger.addHandler(consHandler)

    return logger
