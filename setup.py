#!/usr/bin/env python3
"""
Fallback setup.py for chatterbox-vllm
Used when pyproject.toml editable install fails
"""

from setuptools import setup, find_packages
import os

# Read version from generated file if it exists
version = "0.1.0"  # default version
version_file = ".latest-version.generated.txt"
if os.path.exists(version_file):
    with open(version_file, "r") as f:
        version = f.read().strip()

setup(
    name="chatterbox-vllm",
    version=version,
    description="Chatterbox TTS ported to VLLM for efficient and advanced inference tasks",
    author="David Li",
    author_email="david@david-li.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={
        "chatterbox_tts": ["models/t3/*.json", "models/*/t3/*.json"]
    },
    python_requires=">=3.10",
    install_requires=[
        "torch",
        "torchaudio",
        "transformers<4.54.0",
        "tokenizers",
        "scipy",
        "numpy",
        "librosa",
        "s3tokenizer",
        "omegaconf",
        "conformer",
        "diffusers",
        "vllm==0.10.0",
        "peft",
        "llvmlite>=0.44.0",
        "gradio",
        "fastapi",
        "uvicorn",
    ],
    extras_require={
        "dev": ["build", "twine"],
    },
    keywords=["llm", "gpt", "cli", "tts", "chatterbox"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
