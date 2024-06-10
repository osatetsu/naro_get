#! python
#
# An auto run download.py and cat_html.py.
# This reads a config file and executes it.
# That config file is in TOML format.
#
# See https://toml.io/en/
#

import tomllib
import subprocess
from logging import getLogger, DEBUG, INFO, ERROR
import logging.config

default_config_files = ['naroutil.ini', 'naroutil.toml', ]

logger = None

def read_config():
    '''
    Read config file.
    '''
    tomldata = None
    for filepath in default_config_files:
        try:
            with open(filepath, 'rb') as f:
                tomldata = tomllib.load(f)
                logger.debug(f'Read {filepath}')
                break
        except OSError as e:
            logger.error(f'{e.__traceback__}, {filepath}')
        except TypeError as e:
            logger.error(f'{e.__traceback__}, {filepath}')
        except tomllib.TOMLDecodeError as e:
            logger.error(f'{e.__traceback__}, {filepath}')
        except ValueError as e:
            logger.error(f'{e.__traceback__}, {filepath}')
    return tomldata

def update_files(tomldata):
    '''
    Download and Make html.
    '''
    if not tomldata:
        return
    config_common = {}

    if 'common' in tomldata.keys():
        config_common = tomldata['common']

    for ncode in tomldata.keys():
        if not ncode.startswith('n'):
            continue

        # download
        download_args = ['python', 'download.py', ]
        if 'download_path' in config_common.keys():
            download_args.append('--download_path')
            download_args.append(config_common['download_path'])
        download_args.append(ncode)
        logger.debug(download_args)
        subprocess.run(download_args)

        # make html
        cathtml_args = ['python', 'cat_html.py', ]
        arg_dict = config_common | tomldata[ncode]
        for k in arg_dict.keys():
            cathtml_args.append(f'--{k}')
            cathtml_args.append(str(arg_dict[k]))
        cathtml_args.append(ncode)
        logger.debug(cathtml_args)
        subprocess.run(cathtml_args)

if __name__ == "__main__":
    logging.config.fileConfig('logging_settings.ini')
    logger = getLogger('root')

    tomldata = read_config()
    update_files(tomldata)
