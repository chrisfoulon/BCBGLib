from setuptools import setup

setup(
    name='bcblib',        # This is the name of your PyPI-package.
    version='0.1.0',     # Update the version number for new releases
    data_files=[('priors', ['../Data/ants_priors/brainPrior.nii.gz'])],
    keywords='brain neuroimaging',
    packages=find_packages(),
    install_requires=['nibabel numpy'],
    project_urls={  # Optional
        'Source': 'https://github.com/chrisfoulon/BCBlib',
        'Bug Reports': 'https://github.com/chrisfoulon/BCBlib/issues',
        'BCBlab website' : 'http://bcblab.com'
    }
    )