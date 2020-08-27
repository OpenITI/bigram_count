"""Count all bigrams in all texts in a folder and its subfolders.
Save bigram counts in json file.
Format as a matrix and as a heatmap in an html file.
"""


import os
import json
import math
import seaborn as sns
from statistics import median

exclude_folders = ["OpenITI.github.io", "Annotation", "maintenance",
                   "i.mech00", "i.mech01", "i.mech02", "i.mech03",
                   "i.mech04", "i.mech05", "i.mech06", "i.mech07",
                   "i.mech", "i.mech_Temp", "i.mech08", "i.mech09",
                   "i.logic", "i.cex", "i.cex_Temp", ".git"]

exclude_files = ["README.md", ".DS_Store",
                 ".gitignore", "text_questionnaire.md"]

def create_bigram_dict(json_fp, alph):
    """Create a dictionary that has all combinations of letters in `alph`\
    as keys, and 0 as values"""
    bigrams = dict()
    for i in range(len(alph)):
        for j in range(len(alph)):
            bigrams[alph[i]+alph[j]] = 0
    with open(json_fp, mode="w", encoding="utf-8") as file:
        json.dump(bigrams, file, ensure_ascii=False, indent=4)
    return bigrams

def count_bigrams_in_file(fp, bigrams):
    """Count all bigrams in a file and add the counts to the bigrams dictionary"""
    with open(fp, mode="r", encoding="utf-8") as file:
        text = file.read()
    for i in range(len(text) - 1):
        if text[i:i+2] in bigrams:
            bigrams[text[i:i+2]] += 1

def walk_text_files(start_folder):
    """Generator that yields all OpenITI text files in `start_folder`\
    and its subfolders"""
    for root, dirs, files in os.walk(start_folder):
        dirs[:] = [d for d in dirs if d not in exclude_folders]
        files[:] = [f for f in files if f not in exclude_files]
        for fn in files:
            if re.findall(r"-\w\w\w\d(?:.inProgress|completed|mARkdown)?\Z", fn):
                fp = os.path.join(root, fn)
                yield(fp)

def count_bigrams_in_folder(start_folder, bigrams):
    """Count all bigrams in all files in `start_folder` and its subfolders"""
    for fp in walk_text_files(start_folder):
        print(fp)
        count_bigrams_in_file(fp, bigrams)
        with open(json_fp, mode="w", encoding="utf-8") as file:
            json.dump(bigrams, file, ensure_ascii=False, indent=4, sort_keys=True)
            

def make_freq_matrix(bigrams):
    """Create a frequency matrix from the bigrams dictionary

    Args:
        bigrams (dict): key: bigram, val: count
    Returns:
        (list): matrix in which each cell is a tuple (bigram, count)
    """
    matrix = []
    #print("\t"+"\t".join([letter for letter in alph]))
    for i in range(len(alph)):
        row = []
        for j in range(len(alph)):
            bigram = alph[i]+alph[j]
            row.append((bigram, bigrams[bigram]))
        matrix.append(row)
        #print(alph[i]+"\t"+("\t".join(row)))
    return matrix

def get_boundaries(bigrams):
    """Get the minimum and maximum values in the bigrams dictionary

    Args:
        bigrams (dict): key: bigram, val: count
    """
    max_val = sorted(bigrams.items(), key=lambda x: x[1])[-1][1]
    min_val = sorted(bigrams.items(), key=lambda x: x[1])[0][1]
    return max_val, min_val
        

def define_class(n, q, cut_off_min=1000):
    """Define the css class of an bigram count based on its log value

    Args:
        n (int): number of times an bigram is in the corpus
        q (int): value through which `n` must be divided to be assigned to a
            frequency bucket
        cut_off_min (int): if an bigram occurs less than `cut_off_min` times,
            it will be assigned to bucket 0;
            if cut_off_min is set to None, only the log value will
            define the bucket into which the n-gram will be assigned"""
    #return "b{}".format(math.floor(int(n)/q))
    if cut_off_min:
        if n < cut_off_min:
            return "b0"
    return "b{}".format(math.floor(math.log(n+1)/q)) # use n+1 because log(0) does not exist

def create_heatmap(matrix, max_val, min_val, buckets=10, cut_off_min=1000):
    """Format the matrix as an html table (with bigram count in tooltip)

    Args:
        matrix (list): a frequency matrix expressed in a list of lists
            (each cell contains a (bigram, count) tuple)
        max_val (int): the largest value in the matrix
        min_val (int): the smallest value in the matrix
        buckets (int): the number of buckets (colours) to be used
    """
    # define the value through which the number of results must be
    # divided to be assigned a frequency bucket:
    q = (max_val-min_val)/buckets
    q = (max_val+1) / buckets
    # or better: use logarithmic scale:
    max_log = math.log(max_val)
    print("max_log:", max_log)
    q = (max_log + 1) / buckets
    print("q:", q)

    # build table:
    table = '<table>\n  <tr>\n'
    for letter in " "+alph:
        table += "    <th>{}</th>\n".format(letter)
    table += '  </tr>\n'
    for i, row in enumerate(matrix):
        tr = '  <tr>\n    <th>{}</th>\n'.format(alph[i])
        for c in row:
            c_class = define_class(c[1], q, cut_off_min)
