GitHub Repo Analyzer
========================

Utility scripts to work with large git repos.

Contents (README files are in each subdirectory):

* branch_report: old branches
* large_files_report: large files that have been committed at any point in repo history


# Python

## Install prereqs

```
brew install python3  # mac
sudo pip install --upgrade pip
sudo pip install --upgrade virtualenv

# Optionally, use a pre-provisioned Vagrant box,
# eg. https://github.com/jeff-zohrab/devops-box.git
```

## Create sample repo

```
./conflicts_report/make_test_repo.sh /tmp/zz_test_repo
```

## Running

```
# Make venv
make PYTHON=`which python3` venv

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
