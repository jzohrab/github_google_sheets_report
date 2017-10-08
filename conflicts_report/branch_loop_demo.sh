fs=`git branch | grep feature`
for b in $fs; do
    echo ==================
    echo $b
    git reset --hard
    git clean -f
    git checkout $b
    for other in $fs; do
	echo ------------------
	echo Try merging $other
	git reset --hard
	git clean -f
	git merge --no-commit $other
	git diff --name-only --diff-filter=U
    done
done
