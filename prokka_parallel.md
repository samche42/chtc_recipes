Annotating _n_ genomes in parallel
==================================

For this recipe, we assume that you have _n_ genomes as nucleotide fasta files with arbitrary names but with the .fasta suffix. We will be annotating the genomes with the [Prokka](https://github.com/tseemann/prokka) pipeline.

Setting up the required software
--------------------------------
* Log into your CHTC submit node by SSH
* Create a directory to hold your build and submit files, then `cd` into that directory
* Download the [Miniconda](https://docs.conda.io/en/latest/miniconda.html) install script for Python 2.7:

```bash
wget https://repo.anaconda.com/miniconda/Miniconda2-latest-Linux-x86_64.sh
```

* Use a text editor to create a file called `build.sub` with the following contents:

```bash
universe = vanilla
log = interactive.log

output = process.out
error = process.err

+IsBuildJob = true
requirements = (OpSysMajorVer =?= 7) && (IsBuildSlot == true)

transfer_input_files = Miniconda2-latest-Linux-x86_64.sh
should_transfer_files = YES
when_to_transfer_output = ON_EXIT

request_cpus = 1
request_memory = 2GB
request_disk = 6GB

queue
```

* Now start an interactive build job with the following command:

```bash
condor_submit -i build.sub
```
* Once you get the command prompt of the interactive job, take a note of the current directory path with the `pwd` command
* Now issue the following command:

```bash
bash Miniconda2-latest-Linux-x86_64.sh
```

* Read through and agree to the license agreement, then choose to install miniconda in the directory `${PWD}/miniconda2` directory, where `${PWD}` is the directory path you took note of above
* When asked, choose to NOT initialize the installation
* Issue the following command:

```bash
export PATH=${PWD}/miniconda2/bin:$PATH
```

This adds the miniconda installation to your path. Check that the right python and conda are being used with these commands:

```bash
which python
which conda
```

* Now install prokka:

```bash
conda install -c conda-forge -c bioconda prokka
```

* Now we compress the `miniconda2` directory, so we can use it for other jobs:

```bash
tar -czvf miniconda2.tar.gz miniconda2
```

* Then you can exit the interactive job with the `exit` command. 

If everything has worked correctly, you should have a file called `miniconda2.tar.gz` in the directory you created in the second step.

Running parallel Prokka jobs
----------------------------
* Create a directory to hold your job files and `cd` to that directory
* Create a subdirectory to hold your input fasta files. We'll assume here it is called `fasta_input_files`
* Copy over your input files to the `fasta_input_files` directory with `scp` or `rsync`
* Do the following to get a list of fasta filenames:

```bash
cd fasta_input_files
ls -1 *.fasta > ../fasta_list
cd ..
```

* Now use a text editor to make a submit file called `prokka.sub`, with the following contents:

```bash
universe = vanilla
log = prokka_$(Cluster).log
error = prokka_$(Cluster)_$(Process).err
executable = run_prokka.sh
arguments = $(fasta_file)
should_transfer_files = YES
when_to_transfer_output = ON_EXIT
transfer_input_files = fasta_input_files/$(fasta_file),miniconda2.tar.gz
request_cpus = 1
request_memory = 1GB
request_disk = 6GB
queue fasta_file from fasta_list
```

Note: You may want to include the exact path to the `miniconda2.tar.gz` file you created above if it is not in the same directory.

The above submit script queues a job for every line in the `fasta_list` file, and stores the filename in the `fasta_file` variable. 

* Use a text editor to make a bash script to set up and run the job called `run_prokka.sh` with the following contents:

```bash
#!/usr/bin/bash

# Expand miniconda
tar xvf miniconda2.tar.gz
rm miniconda2.tar.gz

# Set up path to executables and python etc.
export PATH=${PWD}/miniconda2/bin:$PATH

# Run prokka
prokka --compliant --cpus 1 --outdir ${1}_prokka $1

# Compress output
tar -czvf ${1}_prokka.tar.gz ${1}_prokka
```

Note: You may want to change the Prokka arguments, but make sure that the cpus requested matches the number in your submit script.

* Make the script executable:

```bash
chmod +x run_prokka.sh
```

* Now you can submit the job:

```bash
condor_submit prokka.sub
```

This will run _n_ Prokka jobs in parallel. Sometimes a job here and there will fail. To find the process number of a failed job, search the log file for the word `held`. You will find something like this:

```bash
012 (590072.033.000) 05/20 15:47:48 Job was held.
       	Error from slot1_3@atlas3025.chtc.wisc.edu: disk usage exceeded request_disk
       	Code 21 Subcode 102
```

In this case it is job process 33 that was held. Because the numbering starts at 0, that means that the job used the 34th line of `fasta_list`. You can find what that is with the following command:

```bash
head -n 34 fasta_list
```

The relevant fasta file will be on the last line of the output from this command. If you got the above error, you would need to increase the disk space requested. Make a new file called `fasta_list2` that just contains the fasta files that need to be done, and make a new submit script called `prokka2.sub`:

```bash
universe = vanilla
log = prokka_$(Cluster).log
error = prokka_$(Cluster)_$(Process).err
executable = run_prokka.sh
arguments = $(fasta_file)
should_transfer_files = YES
when_to_transfer_output = ON_EXIT
transfer_input_files = fasta_input_files/$(fasta_file),/home/jkwan2/2019_05_20_miniconda_prokka_build/miniconda2.tar.gz
request_cpus = 1
request_memory = 1GB
request_disk = 10GB
queue fasta_file from fasta_list2
```