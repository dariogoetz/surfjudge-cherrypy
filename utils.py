import csv

def read_surfers(filename):
    res = {}
    with open(filename, 'rb') as fp:
        surfer_reader = csv.DictReader(fp, delimiter=';')
        for row in surfer_reader:
            res.setdefault(int(row['id']), row)
    return res

def read_lycra_colors(filename):
    res = {}
    with open(filename, 'rb') as fp:
        colors = csv.DictReader(fp, delimiter=';')
        for row in colors:
            res.setdefault(row['COLOR'], row)
    return res
