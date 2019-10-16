import argparse
import copy
import glob
import logging
import os
from functools import singledispatch
from itertools import chain
from multiprocessing import Pool

from fontTools.ttLib import TTCollection, TTFont, getTableClass

from fixMacFonts import scriptLangTag

basicStyles = ('Regular', 'Bold', 'Italic', 'Bold Italic')

options = dict(recalcBBoxes=False, recalcTimestamp=False)

parser = argparse.ArgumentParser(description='Fixes some incompatible fonts from macOS.')
parser.add_argument('files', metavar='font', nargs='+',
                    help='incompatible font files (supports file wildcards).')
parser.add_argument('-d', '--dir', dest='dirname', default='compatible',
                    help='the directory to store the font files.'
                         '(default: "compatible" directory relative to the font file)')
parser.add_argument('--otf2ttf', action='store_true',
                    help='converts OpenType font to TrueType font.')
parser.add_argument('-v', '--verbose', action='count', default=0,
                    help='increases output verbosity')
args = parser.parse_args()

if args.otf2ttf:
    try:
        from afdko.otf2ttf import otf_to_ttf
    except ImportError:
        from fixMacFonts.otf2ttf import otf_to_ttf

if args.verbose == 1:
    logging.basicConfig(level=logging.INFO)
elif args.verbose > 1:
    logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

Script, likelyLang, likelyScript = scriptLangTag.get()
Script = set(Script)


@singledispatch
def rewrite(table):
    logger.debug(f"The '{table.tableTag}' table will not be rewritten")


@rewrite.register(getTableClass('cmap'))
def _(table):
    if table.getcmap(platformID=3, platEncID=1):
        return

    logger.info("Adding a format 4 'cmap' subtable")

    best_cmap = table.getBestCmap()

    cmap_format_4 = table.tables[-1].newSubtable(format=4)

    cmap_format_4.platformID, cmap_format_4.platEncID, cmap_format_4.language = 3, 1, 0
    cmap_format_4.cmap = {k: v for k, v in best_cmap.items() if k < 0x10000}

    table.tables.append(cmap_format_4)


@rewrite.register(getTableClass('meta'))
def _(table):
    for tag in ['dlng', 'slng']:
        langs = {lang.strip() for lang in table.data[tag].split(',')}
        scripts = set()

        for lang in langs:
            for script in lang.split('-'):
                if script in Script:
                    scripts.add(script)
                    break
            else:
                try:
                    script = likelyScript[lang]
                    if likelyLang[script] in langs:
                        scripts.add(script)
                except KeyError:
                    logger.warning(f'The ScriptLangTag "{lang}" probably'
                                   ' not conforming to BCP 47 is ignored')

        logger.debug(f"Rewriting values for '{tag}' in the 'meta' table")
        logger.info(f'old {tag}: "{table.data[tag]}"')

        table.data[tag] = ','.join(sorted(scripts))

        logger.info(f'new {tag}: "{table.data[tag]}"')


@rewrite.register(getTableClass('name'))
def _(table):
    names = dict()
    langs = set()

    for namerecord in table.names:
        if namerecord.platformID == 3:
            names[(namerecord.nameID, namerecord.langID)] = namerecord
            langs.add(namerecord.langID)

    for style in basicStyles:
        if str(names[(17, 0x409)]).endswith(style):
            break
    else:
        style = ''

    style = style.split()

    for lang in langs:
        try:
            family, subfamily = str(names[(16, lang)]), str(names[(17, lang)])
        except KeyError:
            continue

        fullname = family.split() + subfamily.split()

        logger.debug(f'Rewriting Family name')
        logger.info(f'old Family name: "{names[(1, lang)]!s}"')

        names[(1, lang)].string = ' '.join(fullname[:-len(style)]) if style else ' '.join(fullname)

        logger.info(f'new Family name: "{names[(1, lang)]!s}"')

        logger.debug(f'Rewriting Subamily name')
        logger.info(f'old Subamily name: "{names[(2, lang)]!s}"')

        names[(2, lang)].string = ' '.join(fullname[-len(style):]) if style else 'Regular'

        logger.info(f'new Subamily name: "{names[(2, lang)]!s}"')

        try:
            logger.debug(f'Rewriting Full name')
            logger.info(f'old Full name: "{names[(4, lang)]!s}"')

            names[(4, lang)].string = ' '.join(fullname)

            logger.info(f'new Full name: "{names[(4, lang)]!s}"')
        except KeyError:
            name4 = copy.copy(names[(1, lang)])
            name4.nameID = 4
            name4.string = ' '.join(fullname)
            table.names.append(name4)

            logger.info(f'Adding Full name "{name4.string!s}"')


@singledispatch
def repair(font):
    for tag in font.reader.keys():
        rewrite(font[tag])

    if font['OS/2'].fsSelection & 1:
        font['head'].macStyle |= 1 << 1
    if font['OS/2'].fsSelection & 1 << 5:
        font['head'].macStyle |= 1
    if font['OS/2'].fsSelection & 1 << 6:
        font['head'].macStyle &= ~0b11

    if args.otf2ttf:
        font.recalcBBoxes = True
        otf_to_ttf(font)


@repair.register(TTCollection)
def _(fonts):
    for font in fonts:
        repair(font)


def fix(file):
    dirname = args.dirname if os.path.exists(args.dirname) \
        else os.path.join(os.path.dirname(file), args.dirname)
    basename = os.path.basename(file)

    if not os.path.exists(dirname):
        os.mkdir(dirname)

    logger.name = basename

    with open(file, 'rb') as f:
        header = f.read(4)

    font = TTCollection(file, **options) if header == b'ttcf' \
        else TTFont(file, **options)

    repair(font)

    font.save(os.path.join(dirname, basename))


def main():
    files = chain.from_iterable(map(glob.glob, args.files))

    with Pool() as pool:
        pool.map(fix, files)


if __name__ == '__main__':
    main()
