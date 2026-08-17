from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='tarpeek',
    version='0.1.0',
    description='Summarize tar archive contents without extracting',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Your Name',
    author_email='your.email@example.com',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    python_requires='>=3.8',
    install_requires=[
        'tabulate>=0.9.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'tarpeek=tarpeek.cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)
