import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pychromat",
    version="0.0.1",

    author="David Robertson",
    author_email="david@robertson.yt",

    # url="https://github.com/DavidJRobertson/PyChromat",

    description="Chromatographic analysis tool",
    long_description=long_description,
    long_description_content_type="text/markdown",

    classifiers=[
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Chemistry",

        "Natural Language :: English",

        "Development Status :: 2 - Pre-Alpha"
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",

        # "License :: OSI Approved :: MIT License",
        "License :: OSI Approved :: Apache Software License",
    ],


    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[
        "numpy",
        "scipy",
        "matplotlib",
    ],
    scripts=['bin/pychromat'],
    zip_safe=False,
)
