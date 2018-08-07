DeepLearning Reversi Project
============================

## pyenv + virtualenv + wxPython

pyenv

```sh
$ git clone https://github.com/pyenv/pyenv.git ~/.pyenv
$ echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bash_profile # or .zshrc
$ echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bash_profile # or .zshrc
$ exec $SHELL -l

$ pyenv -v
$ env PYTHON_CONFIGURE_OPTS="--enable-framework" pyenv install 3.6.0
```

virtualenv

```sh
$ mkdir reversi-proj
$ cd reversi-proj
$ pyenv local 3.6.0
$ pip install virtualenv
$ pyenv rehash
$ virtualenv --distribute --no-site-packages --unzip-setuptools .venv
$ source .venv/bin/activate
$ python --version && which python
```

install pythonw in virtualenv to run wxPython in virtualenv

```sh
$ wget https://s3-ap-northeast-1.amazonaws.com/python-distribution/virtualenv-pythonw.tar.gz
$ tar zxvf virtualenv-pythonw.tar.gz
$ cd virtualenv-pythonw
$ python setup.py install
$ rm -rf virtualenv-pythonw*
```

wxPython and other dependencies

```sh
$ pip install -r requirements.txt
```

<!-- ## PyQt in virtualenv

Intall Qt packages (14GiB on Disk) from `dependencies/setup-qt-mac-x64-3.0.5-online.app`. This takes about over 10min.
When installer asks you directory to put packages, please enter following path.
> /Users/{your_name}/{path-to-project}/reversi-proj/dependencies/Qt

And after this, run installation shell scripts

```sh
# install PyQt5
$ cd dependencies
$ chmod a+x ./sip.sh && sh ./sip.sh
$ chmod a+x ./pyqt5.sh && sh ./pyqt5.sh
``` -->

## Run reversi playing server

```sh
$ pythonw manage.py runserver --tick=1000
```

## Run reversi your own brain client

```sh
$ python manage.py join_brain
```

## Run reversi random brain client

```sh
$ python manage.py join_random
```
