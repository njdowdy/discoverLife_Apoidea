import pandas as pd
import re


# define custom functions

def apply_manual_fixes(data):
    data[0][1401] = '\xa0\xa0\xa0Andrena takachihoi\xa0Hirashima, 1964, emend.' \
                    '\xa0--\xa0Andrena (Euandrena) takachihsi\xa0' \
                    'Hirashima, 1964, incorrect original spelling in species heading'
    return data


def read_data(names_file):
    df = pd.read_csv(names_file, header=None)
    return df


def write_data(data, output_file):
    data_out = pd.DataFrame(data)
    data_out.to_csv(output_file, encoding='utf-8-sig')


def flatten(mylist):
    rt = []
    for i in mylist:
        if isinstance(i, list):
            rt.extend(flatten(i))
        else:
            rt.append(i)
    return rt

def unicode_name_fix(line_in, parent_id_in):
    line_out = line_in.replace('ůoziůski', 'Ůoziůski')
    line_out = line_out.replace('_cincta', ' cincta')
    line_out = line_out.replace('Azorae', 'azorae')
    line_out = line_out.replace(' Evylaeus)', '\xa0Lasioglossum (Evylaeus)')
    line_out = line_out.replace(' Dialictus)', '\xa0Lasioglossum (Dialictus)')
    line_out = line_out.replace(' Austronomia)', '\xa0Lipotriches (Austronomia)')
    line_out = line_out.replace('\xa0Hedicke, 1938, Andrena ', '\xa0Hedicke, 1938;\xa0Andrena ')
    line_out = line_out.replace('Michener, 1966, Compsomelissa', 'Michener, 1966;\xa0Compsomelissa')
    line_out = line_out.replace('Andrena cingulata auct , not Fabricius', 'Andrena cingulata_auct,_not_Fabricius')
    line_out = line_out.replace('argentata auct, not Fabricius, 1793', 'argentata_auct_not_Fabricius,_1793')
    line_out = line_out.replace('subspecies Dieunomia', 'subspecies;\xa0Dieunomia')

    # log which lines got changed for manual verification!
    if line_out != line_in:
        log_out = {
            'parent_id': parent_id_in,
            'original_text': line_in,
            'altered_text': line_out
        }
    else:
        log_out = {
            'parent_id': '',
            'original_text': '',
            'altered_text': ''
        }
    line_out = line_out.replace('\xa0', ' ')
    return line_out, log_out


def genus_extractor(record):
    genus_out = [x for x in record.split(' ') if re.match(r'^[A-Z]', x)][0]
    return genus_out


def species_extractor(record):
    species_exists = [x for x in record.split(' ') if re.match(r'^[a-z]', x) or
                      re.search(r'^[A-Z]-', x) or re.search(r'^[0-9]-', x)]
    species_exists = [x for x in species_exists if '(' not in x and ')' not in x]  # handles (Subgenus [text])
    if species_exists:
        species_out = species_exists[0]
    else:
        species_out = ''
    return species_out


def subspecies_extractor(species_in, record):
    subspecies_exists = re.findall(fr'{species_in} (.*?) [A-Z]', record)
    subspecies_exists = [x for x in subspecies_exists if not re.search(r',$|^[A-Z]|and', x)]
    if subspecies_exists:
        # if subspecies_exists and len(subspecies_exists[0].split(' ')) == 1:
        subspecies_out = subspecies_exists[0].replace('(', '').replace(')', '')
    elif subspecies_exists:
        subspecies_out = ''  # not sure how to handle something like: 'Andrena cingulata auct , not Fabricius'
    else:
        subspecies_out = ''
    return subspecies_out


def subgenus_extractor(genus_in, species_in, record):
    subgenus_exists = re.findall(fr'{genus_in} (.*?) {species_in}', record)
    if subgenus_exists:
        subgenus_out = subgenus_exists[0].replace('(', '').replace(')', '')
        # if contains 'sl' change to a subgenus note of 'sensu latu'
        if ' sl' in subgenus_out:
            subgenus_out = subgenus_out.replace(' sl', '_sl')
    else:
        subgenus_out = ''
    return subgenus_out


def publication_extractor(record):
    publication_exists = [x for x in record.split(' ') if re.match(r'^\(|[A-Z]', x) and ')' not in x]
    if len(publication_exists) > 1:
        publication_start = publication_exists[1]
        publication_out = record[record.index(publication_start):].replace('(', '').replace(')', '').strip()
    else:
        publication_out = ''
    return publication_out


