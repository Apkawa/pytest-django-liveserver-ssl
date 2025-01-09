
## Run tests

```bash
pip install -r requirements-dev.txt
pytest # run tests
tox # run test matrix
```

## Run tests with pyenv with specific python and pypy

```shell
pyenv install 3.8 3.13 pypy3.10
pyenv local 3.8 3.13 pypy3.10
pip install -r requirements-dev.txt
tox -e py313,pypy3
```

## Type checks

```shell
tox -e type
```

## Lint code

```shell
tox -e qa
```


## Before commit

Install git hook

```shell
pip install -r requirements.txt

pre-commit install
```

For pycharm needs install `tox` to global


## Docs

```shell
pip install -r requirements-dev.txt
cd docs
make html
```

## Bump version

```bash
python setup.py bumpversion
```
