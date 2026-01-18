from setuptools import setup, find_packages

setup(
    name="municipal-miner",
    version="0.1.0",
    description="Pre-RFP intelligence mining from municipal meeting documents",
    author="Turnberry",
    packages=find_packages(),
    install_requires=[
        "click>=8.1.0",
        "sqlite-utils>=3.35",
        "llm>=0.13",
        "pymupdf>=1.23.0",
        "pydantic>=2.5.0",
        "python-dotenv>=1.0.0",
        "rich>=13.7.0",
        "loguru>=0.7.2",
    ],
    entry_points={
        "console_scripts": [
            "municipal-miner=municipal_miner.cli:cli",
        ],
    },
    python_requires=">=3.9",
)
