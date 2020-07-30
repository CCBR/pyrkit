
from __future__ import print_function, division
import sys, os, re
import pandas as pd

# Configuration for defining valid files, cleaning sample names, parse fields, rename fields
# Add new files to parse and define their specifications below
config = {
    ".warning": ["\033[93m", "\033[00m"], ".error": ["\033[91m", "\033[00m"],

	"multiqc_cutadapt.txt": {
        "delimeter": "\t",
		"clean_sample_name": [".R1$", ".R2$"],
		"parse_column": ["Sample", "pairs_processed"],
		"rename_field": {
			"pairs_processed": "total_read_pairs"
		},
        "typecast": {
            "total_read_pairs": int
        }
	},

	"multiqc_fastqc.txt": {
        "delimeter": "\t",
		"clean_sample_name": ["^QC \\| ", "^rawQC \\| ", ".trim$", ".R1$", ".R2$"],
        "collapse": True,
		"parse_column": ["Sample", "Encoding", "Total Sequences", "Sequence length", "%GC", "avg_sequence_length"],
		"rename_field": {
			"Total Sequences": "trimmed_read_pairs",
			"Sequence length": "sequence_length",
            "%GC": "gc_content",
		},
        "typecast": {
            "trimmed_read_pairs": int,
            "avg_sequence_length": float
        }
	},

	"multiqc_fastq_screen.txt": {
        "delimeter": "\t",
		"clean_sample_name": ["^FQscreen \\| ", "^FQscreen2 \\| ", "_screen$", ".trim$", ".R1$", ".R2$"],
		"parse_column": ["Sample", "Uni_Vec percentage", "rRNA percentage", "Human percentage", "Mouse percentage", "Bacteria percentage", "Fungi percentage", "Virus percentage"],
		"rename_field": {
			"Uni_Vec percentage": "uni_vec_percent_aligned",
			"rRNA percentage": "rRNA_percent_aligned",
            "Human percentage": "human_percent_aligned",
            "Mouse percentage": "mouse_percent_aligned",
            "Bacteria percentage": "bacteria_percent_aligned",
            "Fungi percentage": "fungi_percent_aligned",
            "Virus percentage": "virus_percent_aligned"
		},
        "typecast": {
            "uni_vec_percent_aligned": float,
            "rRNA_percent_aligned": float,
            "human_percent_aligned": float,
            "mouse_percent_aligned": float,
            "bacteria_percent_aligned": float,
            "fungi_percent_aligned": float,
            "virus_percent_aligned": float
        }
	},

	"multiqc_picard_dups.txt": {
        "delimeter": "\t",
		"clean_sample_name": [".p2$"],
		"parse_column": ["Sample", "PERCENT_DUPLICATION"],
		"rename_field": {
			"PERCENT_DUPLICATION": "percent_duplication"
		},
        "typecast": {
            "percent_duplication": float
        }
	},

	"multiqc_picard_RnaSeqMetrics.txt": {
        "delimeter": "\t",
		"clean_sample_name": [".p2$"],
		"parse_column": ["Sample", "PCT_CODING_BASES", "PCT_MRNA_BASES", "MEDIAN_CV_COVERAGE", "PCT_INTRONIC_BASES", "MEDIAN_3PRIME_BIAS", "MEDIAN_5PRIME_BIAS", "MEDIAN_5PRIME_TO_3PRIME_BIAS", "PCT_INTERGENIC_BASES", "PCT_UTR_BASES"],
		"rename_field": {
			"PCT_CODING_BASES": "pct_coding_bases",
			"PCT_MRNA_BASES": "pct_mrna_bases",
			"MEDIAN_CV_COVERAGE": "median_cv_coverage",
			"PCT_INTRONIC_BASES": "pct_intronic_bases",
			"MEDIAN_3PRIME_BIAS": "median_3prime_bias",
			"MEDIAN_5PRIME_BIAS": "median_5prime_bias",
			"MEDIAN_5PRIME_TO_3PRIME_BIAS": "median_5prime_to_3prime_bias",
			"PCT_INTERGENIC_BASES": "pct_intergenic_bases",
			"PCT_UTR_BASES": "pct_utr_bases"
		},
        "typecast": {
            "pct_coding_bases": float,
            "pct_mrna_bases": float,
            "median_cv_coverage": float,
            "pct_intronic_bases": float,
            "median_3prime_bias": float,
            "median_5prime_bias": float,
            "median_5prime_to_3prime_bias": float,
            "pct_intergenic_bases": float,
            "pct_utr_bases": float
        }
	},

	"multiqc_rseqc_infer_experiment.txt": {
        "delimeter": "\t",
		"clean_sample_name": ["^RSeQC \\| ", ".strand.info$",".info.strand$", "^output.", ".p2$"],
		"parse_column": ["Sample", "pe_sense", "pe_antisense"],
		"rename_field": {
			"pe_sense": "percent_sense_strand",
			"pe_antisense": "percent_antisense_strand"
		},
        "typecast": {
            "percent_sense_strand": float,
            "percent_antisense_strand": float
        }
	},

	"multiqc_star.txt": {
        "delimeter": "\t",
		"clean_sample_name": [".p2$"],
		"parse_column": ["Sample", "uniquely_mapped_percent", "avg_input_read_length"],
		"rename_field": {
			"uniquely_mapped_percent": "percent_aligned",
			"avg_input_read_length": "avg_aligned_read_length"
		},
        "typecast": {
            "percent_aligned": float,
            "avg_aligned_read_length": int
        }
	},

	"multiqc_qualimap_bamqc_genome_results.txt": {
        "delimeter": "\t",
		"clean_sample_name": [".p2$"],
		"parse_column": ["Sample", "mean_insert_size", "median_insert_size", "mean_mapping_quality", "mean_coverage"],
		"rename_field": {},
        "typecast": {
            "mean_insert_size": float,
            "median_insert_size": float,
            "mean_mapping_quality": float,
            "mean_coverage": float
        }
	}
}