def publication_parser(mypub):
    if mypub:
        year_exists = re.search(r'[0-9][0-9][0-9][0-9]', mypub)  # find position of year, if it exists
        if year_exists:
            year_start_index = year_exists.span()[0]
            year_end_index = year_exists.span()[1]
            year_out = mypub[year_start_index:year_end_index]
            bracketed_date_exists = re.search(fr"\[{year_out}\]", mypub)
            mypub = mypub.replace('[', '').replace(']', '')
            if bracketed_date_exists:
                bracketed_date_out = True
                year_out_print = f'[{year_out}]'
                year_start_index -= 1
            else:
                bracketed_date_out = False
                year_out_print = year_out
            publication_notes_out = '; '.join([x.strip() for x in mypub[year_end_index:].split(',') if x])
            authors_exist = mypub[0:year_start_index].strip()
            if authors_exist:
                year_separated_by_comma = authors_exist[-1] == ','
            else:
                year_separated_by_comma = False
        else:
            year_out = '????'
            year_out_print = '????'
            publication_notes_exist = re.search(r', [a-z].*?$', mypub)  # notes are typically ', [a-z][a-z]...'
            if publication_notes_exist:
                publication_notes_out = '; '.join([x.strip() for x in publication_notes_exist[0].split(',') if x])
                year_start_index = publication_notes_exist.span()[0]
                authors_exist = re.sub(fr'{publication_notes_exist[0]}', '', mypub)
            else:
                publication_notes_out = ''
                year_start_index = len(mypub)
                authors_exist = True  # if no notes, no year, but pub exists, authors must exist
            bracketed_date_out = False
            year_separated_by_comma = True
        ### AUTHOR PARSING STARTS HERE
        if authors_exist:  # if an author exists
            authors = mypub[0:year_start_index].strip()
            # authors = re.sub(r'([A-Z]) ([A-Z]) ', '\\1\\2 ', authors.replace('.', ''))  # no spaces between initials
            if not year_separated_by_comma:
                authors = authors + ','
            #space_sep_authors = [x for x in authors.replace(', ', '').replace(',', '').split(' ') if
            #                     x not in ['and', '&', 'y']]
            space_sep_authors = [x.replace(',', '') for x in authors.split(' ') if x not in ['and', '&', '&']]
            names2 = [x for x in space_sep_authors if re.search(r"^[A-z]([^A-Z]| [A-Z]|'[A-Z])*?[a-z]$", x)]
            single_name_authors_only = len(names2) - len(space_sep_authors)
            if single_name_authors_only == 0:
                author_list_out = space_sep_authors
                # combine 'van' and 'de' with next word, until added to a word starting with [A-Z]
                author_list_out = [re.sub(r'\s+', ' ', x).strip() for x in ''.join(
                    ['!' if x == 'van' else '@' if x == 'de' else x + ';' for x in
                     author_list_out]).replace('@', ' de ').replace('!', ' van ').strip().split(';') if x]
            else:
                authors = re.sub(r', $|,$', '', authors)
                if ',' not in authors:
                    test = [x.capitalize() if re.match(r'^[a-zA-Z]$', x) else x for x in space_sep_authors]
                    if any([re.match(r'^[A-Z]$', x) for x in test]):  # if any test are single letter only
                        authors = ''.join([x.capitalize() if re.match(r'^[a-zA-Z]$', x) else x for x
                                           in space_sep_authors])
                        authors = re.sub(r'([a-z])([A-Z][a-zA-z])', '\\1, \\2', authors)
                comma_sep_authors = authors.replace(' and ', ', ').replace(' y ', ', ').replace(' & ', ', ').split(',')
                author_list_out = [x.replace(',', '').strip() for x in comma_sep_authors if
                                   x.replace(',', '').replace(' ', '')]
                # unseparated_authors_exists = [re.findall(r'[A-Z][A-Z]([a-z]*?)[a-z][A-Z]', x) for x in
                #                               author_list_out]  # unseparated means AuthorAuthor
                # BELOW BREAKS A LOT OF BASIC FUNCTIONALITY???
                # unseparated_authors_exists = [
                #    re.findall(r'[A-Z][A-Z]([a-z]*?)[a-z][A-Z]|[A-Z]([a-z]*?)[A-Z]', x.replace('.', '').\
                #    replace(' ', ''))
                #    for x in author_list_out]  # unseparated means AuthorAuthor
                # if any(unseparated_authors_exists):
                #     # author_list_out = [re.findall(r'.*?[a-z](?=(?:[A-Z])|$)', x.strip()) for x in author_list_out][0]
                #     author_list_out = ';'.join(author_list_out).replace(' ', ';').split(';')
                    # items = [re.findall(r'.*?[a-z](?=(?:[A-Z])|$)', x.replace('.', '').replace(' ', '').\
                    # strip()) for x in
                    #          author_list_out]
                    # author_list_out = [item for elem in items for item in elem]
                author_list_out = [re.sub(r"([a-z])\. ", "\\1 ",
                                          re.sub(r'^\. ', '', re.sub(r"([A-Z])", ". \\1", x).strip().
                                                 replace('..', '.')))
                                   for x in author_list_out]  # expands 'AB' to 'A. B'
            author_list_out = [re.sub(r'([A-Z]\.)([A-Z]\.) ', '\\1 \\2 ', re.sub(r'([a-z])\. ', '\\1 ',
                                                                                 x.replace('. . ', '. ').
                                                                                 replace(' . ', '. ').
                                                                                 replace("'. ", "'")))
                               for x in author_list_out]
            author_list_out = [x + '.' if re.search(r' [A-Z]$', x) else x for x in author_list_out]  # sometimes initals lose their trailing '.'
            if len(author_list_out) > 1 and any([re.search(r'\. ([A-Z]\.)', x) for x in author_list_out]):
                # fix names not properly separated with commas
                author_list_out = [re.sub(r'\. (?![A-Z]\.)', '.;', x).split(';') for x in author_list_out]
                #author_list_out = [' '.join(x) if re.search('[a-z]', x) else x for x in author_list_out]
                author_list_out = [' '.join(x) if re.search(r'[a-z] [A-Z]', x[0]) else x for x in [y for y in author_list_out]] # EXPERIMENTAL
                #author_list_out = [item.replace('. ', '.') for elem in author_list_out for item in elem]
                # method 1 below
                #author_list_out = [re.sub(r'\. ([A-Z]\.)', '.\\1', x) for x in author_list_out]  # by condensing initials
                #author_list_out = [x.split(' ') if '.' in x else x for x in author_list_out]  # split on remaining spaces
                author_list_out = flatten(author_list_out)  # flatten list
            # fix name ordering
            initials = [' '.join(y).strip() for y in
                        [re.findall(r'([A-Z]\. |[A-Z] |[A-Z]\.)', x) for x in author_list_out]]
            noninitials = [re.sub(r'([A-Z]\. |[A-Z] |[A-Z]\.)', '', x).strip().replace(',', '')
                           for x in author_list_out]
            author_list_out2 = []
            author_list_display_out = []
            i, j = 0, 0
            for initial, name in zip(initials, noninitials):
                if i < len(noninitials) and j < len(initials):
                    # set initial and name positions
                    name = noninitials[i]
                    initial = initials[j]
                    # clean initials and names
                    initial = initial.strip().replace('  ', ' ')
                    name = name.strip().replace('  ', '')
                    if name == '' or initial == '':  # if either is empty, we may need to do some kind of merge
                        if name == '':  # indicates a merge is needed
                            i += 1  # name looks ahead
                            name = noninitials[i]
                            if i < len(initials):
                                if initials[i] == '':
                                    j += 1  # skip the next initial
                        elif initial == '' and j+1 < len(noninitials):  # indicates a merge may be needed
                            if noninitials[j+1] == '':  # indicates a merge is needed
                                j += 1  # initial looks ahead
                                initial = initials[j]
                                i += 1  # skip the next name
                        else:  # indicates no initials for name (we assume we never have initials without surname)
                            initial = ''
                    if initial != '':
                        namelength = len([x for x in name.split(' ') if x not in ['de', 'van', 'van de']])
                        lowercaseSurnameExists = len(name.split(' ')) != namelength  # lower case surname exists
                        if namelength == 1:  # one word name; e.g., Dowdy
                            insert_position = 0
                        elif namelength > 1 and not lowercaseSurnameExists:  # more than one word in name; e.g., Nick Dowdy
                            insert_position = re.search(r'[a-z] [A-Z]', name).span()[0] + 1
                        else:  # more than one word in name; e.g., Nick van Dowdy
                            insert_position = re.search(r'[a-z] [a-z]', name).span()[0] + 1
                        author_list_out2.append((name[0:insert_position] + ' ' + initial + ' ' + name[insert_position:]).replace('  ', ' ').strip())
                        author_list_display_out.append((name[0:insert_position] +
                                                       ' ' + initial.replace(' ', '') + ' ' + name[insert_position:]).replace('  ', ' ').strip())
                    else:
                        author_list_out2.append(name)
                        author_list_display_out.append(name)
                    i += 1
                    j += 1
            author_list_out = author_list_out2
            author_list_display = author_list_display_out
            number_of_authors = len([x for x in author_list_out if x])  # This was moved one line down
            # if number_of_authors != 0:
            #     # fix out of order surnames and first name initials
            #     i, j = 0, 0
            #     author_list_out2 = []
            #     last_i_merged = False
            #     forward_merged = False
            #     for author in author_list_out:
            #         # author = author_list_out[i]  # for testing
            #         if not forward_merged:
            #             if re.search(r'[A-Z]\. [A-Z]$|[A-Z]\. [A-Z]\.$', author.strip()) and \
            #                     not last_i_merged:  # if initials only AND last was not merged, look behind
            #                 out = (author + '. ' + author_list_out[i - 1]). \
            #                     replace('..', '.')  # look backwards for merge
            #                 author_list_out2 = author_list_out2[0:(j - 1)]
            #                 last_i_merged = True
            #                 j -= 1
            #             elif re.search(r'[A-Z]\. [A-Z]$|[A-Z]\. [A-Z]\.$', author.strip()) and \
            #                     last_i_merged:  # if initials only AND last was merged, look ahead
            #                 out = author + '. ' + author_list_out[i + 1]  # look forwards for merge
            #                 author_list_out2 = author_list_out2[0:(j + 1)]
            #                 last_i_merged = False
            #                 forward_merged = True
            #             else:  # if not initials only
            #                 out = author
            #                 last_i_merged = False
            #             author_list_out2.append(out)
            #             i += 1
            #             j += 1
            #         else:
            #             i += 1
            #             forward_merged = False
            #             last_i_merged = True
            #         # print(author_list_out2)
            #     author_list_out = author_list_out2
            # number_of_authors = len([x for x in author_list_out if x])  # Must be recalculated after above loop
            # if any([re.search('[A-Z]\. ', x) for x in author_list_out]):
            #     surnames = [re.sub(r'(.*)(\s)', '\\2', x) for x in author_list_out]
            #     i = 0
            #     author_list_display = []
            #     for author in author_list_out:
            #         author_list_display.append(author.replace(surnames[i], '').replace('. ', '.') + surnames[i])
            #         i += 1
            # else:
            #     author_list_display = author_list_out
        else:
            number_of_authors = 0
            author_list_out = ['']
            author_list_display = ['']
        if number_of_authors == 0:
            citation_out = 'Unknown, ' + year_out_print
        elif number_of_authors == 1:
            citation_out = author_list_display[0] + ', ' + year_out_print
        elif number_of_authors == 2:
            citation_out = ', '.join(author_list_display[0:-1]) + ' and ' + author_list_display[
                -1] + ', ' + year_out_print
        elif number_of_authors == 3:
            citation_out = ', '.join(author_list_display[0:-1]) + ', and ' + author_list_display[
                -1] + ', ' + year_out_print
        else:
            citation_out = author_list_display[0] + ' et al., ' + year_out_print
    else:
        author_list_out, year_out, citation_out, publication_notes_out, bracketed_date_out = [''], '', '', '', False
    return author_list_out, year_out, citation_out, publication_notes_out, bracketed_date_out


