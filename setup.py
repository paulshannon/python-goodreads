from distutils.core import setup

setup(
    name='goodreads',
    description='A python library to access the goodreads.com api',
    url='https://github.com/paulshannon/python-goodreads',
    install_requires=['oauth2', 'requests', 'lxml'],
    version='0.1',
    author='Paul Shannon',
    license="GPLv3",
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    packages=['goodreads'],
)
