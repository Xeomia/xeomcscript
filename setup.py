from distutils.core import setup
setup(
  name = 'xeomcscript',
  packages = ['xeomcscript'],
  version = '0.1',
  license='MIT',
  description = 'All the functions used to use my minecraft scripts or create your own',
  author = 'Xeo v2',
  author_email = 'xeomiayt@gmail.com',
  url = 'https://github.com/Xeomia/xeomcscript',
  download_url = 'https://github.com/Xeomia/xeomcscript/archive/v0.1.tar.gz',
  keywords = ['Minecraft', 'MySQL'],
  install_requires=[
          'mysql.connector',
          'pydirectinput',
          'pyautogui',
          'cv2',
          'pytesseract',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers - Gamers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
  ],
)

