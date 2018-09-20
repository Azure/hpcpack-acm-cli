import setuptools
import os.path

requires = ["terminaltables >= 3.1.0", "tqdm >= 4.24.0"]

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hpc_acm_cli",
    version="2.7.0",
    author="Robert Zhang",
    description="HPC ACM client",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    entry_points={
        'console_scripts': [
            'clusnode=hpc_acm_cli.node:main',
            'clusrun=hpc_acm_cli.clus:main',
            'clusdiag=hpc_acm_cli.diag:main',
        ],
    },
    # NOTE: DO NOT rely on "data_files" since it's very buggy and confusing. See the
    # following link for more info.
    # https://stackoverflow.com/questions/47460804/copy-configuration-file-on-installation
    package_data={
        'hpc_acm_cli': ['.hpc_acm_cli_config']
    },
    install_requires=requires
)
