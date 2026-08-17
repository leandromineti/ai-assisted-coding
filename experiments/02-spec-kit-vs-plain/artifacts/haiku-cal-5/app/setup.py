from setuptools import setup, find_packages

setup(
    name="tarpeek",
    version="1.0.0",
    description="Summarize tar archive contents without extracting",
    author="Claude",
    py_modules=["tarpeek"],
    entry_points={
        "console_scripts": [
            "tarpeek=tarpeek:main",
        ],
    },
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
