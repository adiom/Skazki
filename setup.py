from setuptools import setup, find_packages

setup(
    name="village_simulation",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "networkx>=3.1",
        "mesa>=2.1.1",
        "matplotlib>=3.7.0",
        "plotly>=5.13.0",
        "pytest>=7.3.1",
        "jupyter>=1.0.0",
        "sqlalchemy>=2.0.0",
        "python-dotenv>=1.0.0",
        "tqdm>=4.65.0",
        "pygame>=2.5.0"
    ],
) 