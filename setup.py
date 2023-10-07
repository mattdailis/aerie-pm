from setuptools import setup

setup(
    name="pm",
    version="1.0.0",
    py_modules=["main"],
    install_requires=[
        "Click",
    ],
    entry_points={
        "console_scripts": [
            "pm = main:cli",
        ],
    },
)
