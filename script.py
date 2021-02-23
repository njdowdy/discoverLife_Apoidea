import pandas as pd
import re

names_file = 'input/bee_names.csv'
output_file = 'output/bee_names_extracted.csv'
name_list = []

data = pd.read_csv(names_file, header=None)

# this line is broken in the input file; requires manual fix
data[0][1401] = '\xa0\xa0\xa0Andrena takachihoi\xa0Hirashima, 1964, emend.\xa0--\xa0Andrena (Euandrena) takachihsi\xa0Hirashima, 1964, incorrect original spelling in species heading'

# define custom functions

def contains_capital(mystring):
    return re.findall(r'[A-Z]', mystring)


def pub_parser(mypub):
    year_start = re.search(r'[0-9]', mypub)
    if year_start:
        author_string = mypub[0:year_start.span()[0]]
        year = mypub[year_start.span()[0]:].split(',')[0]
        extras = [x.strip() for x in year.split(',')[1:]]
    else:
        author_string = mypub
        year = ''
        extras = ''
    if len(extras) == 0:
        extras = ''
    elif len(extras) == 1:
        extras = extras[0]
    else:
        extras = '; '.join(extras)
    return {'extras': extras,
            'authors': author_string,
            'year': year}


def oxford_comma(mypub):
    if len(mypub.split(' ')) > 4:
        return ' '.join([x.replace(',', '') + ',' if x != 'and' else x for x in mypub.split(' ')])[
               0:-1]  # insert oxford comma
    else:
        return mypub


# define temp structures and variables
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
        genus1 = [x for x in parsed.split(' ') if x][0]
        species1 = [x for x in parsed.split(' ') if x][1]
        if '--' in line:
            pub1 = ' '.join([x for x in parsed.split('--')[0].split(' ') if x][2:]). \
                strip().replace(')', '').replace('(', '')
            subgenus1 = re.findall(fr'{genus1} (.*?) {species1}', parsed.split('--')[0].strip())
        else:
            pub1 = ' '.join(parsed.split(' ')[-2:])
            subgenus1 = re.findall(fr'{genus1} (.*?) {species1}', parsed)
        # [x.replace(',', '') for x in pub1.split(' ') if x != 'and']  # not using this right now
        pub_extra1 = pub_parser(pub1).get("extras")
        pub1 = pub_parser(pub1).get("authors") + pub_parser(pub1).get("year")
        pub1 = oxford_comma(pub1)
        if subgenus1:
            subgenus1 = subgenus1[0].replace('(', '').replace(')', '')
        else:
            subgenus1 = ''
        name = {
            'name_id': name_id,
            'parent_id': parent_id,
            'status': 'accepted',
            'accepted_genus': genus1,
            'accepted_species': species1,
            'subgenus': subgenus1,
            'genus': genus1,
            'species': species1,
            'accepted_canonical_name': ' '.join(parsed.split(' ')[3:5]),
            'canonical_name': ' '.join(parsed.split(' ')[3:5]),
            'publication': pub1,
            'publication_note': pub_extra1  #TODO: this isn't working
        }
        name_id += 1
        names.append(name)
        if '--' in line:
            synonyms = [x.strip() for x in parsed.split('--')[1:][0].split(';')]
            for syn in synonyms:
                syn_problem = re.search(r'[a-z]\([A-Z]', syn)
                if syn_problem:  # if space missing between genus and subgenus
                    syn = syn[0:syn_problem.span()[0] + 1] + ' ' + syn[syn_problem.span()[0] + 1:]
                syn_len = len(syn.strip().split(' '))
                genus2 = syn.strip().split(' ')[0]
                if syn_len == 1:
                    species2 = ''
                    pub2 = ''
                elif syn_len == 2:
                    species2 = syn.strip().split(' ')[1]
                    pub2 = ''
                elif syn_len > 2:
                    word = syn.strip().split(' ')
                    # determine specific_epithet START
                    if contains_capital(word[1]) and '(' not in word[0] and ')' not in word[2]:
                        # (Subgenus
                        # Subgenus)
                        # (Subgenus)
                        # Subgenus
                        wpos_start = 2
                    elif contains_capital(word[1]) and '(' in word[1] and ')' in word[2]:
                        # (Subgenus1
                        # subgenus2)
                        wpos_start = 3
                    else:
                        # species
                        wpos_start = 1
                    # determine specific_epithet END
                    apos_start = [x for x in word[wpos_start:] if contains_capital(x)]
                    if apos_start:
                        index = word.index(apos_start[0])
                    else:
                        index = None
                    if apos_start:  # pub exists
                        species2 = ' '.join(word[wpos_start:index]).split(' ')[0]
                        pub2 = ' '.join(word[index:]).strip().replace(')', '').replace('(', '')
                        pub_extra2 = pub_parser(pub2).get("extras")
                        pub2 = pub_parser(pub2).get("authors") + pub_parser(pub2).get("year")
                        pub2 = oxford_comma(pub2)
                    else:  # pub does not exist
                        species2 = ' '.join(word[wpos_start:])
                        pub2 = ' '
                        pub_extra2 = ''
                else:
                    species2 = ''
                # clean genus name, without possibly assigning subgenus to genus name
                if ')' in genus2 and '(' not in genus2:
                    genus2 = genus2.replace(')', '')
                elif '(' in genus2 and ')' not in genus2:
                    genus2 = genus2.replace('(', '')
                elif '(' in genus2 and ')' in genus2:
                    print('WARNING: subgenus possibly in genus!')
                    print(f'{parsed}')
                canon = ' '.join([genus2, species2])
                subgenus2 = re.findall(fr'{genus2} (.*?) {species2}', syn)
                if subgenus2:
                    subgenus2 = subgenus2[0].replace('(', '').replace(')', '')
                else:
                    subgenus2 = ''
                name = {
                    'name_id': name_id,
                    'parent_id': parent_id,
                    'status': 'synonym',
                    'accepted_genus': genus1,
                    'accepted_species': species1,
                    'subgenus': subgenus2,
                    'genus': genus2,  # TODO: remove "sic", "homonym"
                    'species': species2,  # TODO: remove "sic", "homonym"
                    'accepted_canonical_name': ' '.join(parsed.split(' ')[3:5]),
                    'canonical_name': canon,
                    'publication': pub2,
                    'publication_note': pub_extra2
                }
                name_id += 1
                names.append(name)

# write out
out = pd.DataFrame(names)
out.to_csv(output_file)
