GitHub Repo Analyzer
========================

Utility scripts to work with large git repos.

Contents (README files are in each subdirectory):

* branch_report: old branches
* large_files_report: large files that have been committed at any point in repo history


# Python

```
brew install python3
sudo pip install --upgrade pip
sudo pip install --upgrade virtualenv

# Make venv
make PYTHON=/usr/local/bin/python3 venv


source venv/bin/activate   # start venv

make init                  # load reqs


python --version  # verify python version
# should return python 3.x.x
```

# Start stuff

```
cp config.yml.example config.yml
python scrap.py
```

# Testing

```
make test
```

# Clean up
```
deactivate

make clean
```
