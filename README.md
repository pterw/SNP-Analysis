This is a work-in-progress bioinformatic tool that aims to take the raw txt file from your 23andme account and analyze the SNPs via the NIH.

It also aims to categorize an SNP as "positive" "neutral" "negative", so, an SNP leading to a deficiency of triiodide would be classified as "negative". One that has no tangible effects is neutral, one leading to higher muscle mass is positive,  etc. 

As of 2024-07-26 the categorization is not yet robustly defined nor implemented.

The code requires optimization as to not make too many API calls and should be optimized via multiprocessing to speed it up (for what little it can do, it's slow.)
