Running AntiSMASH on _n_ genomes in parallel
==============

For this recipe, we assume that you have _n_ genomes as genbank files, perhaps created with [Prokka](https://github.com/tseemann/prokka). We will use AntiSMASH 4, because the output is compatible with [BiG-SCAPE](https://git.wageningenur.nl/medema-group/BiG-SCAPE/).

Setting up the required software
--------------------------------
Note: This is complicated, but you will only have to do this once, and then you will have compressed files with the setup software that you can use over and over again.

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
request_memory = 16GB
request_disk = 40GB

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
* Now install some required python packages:

```bash
conda install -c conda-forge -c bioconda cssselect pyquery==1.2.9 \
	numpy helperlibs pysvg pyExcelerator backports.lzma bcbio-gff \
	ete2 networkx pandas==0.20.3 matplotlib scipy scikit-learn
```

* Now we download some other dependencies:

```bash
mkdir bin
```

```bash
wget https://github.com/bbuchfink/diamond/releases/download/v0.8.36/diamond-linux64.tar.gz
tar xvf diamond-linux64.tar.gz
mv diamond bin/
rm diamond*
```

```bash
wget http://www.microbesonline.org/fasttree/FastTree-2.1.7.c
gcc -O3 -finline-functions -funroll-loops -Wall -o FastTree FastTree-2.1.7.c -lm
mv FastTree bin/
rm FastTree-2.1.7.c
```

```bash
wget https://ccb.jhu.edu/software/glimmer/glimmer302b.tar.gz
tar xvf glimmer302b.tar.gz
cd glimmer3.02/src
make
cd ../bin
mv ./* ../../bin
cd ../..
rm -rf glimmer*
```

```bash
wget ftp://ccb.jhu.edu/pub/software/glimmerhmm/GlimmerHMM-3.0.4.tar.gz
tar xvf GlimmerHMM-3.0.4.tar.gz
cd GlimmerHMM/sources
make
mv glimmerhmm ../../bin/
cd ../..
rm -rf GlimmerHMM*
```

```bash
wget http://eddylab.org/software/hmmer/hmmer-2.3.2.tar.gz
tar xvf hmmer-2.3.2.tar.gz
cd hmmer-2.3.2
./configure
make
cd src
mv hmmalign ../../bin/hmmalign2
mv hmmbuild ../../bin/hmmbuild2
mv hmmcalibrate ../../bin/hmmcalibrate2
mv hmmconvert ../../bin/hmmconvert2
mv hmmemit ../../bin/hmmemit2
mv hmmfetch ../../bin/hmmfetch2
mv hmmindex ../../bin/hmmindex2
mv hmmpfam ../../bin/hmmpfam2
mv hmmsearch ../../bin/hmmsearch2
cd ../..
rm -rf hmmer-2.3.2*
```

```bash
wget http://eddylab.org/software/hmmer/hmmer-3.1b2.tar.gz
tar xvf hmmer-3.1b2.tar.gz
cd hmmer-3.1b2
./configure
make
cd src
mv alimask ../../bin/
mv hmmalign ../../bin/
mv hmmbuild ../../bin/
mv hmmc2 ../../bin/
mv hmmconvert ../../bin/
mv hmmemit ../../bin/
mv hmmerfm-exactmatch ../../bin/
mv hmmfetch ../../bin/
mv hmmlogo ../../bin/
mv hmmpgmd ../../bin/
mv hmmpress ../../bin/
mv hmmscan ../../bin/
mv hmmsearch ../../bin/
mv hmmsim ../../bin/
mv hmmstat ../../bin/
mv jackhmmer ../../bin/
mv makehmmerdb ../../bin/
mv nhmmer ../../bin/
mv nhmmscan ../../bin/
mv phmmer ../../bin/
cd ../..
rm -rf hmmer-3.1b2*
```

```bash
wget https://mafft.cbrc.jp/alignment/software/mafft-7.271-without-extensions-src.tgz
tar xvf mafft-7.271-without-extensions-src.tgz
cd mafft-7.271-without-extensions/core
make clean
make
cd ../binaries
mv ./* ../../bin/
cd ../..
rm -rf mafft-7.271-without-extensions*
```

```bash
wget http://meme-suite.org/meme-software/4.11.2/meme_4.11.2_2.tar.gz
tar xvf meme_4.11.2_2.tar.gz
cd meme_4.11.2
# Substitute absolute path for prefix in line below
./configure --prefix=../bin --with-url="http://meme-suite.org" --enable-build-libxml2 --enable-build-libxslt
make
make install
cd ..
rm -rf meme_4.11.2*
```

```bash
wget http://www.drive5.com/muscle/downloads3.8.31/muscle3.8.31_i86linux64.tar.gz
tar xvf muscle3.8.31_i86linux64.tar.gz
mv muscle3.8.31_i86linux64 bin/muscle
rm muscle3.8.31_i86linux64.tar.gz
```

```bash
wget ftp://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/2.2.31/ncbi-blast-2.2.31+-x64-linux.tar.gz
tar xvf ncbi-blast-2.2.31+-x64-linux.tar.gz
cd ncbi-blast-2.2.31+/bin/
mv ./* ../../bin/
cd ../..
rm -rf ncbi-blast-2.2.31+*
```

```bash
wget https://github.com/hyattpd/Prodigal/releases/download/v2.6.1/prodigal.linux
chmod +x prodigal.linux
mv prodigal.linux bin/prodigal
```

* We now add a few folders to the `PATH` and `LD_LIBRARY_PATH` variables:

```bash
export PATH=$PATH:${PWD}/bin:${PWD}/bin/bin
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:${PWD}/bin/lib
```

* Now we download AntiSMASH 4 and set up the databases:

```bash
wget https://dl.secondarymetabolites.org/releases/4.2.0/antismash-4.2.0.tar.gz
tar xvf antismash-4.2.0.tar.gz
cd antismash-4.2.0/antismash/generic_modules/fullhmmer/
wget ftp://ftp.ebi.ac.uk/pub/databases/Pfam/releases/Pfam27.0/Pfam-A.hmm.gz
gunzip Pfam-A.hmm.gz
hmmpress -f Pfam-A.hmm
cd ..
# This next line takes a while
wget https://dl.secondarymetabolites.org/releases/4.0.0/clusterblast_20170105_v8_31.tar.xz
tar xf clusterblast_20170105_v8_31.tar.xz
rm clusterblast_20170105_v8_31.tar.xz
cd ../specific_modules/nrpspks/
hmmpress -f abmotifs.hmm
hmmpress -f dockingdomains.hmm
hmmpress -f ksdomains.hmm
hmmpress -f nrpspksdomains.hmm
cd sandpuma/flat/fullset0_smiles
hmmpress -f fullset0_smiles_nrpsA.hmmdb
cd ../../../../..
cd generic_modules/smcogs/
hmmpress -f smcogs.hmm
cd ../active_site_finder/hmm
hmmpress -f p450.hmm3
cd ../../../../scripts
./create_bgc_seeds.sh ../
cd ../antismash/generic_modules/hmm_detection/
hmmpress -f bgc_seeds.hmm
cd ../../../..
```

Before installing AntiSMASH, we need to edit a file in the miniconda2 installation:

```bash
nano miniconda2/lib/python2.7/site-packages/setuptools/command/bdist_egg.py
```

Then go to line 495 (`Ctrl+W` then `Ctrl+T`, then enter `495`). The line should look like this:

```bash
z = zipfile.ZipFile(zip_filename, mode, compression=compression)
```

Edit it so that it looks like this:

```bash
z = zipfile.ZipFile(zip_filename, mode, compression=compression, allowZip64 = True)
```

Then save with `Ctrl+O`, and exit with `Ctrl+X`.

* Now install AntiSMASH:

```bash
cd antismash-4.2.0
python setup.py install
```

* Before finishing, you need to compress the `bin` and `miniconda2` directories:

```bash
tar -czvf antismash_miniconda.tar.gz miniconda2
tar -czvf antismash_bin.tar.gz bin
```

* Then finish the interactive job with the `exit` command. If everything worked correctly, the job should copy over the `antismash_miniconda.tar.gz` and `antismash_bin.tar.gz` files to the submit node.

