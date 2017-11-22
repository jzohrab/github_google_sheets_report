GitHub Repo Analyzer
========================

Generate gsheets report.

# Python

## Install prereqs

```
brew install python3  # mac
sudo pip install --upgrade pip
sudo pip install --upgrade virtualenv

# Optionally, use a pre-provisioned Vagrant box,
# eg. https://github.com/jeff-zohrab/devops-box.git
```

## Running

```

make venv                  # Make venv
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
