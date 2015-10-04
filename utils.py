import csv
from keys import *

def read_surfers(f):
    res = {}
    surfer_reader = csv.DictReader(f, delimiter=';')
    for row in surfer_reader:
        key = '{} {}'.format(row['first_name'], row['last_name'])
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
    text_format = workbook.add_format({'align': 'right', 'num_format': '#,##0.00', 'font_color': 'blue'})
    number_format = workbook.add_format({'num_format': '#,##0.00', 'font_color': 'blue'})
    judge_id_format = workbook.add_format({'num_format': '#,##0', 'font_color': 'blue'})
    headline_format = workbook.add_format({'bold': True, 'font_color': 'blue', 'bottom': True})
    headcol_format = workbook.add_format({'bold': True, 'font_color': 'blue'})

    highlighted_number_format = workbook.add_format({'num_format': '#,##0.00', 'font_color': 'blue', 'border': True, 'bg_color': '#DDDDDD'})

    for mode, d in data.items():
        sheet = workbook.add_worksheet(mode)
        header = d['header']
        sheet_data = d['data']
        highlight_cells = d.get('highlights', {})

        for idx, field in enumerate(header):
            sheet.write(0, idx, field, headline_format)

        for row_idx, row_data in enumerate(sheet_data):
            high = highlight_cells.get(row_data['color'], {}).get(row_data['judge_id'], [])

            for col_idx, field in enumerate(header):
                if col_idx == 0:
                    val = row_data.get(field)
                    f = headcol_format
                elif col_idx == 1:
                    val = row_data.get(field)
                    try:
                        val = int(val)
                    except:
                        pass
                    f = judge_id_format
                else:
                    val = row_data.get(field)
                    if val is not None:
                        if val == VAL_MISSED:
                            val = 'M'
                            f = text_format
                        else:
                            try:
                                val = float(val)
                            except:
                                pass
                            if field in high:
                                f = highlighted_number_format
                            else:
                                f = number_format
                sheet.write(row_idx+1, col_idx, val, f)


    workbook.close()
