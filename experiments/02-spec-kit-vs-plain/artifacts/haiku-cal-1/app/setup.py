from setuptools import setup, find_packages

setup(
    name="tarpeek",
    version="1.0.0",
    description="Summarize tar archive contents without extracting",
    author="Claude",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "tarpeek=tarpeek.cli:main",
        ],
    },
    python_requires=">=3.7",
)
