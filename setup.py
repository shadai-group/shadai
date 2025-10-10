from setuptools import find_packages, setup

setup(
    name="shadai",
    version="0.1.28",
    packages=find_packages(),
    install_requires=[
        "aiohttp>=3.8.0",
        "pydantic>=2.0.0",
        "langchain-core==1.0.0a8",
    ],
    author="SHADAI GROUP",
    author_email="noreply@shadai.ai",
    description="SHADAI Client",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    package_dir={"shadai": "shadai"},
)
