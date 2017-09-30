# Analyze all branches in a checked-out repository, print out stats
# for each relative to a given base branch.

require 'yaml'

####################################
# Helpers

def get_branch_data(master, branch_name)
  log = `git log --date=short --format="%cd %aE" #{master}..#{branch_name}`
  commits_ahead = log.split("\n").map do |c|
    c.split(' ')
  end
  num_commits_ahead = commits_ahead.size
  latest_commit = commits_ahead.map { |d, c| d }.max
  authors = commits_ahead.map { |d, c| c }.sort.uniq
  authors = authors.join(', ')

  # Expensive ... add if desired.
  # approx_diff_linecount = `git diff #{master}...#{branch_name} | grep ^[+-] | wc -l`.strip

  return [branch_name, num_commits_ahead, latest_commit, authors]
end

####################################
# Script

if ARGV.size == 0 then
  puts 'Specify config file.'
  exit 0
end
filename = ARGV[0]
if !File.exist?(filename) then
  puts "Missing config file #{filename}."
  exit 0
end
config = YAML.load_file(filename)

report_file = File.expand_path('./branch_report.txt')

Dir.chdir(config[:source_dir]) do
  if config[:do_fetch] then
    $stderr.puts 'Fetching'
    `git fetch #{config[:origin_name]}`
  end
  if config[:do_prune] then
    $stderr.puts 'Pruning'
    `git remote prune #{config[:origin_name]}`
  end
  branches = `git branch -r`.split("\n").map { |b| b.strip }
  branches = config[:sample_branches] if config.key?(:sample_branches)

  curr_branch = 0
  $stderr.puts "Analyzing #{branches.size} branches"
  File.open(report_file, 'w') do |f|
    f.puts ['branch_name', 'num_commits_ahead', 'latest_commit', 'authors'].join('|')
    branches.each do |branch_name|
      curr_branch += 1
      $stderr.puts "Completed #{curr_branch} of #{branches.size}" if (curr_branch % 10 == 0)
      f.puts get_branch_data(config[:master_branch], branch_name).join("|")
    end
  end
end

puts "Generated #{report_file}."
