import pandas as pd
import re

names_file = '../input/bee_names.csv'
output_file = '../output/bee_names_extracted.csv'
name_list = []
pLu = "[A-Z\u00C0-\u00D6\u00D8-\u00DE\u0100\u0102\u0104\u0106\u0108\u010A\u010C\u010E\u0110\u0112\u0114\u0116\u0118\u011A\u011C\u011E\u0120\u0122\u0124\u0126\u0128\u012A\u012C\u012E\u0130\u0132\u0134\u0136\u0139\u013B\u013D\u013F\u0141\u0143\u0145\u0147\u014A\u014C\u014E\u0150\u0152\u0154\u0156\u0158\u015A\u015C\u015E\u0160\u0162\u0164\u0166\u0168\u016A\u016C\u016E\u0170\u0172\u0174\u0176\u0178\u0179\u017B\u017D\u0181\u0182\u0184\u0186\u0187\u0189-\u018B\u018E-\u0191\u0193\u0194\u0196-\u0198\u019C\u019D\u019F\u01A0\u01A2\u01A4\u01A6\u01A7\u01A9\u01AC\u01AE\u01AF\u01B1-\u01B3\u01B5\u01B7\u01B8\u01BC\u01C4\u01C7\u01CA\u01CD\u01CF\u01D1\u01D3\u01D5\u01D7\u01D9\u01DB\u01DE\u01E0\u01E2\u01E4\u01E6\u01E8\u01EA\u01EC\u01EE\u01F1\u01F4\u01F6-\u01F8\u01FA\u01FC\u01FE\u0200\u0202\u0204\u0206\u0208\u020A\u020C\u020E\u0210\u0212\u0214\u0216\u0218\u021A\u021C\u021E\u0220\u0222\u0224\u0226\u0228\u022A\u022C\u022E\u0230\u0232\u023A\u023B\u023D\u023E\u0241\u0243-\u0246\u0248\u024A\u024C\u024E\u0370\u0372\u0376\u037F\u0386\u0388-\u038A\u038C\u038E\u038F\u0391-\u03A1\u03A3-\u03AB\u03CF\u03D2-\u03D4\u03D8\u03DA\u03DC\u03DE\u03E0\u03E2\u03E4\u03E6\u03E8\u03EA\u03EC\u03EE\u03F4\u03F7\u03F9\u03FA\u03FD-\u042F\u0460\u0462\u0464\u0466\u0468\u046A\u046C\u046E\u0470\u0472\u0474\u0476\u0478\u047A\u047C\u047E\u0480\u048A\u048C\u048E\u0490\u0492\u0494\u0496\u0498\u049A\u049C\u049E\u04A0\u04A2\u04A4\u04A6\u04A8\u04AA\u04AC\u04AE\u04B0\u04B2\u04B4\u04B6\u04B8\u04BA\u04BC\u04BE\u04C0\u04C1\u04C3\u04C5\u04C7\u04C9\u04CB\u04CD\u04D0\u04D2\u04D4\u04D6\u04D8\u04DA\u04DC\u04DE\u04E0\u04E2\u04E4\u04E6\u04E8\u04EA\u04EC\u04EE\u04F0\u04F2\u04F4\u04F6\u04F8\u04FA\u04FC\u04FE\u0500\u0502\u0504\u0506\u0508\u050A\u050C\u050E\u0510\u0512\u0514\u0516\u0518\u051A\u051C\u051E\u0520\u0522\u0524\u0526\u0528\u052A\u052C\u052E\u0531-\u0556\u10A0-\u10C5\u10C7\u10CD\u13A0-\u13F5\u1E00\u1E02\u1E04\u1E06\u1E08\u1E0A\u1E0C\u1E0E\u1E10\u1E12\u1E14\u1E16\u1E18\u1E1A\u1E1C\u1E1E\u1E20\u1E22\u1E24\u1E26\u1E28\u1E2A\u1E2C\u1E2E\u1E30\u1E32\u1E34\u1E36\u1E38\u1E3A\u1E3C\u1E3E\u1E40\u1E42\u1E44\u1E46\u1E48\u1E4A\u1E4C\u1E4E\u1E50\u1E52\u1E54\u1E56\u1E58\u1E5A\u1E5C\u1E5E\u1E60\u1E62\u1E64\u1E66\u1E68\u1E6A\u1E6C\u1E6E\u1E70\u1E72\u1E74\u1E76\u1E78\u1E7A\u1E7C\u1E7E\u1E80\u1E82\u1E84\u1E86\u1E88\u1E8A\u1E8C\u1E8E\u1E90\u1E92\u1E94\u1E9E\u1EA0\u1EA2\u1EA4\u1EA6\u1EA8\u1EAA\u1EAC\u1EAE\u1EB0\u1EB2\u1EB4\u1EB6\u1EB8\u1EBA\u1EBC\u1EBE\u1EC0\u1EC2\u1EC4\u1EC6\u1EC8\u1ECA\u1ECC\u1ECE\u1ED0\u1ED2\u1ED4\u1ED6\u1ED8\u1EDA\u1EDC\u1EDE\u1EE0\u1EE2\u1EE4\u1EE6\u1EE8\u1EEA\u1EEC\u1EEE\u1EF0\u1EF2\u1EF4\u1EF6\u1EF8\u1EFA\u1EFC\u1EFE\u1F08-\u1F0F\u1F18-\u1F1D\u1F28-\u1F2F\u1F38-\u1F3F\u1F48-\u1F4D\u1F59\u1F5B\u1F5D\u1F5F\u1F68-\u1F6F\u1FB8-\u1FBB\u1FC8-\u1FCB\u1FD8-\u1FDB\u1FE8-\u1FEC\u1FF8-\u1FFB\u2102\u2107\u210B-\u210D\u2110-\u2112\u2115\u2119-\u211D\u2124\u2126\u2128\u212A-\u212D\u2130-\u2133\u213E\u213F\u2145\u2160-\u216F\u2183\u24B6-\u24CF\u2C00-\u2C2E\u2C60\u2C62-\u2C64\u2C67\u2C69\u2C6B\u2C6D-\u2C70\u2C72\u2C75\u2C7E-\u2C80\u2C82\u2C84\u2C86\u2C88\u2C8A\u2C8C\u2C8E\u2C90\u2C92\u2C94\u2C96\u2C98\u2C9A\u2C9C\u2C9E\u2CA0\u2CA2\u2CA4\u2CA6\u2CA8\u2CAA\u2CAC\u2CAE\u2CB0\u2CB2\u2CB4\u2CB6\u2CB8\u2CBA\u2CBC\u2CBE\u2CC0\u2CC2\u2CC4\u2CC6\u2CC8\u2CCA\u2CCC\u2CCE\u2CD0\u2CD2\u2CD4\u2CD6\u2CD8\u2CDA\u2CDC\u2CDE\u2CE0\u2CE2\u2CEB\u2CED\u2CF2\uA640\uA642\uA644\uA646\uA648\uA64A\uA64C\uA64E\uA650\uA652\uA654\uA656\uA658\uA65A\uA65C\uA65E\uA660\uA662\uA664\uA666\uA668\uA66A\uA66C\uA680\uA682\uA684\uA686\uA688\uA68A\uA68C\uA68E\uA690\uA692\uA694\uA696\uA698\uA69A\uA722\uA724\uA726\uA728\uA72A\uA72C\uA72E\uA732\uA734\uA736\uA738\uA73A\uA73C\uA73E\uA740\uA742\uA744\uA746\uA748\uA74A\uA74C\uA74E\uA750\uA752\uA754\uA756\uA758\uA75A\uA75C\uA75E\uA760\uA762\uA764\uA766\uA768\uA76A\uA76C\uA76E\uA779\uA77B\uA77D\uA77E\uA780\uA782\uA784\uA786\uA78B\uA78D\uA790\uA792\uA796\uA798\uA79A\uA79C\uA79E\uA7A0\uA7A2\uA7A4\uA7A6\uA7A8\uA7AA-\uA7AE\uA7B0-\uA7B4\uA7B6\uFF21-\uFF3A\U00010400-\U00010427\U000104B0-\U000104D3\U00010C80-\U00010CB2\U000118A0-\U000118BF\U0001D400-\U0001D419\U0001D434-\U0001D44D\U0001D468-\U0001D481\U0001D49C\U0001D49E\U0001D49F\U0001D4A2\U0001D4A5\U0001D4A6\U0001D4A9-\U0001D4AC\U0001D4AE-\U0001D4B5\U0001D4D0-\U0001D4E9\U0001D504\U0001D505\U0001D507-\U0001D50A\U0001D50D-\U0001D514\U0001D516-\U0001D51C\U0001D538\U0001D539\U0001D53B-\U0001D53E\U0001D540-\U0001D544\U0001D546\U0001D54A-\U0001D550\U0001D56C-\U0001D585\U0001D5A0-\U0001D5B9\U0001D5D4-\U0001D5ED\U0001D608-\U0001D621\U0001D63C-\U0001D655\U0001D670-\U0001D689\U0001D6A8-\U0001D6C0\U0001D6E2-\U0001D6FA\U0001D71C-\U0001D734\U0001D756-\U0001D76E\U0001D790-\U0001D7A8\U0001D7CA\U0001E900-\U0001E921\U0001F130-\U0001F149\U0001F150-\U0001F169\U0001F170-\U0001F189]"