def help():
        return """
        USAGE:
            python rnaseq_qc_table.py <file_1> <file_2> <file_3> <file_N> [-h]

            Positional Arguments:
                [1...N]       Type [File]: An output file from MultiQC, or a list of
                                           output files generated from MultiQC. Each provided
                                           file is parsed, and information is aggregated
                                           across all samples into a single tab-seperated
                                           ouput file: multiqc_matrix.txt
            Supported MultiQC Files:
            multiqc_cutadapt.txt, multiqc_star.txt, multiqc_picard_dups.txt,
            multiqc_fastq_screen.txt, multiqc_picard_RnaSeqMetrics.txt,
            multiqc_fastqc.txt, multiqc_rseqc_infer_experiment.txt,
            multiqc_qualimap_bamqc_genome_results.txt

            Optional Arguments:
                [-h, --help]  Displays usage and help information for the script.

            Example:
                # Creates QC table: multiqc_matrix.txt
                $ python rnaseq_qc_table.py multiqc_cutadapt.txt multiqc_fastqc.txt multiqc_fastq_screen.txt multiqc_picard_dups.txt
                > multiqc_matrix.txt

            Requirements:
                multiqc == 1.9
                python >= 2.7
        """


def args(argslist):
    """Parses command-line args from "sys.argv". Returns a list of filenames to parse."""
    # Input list of filenames to parse
    files = argslist[1:]

    # Check for optional args
    if '-h' in files or '--help' in files:
        print(help())
        sys.exit(0)
    # Check to see if user provided input files to parse
    elif not files:
        print("\n{}Error: Failed to provide input files to parse!{}".format(*config['.error']), file=sys.stderr)
        print(help())
        sys.exit(1)

    return files


def isvalid(file):
    """Checks if a file is a recognized/supported file to parse.
    Comparse file's name against list of supported files in config specification"""

    # Supported files are keys in config
    supported = config.keys()

    # Remove absolute or relateive PATH
    if os.path.basename(file) not in supported:
        cstart, cend = config['.warning']
        print("{}Warning:{} {} is a not supported file to parse... Skipping over file!".format(cstart, cend, file))
        return False

    return True


def exists(file):
    """Checks to see if file exists or is accessible.
    Avoids problem with inconsistencies across python2.7 and >= python3.4 and
    works in both major versions of python"""

    try:
        fh = open(file)
        fh.close()
    # File cannot be opened for reading (may not exist) or permissions problem
    except IOError:
        cstart, cend = config['.warning']
        print("{}Warning:{} Cannot open {}... File may not exist... Skipping over file!".format(cstart, cend, file))
        return False

    return True


def column_indexes(line, filename, verbose=True):
    """Parses header of file to find fields of interest defined in config[filename][parse_column]
    Returns a list of integers corresponding to an index of a column to parse."""

    indices = []
    found = []
    header = line
    # Remove file's PATH before cross-referencing config
    filename = os.path.basename(filename)
    fields2parse = config[filename]["parse_column"] # Attributes or columns of interest

    # Get index of column to parse
    for i in range(0, len(header), 1):
        if header[i] in fields2parse:
            indices.append(i)
            found.append(header[i])

    if verbose:
        # Warning that an expected field could not be found
        fields_not_found = set(fields2parse) - set(found)
        for field in fields_not_found:
            cstart, cend = config['.warning']
            print("{}Warning:{} Cannot find expected field '{}' in {}... skipping over parsing that field!".format(cstart, cend, field, filename))

    return indices


