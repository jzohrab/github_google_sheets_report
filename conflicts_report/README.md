# Conflicts report.

Still under development.

Create a test repo and run a script to check conflicts:

    ./make_test_repo.sh ../../zzblah f
    pushd ../../zzblah/
    ../analyze_git_repo/conflicts_report/branch_loop_demo.sh
    popd
