import pandas as pd
import re
from helpers.pLl import pLl

# define custom functions


def apply_manual_fixes(data):
    data[0][1401] = '\xa0\xa0\xa0Andrena takachihoi\xa0Hirashima, 1964, emend.' \
                    '\xa0--\xa0Andrena (Euandrena) takachihsi\xa0' \
                    'Hirashima, 1964, incorrect original spelling in species heading'
    return data


def encoding_fix(author_in):
    author_out = re.sub(r'Reb.lo', 'Rebêlo', author_in)
    author_out = re.sub(r'Sep.lveda', 'Sepúlveda', author_out)
    author_out = re.sub(r'Qui.onez', 'Quiñonez', author_out)
    author_out = re.sub(r'J.nior', 'Júnior', author_out)
    author_out = re.sub(r'Y..ez', 'Yáñez', author_out)
    author_out = re.sub(r'Ord..ez', 'Ordóñez', author_out)
    return author_out


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
    line_out = line_out.replace('hypochrysea\xa0Rohweri Cockerell, 1907',
                                'hypochrysea\xa0rohweri Cockerell, 1907, author requires verification - NJD')
    line_out = line_out.replace('Prosopis Bequaerti Schrottky, 1910',
                                'Prosopis bequaerti Schrottky, 1910, author requires verification - NJD')
    line_out = line_out.replace('Halictus flavopunctatus\xa0(Halictus, 1924)',
                                'Halictus flavopunctatus\xa0(Friese, 1924), author requires verification - NJD')
    line_out = line_out.replace('(Tkalců, valid subspecies, 1979)', '(Tkalců, 1979), valid subspecies')
    line_out = line_out.replace('Megachile Megachile (Austromegachile)', 'Megachile (Austromegachile)')
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


def capitalize_repl(match):
    match = match.group(1)
    if match[0] == ' ':
        match = match[1:]
        match_reformatted = ' ' + match.capitalize()
    else:
        match_reformatted = match.capitalize()
    return match_reformatted


def upper_repl(match):
    return match.group(1).upper()


def lower_repl(match):
    return match.group(1).lower()


def genus_extractor(record):
    genus_out = [x for x in record.split(' ') if re.match(r'^[A-Z]', x)][0]
    return genus_out


def species_extractor(record):
    species_exists = [x for x in record.split(' ') if re.match(r'^[a-z]', x) or
                      re.search(r'^[A-Z]-', x) or re.search(r'^[0-9]-', x)]
    # TODO: above does not seem to be working for: Allodape T-insignita Strand, 1912
    # TODO: above does not seem to be working for:  Anthophora T-insignata Strand, 1913, invalid symbol
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
        subspecies_out = ''
    else:
        subspecies_out = ''
    return subspecies_out