def to_canonical(genus_in, species_in):
    return ' '.join([genus_in.strip(), species_in.strip()])


def encoding_fix(author_in):
    author_out = re.sub(r'Reb.lo', 'Rebêlo', author_in)
    author_out = re.sub(r'Sep.lveda', 'Sepúlveda', author_out)
    author_out = re.sub(r'Qui.onez', 'Quiñonez', author_out)
    author_out = re.sub(r'J.nior', 'Júnior', author_out)
    author_out = re.sub(r'Y..ez', 'Yáñez', author_out)
    author_out = re.sub(r'Ord..ez', 'Ordóñez', author_out)
    return author_out


def name_note_extractor(name_in):
    if '_' in name_in:
        note_out = '_'.join([x.strip() for x in name_in.split('_')[1:]])
        # remove numbers from name notes (these are probably citation numbers?)
        # resolve some common abbreviated notes
        note_out = '; '.join([re.sub(r'[a-z][0-9]$', '', x).
                             replace('sic.', 'sic').
                             replace('.', '').replace('auct', 'auctorum')
                              for x in note_out.split(' ')]). \
            replace('.', '').replace('sl', 'sensu lato').replace('homonytm', 'homonym')
        note_out = re.sub(r'homony$', 'homonym', note_out)
        note_out = re.sub(r'misdet', 'misidentification', note_out.replace('.', ''))
        name_out = name_in.split('_')[0].replace('_', ' ')
    else:
        name_out = name_in
        note_out = ''
    return name_out, note_out


def subspecies_prefix_cleaner(name_in):
    name_out = name_in.replace('.', '').replace(',', '').replace('var ', 'variety '). \
        replace('v ', 'variety ').replace('m ', 'morph ').replace('morpha ', 'morph '). \
        replace('f ', 'form ').replace('ab ', 'abberration '). \
        replace('aber ', 'abberration ').replace('aberr ', 'abberration '). \
        replace('r ', 'race ').replace('rasse ', 'race ').replace('mut ', 'mutant')
    # mod = ???  # not sure what 'mod' means, but it is present sometimes
    return name_out
