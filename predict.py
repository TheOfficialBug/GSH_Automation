import os
import argparse
import pybedtools
from pybedtools import BedTool

def print_help():
    print("""
    Description: Find all universal genomic safe harbors in the human genome.
    Usage: python predict_gsh.py [-dist_from_genes] [-dist_from_oncogenes] [-dist_from_micrornas] [-dist_from_trnas] [-dist_from_lncrnas] [-dist_from_enhancers] [-dist_from_centromeres] [-dist_from_gaps] [-h|--help]
    Arguments:
        -genes: Whether to exclude regions with and around genes (default=True)
        -oncogenes: Whether to exclude regions with and around oncogenes (default=True)
        -micrornas: Whether to exclude regions with and around microRNAs (default=True)
        -trnas: Whether to exclude regions with and around tRNAs (default=True)
        -lncrnas: Whether to exclude regions with and around lncRNAs (default=True)
        -enhancers: Whether to exclude regions with and around enhancers (default=True)
        -centromeres: Whether to exclude regions with and around centromeres (default=True)
        -gaps: Whether to exclude regions with and around gaps (default=True)
        -dist_from_genes: Minimal distance from any safe harbor to any gene in bp (default=50000)
        -dist_from_oncogenes: Minimal distance from any safe harbor to any oncogene in bp (default=300000)
        -dist_from_micrornas: Minimal distance from any safe harbor to any microRNA in bp (default=300000)
        -dist_from_trnas: Minimal distance from any safe harbor to any tRNA in bp (default=150000)
        -dist_from_lncrnas: Minimal distance from any safe harbor to any long-non-coding RNA in bp (default=150000)
        -dist_from_enhancers: Minimal distance from any safe harbor to any enhancer in bp (default=20000)
        -dist_from_centromeres: Minimal distance from any safe harbor to any centromere in bp (default=300000)
        -dist_from_gaps: Minimal distance from any safe harbor to any gaps in bp (default=300000)
        -h, --help: Prints help
    """)

def main():
    parser = argparse.ArgumentParser(description="Find all universal genomic safe harbors in the human genome.")
    parser.add_argument("-genes", action="store_true", default=True)
    parser.add_argument("-oncogenes", action="store_true", default=True)
    parser.add_argument("-micrornas", action="store_true", default=True)
    parser.add_argument("-trnas", action="store_true", default=True)
    parser.add_argument("-lncrnas", action="store_true", default=True)
    parser.add_argument("-enhancers", action="store_true", default=True)
    parser.add_argument("-centromeres", action="store_true", default=True)
    parser.add_argument("-gaps", action="store_true", default=True)
    parser.add_argument("-dist_from_genes", type=int, default=50000)
    parser.add_argument("-dist_from_oncogenes", type=int, default=300000)
    parser.add_argument("-dist_from_micrornas", type=int, default=300000)
    parser.add_argument("-dist_from_trnas", type=int, default=150000)
    parser.add_argument("-dist_from_lncrnas", type=int, default=150000)
    parser.add_argument("-dist_from_enhancers", type=int, default=20000)
    parser.add_argument("-dist_from_centromeres", type=int, default=300000)
    parser.add_argument("-dist_from_gaps", type=int, default=300000)
    parser.add_argument("-h", "--help", action="store_true")

    args = parser.parse_args()

    if args.help:
        print_help()
        return

    # Create temporary directory
    if os.path.exists("tmp"):
        os.rmdir("tmp")
    os.mkdir("tmp")

    # Process genes
    if args.genes:
        print(f"Distance from genes = {args.dist_from_genes} bp")
        process_genes(args.dist_from_genes)

    # Process oncogenes
    if args.oncogenes:
        print(f"Distance from oncogenes = {args.dist_from_oncogenes} bp")
        process_oncogenes(args.dist_from_oncogenes)

    # Process microRNAs
    if args.micrornas:
        print(f"Distance from microRNAs = {args.dist_from_micrornas} bp")
        process_micrornas(args.dist_from_micrornas)

    # Process tRNAs
    if args.trnas:
        print(f"Distance from tRNAs = {args.dist_from_trnas} bp")
        process_trnas(args.dist_from_trnas)

    # Process lncRNAs
    if args.lncrnas:
        print(f"Distance from lncRNAs = {args.dist_from_lncrnas} bp")
        process_lncrnas(args.dist_from_lncrnas)

    # Process enhancers
    if args.enhancers:
        print(f"Distance from enhancers = {args.dist_from_enhancers} bp")
        process_enhancers(args.dist_from_enhancers)

    # Process centromeres
    if args.centromeres:
        print(f"Distance from centromeres = {args.dist_from_centromeres} bp")
        process_centromeres(args.dist_from_centromeres)

    # Process gaps
    if args.gaps:
        print(f"Distance from gaps = {args.dist_from_gaps} bp")
        process_gaps(args.dist_from_gaps)

    # Merge all regions to avoid
    merge_regions()

    # Obtain safe harbors
    obtain_safe_harbors()

