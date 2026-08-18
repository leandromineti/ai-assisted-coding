from setuptools import setup

setup(
    name='logpeek',
    version='1.0.0',
    py_modules=['logpeek'],
    entry_points={
        'console_scripts': [
            'logpeek=logpeek:main',
        ],
    },
)
