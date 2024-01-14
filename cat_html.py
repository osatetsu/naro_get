#! python
#
# 各話個別のhtmlファイルを結合する。
#

import os
import argparse
from logging import getLogger, DEBUG, INFO, ERROR
import logging.config

import naroutil

logger = None

html_header_template = """
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="ja" lang="ja">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<title>__NOVEL_TITLE__</title>
</head>
<body>
"""

html_footer = """
</body></html>
"""

title_header_template = """
<h1>__NOVEL_TITLE__</h1>
"""

part_header_template = """
<hr />
<h2>__NOVEL_SUBTITLE__</h2>
"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--download_path", type=str, help="Download path.", default='download')
    parser.add_argument("n_code", type=str, help="Codes starting with N assigned to novels on syosetu.com")
    args = parser.parse_args()

    logging.config.fileConfig('logging_settings.ini')
    logger = getLogger('root')
    naroutil.set_logger(logger)

    logger.debug('n_code: {}'.format(args.n_code))

    #baseurl = 'https://ncode.syosetu.com/'
    title_text = naroutil.get_title_text(prefix=args.download_path, n_code=args.n_code)
    html_header = html_header_template.replace('__NOVEL_TITLE__', title_text)
    title_header = title_header_template.replace('__NOVEL_TITLE__', title_text)

    subtitles = naroutil.get_subtitle_refs(prefix=args.download_path, n_code=args.n_code)
    output_dir = naroutil.make_subdir_for_output(args.download_path, args.n_code)

    logger.debug('Start parse of parts.')
    part_files = []
    for s in subtitles:
        html_file = naroutil.make_html_filename(s['number'])
        logger.debug('parse {}'.format(html_file))
        html_path = os.path.join(output_dir, html_file)
        if os.path.exists(html_path):
            continue
        body = naroutil.get_body_of_part(os.path.join(args.download_path, args.n_code, html_file))
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(body)
        part_files.append(html_path)

    logger.debug('Start concatenation.')
    cat_file = os.path.join(output_dir, '{}_all.html'.format(args.n_code))
    with open(cat_file, 'w', encoding='utf-8') as wf:
        wf.write(html_header)
        wf.write(title_header)
        for s in subtitles:
            html_file = naroutil.make_html_filename(s['number'])
            logger.debug('cat {}'.format(html_file))
            html_path = os.path.join(output_dir, html_file)
            part_header = part_header_template.replace('__NOVEL_SUBTITLE__', s['subtitle'])
            body_of_part = None
            with open(html_path, 'r', encoding='utf-8') as rf:
                body_of_part = rf.read()
            wf.write(part_header)
            wf.write(body_of_part)
        wf.write(html_footer)

    logger.debug('created {}'.format(cat_file))
