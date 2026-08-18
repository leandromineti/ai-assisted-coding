from setuptools import setup, find_packages

setup(
    name="logpeek",
    version="0.1.0",
    description="A Python CLI that summarizes structured log files",
    author="",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "logpeek=logpeek.cli:main",
        ],
    },
    python_requires=">=3.8",
    install_requires=[],
)
