#! python
#
# 小説を読もうから、各話を html でダウンロードする。
# 横書き前提の小説が存在すること、および、ルビがまっとうに見えることから、html 形式としている。
# なお、text 形式の場合、ルビが《 》で奇妙な場所へ挿入されることもあった。
#
# ダウンロードしたファイルの結合は、別のツール(モジュール)としている。
# 結合自体はファイルが存在すれば、並行して動作可能であるため。
#
# 小説を読もうにおける http header に、'Last-Modified' は存在しない。
# よって、更新された部分だけを得ようとする場合、手間をかける必要がある。
# タイトルページの各話に対応する更新日時を得てタイムスタンプを比較するか、あるいは、無視するか。
# 一旦、更新日時は無視し、追加された話数だけダウンロードするようにしたい。
#
# 各話のダウンロードは、少し時間を空けて行う。
#

import os
import argparse
from logging import getLogger, DEBUG, INFO, ERROR
import logging.config

import naroutil

logger = None

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--download_path", type=str, help="Download path.", default='download')
    parser.add_argument("n_code", type=str, help="Codes starting with N assigned to novels on syosetu.com")
    args = parser.parse_args()

    logging.config.fileConfig('logging_settings.ini')
    logger = getLogger('root')
    naroutil.logger = logger

    logger.debug('n_code: {}'.format(args.n_code))

    baseurl = 'https://ncode.syosetu.com/'
    try:
        os.makedirs(os.path.join(args.download_path, args.n_code), exist_ok=True)
    except OSError as err:
        logger.error('makedirs: OSError: {}', err.strerror)

    if naroutil.download_main(args.download_path, args.n_code, baseurl) == 0:
        subtitles = naroutil.get_subtitle_refs(prefix=args.download_path, n_code=args.n_code)
        naroutil.make_subdir_for_subtitle(args.download_path, args.n_code)
        naroutil.download_subs(args.download_path, args.n_code, baseurl, subtitles)
 