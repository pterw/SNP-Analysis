from Bio import Entrez
import csv
import os
import time
import random
from concurrent.futures import ThreadPoolExecutor
import traceback
import xml.etree.ElementTree as ET
import pandas as pd
from pathlib import Path

print("Script started")

Entrez.email = "peter.wiercioch@gmail.com"  # Always tell NCBI who you are

def read_23andme_file(file_path):
    print(f"Reading file: {file_path}")
    snps = []
    with open(file_path, 'r') as file:
        for i, line in enumerate(file):
            if not line.startswith('#'):
                parts = line.strip().split()
                if len(parts) == 4:
                    rsid, chromosome, position, genotype = parts
                    snps.append((rsid, chromosome, position, genotype))
                if i == 100:  # Only read the first 100 SNPs for testing
                    break
    print(f"Read {len(snps)} SNPs")
    return snps

def get_snp_info(rsid):
    print(f"Fetching info for SNP: {rsid}")
    max_retries = 3
    for attempt in range(max_retries):
        try:
            time.sleep(random.uniform(1, 2))  # Random delay between 1 and 2 seconds
            handle = Entrez.esummary(db="snp", id=rsid)
            response = handle.read().decode('utf-8')
            
            root = ET.fromstring(response)
            clinical_significance = root.find(".//CLINICAL_SIGNIFICANCE")
            if clinical_significance is not None:
                return clinical_significance.text
            else:
                return 'No known implications'
        except ET.ParseError as e:
            print(f"XML parsing error for {rsid}: {str(e)}")
            return 'Error parsing XML'
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Attempt {attempt + 1} failed for {rsid}. Retrying...")
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            print(f"Error fetching info for {rsid}: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            return f'Error fetching information: {str(e)}'

def process_snp(snp):
    rsid, chromosome, position, genotype = snp
    implications = get_snp_info(rsid)
    return [rsid, chromosome, position, implications]

def analyze_snps(file_path):
    print("Starting SNP analysis")
    file_path = file_path.strip().strip('"')
    file_path = os.path.normpath(file_path)
    
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {file_path} does not exist.")
        
        snps = read_23andme_file(file_path)
    except FileNotFoundError as e:
        print(f"File not found. Error: {str(e)}")
        return
    except Exception as e:
        print(f"An error occurred while reading the file: {str(e)}")
        return

    print("Processing SNPs... This may take a while.")
    
    results = []
    with ThreadPoolExecutor(max_workers=2) as executor:  # Further reduced number of workers
        results = list(executor.map(process_snp, snps))

    print("Finished processing SNPs")

    # Save the file to the user's Downloads folder
    downloads_path = str(Path.home() / "Downloads")
    output_file = os.path.join(downloads_path, 'snp_analysis_results.csv')
    
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['SNP', 'Chromosome', 'Position', 'Implications'])
        writer.writerows(results)
    
    print(f"Analysis complete. Results have been saved to {output_file}")
    print("\nHere's a preview of the results:")
    for row in results[:5]:
        print(f"SNP: {row[0]}, Chromosome: {row[1]}, Position: {row[2]}, Implications: {row[3]}")

    # Display results in a table format using pandas
    df = pd.DataFrame(results, columns=['SNP', 'Chromosome', 'Position', 'Implications'])
    print(df.head())
    return df

# Set your file path here
file_path = r"C:\Users\peter\OneDrive\Documents\__Important_Docs\Health\genome_Peter_Wiercioch_v5_Full_20211125094157.txt"

print("File path set")

# Run the analysis
print("Starting analysis")
df = analyze_snps(file_path)
print("Analysis function called")