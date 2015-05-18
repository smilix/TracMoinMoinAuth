from setuptools import find_packages, setup

extra = {}

setup(
    name='TracMoinMoinAuthPlugin',
    version="0.2",
    description="Trac MoinMoin Auth",
    author="HolgerCremer",
    author_email="HolgerCremer@gmail.com",
    license="MIT",
    packages=[
        'tracmoinmoinauth',
        ],
    keywords="trac moin auth plugin",
    classifiers=[
        'Framework :: Trac',
    ],
    install_requires=['TracAccountManager'],
    entry_points={
        'trac.plugins': [
            'tracmoinmoinauth.auth_moinmoin = tracmoinmoinauth.auth_moinmoin',
            ]
    }
)

