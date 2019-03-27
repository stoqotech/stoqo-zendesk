import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="stoqo_zendesk",
    version="1.1.1",
    author="STOQO",
    author_email="tech@stoqo.com",
    description="STOQO-Zendesk unifying interface",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/stoqo/stoqo-zendesk/src/master/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
