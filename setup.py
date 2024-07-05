from setuptools import setup, find_packages

setup(
    name='pt-onlinellm2',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'flask',
        'Werkzeug',
        'gunicorn',
        'requests',
        'beautifulsoup4',
        'openai',
        'python-dotenv',
        'json'
    ],
    entry_points={
        'console_scripts': [
            'pt-onlinellm2=src.api:app',
        ],
    },
)
