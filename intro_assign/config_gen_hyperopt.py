import os
import subprocess
from hyperopt import tpe, hp, fmin, space_eval
from datetime import datetime


now = datetime.now()

current_time = now.strftime("%H_%M")


def generate_config(projectName, pathToReads, genomeSize, threads, coverage, args):
    output = open("necat.config", "w")
    project_l = "PROJECT=" + projectName
    readlist_l="ONT_READ_LIST=" + pathToReads
    genomeSize_l = "GENOME_SIZE=" + str(genomeSize)
    threads_l = "THREADS=" + str(threads)
    minReadL_l = "MIN_READ_LENGTH=" + "3000"
    prepOutputCov_l = "PREP_OUTPUT_COVERAGE=" + str(coverage)
    ovlpFast_l = "OVLP_FAST_OPTIONS=" + "-n "+str(int(args['-n']))+" -z "+str(int(args['-z']))+" -b "+str(int(args['-b']))+" -e " +str(args['-e'])+ " -j 0 -u 1 -a " + str(int(args['-a'])) + "-q " + str(int(args['-q'])) + "-k " + str(int(args['-k']))
    ovlpSensitive_l = "OVLP_SENSITIVE_OPTIONS=" + "-n "+str(int(args['-n1']))+" -z "+str(int(args['-z1']))+" -b "+str(int(args['-b1']))+" -e " +str(args['-e1'])+ " -j 0 -u 1 -a " + str(int(args['-a1'])) + "-q " + str(int(args['-q1'])) + "-k " + str(int(args['-k1']))
    cnsFast_l = "CNS_FAST_OPTIONS=" + "-a "+str(int(args['-a2']))+" -x "+str(int(args['-x']))+" -y "+str(int(args['-y']))+" -l "+str(int(args['-l']))+" -e " + str(args['-e2']) + " -p "+str(args['-p'])+" -u 0" 
    cnsSensitive_l = "CNS_SENSITIVE_OPTIONS=" + "-a "+str(int(args['-a3']))+" -x "+str(int(args['-x1']))+" -y "+str(int(args['-y1']))+" -l "+str(int(args['-l1']))+" -e " + str(args['-e3']) + " -p "+str(args['-p1'])+" -u 0"
    trimOvlp_l = "TRIM_OVLP_OPTIONS=" + "-n "+str(int(args['-n2']))+" -z "+str(int(args['-z2']))+" -b "+str(int(args['-b2']))+" -e " + str(args['-e4']) + " -j 1 -u 1 -a " + str(int(args['-a4']))  + "-q " + str(int(args['-q2'])) + "-k " + str(int(args['-k2']))
    asmOvlp_l = "ASM_OVLP_OPTIONS=" + "-n "+str(int(args['-n3']))+" -z "+str(int(args['-z3']))+" -b "+str(int(args['-b3']))+" -e " + str(args['-e5']) + " -j 1 -u 0 -a " + str(int(args['-a5'])) + "-q " + str(int(args['-q3'])) + "-k " + str(int(args['-k3']))
    numItr = "NUM_ITER=" + "2"
    cnsOutCov_l = "CNS_OUTPUT_COVERAGE=" + str(int(coverage * 0.8))
    cleanup_l = "CLEANUP=1"
    useGrid_l = "USE_GRID=false"
    gridNode_l = "GRID_NODE=0"
    gridOption_l = "GRID_OPTIONS="
    smallMem_l = "SMALL_MEMORY=0"
    fsaOl_l = "FSA_OL_FILTER_OPTIONS="
    fsaAssemble_l = "FSA_ASSEMBLE_OPTIONS="
    fsaCtg_l = "FSA_CTG_BRIDGE_OPTIONS="
    polishContig_l = "POLISH_CONTIGS=false"

    outputList = [project_l, readlist_l, genomeSize_l, threads_l, minReadL_l, prepOutputCov_l,
    ovlpFast_l,ovlpSensitive_l,cnsFast_l,cnsSensitive_l,trimOvlp_l,asmOvlp_l,numItr,
    cnsOutCov_l,cleanup_l,useGrid_l,gridNode_l,gridOption_l,smallMem_l,fsaOl_l,
    fsaAssemble_l,fsaCtg_l,polishContig_l]
    
    for s in outputList:
        output.write(s + "\n")


