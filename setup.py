from setuptools import setup, find_packages

setup(
    name="ainexus-phoenix",
    version="3.0.0",
    packages=find_packages(),
    install_requires=[
        "flask==2.3.3",
        "web3==6.5.0", 
        "numpy==1.24.3",
        "pandas==2.0.3",
        "requests==2.31.0",
        "python-dotenv==1.0.0",
        "jinja2==3.1.2",
        "setuptools==65.5.0",
        "wheel==0.38.4",
    ],
    python_requires=">=3.8,<3.12",
)
