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
        "Framework :: Django",
    ],
    install_requires=["future", "lockfile >= 0.8", "six",],
)
