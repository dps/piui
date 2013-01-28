import os
from setuptools import setup

setup(
    name = "piui",
    version = "0.0.3",
    author = "David Singleton",
    author_email = "davidsingleton@gmail.com",
    description = ("Add a mobile UI to your RaspberryPi"
                   " project."),
    license = "BSD",
    keywords = "raspberrypi mobile ui",
    url = "http://github.com/dps/piui",
    packages=['piui'],
    long_description=("Add a mobile UI to your RaspberryPi"
                   " project."),
    package_data = {'piui' : ['piui/static/*']},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: BSD License",
    ],
    install_requires = ['cherrypy'],
)
