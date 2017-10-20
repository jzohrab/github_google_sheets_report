Utility scripts to work with large git repos.

Contents of 'bin'

* `create_branch_report.rb`: old branches
* `create_large_files_report.rb`: large files that have been committed at any point in repo history

The repo to analyze should already be checked out onto your machine.

Copy config.yml.example to your own config file, and pass that
filename as an argument to any `bin` script.  e.g.,

    ruby bin/create_branch_report.rb config.yml