#!/usr/bin/env python
from __future__ import print_function
import sys
import msprime
import math
from datetime import datetime
import gzip
import argparse
import os

# NOTE - All comments are from KONI unless otherwise indicated. 

# Cribbed from Alicia's script, she uses it as a shorthand to print to stderr
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

# Cribbed from Alicia's script (alicia-simulate-prs.py)
def current_time():
    return(' [' + datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S') + ']')


# Cribbed from Alicia's script (alicia-simulate-prs.py), but this is now heavily modified
# to extract the parameters Alicia had hard coded from Gravel et al 2011 PNAS to accept
# them from the Namespace sp which is generated from command line parsing. All values
# Alicia had hard coded from the paper (see Figure 4, and Table 2), are currently as of
# this writing set to default values from that paper and equivalent to what Alicia had
# EXCEPT THE MIGRATION PARAMETERS. This is still using Alicia's code and hard coded values.
# It can not yet be set on the command line.
def out_of_africa(sp):
    """
    Do any adjustments/calculations for units and construct the msprime objects 
    needed to call msprime to execute the simulation
    """

    # Command line accepts number of diploid individuals simulated, so double
    # as msprime thinks in terms of haploid lineages
    n_samples = [ x*2 for x in args.n_samples ]

    # Calculate the final sizes, or in coalescent terms, the starting sizes, of the
    # Europe and East Asia populations which under the Gravel et al. 2011 out of africa
    # model experience exponential growth after diverging from each other going
    # separate ways in the world. Command line accepts values in percentages as given in
    # the Gravel et al. paper. We just need to know the starting effective size, starting
    # as in the present day effective size, as the simulation goes backward in time.
    sp.europe_final_size = sp.out_to_europe_size / math.exp(-(sp.europe_growth_rate/100.) * (sp.merge_europe_asia_time/sp.generation_time))
    sp.asia_final_size = sp.out_to_asia_size / math.exp(-(sp.asia_growth_rate/100.) * (sp.merge_europe_asia_time/sp.generation_time))

    # Set the number of distinct initial populations and their effective sizes, also
    # the number of lineages to simulate (coalesce) (sp.n_samples[])
    #
    # NOTE: User can specify population labels on the command line and these
    #       can, by user error, then not map correctly to the values they specified
    #       for the model as they intended, and so also the variable terms used
    #       here may not actually mean what the user specified. The labels however
    #       are only for use in the sample map output, leaving the user the choice
    #       of how to indicate them - maybe integers, maybe HapMap codes, maybe words
    #       but it is user responsibility to understand this
    population_configurations = [
        msprime.PopulationConfiguration(
            sample_size=n_samples[0], initial_size=sp.africa_size),
        msprime.PopulationConfiguration(
            sample_size=n_samples[1], initial_size=sp.europe_final_size,
            growth_rate=sp.europe_growth_rate/100.),
        msprime.PopulationConfiguration(
            sample_size=n_samples[2], initial_size=sp.asia_final_size,
            growth_rate=sp.asia_growth_rate/100.)
    ]

    # TODO: migration parameters to command line, though that may be difficult or awkward
    # NOTE: Using Alicia's hard-coded values sourced from Gravel et al. 2011
    # Migration rates during the various epochs.
    m_AF_B = 15e-5
    m_AF_EU = 2.5e-5
    m_AF_AS = 0.78e-5
    m_EU_AS = 3.11e-5

    migration_matrix = [
        [      0, m_AF_EU, m_AF_AS],
        [m_AF_EU,       0, m_EU_AS],
        [m_AF_AS, m_EU_AS,       0],
    ]

    # Set up the list of changes to populations that happen and when they happen
    europe_asia_merge_time = sp.merge_europe_asia_time/sp.generation_time
    demographic_events = [
        # All the next events, until indicated below, are coincident and thus really one
        # event
        
        # The Europe (pop 1) and East Asia (pop 2) populations merge and become population 1
        msprime.MassMigration(
            time=europe_asia_merge_time, source=2, destination=1, proportion=1.0),
        # Migration rates must now refelect migration between the original African population
        # and the merged Europe/East Asian population which are still separate at this point
        msprime.MigrationRateChange(time=europe_asia_merge_time, rate=0),
        msprime.MigrationRateChange(
            time=europe_asia_merge_time, rate=m_AF_B, matrix_index=(0, 1)),
        msprime.MigrationRateChange(
            time=europe_asia_merge_time, rate=m_AF_B, matrix_index=(1, 0)),
        # Finally, the effective size of the merged population (pop 1 now) is different
        # otherwise it would be whatever the shrinking Europe population size is/was.
        msprime.PopulationParametersChange(
            time=europe_asia_merge_time, initial_size=sp.out_of_africa_size,
            growth_rate=0, population_id=1),

        # Now we are backward further in time
        # Next, the migrating out of africa population (currently pop 1) joins to the
        # population of origin (pop 0), the african population
        msprime.MassMigration(
            time=sp.merge_to_africa_time/sp.generation_time, source=1, destination=0, proportion=1.0),

        # In the final event of the model, the African population (pop 0, the only one left)
        # reduces in size to the ancestral population size until the MRCA (end of the simulation)
        msprime.PopulationParametersChange(
            time=sp.africa_expansion_time/sp.generation_time,
            initial_size=sp.ancestral_size, population_id=0)
    ]

    # Use the demography debugger to print out the demographic history
    # that we have just described.
    # Shows on stderr what will be performed and when. Requires some knowledge to decode
    # what those messages mean, but they are important to check. Note that the values
    # shown will be in generations, not years, but the command line accepts values in
    # years.
    dp = msprime.DemographyDebugger(
        Ne=sp.ancestral_size,
        population_configurations=population_configurations,
        migration_matrix=migration_matrix,
        demographic_events=demographic_events)
    dp.print_history(output=sys.stderr)
    
    return(population_configurations, migration_matrix, demographic_events)

