#! python
#
# 各話個別のhtmlファイルを結合する。
# 結合単位は、既定で『章』単位としている。
# オプション指定で、章単位の代わりに文字数単位とすることも可能。
#
# * TODO: 挿絵をどうするか？
# * TODO: TOML か何かで、Nコード毎に、どこで区切るかなどの設定をしたい → 上位スクリプトを作るのが良いか。
#

import os
import argparse
from logging import getLogger, DEBUG, INFO, ERROR
import logging.config
import re
from string import Template

import naroutil

logger = None

html_header_template = Template("""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="ja" lang="ja">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<title>${novel_title}</title>
</head>
<body>
""")

html_footer = """
</body></html>
"""

title_page_template = Template("""
<h1>${novel_title}</h1>
<p>著者: ${author}</p>
""")

chapter_header_template = Template("<h2 id=\"${anchor_id}\">${chapter}</h2>\n")
chapter_part_template = Template("<hr />\n<h3 id=\"${anchor_id}\">${part}</h3>\n")

br_line_pattern = '<p\s.*>\s*<br\s*/?>\s*</\s*p>\s*'
body_id_pattern = ' id="L\d+"' ## e.g. <p id="L123">

### br(改行) 単体の行は削除するなら True
enabled_remove_br = True

### html として完成させるなら True. ヘッダーあり、フッターありという意味。
enabled_complete_html = True

def make_toc_elem(text: str, type: str, anchor_id: str):
    return {'text': text, 'type': type, 'anchor_id': anchor_id}

def write_toc_html(filehandler, toc_list):
    """
    toc_list:
        Ordered list has dictionary element.
            text: text name.
            type: 'no_c' is chapter-less. 'c' is a chapter. 'p' is a part.
            anchor_id: reference to.
    """
    if toc_list is None or len(toc_list) == 0:
        return

    filehandler.write("<p>目次</p>")
    was_part = False
    for elem in toc_list:
        if elem['type'] == 'no_c':
            if was_part:
                filehandler.write("</ol>\n")
                was_part = False
            filehandler.write("<ol>\n")
        if elem['type'] == 'c':
            if was_part:
                filehandler.write("</ol>\n")
                was_part = False
            filehandler.write("<p><a href=\"#{}\">{}</a></p>\n<ol>\n".format(elem['anchor_id'], elem['text']))
        elif elem['type'] == 'p':
            was_part = True
            filehandler.write("<li><a href=\"#{}\">{}</a></li>\n".format(elem['anchor_id'], elem['text']))
    if was_part:
        filehandler.write("</ol>\n")

def write_html(filehandler, title_page, header_list, toc_list, body_list):
    if enabled_complete_html:
        for e in header_list:
            filehandler.write(e)

    filehandler.write(title_page)

    write_toc_html(filehandler, toc_list)

    for e in body_list:
        filehandler.write(e)

    if enabled_complete_html:
        filehandler.write(html_footer)

def is_chapter_end(new_chapter_title, prev_chapter_title, char_count, char_count_max):
    """
    章の区切り(出力ファイルの切り替え契機)であれば、True を返す。
    params:
        new_chapter_title: 章の見出し。
        prev_chapter_title: 前回の章の見出し。
        char_count: 章(区切り単位)の中の文字数。
        char_count_max: 区切り単位内と判断する最大文字数。0 なら、文字数では区切らない。
    """

    is_end = False
    if prev_chapter_title is None:
        # Maybe, first time.
        is_end = True
    elif char_count_max > 0:
        if char_count >= char_count_max:
            is_end = True
    else:
        if prev_chapter_title != new_chapter_title:
            is_end = True
    
    return is_end

