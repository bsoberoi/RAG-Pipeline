#!/usr/bin/env python3
"""Setup script for RAG Pipeline CLI application."""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    try:
        with open('README.md', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "RAG Pipeline - Retrieval-Augmented Generation System"

# Read requirements
def read_requirements():
    try:
        with open('requirements.txt', 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        return []

setup(
    name="rag-pipeline",
    version="1.0.0",
    description="RAG Pipeline - Retrieval-Augmented Generation System",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/rag-pipeline",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        '': ['config/*.yaml', 'docs/*.md'],
    },
    install_requires=read_requirements(),
    python_requires=">=3.8",
    entry_points={
        'console_scripts': [
            'rag=main:main',
            'rag-pipeline=main:main',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="rag retrieval augmented generation ai nlp chatbot",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/rag-pipeline/issues",
        "Source": "https://github.com/yourusername/rag-pipeline",
        "Documentation": "https://github.com/yourusername/rag-pipeline/blob/main/README.md",
    },
) 