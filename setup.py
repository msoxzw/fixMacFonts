from setuptools import setup

setup(
    name='fixMacFonts',
    version='1.0.0',
    packages=['fixMacFonts'],
    license='apache-2.0',
    description='Fixes some incompatible fonts from macOS.',
    python_requires='>=3.6',
    install_requires=['fontTools >= 3.22.0'],
    extras_require={
        'ttf': ['cu2qu'],
    },
    entry_points={
        'console_scripts': [
            'fixMacFonts=fixMacFonts.fix:main',
        ],
    },
)
