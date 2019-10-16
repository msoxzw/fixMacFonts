# Improve compatibility of fonts from macOS

Granted, macOS carries many high quality fonts, but Apple modified them intentionally
for incompatibility with other Operating system. However, these modifications, actually,
violate OpenType spec. This project aims to recover the original faces of these fonts,
thereby making fonts installed on other OS, e.g. Windows.

## Highlight

Do never touch typefaces themselves

Accept ttc font (TrueType Collection) without splitting

Support conversion from OpenType to TrueType

Support multiprocessing to leverage modern multi-core CPU

Support file wildcards

### Requirements

Python >= 3.6

fontTools >= 3.22.0

afdko or cu2qu if need TrueType conversion

### Installation

`pip install "fixMacFonts-*.whl"`

### Usage

Fixes some incompatible fonts from macOS

`fixMacFonts font.ttc fonts/*.otf`

Convert to TrueType (CPU intensive!)

`fixMacFonts --otf2ttf font.ttc fonts/*.otf`

"Need Internet connection for the first use in order to download data for speculation from
language subtag to script subtag"

### Details

Fix 'cmap' table given [here](https://docs.microsoft.com/typography/opentype/spec/cmap)
and [there](https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6cmap.html)

Fix 'meta' table given [here](https://docs.microsoft.com/typography/opentype/spec/meta)
and [there](https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6meta.html)

Fix 'name' table given [here](https://docs.microsoft.com/typography/opentype/spec/name)
and [there](https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6name.html)

fix 'head' table given [here](https://docs.microsoft.com/typography/opentype/spec/head)
and [there](https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6head.html)

Apparently and ironically, Apple do not adhere to their own documents.