data = pd.read_csv(names_file, header=None)

# these lines are broken in the input file; requires manual fix
data[0][1401] = '\xa0\xa0\xa0Andrena takachihoi\xa0Hirashima, 1964, emend.' \
                '\xa0--\xa0Andrena (Euandrena) takachihsi\xa0' \
                'Hirashima, 1964, incorrect original spelling in species heading'
data[0][10066] = data[0][10066].replace('Azorae', 'azorae')

# define custom functions


def contains_capital(mystring):
    return re.findall(r'[A-Z]', mystring)


def pub_parser(mypub):
    year_start = re.search(r'[0-9]', mypub)
    if year_start:
        author_string = mypub[0:year_start.span()[0]]  # assumes start of string to year corresponds to author
        year = mypub[year_start.span()[0]:].split(',')[0]  # assumes EOL or comma to separate year
        # year_index = [x.strip() for x in mypub.split(',')].index(f'{year}')
        extras = '; '.join([x.strip() for x in mypub[year_start.span(0)[0] + len(year) + 1:].strip().split(',')])
    else:
        author_string = mypub
        year = ''
        extras = ''
    return {'extras': extras,
            'authors': author_string,
            'year': year}


def oxford_comma(mypub):
    if len(mypub.split(' ')) > 4:
        return ' '.join([x.replace(',', '') + ',' if x != 'and' else x for x in mypub.split(' ')])[
               0:-1]  # insert oxford comma
    else:
        return mypub


