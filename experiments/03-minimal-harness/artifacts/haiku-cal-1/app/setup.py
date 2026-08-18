from setuptools import setup, find_packages

setup(
    name="logpeek",
    version="1.0.0",
    description="Summarize structured log files",
    author="Claude",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "logpeek=logpeek.cli:main",
        ],
    },
    install_requires=[],
    python_requires=">=3.8",
    include_package_data=True,
)
