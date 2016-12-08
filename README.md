## Simulate one full chromosome of the human genome for the Out of Africa migration and expansion model

In brief, the model describes the origin and spread of the human species as a single ancestral population that grew instaneously (nearly so anyway?) into the population inhabiting the African continent. This population stayed the same size (effective population size, N_e) to the present day. At a point in the past, some individuals began migrating out of Africa. This group later split and went in opposite directions, some going on to found the present day European population, the rest founding the present day East Asian population. Both latter populations experienced exponential growth following the division of the originating out-of-africa population. The parameters, which determine the timing of events, effective population sizes, and grow rates of the European and East Asian populations are estimated from the existing human genetic data available at the time and presented in Gravel S, et al., 2011 "Demographic history and rare allele sharing among human populations." PNAS 108(29):11983-11988. These parameters are all configurable by command line options to this simulation framework, except the migration rate parameters (at this time). The default values are set to the maximum likelihood estimated values given in Table 2 of Gravel et al. for "Low coverage + exons" 1000 Genomes Project data. 

See Gravel et al. 2011 PNAS Figure 4 for a graphical view of the model.

This framework is based on using the msprime coalesent simulator by Jerome Kelleher (https://github.com/jeromekelleher), imported automatically by the docker container build and used under the GPLv3 License. See https://msprime.readthedocs.io/en/stable/introduction.html for an introduction to msprime and its documentation. 

## Output

This program will produce a VCF output file with the simulated diploid individuals, and a sample map file that maps the VCF sample names to their respective populations. The population labels are configurable on the command line, but are set to correct defaults if the framework is for the purpose of modeling the populations described above.

