from setuptools import setup

setup(
    name="quickcrop",
    version="0.1.0",
    description="A UI-based method to quickly crop an image to a square using matplotlib by " +
                "specifying four corners within which to crop.  Meant to be easily integrated " +
                "into image processing scripts.",
    url="https://github.com/realitychemist/quickcrop",
    author="Charles Evans",
    author_email="charlese@andrew.cmu.edu",
    license="MPL 2.0",
    packages=["quickcrop"],
    install_requires=["numpy",
                      "matplotlib",
                      "typing"],
    classifiers=["Development Status :: 2 - Pre-Alpha",
                 "Framework :: Matplotlib",
                 "Intended Audience :: Science/Research",
                 "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
                 "Natural Language :: English",
                 "Programming Language :: Python :: 3",
                 "Topic :: Scientific/Engineering :: Image Processing"])