# cribbed from Alicia's script. Doc string modified some, but otherwise unmodified.
# Returns the opaque msprime object which I believe is the tree sequence
# 2017-12-07
# NOTE/TODO: MUTATION RATE IS HARD CODED, could be a command line option
def simulate_ooa(population_configurations, migration_matrix, demographic_events, recomb):
    """
    Accepts the objects configured above and calls msprime to perform the coalescent
    simulation of an entire chromosome. Length of the chromosome and recombination
    rate is dictated by the genetic map file which is passed here (set by command line)
    """
    eprint('Starting simulations' + current_time())
    simulation = msprime.simulate(
        population_configurations = population_configurations,
        migration_matrix=migration_matrix,
        mutation_rate=2e-8,
        recombination_map = msprime.RecombinationMap.read_hapmap(recomb)
    )
    eprint('Ending simulations' + current_time())
    return(simulation)



## MAIN SCRIPT

# Setup the command line options and their defaults. All defaults are or are equivalent
# to Alicia's hard-coded values for Gravel et al 2011 out of africa model
#
# Note that the timing of things, sizes and growth rates, can therefore be changed by
# these parameters, but the basic tree structure of the population divergence can't.
# It is still and always going to be
# Ancestral -> Africa -> { Africa, { Europe + East Asia } } -> { Africa, Europe, East Asia }
cmdline = argparse.ArgumentParser(description="Read command-line settings for population simulation")

cmdline.add_argument("--generation-time", help="Set generation time in years", type=int, default=25)
cmdline.add_argument("--ancestral-size",help="Set ancestral population size from which --africa-size population emerges (N_A)",type=int,default=7300)
cmdline.add_argument("--africa-size", help="Set effective population size of African population (held constant throughout) (N_AF)",type=int,default=14474)
cmdline.add_argument("--out-of-africa-size",help="Set effective size of population that leaves africa at --merge-to-africa time (T_B)", type=int, default=1861)
cmdline.add_argument("--out-to-europe-size",help="Set effective size of population that leaves out of africa population to go to Europe (N_EU0)",type=int, default=1032)
cmdline.add_argument("--out-to-asia-size",help="Set effective size of population that leaves out of africa population to go to Asia (N_AS0)",type=int,default=550)

cmdline.add_argument("--asia-growth-rate",help="Set %% growth rate per generation of Asian population", type=float, default=0.38)
cmdline.add_argument("--europe-growth-rate",help="Set %% growth rate per generation of European population", type=float, default=0.48)

cmdline.add_argument("--merge-europe-asia-time", help="Set time in years when separated European and Asian populations merge to out of africa population (T_EuAs)",type=float,default=23000.)
cmdline.add_argument("--merge-to-africa-time", help="Set time in years when merged European and Asian populations merge to African population (T_B)", type=float, default=51000.)
cmdline.add_argument("--africa-expansion-time",help="Set time in years when ancestral population size becomes the full african population size (instantaneous change) (T_AF)", type=float, default=148000.)

cmdline.add_argument("--n-samples",metavar="N",help="sample sizes to generate, order africa europe asia",type=int,nargs=3,default=[10, 10, 10])

cmdline.add_argument("--population-labels",help="Labels for simulated populations",type=str,nargs=3,default=[ 'Africa', 'Europe', 'East Asia' ])
cmdline.add_argument("--output-basename",help="prefix for filename (may include path) for VCF and sample mapping output",type=str,default="",required=True)

# Note - if a genetic map isn't specified, need to figure out how to set a sensible default
#        map. Totally extra to do that though though.
cmdline.add_argument("--genetic-map",help="Genetic map file for chromosome to simulate, hapmap phase2 4 column format. This will control the size in bp of the chromosome as well. Only a single chromosome is simulated, the map file should be for exactly one chromosome, not the genome.",type=str,default="")
cmdline.add_argument("--chromosome",help="Simulate the specified human genome chromosome (GRCh37), any autosome 1 through 22 or X. Either an explicit genetic map with the --genetic-map option or --chromosome must be specified, but --genetic-map option overrides this option",type=str,default=20)

# Now that we know how to understand them, get the user's options
args = cmdline.parse_args()
outcmd = "sed -e 's/^##contig=<ID=1/^##contig=<ID=%s/' | sed -e 's/^1\\t/%s\\t/' > %s.vcf" % (str(args.chromosome), str(args.chromosome), args.output_basename)
print(outcmd,file=sys.stderr)

# If the user did not specify and explicit genetic map and instead gave a chromosome
# set the genetic map argument to the appropriate genetic map from hapmap phaseII
if args.genetic_map == "" and args.chromosome != "":
    args.genetic_map="hapmap-phaseII-genetic-maps/genetic_map_GRCh37_chr%s.txt.gz" % args.chromosome

# Construct what we need to specify a simulation to msprime
(pop_config, migration_matrix, demography) = out_of_africa(args)

# Run the simulation and get the opaque msprime simulation object
simulation = simulate_ooa(pop_config, migration_matrix, demography, args.genetic_map)

# Write VCF and sample map output. Sample map only if an output basename was given
# otherwise VCF goes to stdout. I am so glad msprime has a VCF output function!
if args.output_basename != "":
    f = os.popen(outcmd, "w");
else:
    f = sys.stdout
simulation.write_vcf(f,ploidy=2)
f.close()

if args.output_basename != "":
    f = open(args.output_basename + '.map','w')
    sm = 0
    for i in xrange(0,len(args.n_samples)):
        for j in xrange(0,args.n_samples[i]):
            f.write("msp_%d\t%s\n" % (sm,args.population_labels[i]))
            sm += 1;

    f.close()

