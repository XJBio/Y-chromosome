#Read phasing
canu -d Canu-hifi -p canu-hifi genomeSize=3g useGrid=false maxThreads=40 -haplotypePat pat.NGS.read.fastq -haplotypeMat mat.NGS.read.fastq -pacbio F.hifi.read.fastq.gz
canu -d Canu-nano -p canu-nano genomeSize=3g useGrid=false maxThreads=40 -haplotypePat pat.NGS.read.fastq -haplotypeMat mat.NGS.read.fastq -nanopore F.hifi/ont.read.fastq.gz

#Assemble
#hifiasm
hifiasm -o genome.asm --h1 read1.fq.gz --h2 read2.fq.gz –ul ultralongont.fq.gz HiFi.fq.gz
#HiCanu
HiCanu genomeSize=3.1g -pacbio-hifi hifi.fq -haplotypeP1 pat.fq -haplotypeM1 mat.fq corFilter="quick"
# NextDenovo
NextDenovo read_cutoff = 200k seed_cutoff = 240000 genome_size = 3.1g
#Flye
Flye --nano-hq ont.fq -g 3.1g 
#verkko
meryl count compress k=31 memory=200 threads=6 output Pat-compress.k31mer.meryl P1.NGS.1.fq.gz  &
meryl count compress k=31 memory=200 threads=6 output Mat-compress.k31mer.meryl M1.NGS.1.fq.gz  &
meryl count compress k=13 memory=200 threads=6 output child-compress.k31mer.meryl F1.NGS.1.fq.gz
hapmers.sh Mat-compress.k31mer.meryl/ Pat-compress.k31mer.meryl/ child_allcompress.k31.meryl/ &
verkko -d trio-k31 --hifi hifi.css.read.fasta.gz --nano ontall.fasta --hap-kmers Mat-compress.k31mer.hapmer.meryl/ Pat-compress.k31mer.hapmer.meryl/  trio --threads 50 --local --local-memory 200 &

#Alignment 
# winnowmap
meryl count k=21 output merylDB genome.fasta
meryl print greater-than distinct=0.9998 merylDB > repetitive_k21.txt
winnowmap -k 21 -t 40 --MD -W repetitive_k21.txt -ax map-ont/map-pb genome.fa haplotype.hifi/ont.fastq.gz -o genome.alin.sam

#Polishing
# nextPolish2
yak count -o k21.yak -k 21 -b 37 <(zcat sr.R*.fastq.gz) <(zcat sr.R*.fastq.gz)
yak count -o k31.yak -k 31 -b 37 <(zcat sr.R*.fastq.gz) <(zcat sr.R*.fastq.gz)
nextPolish2 -t 5 hifi.map.sort.bam genome.fa.gz k21.yak k31.yak > genome.np2.fa
#DeepVariant
run_deepvariant --model_type=PACBIO --ref=genome.fa --reads=genome.alin.sorted.bam --output_vcf=genome.hifi.vcf  --output_gvcf=genome.hifi,gvcf 
bcftools view -f "PASS" -e 'FORMAT/VAF<=0.5 | FORMAT/GQ<=30' -Oz genome.hifi.vcf > genome.hifi.filtered.vcf
#PEPPER-DeepVariant
run_pepper_margin_deepvariant call_variant -b genome.alin.sorted.bam -f genome.fa -o $out/ -p genome.ont --ont_r9_guppy5_sup -t 48
bcftools view -f "PASS" -e 'FORMAT/VAF<=0.5 | FORMAT/GQ<=25' -Oz genome.ont.vcf > genome.ont.filtered.vcf
/opt/hap.py/bin/hap.py genome.ont.filtered.vcf.gz genome.hifi.filtered.vcf.gz -r genome.fa -o genome.happy.output --pass-only --engine=vcfeval --threads=48
python3 vcf_merge_t2t.py -v1 genome.hifi.filtered.vcf.gz -v2 genome.ont.filtered.vcf.gz -hv genome.happy.output.vcf -o genome.merged.vcf
#Merfin
merfin -polish -threads 2 -sequence genome.fa -vcf genome.merged.vcf -readmers F.meryl -peak 46.4 -prob lookup_table.txt -seqmers genome.fa.meryl  -output $out 
bcftools consensus -f genome.fa -H 1 merfin.out.gz > genome.polish.fa 
#Sniffle
sniffles –input mat.win.ont/hifi.aln.sorted.bam --reference mat.fasta --vcf mat.ont/hifi.sniff.vcf.gz
python3 filter.py mat.ont/hifi.sniff.vcf > mat.ont/hifi.filter.sniff.vcf
jasmine.jar Main max_dist=500 min_seqid =0.3 spec_reads=3 –output_genotypes in_support=2 file_list=filelist.txt out_file=merge.mat.sniff.sv.vcf

