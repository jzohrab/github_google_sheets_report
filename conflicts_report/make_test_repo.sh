#!/bin/bash

# Creates a master git repo with some branches
# with conflicts.
#
# ---o----o----o develop
#     \
#      o----o    feature/A
#      |     \
#      |      o  feature/Achild
#      |
#      +----o    feature/B - conflicts with A only
#      |
#      +----o    feature/C - conflicts with A and B
#      |
#      +----o    feature/D - conflicts with develop

if [ "$#" -gt 2 ]; then
    echo "Usage: $0 <path_to_repo_to_create> [force]"
    exit 1
fi

REPODIR=$1
FORCE=$2

if [ "$FORCE" != "" ]; then
    echo "Removing dir"
    rm -rf $REPODIR
fi

if [ -d $REPODIR ]; then
    echo "Error: directory already exists, exiting."
    exit 1
fi

mkdir -p $REPODIR
pushd $REPODIR

git init
echo 'hello' > README.md
git add .; git commit -m "Initial commit."

git checkout -b develop
echo 'dev1' > devwork.txt; git add .; git commit -m "Dev."
echo 'dev2' >> devwork.txt; git add .; git commit -m "More dev."

git checkout master -b feature/A
echo 'A1' > A.txt; git add .; git commit -m "A1"

git checkout feature/A -b feature/B
echo 'B1' >> A.txt; git add .; git commit -m "B"
git checkout feature/A -b feature/C
echo 'C1' >> A.txt; git add .; git commit -m "C"
git checkout feature/A -b feature/D
echo 'mydevwork' > devwork.txt; git add .; git commit -m "D"

git checkout feature/A
echo 'A2' >> A.txt; git add .; git commit -m "A2"

git checkout -b feature/Achild
echo 'A3' >> A.txt; git add .; git commit -m "Achild"
git checkout develop

popd


