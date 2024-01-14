#! python
#
# 小説を読もうから、各話を html でダウンロードする。
# 横書き前提の小説が存在すること、および、ルビがまっとうに見えることから、html 形式としている。
# なお、text 形式の場合、ルビが《 》で奇妙な場所へ挿入されることもあった。
#
# ダウンロードしたファイルの結合は、別のツール(モジュール)としている。
# 結合自体はファイルが存在すれば、並行して動作可能であるため。
#
# 小説を読もう web site における http header に、'Last-Modified' は存在しない。
# よって、更新された部分だけを得ようとする場合、手間をかける必要がある。
# タイトルページの各話に対応する更新日時を得てタイムスタンプを比較するか、あるいは、無視するか。
# 一旦、更新日時は無視し、追加された話数だけダウンロードするようにしたい。
#
# 各話のダウンロードは、少し時間を空けて行う。
# 小説を読もうサイトへ負荷をかけることは本意ではない。
#

import os
import argparse
import urllib.request
import time
import random
from logging import getLogger, DEBUG, INFO, ERROR
import logging.config
from lxml import html

logger = None

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

    # Title.
#    title_obj = xroot.find_class('novel_title')
#    title_text = title_obj[0].text
#    print(title_text)

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

def make_subdir_for_subtitle(download_path, subdir):
    p = os.path.join(download_path, subdir)
    try:
        os.makedirs(p, exist_ok=True)
    except OSError as e:
        logger.error('os.makedirs({}). {}'.format(p, e.strerror))

def make_download_filename(download_path, subdir, number_of_part):
    """
    Make filename for subtitles.
    Subtitles format likes are '/n2749hf/12/'.
    And, concatenates to {download_path}/{subdir}/000012.html.
    """
    return os.path.join(download_path, subdir, '{:06d}.html'.format(number_of_part))

def download_subs(download_path, subdir, base, subtitles):
    for s in subtitles:
        filename = make_download_filename(download_path, subdir, s['number'])
        if os.path.exists(filename):
            logger.debug('Exists {}. Skip this part.'.format(filename))
            continue
        logger.info('Next download: {}, {}'.format(s['number'], s['subtitle']))
        url = '{}/{}/{}/'.format(base, s['code'], s['number'])
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--download_path", type=str, help="Download path.", default='download')
    parser.add_argument("n_code", type=str, help="Codes starting with N assigned to novels on syosetu.com")
    args = parser.parse_args()

    logging.config.fileConfig('logging_settings.ini')
    logger = getLogger('root')

    logger.debug('n_code: {}'.format(args.n_code))

    baseurl = 'https://ncode.syosetu.com/'
    subtitles = get_subtitle_refs(prefix=args.download_path, n_code=args.n_code)
    make_subdir_for_subtitle(args.download_path, args.n_code)
    download_subs(args.download_path, args.n_code, baseurl, subtitles)
