Running GTB-Tk on CHTC
======================
[GTDB-Tk](https://github.com/Ecogenomics/GtdbTk) is a pipeline to identify genomes based on protein markers, using a very large reference bacterial tree of life. The taxonomy used was constructed as a huge genome tree, with fewer polyphyletic groups, and consistent evolutionary divergence (see [this paper](https://www.nature.com/articles/nbt.4229) and the [Genome Taxonomy Database](http://gtdb.ecogenomic.org/)). 

Setting up the necessary software
---------------------------------
* Log into your CHTC submit not through SSH
* Create a directory to hold your build and submit files, then `cd` to that directory
* Use a text editor to create a file called `build.sub` with the following contents:

```bash
universe = vanilla
log = interactive.log

output = process.out
error = process.err

+IsBuildJob = true
requirements = (OpSysMajorVer =?= 7) && (IsBuildSlot == true)

should_transfer_files = YES
when_to_transfer_output = ON_EXIT

request_cpus = 1
request_memory = 4GB
request_disk = 10GB

queue
```

* Now start an interactive job with the following command:

```bash
condor_submit -i build.sub
```

* The first step is to download and compile Python 2.7.16:

```bash
wget https://www.python.org/ftp/python/2.7.16/Python-2.7.16.tgz
tar xvf Python-2.7.16.tgz
cd Python-2.7.16
./configure --prefix=${PWD}/../python
make
make install
cd ..
export PATH=${PWD}/python/bin:$PATH
wget https://bootstrap.pypa.io/get-pip.py
python get-pip.py
rm get-pip.py
rm -rf Python-2.7.16*
```

* Now we install gtdbtk:

```bash
pip install gtdbtk future numpy
```

* Then we install some other programs that gtdbtk needs:

```bash
wget https://github.com/hyattpd/Prodigal/releases/download/v2.6.3/prodigal.linux
chmod +x prodigal.linux
mv prodigal.linux python/bin/prodigal
```

```bash
wget http://eddylab.org/software/hmmer/hmmer-3.2.tar.gz
tar xvf hmmer-3.2.tar.gz
cd hmmer-3.2
./configure
make
find src -perm /a+x -exec cp {} ../python/bin \;
cd ..
rm -rf hmmer-3.2*
```

```bash
wget https://github.com/matsen/pplacer/releases/download/v1.1.alpha19/pplacer-linux-v1.1.alpha19.zip
unzip pplacer-linux-v1.1.alpha19.zip
cd pplacer-Linux-v1.1.alpha19/scripts
python setup.py install
cd ..
cp guppy ../python/bin/
cp pplacer ../python/bin/
cp rppr ../python/bin/
cd ..
rm -rf pplacer-*
```

```bash
wget https://github.com/ParBLiSS/FastANI/releases/download/v1.1/fastani-Linux64-v1.1.zip
unzip fastani-Linux64-v1.1.zip
mv fastANI python/bin/
rm fastani-Linux64-v1.1.zip
```

```bash
wget http://www.microbesonline.org/fasttree/FastTree
wget http://www.microbesonline.org/fasttree/FastTreeMP
chmod +x FastTree*
mv FastTree* python/bin/
```

Before we go on we need to change the first line of a few files in the python installation. The reason is that they will have hard-coded the current absolute path.

* First find the absolute path to your directory with the pwd command, then use the commands below to find all files that mention it and swap it for a general path (below we use the path /var/lib/condor/execute/slot1/dir_5943 as an example - make sure to substitute this for your directory path):

```bash
grep -r -I /var/lib/condor/execute/slot1/dir_5943 ./python/* | cut -f 1 -d ':' | sed "s?^?sed -i 's;#!/var/lib/condor/execute/slot1/dir_5943/python/bin/python;#!/usr/bin/env python;' ?" > sed.sh
chmod +x sed.sh
./sed.sh
rm sed.sh
```

* Before finishing, you need to compress the `python` directory:

```bash
tar -czvf gtdbtk_python.tar.gz python
```

* Then finish the interactive job with the `exit` command. If everything worked correctly, the job should copy over the `gtdbtk_python.tar.gz` file to the submit node.

Before you run GTDB-Tk, you must download a large (23 GB) file to your `/staging` folder. 

```bash
cd /staging/<USERNAME>
wget https://data.ace.uq.edu.au/public/gtdb/data/releases/release95/95.0/auxillary_files/gtdbtk_r95_data.tar.gz

```

Running GTDB-Tk on CHTC
-----------------------
* Create a directory to hold your job files and `cd` into that directory
* Create a subdirectory to hold your genome fasta files. We'll assume it is called `input_fasta_files`
* Copy over your input files to the `input_fasta_files` directory
* Now use a text editor to make a submit file called `gtdbtk.sub`, with the following contents:

```bash
universe = vanilla
log = gtdbtk_$(Cluster).log
error = gtdbtk_$(Cluster)_$(Process).err
output = gtdbtk_$(Cluster)_$(Process).out
executable = run_gtdbtk.sh
should_transfer_files = YES
when_to_transfer_output = ON_EXIT
transfer_input_files = /staging/swaterworth/gtdbtk_python.tar.gz, /staging/swaterworth/gtdbtk_r95_data.tar.gz, /staging/swaterworth/input_fasta_files.tar.gz
request_cpus = 1
request_memory = 400GB
request_disk = 250GB
requirements = (Target.HasCHTCStaging == true)
queue 1
```

Note: Remember to adapt the exact path to the `tar.gz` files to fit your setup. Previously, we were using multiple CPUs. It seems pplacer has taken issue with that and tends to hang/quit the job without completing. You can bypass this by using just a single CPU and throwing the kitchen sink at the job in terms of memory. As you can see, I used 400Gb, but that was for ~180 genomes. You could probably use less if you have only a handful of genomes. 

* Use a text editor to make a bash script to set up and run the job called `run_gtdbtk.sh` with the following contents:

```bash
#!/usr/bin/bash
#Unpack everything and remove the tar.gz files (saves space!)
tar xzvf gtdbtk_python.tar.gz
rm gtdbtk_python.tar.gz
tar xzvf gtdbtk_r95_data.tar.gz
rm gtdbtk_r95_data.tar.gz
tar xzvf input_fasta_files.tar.gz
rm input_fasta_files.tar.gz

#GTDB-Tk likes things on the straigh and narrow, so let's give it a path to walk along
export PATH=${PWD}/python/bin:$PATH
export GTDBTK_DATA_PATH=${PWD}/release95

#For reasons beyong my (Sam's) comprehension: This hard-coded path in the gtdbtk script was not picked up by sed.sh during set up. 
#This just ensures that GTDBtk is looking in the right place

sed -i "1s|.*|#!${PWD}/python/bin/python|" ${PWD}/python/bin/gtdbtk

#Finally, run GTDB-Tk, tar up the results and send it off to the submit node. 

gtdbtk classify_wf --genome_dir input_fasta_files --extension fasta --out_dir gtdbtk_output --cpus 1
tar -czvf gtdbtk_output.tar.gz gtdbtk_output
```

Note: Remember to alter the gtdbtk arguments so that the number of CPUs requested match the `.sub` file. The `--extension` argument specifies the extension of files to use in the genome directory (here we specify `.fasta`), and the `--scratch_dir` argument tells the pipeline to use more disk vs. memory. Removing `--scratch_dir` will make the pipeline faster, but it will need ~90 GB of RAM.

* Make the script executable:

```bash
chmod +x run_gtdbtk.sh
```

* Now submit the job:

```bash
condor_submit gtdbtk.sub
```
