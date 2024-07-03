from setuptools import setup, find_packages

setup(
    name='pt-onlinellm2',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'Flask==3.0.3',
        'Werkzeug==3.0.1',
        'gunicorn==22.0.0',
        'requests==2.31.0',
        'beautifulsoup4==4.12.3',
        'openai==1.13.3',
        'python-dotenv==1.0.1',
    ],
    entry_points={
        'console_scripts': [
            'pt-onlinellm2=src.api:app',
        ],
    },
)
