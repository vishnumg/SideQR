from setuptools import setup, find_packages

setup(
    name="sideqr",
    use_scm_version=True,  # Automatically sets the version from Git tags
    setup_requires=["setuptools-scm"],  # Ensures setuptools-scm is installed
    packages=find_packages(exclude=["examples"]),
    install_requires=[
        "PySide6>=6.0.0",
        "pyzbar",
        "numpy",
        "opencv-python"
    ],
    author="Vishnu Mohan G",
    description="A PySide6 library providing a custom QML component for QR code scanning.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/vishnumg/SideQR",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
