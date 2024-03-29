import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'SQLAlchemy',
    'transaction',
    'pyramid_tm',
    'pyramid_debugtoolbar',
    'zope.sqlalchemy',
    'waitress',
    'dropbox',
    'ziggurat_foundations',
    'oauth2',
    'psycopg2',
    ]

setup(name='cloudyshelf',
      version='0.0',
      description='cloudyshelf',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Gavin Carothers',
      author_email='gavin@carothers.name',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='cloudyshelf',
      install_requires = requires,
      entry_points = """\
      [paste.app_factory]
      main = cloudyshelf:main
      [console_scripts]
      populate_cloudyshelf = cloudyshelf.scripts.populate:main
      """,
      )