##            tr_fmt = '    <td class="{}">{}<br/>{}</td>\n'
##            tr += tr_fmt.format(c_class, c[0], c[1])
            tooltip = '<span class="tooltip">{:,}</span>'.format(c[1])
            tr_fmt = '    <td class="{}">{}\n      {}\n    </td>\n'
            tr += tr_fmt.format(c_class, c[0], tooltip)
        table += tr + "  </tr>\n"
    return table + '</table>'

def create_css(buckets=10, cut_off_min=1000, palette="YlOrBr"):
    """Create the css style sheet for the table

    Args:
        buckets (int): the number of buckets (colours) to be used
        palette (str): the name of the seaborn color palette to be used
    """
    tooltip = '''\
    td {
      width: 20px;
      height: 20px;
    }

    td .tooltip {
      visibility: hidden;
      width: 120px;
      background-color: black;
      color: #fff;
      text-align: center;
      padding: 5px 0;
      border-radius: 6px;
      position: absolute;
      z-index: 1;
    }

    td:hover .tooltip {
      visibility: visible;
    }\n'''
    style = '  <style>\n' + tooltip
    style += '''
    table {
      border-collapse: collapse;
    }
'''
    style += '''
    .b0 {
      background-color: #ffffff;
    }\n'''
    pal = sns.color_palette(palette, buckets-1)
    for i, col in enumerate(pal.as_hex()):
        print(i, col)
        style += '''
    .b%s {
      background-color: %s;
    }\n''' % (i+1, col)
    return style + "  </style>"
    
def compute_bucket_values(buckets, cut_off_min, max_val, log_base=math.e):
    max_log = math.log(max_val, log_base)
    print("max_log:", max_log)
    q = (max_log + 1) / buckets
    bucket_min_vals = []
    for b in range(buckets):
        bucket_min_vals.append(int((log_base**(b*q))-1))
    return bucket_min_vals
        
    

def make_scale_bar(buckets, palette, cut_off_min, min_val, max_val):
    """Create a scale bar for the color palette used."""
    pal = sns.color_palette(palette, buckets-1)
    bar = '''\
<table>
  <tr>
    <td class="b0">{}-{}</td>
    <td class="b0"> </td>
'''.format(min_val, cut_off_min)
    b = compute_bucket_values(buckets, cut_off_min, max_val, log_base=math.e)
    fmt = "{:,}-{:,}"
    #bucket_values = [fmt.format(b[i], b[i+1]) for i in range(len(b[:-1]))]
    #bucket_values.append(fmt.format(b[-1], max_val+1))
    bucket_values = [(b[i], b[i+1]) for i in range(len(b[:-1]))]
    bucket_values.append((b[-1], max_val))
    for i, b in enumerate(bucket_values):
        print(i, b)
    for i, col in enumerate(pal.as_hex()):
        tooltip = '<span class="tooltip">{:,}-{:,}</span>'
        tooltip = tooltip.format(bucket_values[i+1][0], bucket_values[i+1][1])
        bar += '    <td class="b{}">{}</td>\n'.format(i+1, tooltip)
    bar += '    <td class="b{}">{:,}</td>\n'.format(i+1, max_val)
    return bar + "</table>\n"

def save_as_html_table(matrix, max_val, min_val, cut_off_min, buckets, palette,
                       title, outfp):
    """Save the frequency matrix as a table in an html file."""
    table = create_heatmap(matrix, max_val, min_val,
                           cut_off_min=cut_off_min, buckets=buckets)
    scale_bar = make_scale_bar(buckets, palette, cut_off_min, min_val, max_val)
    style = create_css(buckets=buckets, cut_off_min=cut_off_min)
    #print(table)
    html = '''\
    <html>
    <header>
    {}
    </header>
    <body>
    <h1>{}</h1>
    {}
    <p>corrected logarithmic scale (minimum cutoff point: {})</p>
    {}
    </body>
    </html>'''.format(style, title, table, cut_off_min, scale_bar)
    with open(outfp, mode="w", encoding="utf-8") as file:
        file.write(html)


###############################################
#######            CONFIG          ############
###############################################    

start_folder = r"D:\London\OpenITI\25Y_repos"
json_fp = "bigram_count.json"
alph = "اإأآبتثجحخدذرزسشصضطظعغفقكلمنهويىؤءئة"
buckets = 10
palette = "YlOrBr"
cut_off_min = 1000
outfp = "freq_table.html"
html_title = "Bi-gram frequencies in the OpenITI corpus"

###############################################

#bigrams = create_bigram_dict(json_fp, alph=alph)
#count_bigrams_in_folder(start_folder, bigrams)
with open(json_fp, mode="r", encoding="utf-8") as file:
    bigrams = json.load(file)

matrix = make_freq_matrix(bigrams)
max_val, min_val = get_boundaries(bigrams)
print(max_val, min_val)
save_as_html_table(matrix, max_val, min_val, cut_off_min, buckets, palette,
                   html_title, outfp)
            

    
