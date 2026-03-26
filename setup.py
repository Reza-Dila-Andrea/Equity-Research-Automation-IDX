"""
Setup configuration for Equity Research Reports AI
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="equity-research-reports-ai",
    version="1.0.0",
    author="Reza",
    author_email="reza@example.com",
    description="Automated equity research for Indonesian stocks (IDX)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/equity-research-reports-ai",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "Development Status :: 4 - Beta",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    include_package_data=True,
    keywords=[
        "finance",
        "stock",
        "valuation",
        "dcf",
        "equity-research",
        "indonesia",
        "idx",
        "ai",
    ],
)