def to_canonical(genus, species) -> str:
    return ' '.join([genus.strip(), species.strip()])


def note_checker(name2check):
    if '_' in name2check:
        note = ' '.join([x.strip().replace('sic', 'Spelling in context') for x in name2check.split('_')[1:]])
        note = re.sub(r' [0-9]', '', note)  # remove numbers from name notes (these are probably citation numbers?)
        fixed_name = name2check.split('_')[0]
    else:
        fixed_name = name2check
        note = ''
    return fixed_name, note


def subgenus_extractor(genus, species, fullname):
    test = re.findall(fr'{genus} (.*?) {species}', fullname)
    if test:
        subgenus = test[0].replace('(', '').replace(')', '')
    else:
        subgenus = ''
    return subgenus


# define temp structures and variables
name = {}  # each name will be a dictionary
names = []  # all name dictionary will be stored in a list
name_id = 1
family = ''  # if there is a default family name, put it here
i = 1

for line in data[0]:
    print(i)
    if '\xa0' in line:
        #  -- : denotes start of synonyms
        #  ; : separates synonyms
        # ! parsed = parsed.replace(' ('+parsed.split(' ')[3]+') ', ' ')  # remove parent genus flag
        # ABOVE SHOULD BE CAPTURED AS SUBGENUS I THINK
        parent_id = name_id
        genus1 = [x for x in parsed.split(' ') if re.match(r'^[A-Z]', x)][0]
        species1 = [x for x in parsed.strip().split('--')[0].strip().split(' ') if re.match(r'^[a-z]', x) or
                    re.search(r'^[A-Z]-', x) or re.search(r'^[0-9]-', x)][0]
        name_stem = parsed.split('--')[0].strip().split(' ')
        species_start = name_stem.index(species1)
        pub_start = name_stem. \
            index([x for x in name_stem[species_start + 1:] if re.search(pLu, x) is not None][0])
        # pub1 = ' '.join([x for x in parsed.split('--')[0].split(' ') if x][2:]). \
        #     strip().replace(')', '').replace('(', '')
        if pub_start == species_start + 1:
            subspecies1 = ''
        else:
            subspecies1 = ' '.join(name_stem[species_start + 1:pub_start])
        pub1 = ' '.join(name_stem[pub_start:])
        check = parsed.split('--')[0].strip()
        subgenus1 = subgenus_extractor(genus1, species1, check)
        # [x.replace(',', '') for x in pub1.split(' ') if x != 'and']  # not using this right now
        pub_extra1 = pub_parser(pub1).get("extras")
        pub1 = pub_parser(pub1).get("authors") + pub_parser(pub1).get("year")
        pub1 = oxford_comma(pub1)
        genus1, genus_note1 = note_checker(genus1)
        subgenus1, subgenus_note1 = note_checker(subgenus1)
        species1, species_note1 = note_checker(species1)
        subspecies1, subspecies_note1 = note_checker(subspecies1)
        canon1 = to_canonical(genus1, species1)
        name = {
            'name_id': name_id,
            'parent_id': parent_id,
            'status': 'accepted',
            'family': family,
            'accepted_genus': genus1,
            'accepted_species': species1,
            'subgenus': subgenus1,
            'genus': genus1,
            'species': species1,
            'subspecies': subspecies1,
            'accepted_canonical_name': canon1,
            'canonical_name': canon1,
            'genus_note': genus_note1,
            'subgenus_note': subgenus_note1,
            'species_note': species_note1,
            'subspecies_note': subspecies_note1,
            'publication': pub1,
            'publication_note': pub_extra1
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
                genus2 = [x for x in syn.strip().split(' ') if re.match(r'^[A-Z]', x)][0]
                if syn_len == 1:
                    species2 = ''
                    subspecies2 = ''
                    pub2 = ''
                    pub_extra2 = ''
                elif syn_len == 2:
                    species2 = syn.strip().split(' ')[1]
                    subspecies2 = ''
                    pub2 = ''
                    pub_extra2 = ''
                elif syn_len > 2:
                    # word = re.split('[_ ]', syn.strip())
                    word = re.split(' ', syn.strip())
                    # determine specific_epithet START
                    species2 = [y for y in [x for x in word if re.search(r'^[a-z]', x) or
                                            re.search(r'^[A-Z]-', x) or re.search(r'^[0-9]-', x)] if
                                '(' not in y and ')' not in y]
                    if species2:
                        species2 = species2[0]
                        wpos_start = word.index(species2)
                        subspecies2 = [y for y in [x for x in word[wpos_start+1:] if re.search(r'^[a-z]', x) or
                                                re.search(r'^[A-Z]-', x) or re.search(r'^[0-9]-', x)] if
                                    '(' not in y and ')' not in y]
                        if subspecies2:
                            subspecies2 = subspecies2[0]
                        else:
                            subspecies2 = ''
                        species2 = species2.lower()
                    else:
                        species2 = ''
                        wpos_start = None
                        subspecies2 = ''
                    # determine if pub exists (assumes every pub has an an author with Capitalized name)
                    pub_exists = [x for x in word if re.search(r'^[A-Z]', x) if x != genus2]
                    if pub_exists:
                        index = word.index(pub_exists[0])
                        pub2 = ' '.join(word[index:]).strip().replace(')', '').replace('(', '')
                        pub_extra2 = pub_parser(pub2).get("extras")
                        pub2 = pub_parser(pub2).get("authors") + pub_parser(pub2).get("year")
                        pub2 = oxford_comma(pub2)
                    else:  # pub does not exist
                        index = None
                        pub2 = ''
                        pub_extra2 = ''
                else:
                    species2 = ''
                    subspecies2 = ''
                    pub2 = ''
                    pub_extra2 = ''
                # clean genus name, without possibly assigning subgenus to genus name
                if ')' in genus2 and '(' not in genus2:
                    genus2 = genus2.replace(')', '')
                elif '(' in genus2 and ')' not in genus2:
                    genus2 = genus2.replace('(', '')
                # elif '(' in genus2 and ')' in genus2:
                #     print('WARNING: subgenus possibly in genus!')
                #     print(f'{parsed}')
                subgenus2 = subgenus_extractor(genus2, species2, syn)
                genus2, genus_note2 = note_checker(genus2)
                subgenus2, subgenus_note2 = note_checker(subgenus2)
                species2, species_note2 = note_checker(species2)
                subspecies2, subspecies_note2 = note_checker(subspecies2)
                canon2 = to_canonical(genus2, species2)
                name = {
                    'name_id': name_id,
                    'parent_id': parent_id,
                    'status': 'synonym',
                    'family': family,
                    'accepted_genus': genus1,
                    'accepted_species': species1,
                    'subgenus': subgenus2,
                    'genus': genus2,
                    'species': species2,
                    'subspecies': subspecies2,
                    'accepted_canonical_name': ' '.join(parsed.split(' ')[3:5]),
                    'canonical_name': canon2,
                    'genus_note': genus_note2,
                    'subgenus_note': subgenus_note2,
                    'species_note': species_note2,
                    'subspecies_note': subspecies_note2,
                    'publication': pub2,
                    'publication_note': pub_extra2
                }
                name_id += 1
                names.append(name)
    else:
        family = line.strip()
    i += 1
# write out
out = pd.DataFrame(names)
out.to_csv(output_file, encoding='utf-8-sig')
