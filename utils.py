import csv
from keys import *


def utf_8_encoder(unicode_csv_data):
    lines = unicode_csv_data.readlines()
    for line in lines:
        res = line.encode('utf-8').rstrip('\n')
        yield res

def UnicodeDictReader(utf8data, **kwargs):
    csv_reader = csv.DictReader(utf8data, **kwargs)
    for row in csv_reader:
        yield {key: value.decode('utf-8') for key, value in row.iteritems()}

def read_surfers(f, decode=None):
    res = {}
    if decode=='utf-8':
        surfer_reader = UnicodeDictReader(f, delimiter=';')
    else:
        surfer_reader = csv.DictReader(f, delimiter=';')
    for row in surfer_reader:
        print row
        key = u'{} {}'.format(row['first_name'], row['last_name'])
        row['name'] = key
        row['country'] = 'Germany'
        res.setdefault(key, row)
    return res

def read_lycra_colors(filename):
    res = {}
    with open(filename, 'rb') as fp:
        colors = csv.DictReader(fp, delimiter=';')
        for row in colors:
            res.setdefault(row['COLOR'], row)
    return res


def write_csv(filename, data, header):
    from csv import DictWriter
    with open(filename, 'wb') as fp:
        writer = DictWriter(fp, fieldnames=header, delimiter=';')
        writer.writeheader()
        writer.writerows(data)
    return



def write_xlsx(filename, data):
    import xlsxwriter

    workbook = xlsxwriter.Workbook(filename)

    # TEXT blau
    formats = {
        'text': workbook.add_format({'align': 'right', 'num_format': '#,##0.00', 'font_color': 'blue'}),
        'number': workbook.add_format({'num_format': '#,##0.00', 'font_color': 'blue'}),
        'judge_id': workbook.add_format({'num_format': '#,##0', 'font_color': 'blue'}),
        'headline': workbook.add_format({'bold': True, 'font_color': 'blue', 'bottom': True}),
        'headcol': workbook.add_format({'bold': True, 'font_color': 'blue'}),

        'highlighted_number': workbook.add_format({'num_format': '#,##0.00', 'font_color': 'blue', 'border': True, 'bg_color': '#DDDDDD'}),
    }

    for mode, d in data.items():
        sheet = workbook.add_worksheet(mode)
        if mode == 'averaged_scores':
            _write_final_score_sheet(d, sheet, formats)
        else:
            _write_default_data_sheet(d, sheet, formats)

    workbook.close()


def _write_final_score_sheet(d, sheet, formats):
    placing = dict(enumerate(['1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th']))
    header = d['header']
    sheet_data = d['data']

    sheet.write(0, 0, d.get('title_line'), formats['headline'])

    for idx, field in enumerate(header):
        sheet.write(1, idx, field, formats['headline'])


    sheet.set_column(1, 1, 25)
    sheet.set_column(3, 5, 10)
    for row_idx, row_data in enumerate(sheet_data):

        for col_idx, field in enumerate(header):
            if col_idx == 0:
                val = placing.get(row_data.get('Ranking', ''))
                f = formats['headcol']
            elif col_idx == 1:
                val = row_data.get(field)
                f = formats['headcol']
            else:
                val = row_data.get(field)
                f = formats['number']
                if val is not None:
                    if val == VAL_MISSED:
                        val = 'M'
                        f = formats['text']
                    else:
                        try:
                            val = float(val)
                        except:
                            pass
            sheet.write(row_idx+2, col_idx, val, f)
    return


def _write_default_data_sheet(d, sheet, formats):
    header = d['header']
    sheet_data = d['data']
    highlight_cells = d.get('highlights', {})

    sheet.write(0, 0, d.get('title_line'), formats['headline'])

    sheet.set_column(0, 0, 25)
    for idx, field in enumerate(header):
        sheet.write(1, idx, field, formats['headline'])

    for row_idx, row_data in enumerate(sheet_data):
        high = highlight_cells.get(row_data['Color'], {}).get(row_data['Judge Id'], [])

        for col_idx, field in enumerate(header):
            if col_idx == 0:
                val = row_data.get(field)
                f = formats['headcol']
            elif field == 'Judge Id':
                val = row_data.get(field)
                f = formats['judge_id']
                try:
                    val = int(val)
                except:
                    pass
            else:
                val = row_data.get(field)
                f = formats['number']
                if val is not None:
                    if val == VAL_MISSED:
                        val = 'M'
                        f = formats['text']
                    else:
                        try:
                            val = float(val)
                        except:
                            pass
                        if field in high:
                            f = formats['highlighted_number']
            sheet.write(row_idx+2, col_idx, val, f)
    return
