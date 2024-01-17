#! python
#
# Narou url structure:
#   https://ncode.syosetu.com/n2749hf/1/
#       * n2749hf       ... 'n_code'
#       * /n2749hf/     ... Main page. That has table of contents.
#       * /n2749hf/1/   ... A part of pages.
#


import os
import argparse
import urllib.request
import urllib.parse
import time
import random
from logging import getLogger, DEBUG, INFO, ERROR
import logging.config
from lxml import html

logger = None

def make_url(base_url, *uris, **params):
    """
    see https://stackoverflow.com/questions/15799696/how-to-build-urls-in-python-with-the-standard-library
    """
    url = base_url.rstrip('/')
    for uri in uris:
        _uri = uri.strip('/')
        url = '{}/{}'.format(url, _uri) if _uri else url
    if params:
        url = '{}?{}'.format(url, urllib.parse.urlencode(params))
    return url

def get_title_text(prefix, n_code):
    html_file = os.path.join(prefix, n_code, 'index.html')

    html_content = ''
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    xroot = html.document_fromstring(bytes(html_content, encoding='utf-8'))

    title_obj = xroot.find_class('novel_title')
    return title_obj[0].text

def get_subtitle_refs(prefix, n_code):
    """
    Get all subtitles from title page.
    """
    #html_file = 'download/n2749hf/index.html'
    html_file = os.path.join(prefix, n_code, 'index.html')

    html_content = ''
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    xroot = html.document_fromstring(bytes(html_content, encoding='utf-8'))

    # Subtitles and link.
    subtitles = []
    subtitle_obj = xroot.find_class('subtitle')
    for dd in subtitle_obj:
        for a in dd:
            if a.get('href') is None:
                continue
            x = a.get('href').split('/')
            subtitles.append({'code':x[1], 'number':int(x[2]), 'subtitle':a.text})

    return subtitles

def parse_main_page(download_path, n_code):
    """
    return: dictionary.
        title:
        subtitles:
        author:
    """
    html_file = os.path.join(download_path, n_code, 'index.html')
    html_content = ''
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    xroot = html.document_fromstring(bytes(html_content, encoding='utf-8'))
    result = {}

    ### Title
    title_obj = xroot.find_class('novel_title')
    result['title'] = title_obj[0].text

    ### Author
    result['author'] = xroot.xpath('//*[@id="novel_color"]/div[2]/a')[0].text

    ### Subtitles
    subtitles = []
    subtitle_obj = xroot.find_class('subtitle')
    for dd in subtitle_obj:
        for a in dd:
            if a.get('href') is None:
                continue
            x = a.get('href').split('/')
            subtitles.append({'code':x[1], 'number':int(x[2]), 'subtitle':a.text})
    result['subtitles'] = subtitles

    return result

def get_body_of_part(html_file):
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    xroot = html.document_fromstring(bytes(html_content, encoding='utf-8'))

    """
    <div id="novel_honbun" class="novel_view" style="line-height: 180%; font-size: 100%;">
    """
    obj = xroot.get_element_by_id('novel_honbun')
    return html.tostring(obj, encoding="unicode")

def parse_part_page(html_file):
    """
    return: dictionary.
        chapter_title:
        content:
    """
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    xroot = html.document_fromstring(bytes(html_content, encoding='utf-8'))

    result = {}

    chapter_obj = xroot.find_class('chapter_title')
    if chapter_obj is None or len(chapter_obj) == 0:
        result['chapter_title'] = ''
    else:
        result['chapter_title'] = chapter_obj[0].text

    subtitle_obj = xroot.find_class('novel_subtitle')
    result['subtitle'] = subtitle_obj[0].text

    content_obj = xroot.get_element_by_id('novel_honbun')
    ### extract 'p' tags.
    lines = []
    for p in content_obj:
        lines.append(html.tostring(p, encoding="unicode"))
    result['content'] = ''.join(lines)

    return result

def make_subdir_for_subtitle(download_path, subdir):
    p = os.path.join(download_path, subdir)
    try:
        os.makedirs(p, exist_ok=True)
    except OSError as e:
        logger.error('os.makedirs({}). {}'.format(p, e.strerror))

def make_subdir_for_output(download_path, subdir):
    p = os.path.join(download_path, '{}.output'.format(subdir))
    try:
        os.makedirs(p, exist_ok=True)
        return p
    except OSError as e:
        logger.error('os.makedirs({}). {}'.format(p, e.strerror))
        return None

def make_html_filename(number_of_part):
    return '{:06d}.html'.format(number_of_part)

def make_download_filename(download_path, subdir, number_of_part):
    """
    Make filename for subtitles.
    Subtitles format likes are '/n2749hf/12/'.
    And, concatenates to {download_path}/{subdir}/000012.html.
    """
    return os.path.join(download_path, subdir, make_html_filename(number_of_part))

def download_main(download_path, subdir, base):
    ret_val = -1
    download_filepath = os.path.join(download_path, subdir, 'index.html')

    url = make_url(base, subdir)
    if not url.endswith('/'):
        url += '/'
    logger.debug('URL: {}'.format(url))
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req) as res:
            body = res.read()
            with open(download_filepath, 'wb') as f:
                f.write(bytes(body))
            ret_val = 0
    except urllib.error.HTTPError as err:
        logger.error('download_main: HTTPError, {}'.format(err.code))
    except urllib.error.URLError as err:
        logger.error('download_main: URLError, {}'.format(err.reason))
    except OSError as err:
        logger.error('download_main: OSError, {}'.format(err.strerror))

    return ret_val

def download_subs(download_path, subdir, base, subtitles):
    for s in subtitles:
        filename = make_download_filename(download_path, subdir, s['number'])
        if os.path.exists(filename):
            #logger.debug('Exists {}. Skip this part.'.format(filename))
            continue
        logger.info('Next download: {}, {}'.format(s['number'], s['subtitle']))
        url = make_url(base, s['code'], str(s['number']))
        if not url.endswith('/'):
            url += '/'
        logger.debug('URL: {}'.format(url))
        req = urllib.request.Request(url)
        try:
            with urllib.request.urlopen(req) as res:
                body = res.read()
                with open(filename, 'wb') as f:
                    f.write(bytes(body))
        except urllib.error.HTTPError as err:
            logger.error(err.code)
        except urllib.error.URLError as err:
            logger.error(err.reason)
        except OSError as err:
            logger.error(err.strerror)
        time.sleep(random.uniform(0.5, 1.5))

def set_logger(newlogger):
    logger = newlogger

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--download_path", type=str, help="Download path.", default='download')
    parser.add_argument("n_code", type=str, help="Codes starting with N assigned to novels on syosetu.com")
    args = parser.parse_args()

    logging.config.fileConfig('logging_settings.ini')
    logger = getLogger('root')

    logger.debug('n_code: {}'.format(args.n_code))
