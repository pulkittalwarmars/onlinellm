from setuptools import setup, find_packages

setup(
    name='your_project_name',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'flask==3.0.3',
        'werkzeug==3.0.1',
        'requests',
        'beautifulsoup4',
        'openai',
        'python-dotenv',
        'gunicorn',
    ],
    entry_points={
        'console_scripts': [
            'your_project_name=src.api:app',
        ],
    },
)