def make_combined_chapter(download_path, n_code, need_toc, cut_count):
    """
    ひとつの章毎に1ファイル作る。
    もし、cut_count が 0 より大きい場合は、章ではなく、文字数がその値を越えた話で区切り、ファイルを作っていく。
    あくまでファイルを区切る単位は、『話(part)』である。
    """
    main_info = naroutil.parse_main_page(download_path, n_code)
    logger.debug('title: {}'.format(main_info['title']))
    logger.debug('author: {}'.format(main_info['author']))

    title_page = title_page_template.substitute(novel_title=main_info['title'], author=main_info['author'])

    title_text = main_info['title']

    subtitles = main_info['subtitles']
    output_dir = naroutil.make_subdir_for_output(download_path, n_code)

    part_files = []
    chapter_number = 0
    chapter_title = None
    header_list = []
    toc_list = []
    body_list = []
    char_count = 0
    f = None # Output Filehandler.
    for s in subtitles:
        html_file = naroutil.make_html_filename(s['number'])
        part_obj = naroutil.parse_part_page(os.path.join(download_path, n_code, html_file))

        # Chapter
        if is_chapter_end(part_obj['chapter_title'], chapter_title, char_count, cut_count):
            output_filepath = os.path.join(output_dir, '{}_{}.html'.format(n_code, chapter_number))
            if len(body_list) > 0:
                f = open(output_filepath, 'w', encoding='utf-8')
                if not need_toc:
                    toc_list = []
                write_html(f, title_page, header_list, toc_list, body_list)
                logger.info(f'Write to {output_filepath}')
                header_list = []
                toc_list = []
                body_list = []

            chapter_number += 1
            chapter_title = part_obj['chapter_title']
            if len(chapter_title) == 0:
                title = f'{title_text}'
            else:
                title = f'{title_text} / {chapter_title}'
            html_header = html_header_template.substitute(novel_title=title)

            header_list.append(html_header)

            if len(chapter_title) == 0:
                toc_list.append(make_toc_elem('', 'no_c', ''))
            else:
                chapter_anchor = f'c{chapter_number}'
                chapter_header = chapter_header_template.substitute(anchor_id=chapter_anchor, chapter=chapter_title)
                
                body_list.append(chapter_header)
                toc_list.append(make_toc_elem(chapter_title, 'c', chapter_anchor))
            part_files.append(output_filepath)
            char_count = 0

        # Part / Subtitle
        part_anchor = 'p{}'.format(s['number'])
        chapter_part = chapter_part_template.substitute(anchor_id=part_anchor, part=part_obj['subtitle'])
        body_list.append(chapter_part)
        toc_list.append(make_toc_elem(part_obj['subtitle'], 'p', part_anchor))

        # Body / Content
        body = part_obj['content']
        clean_body = None
        if enabled_remove_br:
            ### Remove lines only 'br' tags.
            body2 = re.sub(br_line_pattern, '', body, count=0)
            clean_body = re.sub(body_id_pattern, '', body2, count=0)
        else:
            clean_body = body

        char_count += len(clean_body)
        body_list.append(clean_body)
 
    if len(body_list) > 0:
        output_filepath = os.path.join(output_dir, '{}_{}.html'.format(n_code, chapter_number))
        f = open(output_filepath, 'w', encoding='utf-8')
        if not need_toc:
            toc_list = []
        write_html(f, title_page, header_list, toc_list, body_list)
        logger.info(f'Write to {output_filepath}')
        header_list = []
        toc_list = []
        body_list = []

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--download_path", type=str, help="Download path.", default='download')
    parser.add_argument("--toc", type=bool, help="Make TOC.", default=True)
    parser.add_argument("--cut_char_count", type=int, help="Cut count. If 0, does not cut by character-count.", default=0)
    parser.add_argument("n_code", type=str, help="Codes starting with 'n' each assigned novels. That you can find syosetu.com.")
    args = parser.parse_args()

    logging.config.fileConfig('logging_settings.ini')
    logger = getLogger('root')
    naroutil.logger = logger

    logger.debug('n_code: {}'.format(args.n_code))

    make_combined_chapter(args.download_path, args.n_code, args.toc, args.cut_char_count)