def clean(linelist, sample_name_index, filename):
    """Cleans sample name from suffixes defined in config[filename]['clean_sample_name'] and
    renames fields defined in config[filename]['rename_field']. Returns a list of cleaned fields."""

    samplename = linelist[sample_name_index]

    # Remove file's PATH before cross-referencing config
    filename = os.path.basename(filename)
    for suffix in config[filename]['clean_sample_name']:
            regex = '{}'.format(suffix)
            samplename = re.sub(regex, '', samplename)

    # Update linelist with new sample name
    linelist[sample_name_index] = samplename

    return linelist


def rename(header, filename):
    """Renames fields defined in config[filename]['rename_field']. Returns a list of re-named columns."""
    renamed = []
    for field in header:
        try:
            newname = config[filename]['rename_field'][field]
            renamed.append(newname)
        # Field is not in config, keep old name
        except KeyError:
            renamed.append(field)
    return renamed

def cast_type(value, column, filename, decimals=3):
    """Cast types data in a row/column according to specification in config[filename]["typecast"][column_name].
    Converts string to either an integer or float (rounded to three decimal places).
    """
    try:
        # Python witch-craft, functions are first-class objects and can be used accordingly
        # Storing function object into caster variable for typecasting as int() or float()
        caster = config[filename]["typecast"][column]
        value = caster(value)        # typecast to spec defined in config
        if type(value) is float:
            value = round(value, decimals)
    except ValueError:
        # Must convert to float before converting to integer
        # cannot pass a string representation of a float into int()
        if value: # case for when row/column is empty string
            value = caster(float(value))
    except KeyError:
        # No type is defined in config, pass
        pass
    return value


def populate_table(parsed_header, parsed_line, file, data_dict):
    """Appends parsed sample metadata to a nested dictionary where
    dictionary['Sample_Name']['QC_Attribute'] = QC_Metadata.
    Returns an updated dictionary containing new information for N-th line."""

    sample_index = parsed_header.index('Sample')
    sample_name = parsed_line[sample_index]

    # Add sample name to dictionary, if does not exist [key1]
    if parsed_line[sample_index] not in data_dict:
        data_dict[sample_name] = {}

    for i in range(0, len(parsed_line), 1):
        # Skip over sample name (already first key)
        if parsed_line[i]: # check if empty string
            metadata = cast_type(parsed_line[i], parsed_header[i], file)
            data_dict[sample_name][parsed_header[i]] = metadata

    return data_dict


def parsed(file, delimeter='\t'):
    """Parses columns of file according to specification in config[filename]['parse_column'].
    Column names are renamed according to specification in config[filename]['rename_field'].
    Sample names are cleaned to removed any prefixes or suffixes specified in config[filename]['clean_sample_name'].
    Yields a tuple consisting of the parsed header and N-th parsed line of the file.
    """

    #print('\nBeginning to parse {}'.format(file))
    with open(file, 'r') as fh:
        # Parse header
        header = next(fh).strip().split(delimeter) # Get file header
        indexes = column_indexes(header, file)     # Indexes of columns to parse
        header = [header[i] for i in indexes]  # Parse each column of interest
        header = rename(header, file)   # Rename columns

        # Parse QC metadata from file
        sample_index = header.index('Sample')
        for line in fh:
            #linelist = line.strip().split(delimiter)
            linelist = line.rstrip('\n').split(delimeter)
            parsed_line = [linelist[i] for i in indexes]
            parsed_line = clean(parsed_line, sample_index, file) # remove extensions from sample name

            yield header, parsed_line


def main():

    # Todo:
    #       1. Add ability to split a file before parsing (i.e. FastQC file)
    #       2. Add ability to scale a defined field (add `scaling_factor` to config
    #       3. Add a perferred output sorting mechanism
    #       4. Get rid of pandas dependency, add transpose function and loop through dict to print table
    #       5. Add more advanced argument parsing

    # Check for usage and optional arguements, get list of files to parse
    ifiles = args(sys.argv)

    # Check if files are supported, see config specification, and if file is readable
    ifiles = [file for file in ifiles if isvalid(file) and exists(file)]

    # Parse each file and add to the QC metadata dicitionary
    QC = {}
    for file in ifiles:
        for header, line in parsed(file):
            QC = populate_table(header, line, file, QC)

    df = pd.DataFrame(QC).transpose()

    # Write to file
    df.to_csv('multiqc_matrix.txt', index = False, sep='\t')


if __name__ == '__main__':

    main()
