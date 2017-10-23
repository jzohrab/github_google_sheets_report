# Analyze all branches in a checked-out repository, print out stats
# for each relative to a given base branch.

require 'yaml'

####################################
# Helpers

def write_rev_list_data(path)
  tmpfile = File.expand_path("#{path}.tmp")
  cmd = "git rev-list --objects --all | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' > #{tmpfile}"

  # | awk '/^blob/ {print substr($0,6)}'
  puts cmd
  `#{cmd}`

  # File.open(path, 'w') { |f| f.write(`#{cmd}`) }
  raise 'exit!'
end

def split_line(line)
  sha = line[0..39]
  size, path = line[40..-1].split(' ', 2)
  [sha, size.to_i, path]
end

# Get data for all files like the following:
# [sha, size_in_bytes, full_path]
# ref https://stackoverflow.com/questions/10622179/how-to-find-identify-large-files-commits-in-git-history
def get_blob_data(raw_data_file)
  data = File.read(raw_data_file).split("\n").map do |line|
    split_line(line)
  end.select do |el|
    el[2] != ''
  end
  return data
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

# Create output directories before chdir into the repo
report_file = File.expand_path(File.join(File.dirname(__FILE__), 'large_files_report.txt'))
raw_file = File.expand_path(File.join(File.dirname(__FILE__), 'raw_data.txt'))

Dir.chdir(config[:source_dir]) do
  if config[:use_existing_raw_data] and File.exist?(raw_file) then
    $stderr.puts "Using existing raw data file #{raw_file}"
  else
    if config[:do_fetch] then
      $stderr.puts 'Fetching'
      `git fetch #{config[:origin_name]}`
    end
    if config[:do_prune] then
      $stderr.puts 'Pruning'
      `git remote prune #{config[:origin_name]}`
    end
    $stderr.puts 'Getting repo data'
    write_rev_list_data(raw_file)
  end

  data = get_blob_data(raw_file)
  puts data[0].inspect

  # Now analyze the data (by extension, size, etc)
end

puts "Generated #{report_file}."
