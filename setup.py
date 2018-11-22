from setuptools import setup

setup(name='diversify',
      version='0.1',
      description='Playlists generator based on artificial intelligence',
      url='https://github.com/edujtm/diversify',
      author='Eduardo Jose Tome Macedo',
      author_email='eduzemacedo@gmail.com',
      license='MIT',
      install_requires=[
          'numpy', 'pandas',
          'pprint', 'spotipy',
          'python-dotenv', 'argparse'
      ],
      zip_safe=False)