def process_genes(dist):
    os.mkdir("tmp/genes")
    dir = "tmp/genes"

    # Get gene annotation from GENCODE
    genes_gtf = BedTool("data/fixed_Danio_rerio.GRCz11.113.gtf").filter(lambda x: x[2] == "gene").saveas(f"{dir}/gencode_gene_anotation.gtf")

    # Add transcript_id if missing
    with open(f"{dir}/gencode_gene_anotation.gtf", "r") as infile, open(f"{dir}/gencode_v24_annotation_genes_transcript_id.gtf", "w") as outfile:
        for line in infile:
            if "transcript_id" in line:
                outfile.write(line)
            else:
                outfile.write(line.strip() + ' transcript_id "";')

    # Convert to BED format
    genes_bed = BedTool(f"{dir}/gencode_v24_annotation_genes_transcript_id.gtf").gtf_to_bed().saveas(f"{dir}/gencode_v24_annotation_genes.bed")

    # Get flanking regions
    genes_with_flanks = genes_bed.slop(b=dist, g="data/chromInfo.txt").saveas(f"{dir}/gencode_v24_annotation_genes_with_flanks.bed")

    # Merge regions
    genes_with_flanks.sort().merge().saveas(f"{dir}/gencode_v24_annotation_genes_with_flanks_merged.bed")

def process_oncogenes(dist):
    os.mkdir("tmp/oncogenes")
    dir = "tmp/oncogenes"

    # Get GENCODE gene annotation for oncogenes from COSMIC
    oncogenes_gtf = BedTool("data/zebrafish_oncogene_list.txt").intersect(BedTool("tmp/genes/gencode_v24_annotation_genes_transcript_id.gtf"), wa=True).saveas(f"{dir}/gencode_oncogenes_annotation_transcript_id.gtf")

    # Convert to BED format
    oncogenes_bed = BedTool(f"{dir}/gencode_oncogenes_annotation_transcript_id.gtf").gtf_to_bed().saveas(f"{dir}/gencode_v24_annotation_oncogenes.bed")

    # Get flanking regions
    oncogenes_with_flanks = oncogenes_bed.slop(b=dist, g="data/chromInfo.txt").saveas(f"{dir}/gencode_v24_annotation_oncogenes_with_flanks.bed")

    # Merge regions
    oncogenes_with_flanks.sort().merge().saveas(f"{dir}/gencode_v24_annotation_oncogenes_with_flanks_merged.bed")

def process_micrornas(dist):
    os.mkdir("tmp/micrornas")
    dir = "tmp/micrornas"

    # Get flanking regions
    micrornas_with_flanks = BedTool("data/dre-all.bed").slop(b=dist, g="data/chromInfo_zg11.txt").saveas(f"{dir}/Micrornas_with_flanks.bed")

    # Merge regions
    micrornas_with_flanks.sort().merge().saveas(f"{dir}/Micrornas_with_flanks_merged.bed")

def process_lncrnas(dist):
    os.mkdir("tmp/lncrnas")
    dir = "tmp/lncrnas"

    # Add transcript_id if missing
    with open("data/danRer11-lncRNA.gtf", "r") as infile, open(f"{dir}/gencode_v24_long_noncoding_RNAs_transcript_id.gtf", "w") as outfile:
        for line in infile:
            if "transcript_id" in line:
                outfile.write(line)
            else:
                outfile.write(line.strip() + ' transcript_id "";')

    # Convert to BED format
    lncrnas_bed = BedTool(f"{dir}/gencode_v24_long_noncoding_RNAs_transcript_id.gtf").gtf_to_bed().saveas(f"{dir}/gencode_v24_long_noncoding_RNAs.bed")

    # Get flanking regions
    lncrnas_with_flanks = lncrnas_bed.slop(b=dist, g="data/chromInfo.txt").saveas(f"{dir}/gencode_v24_long_noncoding_RNAs_with_flanks.bed")

    # Merge regions
    lncrnas_with_flanks.sort().merge().saveas(f"{dir}/gencode_v24_long_noncoding_RNAs_with_flanks_merged.bed")

def process_trnas(dist):
    os.mkdir("tmp/trnas")
    dir = "tmp/trnas"

    # Convert to BED format
    trnas_bed = BedTool("data/danRer11-tRNAs.gtf").gtf_to_bed().saveas(f"{dir}/gencode_v24_tRNAs.bed")

    # Get flanking regions
    trnas_with_flanks = trnas_bed.slop(b=dist, g="data/chromInfo.txt").saveas(f"{dir}/gencode_v24_tRNAs_with_flanks.bed")

    # Merge regions
    trnas_with_flanks.sort().merge().saveas(f"{dir}/gencode_v24_tRNAs_with_flanks_merged.bed")

def process_enhancers(dist):
    os.mkdir("tmp/enhancers")
    dir = "tmp/enhancers"

    # Get flanking regions
    enhancers_with_flanks = BedTool("data/hglft_genome_343af_45a580.bed").slop(b=dist, g="data/chromInfo_zg11.txt").saveas(f"{dir}/All_human_enhancers_with_flanks.bed")

    # Merge regions
    enhancers_with_flanks.sort().merge().saveas(f"{dir}/All_human_enhancers_with_flank_merged.bed")

