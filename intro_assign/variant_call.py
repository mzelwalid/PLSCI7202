import os
import subprocess

inputlist = open("time_tag_score_sorted.list", "r")
assembly_suffix = "/6-bridge_contigs/bridged_contigs.fasta"
chromosome_path = "/media/Exthdd1/Cassava/sequences/Mesculenta7.1_Chr12.fa"


for line in inputlist:
    timetag = line.rstrip()
    assembly_path = 'het_assembly-' + timetag + assembly_suffix
    alignment = subprocess.run(['minimap2', '-ax', 'asm20', chromosome_path, assembly_path], stdout=subprocess.PIPE)
    samOut = alignment.stdout.decode('utf-8')
    out = open('alignment.sam', 'w')
    out.write(samOut)
    out.close()
    subprocess.run(['samtools', 'sort','-O', 'bam','-o', 'alignment.sorted.bam', 'alignment.sam'])
    subprocess.run(['samtools', 'index', 'alignment.sorted.bam'])
    pipe = subprocess.run(['bcftools', 'mpileup','-o','mpileupOut.bcf', '-Ou', '-f', chromosome_path, '-r', '12', 'alignment.sorted.bam'])
    subprocess.run(['bcftools','call','-mv','-Ob','-o', timetag +'-het_assembly.bcf.gz', 'mpileupOut.bcf'])
    subprocess.run(['bcftools', 'index', timetag+'-het_assembly.bcf.gz'])
    subprocess.run(['bcftools', 'isec', '-p', 'het_assembly-'+timetag+'/vcf_intersects', timetag+'-het_assembly.bcf.gz','/media/Exthdd1/Cassava/filtered.recode.vcf.gz'])
    grep_process = subprocess.run(['grep', '-v', '^#', 'het_assembly-'+timetag+'/vcf_intersects/0003.vcf'], stdout = subprocess.PIPE)
    wc_process = subprocess.run(['wc','-l'], input = grep_process.stdout, stdout = subprocess.PIPE)
    count = int(wc_process.stdout.decode('utf8').rstrip())

    

inputlist.close()