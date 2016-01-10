from setuptools import setup
import os
import sys

SRC_ROOT, _ = os.path.split(__file__)
PROJECT_ROOT = os.path.dirname(SRC_ROOT)

REVISION = '0.0.1'
PROJECT_NAME = 'neowrapper'
PROJECT_AUTHORS = "Salim Fadhley"
# Please see readme.rst for a complete list of contributors
PROJECT_EMAILS = 'salimfadhley@gmail.com'
PROJECT_URL = ""
SHORT_DESCRIPTION = ''

python_version = (sys.version_info.major, sys.version_info.minor)

DEPENDENCIES = \
    ['py2neo', ] + \
    (['typing'] if python_version < (3, 5) else [])

try:
    DESCRIPTION = open(os.path.join(PROJECT_ROOT, "README.md")).read()
except IOError:
    DESCRIPTION = SHORT_DESCRIPTION

GLOBAL_ENTRY_POINTS = {
    "console_scripts":
        []
}

setup(
        name=PROJECT_NAME.lower(),
        version=REVISION,
        author=PROJECT_AUTHORS,
        author_email=PROJECT_EMAILS,
        packages=['ladygeek'],
        zip_safe=True,
        include_package_data=False,
        install_requires=DEPENDENCIES,
        test_suite='nose.collector',
        tests_require=['mock', 'nose', 'coverage'],
        entry_points=GLOBAL_ENTRY_POINTS,
        url=PROJECT_URL,
        description=SHORT_DESCRIPTION,
        long_description=DESCRIPTION,
        license='MIT',
        classifiers=[
            'Development Status :: 4 - Beta',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Natural Language :: English',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 2.7',
            'Topic :: Software Development :: Testing',
        ],
)
