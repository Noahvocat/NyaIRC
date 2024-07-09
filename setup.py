#!/usr/bin/env python


from glob import glob


from setuptools import setup, find_packages


def parse_requirements(filename):
    with open(filename, "r") as f:
        for line in f:
            if line.startswith("git+http"):
                continue
            if line and line[:2] not in ("#", "-e"):
                yield line.strip()


setup(
    name="NyaIRC",
    description="NyaIRC SFW IRC chatting server",
    long_description=open("README.rst", "r").read(),
    author="James Mills",
    author_email="contact.noahvocat@gmail.com",
    url="http://bitbucket.org/prologic/charla/",
    download_url="http://bitbucket.org/prologic/charla/downloads/",
    classifiers=[
        "Development Status :: 1 - Alpha",
        "Environment :: No Input/Output (Daemon)",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Communications :: Chat :: Internet Relay Chat",
    ],
    license="MIT",
    keywords="irc server",
    platforms="POSIX",
    packages=find_packages("."),
    include_package_data=True,
    scripts=glob("bin/*"),
    install_requires=list(parse_requirements("requirements.txt")),
    entry_points={
        "console_scripts": [
            "charla=charla.main:main",
        ]
    },
    test_suite="tests.main.main",
    zip_safe=False,
    use_scm_version={
        "write_to": "charla/version.py",
    },
    setup_requires=[
        "setuptools_scm"
    ],
)