#Completeness, phasing and base call accuracies
#Merqury
meryl greater-than 1 F.hifi.meryl output F.hifi.gt1.meryl
meryl greater-than 1 F.NGS.meryl output F.NGS.gt1.meryl 
meryl divide-round 3 F.NGS.gt1.meryl output F.NGS.gt1.divideRoun3.meryl 
meryl union-max F.hifi.gt1.meryl F.NGS.gt1.divideRoun3.meryl output F.hybrid.meryl 
sh $MERQURY/trio/hapmers.sh Mat.meryl Pat.meryl F.hybrid.meryl 
merqury.sh /path/F-hybrid-gt1-illuDivide3/F.hybrid.meryl/ /path/F-hybrid-gt1-illuDivide3/M.hapmer.meryl /path/F-hybrid-gt1-illuDivide3/P.hapmer.meryl mat.fasta pat.fasta  hybird 

#Collapsed analyses
#SDA
SDA denovo --threads 20 --platform ccs –input $prefix.hifi.alin.sorted.bam --ref genome.polish.fa -d $prefix_collapse --minaln 15000 --pre $prefix

#Annotation
#cactus
cactus ./mjobStore ./seqfile-hg38-mat hg38-mat-out/hg38-mat.hal --maxDisk 500G --maxMemory 250G --workDir ./hg38-mat-work --binariesMode local
#Comparative Annotation Toolkit
luigi --module cat RunCat --hal=hg38-mat.hal --ref-genome=GRCh38 --workers=10 --config=CAT-mat-hg38-gencode.config –work -dir CAT-mat-work --out-dir CAT-mat-out --local-scheduler --assembly-hub –maxCores 5 --binary-mode local >CAT-mat-hg38gencode.log
#RepeatMasker
RepeatMasker -parallel 20 -species human -gff -xsmall mat.fa -dir ./mat-soft-mask >mat.repeatmasker.log &
#biser
biser -o mat.sd --gc-heap 1G --keep-contigs mat-soft-mask.fa

#Ancestry analysis
#Rfmix
Rfmix -f mat-hg38.pair.vcf.gz -r /path/1kgenomevcf/phase3-hg38X 30-vcf/ALL.chr"$i".shapeit2_integrated_v1a.GRCh38.20181129.phased.vcf.gz -m sample.smap -g /path/chr"$i".GRCh38.map -o chr"$i"-mat-pair-rfmix --chromosome=chr"$i" --n-threads=24 -c 50 -s 5
# yhaplo
yhaplo -i chrY-hg19.vcf -o chrY

#Heterozygosity analysis
#Mummer
nucmer -t 40 -p $prefix genome1.fa genome2.fa 
delta-filter -q -l 100000 -i 98 $prefix.delta > $prefix.delta.filter
show-coords -Trcl -d -o $prefix.delta.filter > $prefix.coords
dnadiff -p $prefix -d $prefix.delta.filter
syri -c $prefix.coords -d $prefix.delta.filter -r ../../chrY_hap2.fa -q genome.fa --prefix $prefix
#minimap and svim-asm #
minimap2 -a -x asm5 chm13v2.0.fa mat.fa -t 24 -eqx --cs >chm13_mat-asm5.sam
samtools view -bS chm13_mat-asm5.sam >chm13_mat-asm5.bam
samtools sort -m 4G -@ 10 -o chm13_mat-asm5.sort.bam chm13_mat-asm5.bam
samtools index chm13_mat-asm5.sort.bam
svim-asm haploid ./mat chm13_mat-asm5.sort.bam chm13v2.0.fa