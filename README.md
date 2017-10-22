Utility scripts to work with large git repos.

Contents (README files are in each subdirectory):

* branch_report: old branches
* large_files_report: large files that have been committed at any point in repo history


# Python

```
brew install python3
sudo pip install --upgrade pip
sudo pip install --upgrade virtualenv

# Create virtual env with specific python
virtualenv -p /usr/local/bin/python3 venv

# start it
source venv/bin/activate

python --version  # verify python version
# should return python 3.x.x

...

deactivate

rm -rf venv
```


Can do the following:

```
$ start_python_venv.sh        # create the venv
$ source venv/bin/activate    # activate
```

