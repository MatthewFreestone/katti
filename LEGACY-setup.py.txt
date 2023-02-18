from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()
with open("requirements.txt", "r") as fh:
    requirements = fh.read()

setup(
    name="katti",
    version="0.0.1",
    author="Matthew Freestone",
    author_email="",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="", # github repo
    packages=find_packages(where='src'),
    py_modules=['src'],
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    entry_points= {
        'console_scripts': [
            'katti = src.katti:main',
        ]
    },
    package_data={'katti': ['config/*.json']},
)