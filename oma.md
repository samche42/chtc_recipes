Running OMA in parallel on CHTC
===============================

[OMA](https://omabrowser.org) is a database of orthologous genes in many genomes (both prokaryotic and eukaryotic). The OMA algorithm is supposed to identify orthologs (homologs with the same function), while rejecting paralogs (homologs that were duplicated at some point, with divergent functions). The algorithm can be run on arbitrary protein sequences to identify which ones are orthologs. Here we will download some reference genomes from the OMA database, then run a comparison with some user-generated genomes.

Download reference genomes from the OMA database
------------------------------------------

1. Go to [https://omabrowser.org](https://omabrowser.org) and navigate to Compute -> Export All/All
2. Navigate through the phylogenetic tree or use the search box to find the species you want. The tree broadly follows the NCBI taxonomy. Reference genomes should be well annotated and/or include relatives to your genomes. Including *E. coli* would be a good option for Proteobacteria.
3. Click "Submit", then wait for the download to be generated.
4. Download the file.

Compile the database
--------------------

Copy the tar.gz file obtained through the OMA website to your working directory (right now this can be on the lab server or your own computer), and expand it:

```bash
tar xvf AllAll-32dea360497588a4ad4218b8b712a9d0.tgz
```

You will notice that this creates a directory called something like `OMA.2.3.1`, which actually includes the OMA executable and support files. Within that is a subdirectory called `DB`, which is where you will copy a protein fasta for each of your genomes that you want to include in the analysis. Note that all fasta files need to have the extension `.fa` to be recognized. 

After you have added your protein fasta files to the `DB` directory, go into the `OMA.2.3.1` directory and compile the database:

```bash
cd OMA.2.3.1
./bin/oma -c
```

After that is finished, we need to tar up the directory:

```bash
cd ..
tar cvzf OMA.2.3.1.tar.gz OMA.2.3.1
```

Then copy the `OMA.2.3.1.tar.gz` file to a new directory on your submit node for CHTC.

Run OMA in parallel on CHTC
---------------------------

In your directory with the `OMA.2.3.1.tar.gz` file, make a file called `OMA.sub` with the following contents:

```bash
job = OMA_AllAll
universe = vanilla
log = $(job)_$(Cluster).log
executable = OMA.sh
arguments = "$(Process)"
output = $(job)_$(Cluster)_$(Process).out
error = $(job)_$(Cluster)_$(Process).err
should_transfer_files = YES
when_to_transfer_output = ON_EXIT
transfer_input_files = OMA.2.3.1.tar.gz
transfer_output_files = OMA.2.3.1_$(Process).tar.gz
request_cpus = 1
request_memory = 4000MB
request_disk = 8000MB
requirements = ((OpSysMajorVer == 6) || (OpSysMajorVer == 7))
queue 100
```

Note the last line. That specifies the number of parallel jobs you will want to run. This number ideally should be large enough so that every job is able to finish before the CHTC time limit of 72 hours. As usual there is a trade-off between speed and number of processes. One thing to watch out for is that each of the jobs will make a new `.tar.gz` file, which at a minimum will be ~53 MB, so make sure you have enough space.

Now make a file called `OMA.sh` with the following contents:

```bash
#!/bin/bash

export NR_PROCESSES=100
export THIS_PROC_NR=$(($1+1))

tar xvf OMA.2.3.1.tar.gz
rm OMA.2.3.1.tar.gz
BASEDIR=$PWD
cd OMA.2.3.1
./bin/oma -s -W 216000

cd ../
mv OMA.2.3.1 OMA.2.3.1_${1}
tar zcvf OMA.2.3.1_${1}.tar.gz OMA.2.3.1_${1}
```

Note here that the line `export NR_PROCESSES=100` must match the `queue 100` line in `OMA.sub`. That should be the only tailoring you need to do. After that you can start the job with:

```bash
condor_submit OMA.sub
```

What you get from this are *n* files with names like `OMA.2.3.1_45.tar.gz`. They all contain the files originally in `OMA.2.3.1.tar.gz` and also any extra made by the respective job. They need to be combined to one directory.

First, in your submit folder, which should contain all the output `.tar.gz` files, make a new directory and move all the output files into it:

```bash
mkdir AllAll_parts
mv OMA.2.3.1_*.tar.gz AllAll_parts/
```

Now make a file called `OMA_combine.sub` with the following contents:

```bash
job = OMA_combine
universe = vanilla
log = $(job)_$(Cluster).log
executable = oma_combine_results.py
arguments = "OMA.2.3.1.tar.gz AllAll_parts 100"
output = $(job)_$(Cluster)_$(Process).out
error = $(job)_$(Cluster)_$(Process).err
should_transfer_files = YES
when_to_transfer_output = ON_EXIT
transfer_input_files = OMA.2.3.1.tar.gz,AllAll_parts
transfer_output_files = OMA.2.3.1_combined.tar.gz
request_cpus = 1
request_memory = 8000MB
request_disk = 20GB
requirements = ((OpSysMajorVer == 6) || (OpSysMajorVer == 7))
queue 1
```

Note that the last number in the `arguments` line should match up to the value you used for number of jobs in the first stage. Also, you may need to adjust the `request_disk` line to allow for enough space to store all your `.tar.gz` files and expand a few at a time. Also, the script `oma_combine_results.py` is included in the `scripts` folder of this repo, and should be copied to your submit folder. The script uses `rsync` to combine the folders after expanding them.

Run this job:

```bash
condor_submit OMA_combine.sub
```

After that is done you should have a `OMA.2.3.1_combined.tar.gz` file in your submit folder. (After you have verified that it is OK), you can delete the separate parts. The next step could be done on either CHTC or the lab server (it requires only 1 CPU, but perhaps more memory).

After you have expanded the `OMA.2.3.1_combined.tar.gz` file, go into it and run OMA:

```bash
cd OMA.2.3.1
./bin/oma
```

This will do all the last jobs going through the All-vs-All stuff and making the final output files that will be stored in the `Output` folder.