def subgenus_extractor(genus_in, species_in, record):
    subgenus_exists = re.findall(fr'{genus_in} (.*?) {species_in}', record)
    if subgenus_exists:
        subgenus_out = subgenus_exists[0].replace('(', '').replace(')', '')
        # if contains 'sl' change to a subgenus note of 'sensu lato'
        if ' sl' in subgenus_out or 's l' in subgenus_out:
            subgenus_out = subgenus_out.replace(' sl', '_sl').replace('s l', '_sl')
        # if contains 'vel' change to a subgenus note of 'vel*'
        if ' vel' in subgenus_out:
            subgenus_out = re.sub(r' (vel) (.*)', '_\\1_\\2', subgenus_out)
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
    original_pub = mypub
    mypub = encoding_fix(mypub)
    if mypub:  # if a publication was passed
        # find position of year, if it exists; ignore any year-like substrings after 'Auctorum'
        year_exists = re.search(r'[0-9][0-9][0-9][0-9]', mypub.split('Auctorum')[0])
        question_exists = re.search(r'\?\?\?\?', mypub)  # test if '????' exists
        auct_at_start = re.search(r'^[Aa]uct', mypub)  # test if pub starts with Auct or auct
        if auct_at_start:
            mypub = re.sub(r'^[Aa](uct)( |\. |, |orum |orum, |orum )(.*)|^[Aa]uct.*',
                           'Unknown, ????, auct. \\3', mypub)
            question_exists = re.search(r'\?\?\?\?', mypub)
        auctorum_exists = re.search(r'Auctorum', mypub)  # test if 'Auctorum' exists anywhere
        if auctorum_exists:  # if 'Auctorum' is still present
            mypub = re.sub(r'Auctorum, |Auctorum$', 'auct. ', mypub)
        if year_exists and not question_exists:  # if a year exists in publication
            year_start_index = year_exists.span()[0]
            year_end_index = year_exists.span()[1]
            year_out = mypub[year_start_index:year_end_index]
            bracketed_date_exists = re.search(rf'\[{year_out}]', mypub)
            mypub = mypub.replace('[', '').replace(']', '')
            if bracketed_date_exists:
                bracketed_date_out = True
                year_out_print = f'[{year_out}]'
                year_start_index -= 1
            else:
                bracketed_date_out = False
                year_out_print = year_out
            publication_notes_out = '; '.join([x.strip() for x in mypub[year_end_index:].split(',') if x])
            publication_notes_out = re.sub(r'\((not .*)\)', '\\1', publication_notes_out)
            publication_notes_out = re.sub(r'non \((.*)\)', 'not \\1', publication_notes_out)
            publication_notes_out = re.sub(r';( [0-9][0-9][0-9][0-9]$)', ',\\1', publication_notes_out)
            authors_exist = mypub[0:year_start_index].strip()
        else:  # a year is not in the publication
            year_out = ''
            year_out_print = '????'
            publication_notes_exist = re.search(r', [a-z].*?$', mypub)  # notes are typically ', [a-z][a-z]...'
            if publication_notes_exist:
                publication_notes_out = '; '.join([x.strip() for x in publication_notes_exist[0].split(',') if x])
                publication_notes_out = re.sub(r'\((not .*)\)', '\\1', publication_notes_out)
                publication_notes_out = re.sub(r'non \((.*)\)', 'not \\1', publication_notes_out)
                publication_notes_out = re.sub(r';( [0-9][0-9][0-9][0-9]$)', ',\\1', publication_notes_out)
                year_start_index = publication_notes_exist.span()[0]
                authors_exist = re.sub(fr'{publication_notes_exist[0]}', '', mypub)
            else:
                publication_notes_out = ''
                year_start_index = len(mypub)
                authors_exist = mypub
            bracketed_date_out = False
            if question_exists:
                year_start_index = re.search(r', \?\?\?\?', authors_exist).span()[0]
            if authors_exist.split(',')[0] in ['unknown', 'Unknown', '????', '']:
                authors_exist = False
        # AUTHOR PARSING STARTS HERE
        if authors_exist:  # if an author string exists
            authors = mypub[0:year_start_index].strip()  # authors are publication string up to location of year
            authors = re.sub(r' -([A-Z])', '\\1', authors)  # fix author initials of the form: 'M. -L. Kim'
            authors = re.sub(r',$', r'', authors)  # remove trailing ','
            authors = re.sub(r'([A-Z])\.', r'\1. ', authors).replace('  ', ' ')  # put a space between initials
            if ' in ' in authors:  # if author string matches 'taxonomy specific' style
                extra_author_info = re.search(r'( in .*)', authors)[0]  # capture 'in ...' text separately
                if extra_author_info[0] != ' ':  # if extra author info does not start with ' '
                    extra_author_info = ' ' + extra_author_info  # ensure extra author info starts with ' '
                if extra_author_info[-1] == ' ':  # if extra author info does not end with ' '
                    extra_author_info = extra_author_info[0:-1]  # ensure extra author info ends with ' '
                authors = re.sub(extra_author_info, '', authors)  # remove extra author info
                extra_author_info = re.sub(r'\b( et al).*', ',\\1.', extra_author_info)  # ensure 'et al' is formatted
            elif ' sensu ' in authors:  # if authora sensu authorb in author string
                if ', sensu ' in authors:  # if authora, sensu authorb in author string
                    authors = authors.replace(', sensu ', ' sensu ')  # make sure no comma before sensu
                extra_author_info = re.search(r'( sensu .*)', authors)[0]  # capture 'in ...' text separately
                if extra_author_info[0] != ' ':  # if extra author info does not start with ' '
                    extra_author_info = ' ' + extra_author_info  # ensure extra author info starts with ' '
                if extra_author_info[-1] == ' ':  # if extra author info does not end with ' '
                    extra_author_info = extra_author_info[0:-1]  # ensure extra author info ends with ' '
                authors = re.sub(extra_author_info, '', authors)  # remove extra author info
                extra_author_info = re.sub(r'\b( et al).*', ',\\1.', extra_author_info)  # ensure 'et al' is formatted
            else:  # if author string does not match 'taxonomy specific' style
                extra_author_info = ''  # there is no extra author info
            authors = re.sub(r' PhD\.|, PhD\.| PhD,|, PhD,| PhD$|, PhD$| PHD\.|, PHD\.| PHD,|, PHD,| PHD$|, PHD$|'
                             r' Esq\.|, Esq\.| Esq,|, Esq,| Esq$|, Esq$| ESQ\.|, ESQ\.| ESQ,|, ESQ,| ESQ$|, ESQ$|'
                             r' MD\.| MD,| MD$|, MD\.|, MD,|, MD$|'
                             r', MS\.| MS\.| MS$| MS,|, MS,|, MS$', r'', authors)  # remove honorary titles
            authors = re.sub(r',( Jnr[^A-Za-z]*?| JNR[^A-Za-z]*?|'
                             r' Snr[^A-Za-z]*?| SNR[^A-Za-z]*?|'
                             r' Jr[^A-Za-z]*?| JR[^A-Za-z]*?|'
                             r' Sr[^A-Za-z]*?| SR[^A-Za-z]*?)$', capitalize_repl, authors)  # protect generational title
            authors = re.sub(r',( I[^a-z]*?| V[^a-z]*?)$', '\\1', authors)  # protect generational titles
            authors = authors.replace('Jnr', 'Jr').replace('Snr', 'Sr')
            if authors[-2:] in ['Jr', 'Sr']:  # ensure these titles end with '.'
                authors = authors + '.'
            et_al_exists = re.search(r', et al*.?| et al*.?', authors)  # check if variants of 'et al' exist
            if et_al_exists:  # if variants of 'et al' present
                et_al_exists = True  # set et_al_exists to True
                authors = re.sub(r', et al*.?| et al*.?', '', authors)  # remove 'et al' variant from author string
            # if there are commas in author string and no 'and'-type character somewhere
            if ',' not in authors:
                style = 'NON-MLA'
            elif ',' in authors and not re.search(r' and | y | & ', authors):
                # Authora AB, Authorb AB, year  # AMA-style (assume AMA MUST have author initials)
                # Authora, Firstname AB, year  # MLA-style
                if ' ' in authors.split(',')[0]:
                    style = 'NON-MLA'  # these conditions indicate AMA-style
                else:
                    style = 'MLA'  # these conditions can indicate MLA-style
            # else, if the number of commas before ', and ...' is equal to 1
            # and any names before ', and ...' end in a space-separated initial
            elif len(re.findall(r',', re.sub(r', and.*', '', authors).strip())) == 1 and any(
                    [re.search(r'[a-z] [A-Z]$|[a-z] [A-Z]\.$', x) for
                     x in re.sub(r', and.*', '', authors).strip().split(',')]):
                style = 'MLA'  # these conditions indicate MLA-style
            elif len(re.findall(r',', re.sub(r', and.*', '', authors).strip())) == 1 and not any(
                    [re.search(r'[a-z] [A-Z]$|[a-z] [A-Z]\.$', x) for
                     x in re.sub(r', and.*', '', authors).strip().split(',')]):
                style = 'NON-MLA'  # these conditions indicate NON MLA-style
            else:  # else, it is ambiguous
                # Authora, Firstnamea Middlenamea, and Firstnameb Authorb  # spelled-out middlename could be MLA
                # Authora, Lasname1 Lastname2, and Firstnameb Authorb  # non-hyphenated lastname could be non-MLA
                #
                # Authora, Firstnamea, and Authorb  # could be MLA
                # Authora, Authorb, and Authorc  # could be non-MLA
                style = 'AMBIGUOUS'
            if style == 'AMBIGUOUS':
                print(f'WARNING: AUTHOR STRING MAY BE AMBIGUOUSLY FORMATTED!: {authors}')
            authors = re.sub(r' and | y | & ', r', ', authors)  # replace 'and', 'y', and '&' with ','
            authors = authors.replace(',,', ',')  # remove extra commas that may exist
            if style == 'MLA':  # if the style is MLA format
                authors_temp = authors.split(',')  # split author string by commas
                # convert authors from MLA to non-MLA format
                new_first_author = [authors_temp[1].strip() + ' ' + authors_temp[0].strip()]
                authors = ', '.join(new_first_author + [x.strip() for x in authors_temp[2:]])
            if ',' in authors:  # if commas exist, we assume the names and initials are comma-separated
                author_list = [x.strip() for x in authors.split(',') if x]  # separate on commas, ignoring empty strings
            else:  # assume only one author exists (does not exclude ' '-separated authors; difficult to deal with)
                author_list = [authors]  # place single author into a list
            temp_author_list = []  # generate new temp list
            for author in author_list:  # CHECKS FOR ASA FORMATTED AUTHORS
                out_of_order = re.search(r' [A-Z]\.$| [A-Z]$', author)  # names end in trailing initials
                if out_of_order:  # if a name is out of order
                    previous_name = temp_author_list[-1]  # store previous name
                    temp_author_list = temp_author_list[0:-1]  # remove the previous name
                    new_name = author.strip() + ' ' + previous_name.strip()  # merge current name with previous name
                    temp_author_list.append(new_name)  # append new name to the list of authors
                else:  # if a name is not out of order
                    temp_author_list.append(author)  # append the name to the list of authors
            author_list = temp_author_list  # write out temporary result to author_list
            temp_author_list = []  # generate new temp list
            for author in author_list:  # CHECKS FOR APA FORMATTED AUTHORS
                # names containing initials ONLY
                out_of_order = re.search(r'^([A-Z]\.)+$|^([A-Z] )+$|^([A-Z]\. )+(?!.*[a-z])', author)
                if out_of_order:  # if a name is out of order
                    surname = temp_author_list[-1]  # store previous name
                    temp_author_list = temp_author_list[0:-1]  # remove the previous name
                    initials = re.sub(r'([A-Z])\.', '\\1. ', author)  # place '. ' between each initial
                    new_name = initials.strip() + ' ' + surname.strip()  # merge current name with previous name
                    temp_author_list.append(new_name)  # append new name to the list of authors
                else:  # if a name is not out of order
                    temp_author_list.append(author)  # append the name to the list of authors
            author_list = temp_author_list  # write out temporary result to author_list
            temp_author_list = []  # generate new temp list
            for author in author_list:  # CHECKS FOR AMA FORMATTED AUTHORS
                trailing = re.search(r'( Jr.*?| Sr.*?| I.*?| V.*?)$', author)  # contains generational title
                if trailing:  # if generation title exists
                    suffix = author[trailing.span()[0]:trailing.span()[1]]  # separate generational title
                    author = author[0:trailing.span()[0]]  # remove generational title
                else:  # if generational title does not exist
                    suffix = ''  # do not add anything as a suffix
                out_of_order = re.search(r' [A-Z]+$', author)  # names end in multiple trailing initials
                if out_of_order:  # if a name is out of order
                    initials = ' '.join(author.split(' ')[1:])  # grab initials
                    initials = re.sub(r'([A-Z])', '\\1. ', initials)  # place '. ' between each initial
                    surname = author.split(' ')[0]  # grab surname
                    new_name = initials.strip() + ' ' + surname.strip() + suffix  # merge initials, surname, and suffix
                    temp_author_list.append(new_name)  # append new name to the list of authors
                else:  # if a name does not contain elements out of order
                    temp_author_list.append(author + suffix)  # append the name and suffix to the list of authors
            author_list = temp_author_list  # write out temporary result to author_list
            number_of_authors = len(author_list)  # calculate final number of authors
            # TODO: next line will not handle names like: "de Villers, III', needs a 'de' protector
            author_list = [re.sub(r'( Jr.*?| Sr.*?| I.*?| V.*?)$', ',\\1', x) if x.split(' ')[0] != 'de' else x for
                           x in author_list]  # comma-separate generational titles
            author_list_out = author_list  # write out result into author_list_out
            author_list_out = [re.sub(r'(^[A-Za-z])([A-Z][a-z])', "\\1'\\2", x)
                               for x in author_list_out]  # ensure 'O' 'd' names separated with "'"
            author_list_out = [', '.join([re.sub(fr"([A-Z])(?!{pLl})(?![a-z])(?!\.)(?!')",
                                                 "\\1. ", x.split(',')[0])] + x.split(',')[1:]).replace('  ', ' ')
                               for x in author_list_out]  # ensure initials are separated by '. ' (protect generational)
            # protect prefixes from next line
            author_list_display = [re.sub(r'(van |de |van de |der |van der )', upper_repl, x) for x in
                                   author_list_out]  # (I couldn't figure out a better regex for this)
            author_list_display = [re.sub(r'([a-z]+)(?!.*^) ', r'. ', x) for x in
                                   author_list_display]  # collapse non-surnames to an initial (does not handle prefix)
            author_list_display = [re.sub(r'(\. (?![A-Z][a-z])+)', r'.', x) for x in
                                   author_list_display]  # remove space between initials
            author_list_display = [re.sub(r'(VAN |DE |VAN DE |DER |VAN DER )', lower_repl, x) for x in
                                   author_list_display]  # unprotect prefixes
            if et_al_exists:  # if input mypub has 'et al' in author string
                number_of_authors = 25  # arbitrarily large value to trigger 'et al' in citation_out
        else:  # if an author string does not exist
            number_of_authors = 0  # the number of authors is zero
            extra_author_info = ''
            author_list_out = ['']  # capture authors as an empty string stored in a list
            author_list_display = ['']  # display authors as an empty string stored in a list
        # GENERATE AUTHOR STRING TO DISPLAY IN OUTPUT
        if number_of_authors == 0:  # if no authors
            citation_out = 'Unknown, ' + year_out_print
        elif number_of_authors == 1:  # if one author
            citation_out = author_list_display[0] + extra_author_info + ', ' + year_out_print
        elif number_of_authors == 2:  # if two authors
            citation_out = ', '.join(author_list_display[0:-1]) + ' and ' + author_list_display[
                -1] + extra_author_info + ', ' + year_out_print
        elif number_of_authors == 3:  # if three authors
            citation_out = ', '.join(author_list_display[0:-1]) + ', and ' + author_list_display[
                -1] + extra_author_info + ', ' + year_out_print
        else:  # if four or more authors
            citation_out = author_list_display[0] + ' et al.' + extra_author_info + ', ' + year_out_print  #
    else:  # no publication was passed
        original_pub, author_list_out, year_out = '', [''], ''
        citation_out, publication_notes_out, bracketed_date_out = '', '', False
    return original_pub, author_list_out, year_out, citation_out, publication_notes_out, bracketed_date_out


def to_canonical(genus_in, species_in):
    return ' '.join([genus_in.strip(), species_in.strip()])


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
    # seu = ???  # not sure what 'seu' means, but it can be present
    # vel = ???  # not sure what 'vel' means, but it is present sometimes
    # sive = ???  # not sure what 'sive' means, but it can be present
    return name_out
