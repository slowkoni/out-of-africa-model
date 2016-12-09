## Simulate one full chromosome of the human genome for the Out of Africa migration and expansion model

In brief, the model describes the origin and spread of the human species as a single ancestral population that grew instaneously (nearly so anyway?) into the population inhabiting the African continent. This population stayed the same size (effective population size, N_e) to the present day. At a point in the past, some individuals began migrating out of Africa. This group later split and went in opposite directions, some going on to found the present day European population, the rest founding the present day East Asian population. Both latter populations experienced exponential growth following the division of the originating out-of-africa population. The parameters, which determine the timing of events, effective population sizes, and growth rates of the European and East Asian populations are estimated from the existing human genetic data available at the time and presented in Gravel S, et al., 2011 "Demographic history and rare allele sharing among human populations." PNAS 108(29):11983-11988. These parameters are all configurable by command line options to this simulation framework, except the migration rate parameters (at this time). The default values are set to the maximum likelihood estimated values given in Table 2 of Gravel et al. for "Low coverage + exons" 1000 Genomes Project data. 

See Gravel et al. 2011 PNAS Figure 4 for a graphical view of the model.

This framework is based on using the msprime coalescent simulator by Jerome Kelleher (https://github.com/jeromekelleher), imported automatically by the docker container build and used under the GPLv3 License. See https://msprime.readthedocs.io/en/stable/introduction.html for an introduction to msprime and its documentation. 

This framework is built as a docker container and the container runs the simulation. All
arguments are passed to the docker run command (see below) and output placed in a directory
shared with the container by the host which you must specify. More specifically, this github
source contains the Dockerfile and docker build context for building the container. Per update
to your clone of the repo, you only need to build the container once. Then you can run it as
much as you like.

## Output

This program will produce a VCF output file with the simulated diploid individuals, and a sample map file that maps the VCF sample names to their respective populations. The population labels are configurable on the command line, but are set to correct defaults if the framework is for the purpose of modeling the populations described above.

## Usage

### Prerequisites

Docker version 1.12 or higher. Any operating system that will run that will do. You do not need any input files or other auxiliary information, other than what you want to set parameters to if you want to change from the Gravel et al. estimates of the parameters.

### To build the docker image

`docker build --build-arg UID=$UID -t out-of-africa-model out-of-africa-model`

This will build a docker image called out-of-africa-model and add it to your collection of images.

### To run the simulation and generate a VCF

Create a directory called shared (or whatever you want, adjusting below), or specify any
existing directory, wherever you want your output to go.

```
mkdir -p shared
docker run -t -i -v $PWD/shared:/home/popsim/shared out-of-africa-model --n-samples 100 100 100 --chromosome 22 --output-basename shared/simulated-chm22
```

This will create 100 diploid individuals for each of the 3 populations and output their genotypes at segregating sites as phased VCF data in shared/simulated-chm22.vcf, and a sample mapping file that indicates which sample is from which population, as shared/simulated-chm22.map. Both of which are suitable directly for use as a reference population for RFMIX v2 (separate project).

NOTE: In the future, you will just have to specify which chromosome, not a path to a genetic map file that is inside the container. For now, just change the "chr22" part of the filename accordingly.

To see a list of command line options that you may modify, just do

`docker run -t -i out-of-africa-model -h`

Note that you can not change the basic structure of the model, just the parameters of it, as described above.

Note also that at this time the migration rates between populations after their divisions can not be changed at this time by the command line and are hard coded to the values found by Gravel et al. 2011. Thus, radically changing the parameters of the model, for whatever purpose, have to deal with these rates being set as well, although you can modify the code and rebuild the container.

### Limitations

If you choose to simulate the X chromosome, consider all output to be females and your responsibility to modify the VCF to simulate males by dropping one of the haplotypes, or however you want to do that. Also, the genetic map files included from hapmap phaseII separate out the pseudo-autosomal region into separate files and thus have gaps in the X chromosome genetic map. That won't cause the end of the world, but for those two regions there will be no variation in recombination rate in the simulation.

Do not think of simulating Y chromosomes or mitochondrial genome using this framework. That is out of any intended scope. Better support for X chromosome simulation may be included in the future, but never will include increasing the effective population size just for the pseudo-autosomal region. If this framework is ever modified to simulate the entire genome including the X chromosome, sex bias in migration and effective size will probably not be considered. If you like these things however, please write in, or of course feel free to fork the repo and modify to your needs. I'm just not planning on doing anything with this that requires considering these aspects, but I'm well aware they exist and in particular would effect X vs. autosome simulations.

This as well as msprime was written in python. Some might consider that a plus.

### License

(c) 2016 Mark Koni Hamilton Wright, Stanford University School of Medicine

Available under the GNU General Public License v3.

Credits to Alicia Martin (https://github.com/armartin) who supplied a script that also performed this simulation in more fixed-purpose form, that was used to construct this framework.
