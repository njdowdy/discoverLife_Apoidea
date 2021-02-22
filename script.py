import pandas as pd
import re

names_file = 'input/bee_names.csv'
output_file = 'output/bee_names_extracted.csv'
name_list = []

data = pd.read_csv(names_file, header=None)

name = {}  # each name will be a dictionary
names = []  # all name dictionary will be stored in a list
name_id = 1

for line in data[0]:
    if '\xa0' in line:
        #  -- : denotes start of synonyms
        #  ; : separates synonyms
        parsed = line.replace('\xa0', ' ')
        # ! parsed = parsed.replace(' ('+parsed.split(' ')[3]+') ', ' ')  # remove parent genus flag
        # ABOVE SHOULD BE CAPTURED AS SUBGENUS I THINK
        parent_id = name_id
        if '--' in line:
            pub = ' '.join(parsed.split('--')[0].split(' ')[5:]).strip().replace(')', '').replace('(', '')
        else:
            pub = ' '.join(parsed.split(' ')[-2:])
        # [x.replace(',', '') for x in pub.split(' ') if x != 'and']  # not using this right now
        if len(pub.split(' ')) > 4:
            pub = ' '.join([x.replace(',', '') + ',' if x != 'and' else x for x in pub.split(' ')])[
                  0:-1]  # insert oxford comma
        name = {
            'name_id': name_id,
            'parent_id': parent_id,
            'status': 'accepted',
            'accepted_genus': parsed.split(' ')[3],
            'accepted_species': parsed.split(' ')[4],
            'subgenus': '',
            'genus': parsed.split(' ')[3],
            'species': parsed.split(' ')[4],
            'accepted_canonical_name': ' '.join(parsed.split(' ')[3:5]),
            'canonical_name': ' '.join(parsed.split(' ')[3:5]),
            'publication': pub
        }
        name_id += 1
        names.append(name)
        synonyms = parsed.split('--')[1:]
        for syn in synonyms:

            syn_len = len(syn.strip().split(' '))
            if syn_len == 1:
                canon = syn.strip().split(' ')[0]
                spec = ''
                pub = ''
            elif syn_len == 2:
                canon = ' '.join(syn.strip().split(' ')[0:2])
                spec = syn.strip().split(' ')[1]
                pub = ''
            elif syn_len > 2:
                canon = ' '.join(syn.strip().split(' ')[0:2])
                spec = syn.strip().split(' ')[1]
                pub = ' '.join(syn.strip().split(' ')[2:])
                if len(pub.split(' ')) > 4:
                    pub = ' '.join([x.replace(',', '') + ',' if x != 'and' else x for x in pub.split(' ')])[
                          0:-1]  # insert oxford comma
            name = {
                    'name_id': name_id,
                    'parent_id': parent_id,
                    'status': 'synonym',
                    'accepted_genus': parsed.split(' ')[3],
                    'accepted_species': parsed.split(' ')[4],
                    'subgenus': '',
                    'genus': syn.strip().split(' ')[0],
                    'species': spec,
                    'accepted_canonical_name': ' '.join(parsed.split(' ')[3:5]),
                    'canonical_name': canon,
                    'publication': pub
            }
            name_id += 1
            names.append(name)

# write out
out = pd.DataFrame(names)
out.to_csv(output_file)
