from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="logpeek",
    version="0.1.0",
    author="Your Name",
    description="A Python CLI that summarizes structured log files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/logpeek",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "logpeek=logpeek.cli:main",
        ],
    },
)
