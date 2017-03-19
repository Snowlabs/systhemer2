import logging

def setup_logger(Settings):

    logging.addLevelName(Settings.VDEBUG, 'VDEBUG')

    fileHandler = logging.FileHandler('systhemer.log', mode='w')
    consHandler = logging.StreamHandler()
    fileFormatter = logging.Formatter(
        '%(levelname)-8s:%(name)-25s: %(message)s')
    llc = '%(line_log_color)s'
    mlc = llc + '%(message_log_color)s'
    lc = llc + '%(log_color)s'
    reset = '%(reset)s'

    if not Settings.no_colorlog:
        from colorlog import ColoredFormatter
        consFormatter = ColoredFormatter(
            lc+'%(levelname)-8s'+reset+llc
            + ':%(name)-25s: ' + mlc+'%(message)s'+reset,
            log_colors={
                'VDEBUG':   'bold_cyan',
                'DEBUG':    'bold_blue',
                'INFO':     'green',
                'WARNING':  'yellow',
                'ERROR':    'red',
                'CRITICAL': 'red,bg_white',
            },
            secondary_log_colors={
                'line': {
                    'DEBUG':    'bg_bold_black,bold_white'
                },
                'message': {
                    'VDEBUG':   'cyan',
                    'DEBUG':    'bold_blue',
                    'ERROR':    'red',
                    'CRITICAL': 'red'
                }
            })
    else:
        consFormatter = fileFormatter

    fileHandler.setLevel(Settings.VDEBUG)
    consHandler.setLevel(Settings.verbose)
    fileHandler.setFormatter(fileFormatter)
    consHandler.setFormatter(consFormatter)

    logger = logging.getLogger('Systhemer')
    logger.setLevel(Settings.VDEBUG)
    logger.addHandler(fileHandler)
    logger.addHandler(consHandler)
    return logger
