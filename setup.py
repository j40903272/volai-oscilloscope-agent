"""Setup script for oscilloscope control system."""

from setuptools import setup, find_packages

setup(
    name="oscilloscope-agent",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pyvisa>=1.14.1",
        "mcp>=1.1.2",
        "fastapi>=0.109.0",
        "uvicorn>=0.31.1",
        "pydantic>=2.9.2",
        "anthropic>=0.39.0",
        "httpx>=0.27.2",
        "langchain>=0.3.7",
        "langchain-anthropic>=0.3.0",
        "langchain-core>=0.3.17",
        "langchain-community>=0.3.5",
        "python-dotenv>=1.0.0",
        "numpy>=1.26.3",
        "pandas>=2.2.0",
    ],
    python_requires=">=3.9",
)

