"""
Setup script for Google Analytics 4 API Wrapper
"""

from setuptools import setup, find_packages
from pathlib import Path

# Ler o README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name='ga4-api-wrapper',
    version='1.0.0',
    author='Apps Factory',
    description='API wrapper completa em Python para Google Analytics 4 Data API',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/gustavozsh/apps-factory',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
    install_requires=[
        'google-analytics-data>=0.18.0',
        'google-auth>=2.23.0',
        'google-auth-oauthlib>=1.1.0',
        'google-auth-httplib2>=0.1.1',
        'python-dotenv>=1.0.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
            'mypy>=1.0.0',
        ],
        'data': [
            'pandas>=2.0.0',
        ]
    },
    entry_points={
        'console_scripts': [
            # Adicione comandos CLI aqui se necessário
        ],
    },
    package_data={
        'src': ['py.typed'],
    },
    zip_safe=False,
)
