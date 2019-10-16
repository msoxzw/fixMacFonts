import json
import logging
import lzma
import os
import xml.etree.ElementTree as ET
from urllib.request import urlopen

ScriptLangTagFile = os.path.splitext(__file__)[0] + '.json.xz'

subtagUrl = 'https://www.iana.org/assignments/language-subtag-registry/language-subtag-registry'

likelySubtagUrl = 'https://raw.githubusercontent.com/unicode-org/cldr/master/common/supplemental/likelySubtags.xml'

logger = logging.getLogger(__name__)


def get(file=ScriptLangTagFile):
    try:
        with lzma.open(file, 'rt') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, lzma.LZMAError):
        return download(file)


def download(file=ScriptLangTagFile):
    Script = list()
    likelyLang = dict()
    likelyScript = dict()

    logger.info(f'Downloading "{os.path.basename(subtagUrl)}" from {subtagUrl}')
    with urlopen(subtagUrl) as f:
        for line in f:
            if line == b'Type: script\n':
                script = f.readline().split()[1]
                Script.append(script.decode('utf-8'))

    logger.info(f'Downloading "{os.path.basename(likelySubtagUrl)}" from {likelySubtagUrl}')
    with urlopen(likelySubtagUrl) as f:
        root = ET.fromstring(f.read())

    for likelySubtag in root.iter('likelySubtag'):
        tag = likelySubtag.get('from').replace('_', '-')
        lang, script, region = likelySubtag.get('to').split('_')

        if tag.startswith('und'):
            if len(tag) == 8 or len(tag) == 3:
                likelyLang[script] = lang
        elif len(tag) < 4:
            likelyScript[lang] = script

    logger.info(f'Saving "{file}"')
    with lzma.open(file, 'wt') as f:
        json.dump([Script, likelyLang, likelyScript], f)

    return Script, likelyLang, likelyScript
