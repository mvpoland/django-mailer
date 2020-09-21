from setuptools import setup, find_packages

from mailer import __version__


setup(
    name="django-mailer-mv",
    version=__version__,
    description="A reusable Django app for queuing the sending of email",
    long_description=open("docs/usage.txt").read(),
    author="James Tauber",
    author_email="jtauber@jtauber.com",
    url="http://code.google.com/p/django-mailer/",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: 3.5",
        "Programming Language :: Python :: 3 :: 3.6",
        "Programming Language :: Python :: 3 :: 3.7",
        "Programming Language :: Python :: 3 :: 3.8",
        "Framework :: Django",
        "Framework :: Django :: 2.0",
        "Framework :: Django :: 2.1",
        "Framework :: Django :: 2.2",
        "Framework :: Django :: 3.0",
        "Framework :: Django :: 3.1",
    ],
    install_requires=[
        "lockfile>=0.8",
        "six",
    ],
    python_requires=">=3.5",
)
