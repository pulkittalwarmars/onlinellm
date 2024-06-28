from setuptools import find_packages # can load and find packages that in the application
from setuptools import setup
from typing import List

HYPEN_E_DOT="-e ."

def get_requirements(file_path:str)->List[str]:
    """
    This function will return the list of requirements
    """
    requirements=[]
    with open(file_path) as file_obj:
        requirements=file_obj.readlines()
        requirements=[req.replace("\n","") for req in requirements]

        if HYPEN_E_DOT in requirements:
            requirements.remove(HYPEN_E_DOT)
    
    return requirements

setup( ##meta data information of the package
    name="mlproject",
    version="0.0.0.1",
    author="pulkit",
    author_email="pulkit@gmail.com",
    packages=find_packages(),
    install_requires=get_requirements('requirements.txt')
)