def process_centromeres(dist):
    os.mkdir("tmp/centromeres")
    dir = "tmp/centromeres"

    # Get centromeres in BED format
    centromeres_bed = BedTool("data/centromeres.txt").tail(n=3).saveas(f"{dir}/hgTables_centromeric_regions_38.bed")

    # Get flanking regions
    centromeres_with_flanks = centromeres_bed.slop(b=dist, g="data/chromInfo_zg11.txt").saveas(f"{dir}/Centromeres_with_flanks.bed")

    # Merge regions
    centromeres_with_flanks.sort().merge().saveas(f"{dir}/Centromeres_with_flanks_merged.bed")

def process_gaps(dist):
    os.mkdir("tmp/gaps")
    dir = "tmp/gaps"

    # Get gaps in BED format
    gaps_bed = BedTool("data/gaps.txt").tail(n=2).cut([0, 1, 2]).saveas(f"{dir}/hgTables_gaps.bed")

    # Get flanking regions
    gaps_with_flanks = gaps_bed.slop(b=dist, g="data/chromInfo_zg11.txt").saveas(f"{dir}/Gaps_with_flanks.bed")

    # Merge regions
    gaps_with_flanks.sort().merge().saveas(f"{dir}/Gaps_with_flanks_merged.bed")

def merge_regions():
    os.mkdir("tmp/merge")
    dir = "tmp/merge"

    regions_to_avoid = BedTool()

    if os.path.exists("tmp/genes/gencode_v24_annotation_genes_with_flanks_merged.bed"):
        regions_to_avoid = regions_to_avoid.cat(BedTool("tmp/genes/gencode_v24_annotation_genes_with_flanks_merged.bed"), postmerge=False)

    if os.path.exists("tmp/oncogenes/gencode_v24_annotation_oncogenes_with_flanks_merged.bed"):
        regions_to_avoid = regions_to_avoid.cat(BedTool("tmp/oncogenes/gencode_v24_annotation_oncogenes_with_flanks_merged.bed"), postmerge=False)

    if os.path.exists("tmp/micrornas/Micrornas_with_flanks_merged.bed"):
        regions_to_avoid = regions_to_avoid.cat(BedTool("tmp/micrornas/Micrornas_with_flanks_merged.bed"), postmerge=False)

    if os.path.exists("tmp/trnas/gencode_v24_tRNAs_with_flanks_merged.bed"):
        regions_to_avoid = regions_to_avoid.cat(BedTool("tmp/trnas/gencode_v24_tRNAs_with_flanks_merged.bed"), postmerge=False)

    if os.path.exists("tmp/lncrnas/gencode_v24_long_noncoding_RNAs_with_flanks_merged.bed"):
        regions_to_avoid = regions_to_avoid.cat(BedTool("tmp/lncrnas/gencode_v24_long_noncoding_RNAs_with_flanks_merged.bed"), postmerge=False)

    if os.path.exists("tmp/enhancers/All_human_enhancers_with_flank_merged.bed"):
        regions_to_avoid = regions_to_avoid.cat(BedTool("tmp/enhancers/All_human_enhancers_with_flank_merged.bed"), postmerge=False)

    if os.path.exists("tmp/centromeres/Centromeres_with_flanks_merged.bed"):
        regions_to_avoid = regions_to_avoid.cat(BedTool("tmp/centromeres/Centromeres_with_flanks_merged.bed"), postmerge=False)

    if os.path.exists("tmp/gaps/Gaps_with_flanks_merged.bed"):
        regions_to_avoid = regions_to_avoid.cat(BedTool("tmp/gaps/Gaps_with_flanks_merged.bed"), postmerge=False)

    regions_to_avoid.sort().merge().saveas("tmp/merge/Regions_to_avoid_merged.bed")

def obtain_safe_harbors():
    os.mkdir("tmp/safe_harbors")
    dir = "tmp/safe_harbors"

    # Subtract all regions to avoid from the whole genome
    all_chrom_bed = BedTool("data/all_chrom.bed")
    regions_to_avoid_bed = BedTool("tmp/merge/Regions_to_avoid_merged.bed")
    safe_harbors_bed = all_chrom_bed.subtract(regions_to_avoid_bed).saveas(f"{dir}/Safe_harbors_with_alt.bed")

    # Exclude pseudo-chromosomes and alternative loci
    safe_harbors_bed.filter(lambda x: "_" not in x[0]).saveas(f"{dir}/Safe_harbors.bed")

    # Sort and save final safe harbors
    safe_harbors_bed.sort().saveas("Safe_harbors.bed")

    # Get sequences of those regions
    safe_harbors_bed.sequence(fi="data/fixed_Danio_rerio.GRCz11.dna.primary_assembly.fa", fo="Safe_harbors.fasta")

if __name__ == "__main__":
    main()