def objective(args):
    score=0.0
    try:
        now = datetime.now()
        name = "het_assembly-" + now.strftime("%d_%H_%M")
        generate_config(name, "/workdir/mze3/Optimize_Necat_Params/long_reads.fofn", 2200000, 24, 50, args)
        thing = subprocess.run(['./NECAT/Linux-amd64/bin/necat.pl', 'bridge', 'necat.config'])
        print(thing.returncode)
        minimapSubCommand = 'het_contig.fasta'
        assembFile = name + '/6-bridge_contigs/bridged_contigs.fasta'
        alignFile = '>align.paf'
        if os.path.isfile(assembFile):
             ret = subprocess.run(['minimap2', '-x','asm20', '-t 24', minimapSubCommand, assembFile], capture_output=True)
             pafOut = ret.stdout.decode('utf-8')
             out = open("align.paf", "w")
             out.write(pafOut)
             out.close()
             score = subprocess.run(['./score_collapse','align.paf', assembFile], capture_output=True)
             score = float(score.stdout.decode('utf-8'))
             os.rename('necat.config', name+'/necat.config')
             os.rename('align.paf', name+'/align.paf')

    except Exception as e:
        print(e)
        score = 0.0
    return (1.0 - score)


space = {
    '-z' : hp.uniform('-z', 5, 100 ),
    '-z1' : hp.uniform('-z1', 5, 100 ),
    '-z2' : hp.uniform('-z2', 5, 100 ),
    '-z3' : hp.uniform('-z3', 5, 100 ),
    '-q' : hp.uniform('-q', 50, 5000),
    '-q1' : hp.uniform('-q1', 50, 5000),
    '-q2' : hp.uniform('-q2', 50, 5000),
    '-q3' : hp.uniform('-q3', 50, 5000),
    '-k' : hp.uniform('-k', 7, 30),
    '-k1' : hp.uniform('-k1', 7, 30),
    '-k2' : hp.uniform('-k2', 7, 30),
    '-k3' : hp.uniform('-k3', 7, 30),
    '-b' : hp.uniform('-b', 1000, 4000),
    '-b1' : hp.uniform('-b1', 1000, 4000),
    '-b2' : hp.uniform('-b2', 1000, 4000),
    '-b3' : hp.uniform('-b3', 1000, 4000),
    '-a' : hp.uniform('-a', 250, 1000),
    '-a1' : hp.uniform('-a1', 250, 1000),
    '-a2' : hp.uniform('-a2', 250, 1000),
    '-a3' : hp.uniform('-a3', 250, 1000),
    '-a4' : hp.uniform('-a4', 250, 1000),
    '-a5' : hp.uniform('-a5', 250, 1000),
    '-e' : hp.uniform('-e', 0.1, 1.0),
    '-e1' : hp.uniform('-e1', 0.1, 1.0),
    '-e2' : hp.uniform('-e2', 0.1, 1.0),
    '-e3' : hp.uniform('-e3', 0.1, 1.0),
    '-e4' : hp.uniform('-e4', 0.1, 1.0),
    '-e5' : hp.uniform('-e5', 0.1, 1.0),
    '-x' : hp.uniform('-x', 2, 8),
    '-x1' : hp.uniform('-x', 2, 8),
    '-y' : hp.uniform('-y', 6, 24),
    '-y1' : hp.uniform('-y', 6, 24),
    '-l' : hp.uniform('-l', 250, 1000),
    '-l1' : hp.uniform('-l', 250, 1000),
    '-p' : hp.uniform('-p', 0.400000, 1.000000),
    '-p1' : hp.uniform('-p', 0.400000, 1.000000),
    '-n' : hp.uniform('-n', 50, 5000 ),
    '-n1' : hp.uniform('-n1', 50, 5000 ),
    '-n2' : hp.uniform('-n2', 50, 5000 ),
    '-n3' : hp.uniform('-n3', 50, 5000 )
}

best = fmin(objective, space, algo=tpe.suggest, max_evals=550)
print(best)
