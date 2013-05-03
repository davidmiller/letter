import re
import os

from distutils.core import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()


VERSION_FILE = os.path.join(here, "letter/_version.py")
verstrline = open(VERSION_FILE, "rt").read()
VSRE = r'^__version__ = [\'"]([^\'"]*)[\'"]'
mo = re.search(VSRE,  verstrline, re.M)
if mo:
    VERSION = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in {0}".format(VERSION_FILE))

setup(
    name = "letter",
    version = VERSION,
    author = "David Miller",
    author_email = "david@deadpansincerity.com",
    url = "https://github.com/davidmiller/letter",
    description = "Send you letters for fun or profit",
    long_description = README + "\n\n" + CHANGES,
    install_requires = [
        'ffs>=0.0.7',
        'jinja2',
        ],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 2.6",
        "Operating System :: OS Independent",
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries"
        ],
    packages = ['letter', 'letter.contrib'],
    )
