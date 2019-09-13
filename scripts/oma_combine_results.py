#!/usr/bin/env python

import sys
import os
import subprocess

original_archive_path = os.path.abspath(sys.argv[1])
directory_of_new_archives = os.path.abspath(sys.argv[2])
number_of_archives_to_merge = int(sys.argv[3])

base_dir = os.path.abspath(os.getcwd())

# Expand the original archive
tar_list = ['tar', 'xvf', original_archive_path]
process = subprocess.Popen(tar_list, stdout=subprocess.PIPE)
out,err = process.communicate()
original_directory = os.path.join(base_dir, out.split('\n')[0])
original_directory_name = '/'.join(out.split('\n')[0].split('/')[:-1])

# Combine new archives with original directory
os.chdir(directory_of_new_archives)
# Note: we assume that the new archives follow the naming convention old_archive_X.tar.gz
archive_base_name = '.'.join(original_archive_path.split('/')[-1].split('.')[:-2])
source_directory_path = os.path.join(directory_of_new_archives, original_directory_name)
for i in range(number_of_archives_to_merge):
	# Expand archive
	if os.path.isfile(archive_base_name + '_' + str(i) + '.tar.gz'):
		tar_list = ['tar', 'xvf', archive_base_name + '_' + str(i) + '.tar.gz']
		process = subprocess.Popen(tar_list, stdout=subprocess.PIPE)
		out,err = process.communicate()
		new_directory_name = out.split('\n')[0]
		# Mv directory
		mv_list = ['mv', new_directory_name, original_directory_name]
		subprocess.call(mv_list)
		# Rm var directory
		rm_list = ['rm', '-rf', 'var']
		subprocess.call(rm_list)
		# Rsync to original directory
		rsync_list = ['rsync', '-avzh', source_directory_path, base_dir]
		subprocess.call(rsync_list)
		# Rm new directory
		rm_list = ['rm', '-rf', source_directory_path]
		subprocess.call(rm_list)

# Compress the resulting directory
os.chdir(base_dir)
tar_list = ['tar', 'zvcf', archive_base_name + '_combined.tar.gz', original_directory_name]
subprocess.call(tar_list)
