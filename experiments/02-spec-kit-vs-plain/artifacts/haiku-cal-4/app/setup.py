from setuptools import setup, find_packages

setup(
    name="tarpeek",
    version="0.1.0",
    description="Summarize tar archive contents without extracting",
    author="Claude",
    packages=find_packages(),
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "tarpeek=tarpeek.cli:main",
        ],
    },
)
