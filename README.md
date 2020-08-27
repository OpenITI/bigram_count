# bigram_count

This script creates a list of all theoretically possible bigrams of Arabic letters
and counts how often these bigrams occur in the OpenITI corpus. 

This may be useful for spotting typos in our texts, 
and especially post-correction of OCR'ed files.

The script creates the following outputs: 

* bigram_count.json: a dictionary in which the keys are the bigrams, and the values the number of times each bigram is attested in our corpus
* freq_matrix.tsv: a tsv file of the frequency matrix
* freq_heatmap.html: the frequency matrix formatted as a heatmap in an html document.
