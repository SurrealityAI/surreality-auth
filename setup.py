from setuptools import setup, find_packages

setup(
    name="surreality-auth",
    version="1.0.0",
    author="SurrealityAI",
    author_email="engineering@surreality.ai",
    description="Shared authentication middleware for Surreality services",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/SurrealityAI/surreality-auth",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "fastapi>=0.68.0",
        "PyJWT>=2.0.0",
        "supabase>=1.0.0",
        "python-dotenv>=0.19.0",
    ],
)