from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mcqgenrator",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A multiple choice question generator using OpenAI GPT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mcqgenrator",
    packages=find_packages(where="scr"),
    package_dir={"": "scr"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
    install_requires=[
        "openai",
        "langchain",
        "pandas",
        "python-dotenv",
        "PyPDF2",
        "streamlit",
    ],
    entry_points={
        "console_scripts": [
            "mcqgenrator=mcqgenrator.MCQ:main",
        ],
    },
)
