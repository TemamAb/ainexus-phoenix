from setuptools import setup, find_packages

setup(
    name="ainexus",
    version="3.0.0",
    packages=find_packages(),
    install_requires=[
        "Flask==2.3.3",
        "Werkzeug==2.3.7",
        "Jinja2==3.1.2",
        "gunicorn==21.2.0",
    ],
)
