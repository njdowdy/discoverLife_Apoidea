import re
from functions import functions

names_file = 'input/bee_names.csv'
names_output_file = 'output/bee_names_extracted.csv'
author_output_file = 'output/bee_authors_extracted.csv'
log_file = 'output/log_file.csv'

data = functions.read_data(names_file)
data = functions.apply_manual_fixes(data)  # some lines are broken in the input file; requires manual fix

# define temp structures and variables
name_attributes = {}  # each name will be a dictionary
names_out_list = []  # all name dictionary will be stored in a list
running_author_list = []  # keeping track of all authors to generate author list
name_id = 1  # name index
accepted_genus = ''  # placeholder value
accepted_species = ''  # placeholder value
accepted_canonical_name = ''  # placeholder value
family = ''  # first line in data should be first family
# i = 1  # loop counter
change_log = []

for line in data[0]:
    # print(i)  # testing
    if '\xa0' in line:
        parent_id, original_parent_id = name_id, name_id
        parsed, log_result = functions.unicode_name_fix(line, parent_id)
        if log_result['parent_id'] != '':
            change_log.append(log_result)
        names = re.split("--|; ", parsed)  # create list of names
        # name = names[0]  # testing
        status = 'accepted'
        for name in names:
            name = name.strip().replace('( ', '(').\
                replace(' )', ')').replace('[ ', '[').replace(' ]', ']')  # clean up any whitespace problems in name
            name = re.sub(r'(\S)(\()', '\\1 \\2', name)  # '(' always preceded by whitespace
            name = re.sub(r'(\))(\S)', '\\1 \\2', name)  # ')' always followed by whitespace
            gcomplete, genus, genus_notes = functions.name_note_extractor(functions.genus_extractor(name))
            spcomplete, species, species_notes = functions.name_note_extractor(functions.species_extractor(name))
            sgcomplete, subgenus, subgenus_notes = functions.name_note_extractor(
                functions.subgenus_extractor(gcomplete, spcomplete, name))
            sppcomplete, subspecies, subspecies_notes = functions.name_note_extractor(
                functions.subspecies_extractor(spcomplete, name))
            canonical_name = functions.to_canonical(genus, species)
            # TODO: support trinomial canonical names if spp valid
            pub_data = functions.publication_extractor(name, gcomplete, sgcomplete, spcomplete, sppcomplete)
            original_publication_data, author_list, year, citation, publication_notes, bracketed_date =\
                functions.publication_parser(pub_data)
            # if publication_notes contains 'valid subspecies', raise status to 'accepted'
            accepted_subspecies = ''
            if 'valid subspecies' in publication_notes:
                status = 'accepted'
                accepted_subspecies = subspecies
                parent_id = name_id
            if status == 'accepted':
                accepted_genus = genus
                accepted_species = species
                accepted_canonical_name = canonical_name
            name_attributes = {
                'name_id': name_id,
                'parent_id': parent_id,
                'status': status,
                'family': family,
                'accepted_genus': accepted_genus,
                'accepted_species': accepted_species,
                'accepted_subspecies': accepted_subspecies,
                'subgenus': subgenus,
                'genus': genus,
                'species': species,
                'subspecies': subspecies,
                'accepted_canonical_name': accepted_canonical_name,
                'canonical_name': canonical_name,
                'genus_notes': genus_notes,
                'subgenus_notes': subgenus_notes,
                'species_notes': species_notes,
                'subspecies_notes': subspecies_notes,
                'publication': citation,
                'publication_notes': publication_notes,
                'verbatim_publication': original_publication_data,
                'verbatim_name': name.strip(),
                'source': 'Discover Life'
            }
            names_out_list.append(name_attributes)
            if author_list:
                running_author_list = list(set(running_author_list + author_list))
            parent_id = original_parent_id
            status = 'synonym'
            name_id += 1
    else:
        family = line.strip()
#    i += 1  # testing

# write out data
functions.write_data(names_out_list, names_output_file)  # write parsed data
running_author_list.sort()  # alphabetical sort of running author list
functions.write_data(running_author_list, author_output_file)  # write author list
functions.write_data(change_log, log_file)  # write out log file
