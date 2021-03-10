from unittest import TestCase
from functions import functions


# Some names are impossible to parse without either:
# 1. Punctuation-separated authors
# 2. External context/information about author identities
# Take for example:
#
# "Abbot Alexander Cash Conner. 2000."
#
# Should it be parsed as:
#
# 1.     "Abbot, Alexander, Cash, and Conner. 2000" - 4 authors
# 2.     "Abbot Alexander and Cash Conner. 2000" - 2 authors
# 3.     "Abbot Alexander and Conner Cash. 2000" - 2 authors, 2nd reversed
# 4.     "Alexander Abbot and Cash Conner. 2000" - 2 authors, 1st reversed
# 5.     "Alexander Abbot and Conner Cash. 2000" - 2 authors, all reversed
# 6.     "Abbot, Alexander Cash, and Conner. 2000" - 3 authors
# 7.     "Abbot Alexander Cash and Conner. 2000" - 2 authors
# 8.     etc, etc
# Some formats cannot be distinguished in some cases:
# Example:
# Authora, Firstnamea, and Authorb # MLA FORMAT
# Authora,    Authorb, and Authorc # APA/other FORMAT


class Test(TestCase):

    def test_encoding_fix(self):
        self.assertEqual('Rebêlo', functions.encoding_fix('Reb�lo'))
        self.assertEqual('Sepúlveda', functions.encoding_fix('Sep�lveda'))
        self.assertEqual('Armas-Quiñonez', functions.encoding_fix('Armas-Qui�onez'))
        self.assertEqual('Júnior', functions.encoding_fix('J�nior'))
        self.assertEqual('Yáñez', functions.encoding_fix('Y��ez'))
        self.assertEqual('Ordóñez', functions.encoding_fix('Ord��ez'))

    def test_publication_nopub(self):
        self.assertEqual(('', [''], '', '', '', False),
                         functions.publication_parser(''))

    def test_publication_noAuthor(self):
        self.assertEqual(('1999', [''], '1999', 'Unknown, 1999', '', False),
                         functions.publication_parser('1999'))
        self.assertEqual(('1999, note', [''], '1999', 'Unknown, 1999', 'note', False),
                         functions.publication_parser('1999, note'))

    def test_publication_noDate(self):
        self.assertEqual(('Unknown, ????, notes', [''], '', 'Unknown, ????', 'notes', False),
                         functions.publication_parser('Unknown, ????, notes'))
        self.assertEqual(('Authora, ????, notes', ['Authora'], '', 'Authora, ????', 'notes', False),
                         functions.publication_parser('Authora, ????, notes'))

    def test_publication_auctorum(self):
        self.assertEqual(('Auctorum', [''], '', 'Unknown, ????', 'auct.', False),
                         functions.publication_parser('Auctorum'))
        self.assertEqual(('Auctorum, misidentification', [''], '', 'Unknown, ????', 'auct. misidentification', False),
                         functions.publication_parser('Auctorum, misidentification'))
        self.assertEqual(('Auctorum, sensu Authora, 1999', [''], '', 'Unknown, ????', 'auct. sensu Authora, 1999', False),
                         functions.publication_parser('Auctorum, sensu Authora, 1999'))
        self.assertEqual(('Authora, 1950, Auctorum, sensu Authora, 1999', ['Authora'], '1950',
                          'Authora, 1950', 'auct. sensu Authora, 1999', False),
                         functions.publication_parser('Authora, 1950, Auctorum, sensu Authora, 1999'))
        self.assertEqual(('Auct not Spinola', [''], '',
                          'Unknown, ????', 'auct. not Spinola', False),
                         functions.publication_parser('Auct not Spinola'))
        self.assertEqual(('Auct (not Kirby)', [''], '',
                          'Unknown, ????', 'auct. not Kirby', False),
                         functions.publication_parser('Auct (not Kirby)'))
        self.assertEqual(('Auct non (Robertson, 1895)', [''], '',
                          'Unknown, ????', 'auct. not Robertson, 1895', False),
                         functions.publication_parser('Auct non (Robertson, 1895)'))

    def test_publication_bracketed_date(self):
        self.assertEqual(('Authora and Authorb, [1999]', ['Authora', 'Authorb'], '1999',
                          'Authora and Authorb, [1999]', '', True),
                         functions.publication_parser('Authora and Authorb, [1999]'))

    def test_publication_notes(self):
        self.assertEqual(('Authora and Authorb, [1999], note1', ['Authora', 'Authorb'], '1999',
                          'Authora and Authorb, [1999]', 'note1', True),
                         functions.publication_parser('Authora and Authorb, [1999], note1'))
        self.assertEqual(('Authora and Authorb, [1999], note1, note2', ['Authora', 'Authorb'], '1999',
                          'Authora and Authorb, [1999]', 'note1; note2', True),
                         functions.publication_parser('Authora and Authorb, [1999], note1, note2'))
        self.assertEqual(('Authora and Authorb, [1999], note1; note2', ['Authora', 'Authorb'], '1999',
                          'Authora and Authorb, [1999]', 'note1; note2', True),
                         functions.publication_parser('Authora and Authorb, [1999], note1; note2'))

    def test_publication_author_separators(self):
        self.assertEqual(('Authora and Authorb, 1999', ['Authora', 'Authorb'], '1999',
                          'Authora and Authorb, 1999', '', False),
                         functions.publication_parser('Authora and Authorb, 1999'))
        self.assertEqual(('Authora y Authorb, 1999', ['Authora', 'Authorb'], '1999',
                          'Authora and Authorb, 1999', '', False),
                         functions.publication_parser('Authora y Authorb, 1999'))
        self.assertEqual(('Authora & Authorb, 1999', ['Authora', 'Authorb'], '1999',
                          'Authora and Authorb, 1999', '', False),
                         functions.publication_parser('Authora & Authorb, 1999'))
        self.assertEqual(('A. Authora & Authorb, 1999', ['A. Authora', 'Authorb'],
                          '1999', 'A. Authora and Authorb, 1999', '', False),
                         functions.publication_parser('A. Authora & Authorb, 1999'))

    def test_publication_author_basic_initials(self):
        self.assertEqual(('A. Authora, 1999', ['A. Authora'], '1999', 'A. Authora, 1999', '', False),
                         functions.publication_parser('A. Authora, 1999'))
        self.assertEqual(('A.B. Authora, 1999', ['A. B. Authora'], '1999', 'A.B. Authora, 1999', '', False),
                         functions.publication_parser('A.B. Authora, 1999'))
        self.assertEqual(('A. B. Authora, 1999', ['A. B. Authora'], '1999', 'A.B. Authora, 1999', '', False),
                         functions.publication_parser('A. B. Authora, 1999'))

    def test_publication_author_mixed_initials(self):
        self.assertEqual(('Nick A. Authora, 1999', ['Nick A. Authora'], '1999', 'N.A. Authora, 1999', '', False),
                         functions.publication_parser('Nick A. Authora, 1999'))
        self.assertEqual(
            ('Nick A. B. Authora and C. Dwayne Authorb, 1999', ['Nick A. B. Authora', 'C. Dwayne Authorb'],
             '1999', 'N.A.B. Authora and C.D. Authorb, 1999', '', False),
            functions.publication_parser('Nick A. B. Authora and C. Dwayne Authorb, 1999'))

    def test_publication_author_mixed_names(self):
        self.assertEqual(('Nick Authora, 1999', ['Nick Authora'], '1999', 'N. Authora, 1999', '', False),
                         functions.publication_parser('Nick Authora, 1999'))
        self.assertEqual(('Nick Authora and Authorb, 1999', ['Nick Authora', 'Authorb'], '1999',
                          'N. Authora and Authorb, 1999', '', False),
                         functions.publication_parser('Nick Authora and Authorb, 1999'))
        self.assertEqual(('Nick Authora and William Authorb, 1999', ['Nick Authora', 'William Authorb'],
                          '1999', 'N. Authora and W. Authorb, 1999', '', False),
                         functions.publication_parser('Nick Authora and William Authorb, 1999'))
        self.assertEqual(
            ('Nick Authora and William E. Authorb, 1999', ['Nick Authora', 'William E. Authorb'], '1999',
             'N. Authora and W.E. Authorb, 1999', '', False),
            functions.publication_parser('Nick Authora and William E. Authorb, 1999'))

    def test_publication_apa_commas(self):  # APA Style, comma-separated authors/initials
        self.assertEqual(('Authora, A., 2000', ['A. Authora'], '2000', 'A. Authora, 2000', '', False),
                         functions.publication_parser('Authora, A., 2000'))
        self.assertEqual(('Authora, A. B., & Authorb, B. C., 2000', ['A. B. Authora', 'B. C. Authorb'], '2000',
                          'A.B. Authora and B.C. Authorb, 2000', '', False),
                         functions.publication_parser('Authora, A. B., & Authorb, B. C., 2000'))
        # self.assertEqual(('Authora, A., Authorb, B. C., Authorc, D. E. F., Authord, G. H., & Authore, I., 2000',
        #                   ['A. Authora', 'B. C. Authorb', 'D. E. F. Authorc', 'G. H. Authord', 'I. Authore'], '2000',
        #                   'A. Authora et al., 2000', '', False),
        #                  functions.publication_parser('Authora, A., Authorb, B. C., Authorc, D. E. F.,'
        #                                               ' Authord, G. H., & Authore, I., 2000'))

    def test_publication_mla_commas(self):  # MLA Style, comma-separated authors/initials
        self.assertEqual(('Authora, Firstnamea, 2000', ['Firstnamea Authora'], '2000', 'F. Authora, 2000', '', False),
                         functions.publication_parser('Authora, Firstnamea, 2000'))
        self.assertEqual(('Authora, Firstnamea Middlenamea, 2000', ['Firstnamea Middlenamea Authora'], '2000',
                          'F.M. Authora, 2000', '', False),
                         functions.publication_parser('Authora, Firstnamea Middlenamea, 2000'))
        self.assertEqual(('Authora, Firstnamea A., 2000', ['Firstnamea A. Authora'], '2000', 'F.A. Authora, 2000', '',
                          False),
                         functions.publication_parser('Authora, Firstnamea A., 2000'))
        self.assertEqual(('Authora, Firstnamea A., and Firstnameb Authorb, 2000',
                          ['Firstnamea A. Authora', 'Firstnameb Authorb'], '2000',
                          'F.A. Authora and F. Authorb, 2000', '', False),
                         functions.publication_parser('Authora, Firstnamea A., and Firstnameb Authorb, 2000'))
        self.assertEqual(('Authora, Firstnamea A., et al., 2000', ['Firstnamea A. Authora'], '2000',
                          'F.A. Authora et al., 2000', '', False),
                         functions.publication_parser('Authora, Firstnamea A., et al., 2000'))

    def test_publication_ieee_commas(self):  # IEEE Style, comma-separated authors/initials
        self.assertEqual(('A. B. C. Authora, III, 2000', ['A. B. C. Authora, III'], '2000', 'A.B.C. Authora, III, 2000',
                          '', False),
                         functions.publication_parser('A. B. C. Authora, III, 2000'))
        self.assertEqual(('A. B. C. Authora, Jr., 2000', ['A. B. C. Authora, Jr.'], '2000', 'A.B.C. Authora, Jr., 2000',
                          '', False),
                         functions.publication_parser('A. B. C. Authora, Jr., 2000'))
        self.assertEqual(('A. B. C. Authora, Sr., 2000', ['A. B. C. Authora, Sr.'], '2000', 'A.B.C. Authora, Sr., 2000',
                          '', False),
                         functions.publication_parser('A. B. C. Authora, Sr., 2000'))
        self.assertEqual(('A. B. C. Authora, Jr, 2000', ['A. B. C. Authora, Jr.'], '2000', 'A.B.C. Authora, Jr., 2000',
                          '', False),
                         functions.publication_parser('A. B. C. Authora, Jr, 2000'))
        self.assertEqual(('A. B. C. Authora, Jnr, 2000', ['A. B. C. Authora, Jr.'], '2000', 'A.B.C. Authora, Jr., 2000',
                          '', False),
                         functions.publication_parser('A. B. C. Authora, Jnr, 2000'))
        self.assertEqual(('A. B. C. Authora, Snr, 2000', ['A. B. C. Authora, Sr.'], '2000', 'A.B.C. Authora, Sr., 2000',
                          '', False),
                         functions.publication_parser('A. B. C. Authora, Snr, 2000'))
        self.assertEqual(('A. B. C. Authora, JR, 2000', ['A. B. C. Authora, Jr.'], '2000', 'A.B.C. Authora, Jr., 2000',
                          '', False),
                         functions.publication_parser('A. B. C. Authora, JR, 2000'))
        self.assertEqual(('A. B. C. Authora, PhD, 2000', ['A. B. C. Authora'], '2000', 'A.B.C. Authora, 2000', '',
                          False),
                         functions.publication_parser('A. B. C. Authora, PhD, 2000'))
        self.assertEqual(('A. B. Authora and C. D. Authorb, 2000', ['A. B. Authora', 'C. D. Authorb'], '2000',
                          'A.B. Authora and C.D. Authorb, 2000', '', False),
                         functions.publication_parser('A. B. Authora and C. D. Authorb, 2000'))
        self.assertEqual(('A. B. Authora, C. D. Authorb, and E. F. Authorc, 2000',
                          ['A. B. Authora', 'C. D. Authorb', 'E. F. Authorc'], '2000',
                          'A.B. Authora, C.D. Authorb, and E.F. Authorc, 2000', '', False),
                         functions.publication_parser('A. B. Authora, C. D. Authorb, and E. F. Authorc, 2000'))
        self.assertEqual(('A. B. Authora, et al., 2000', ['A. B. Authora'], '2000', 'A.B. Authora et al., 2000',
                          '', False),
                         functions.publication_parser('A. B. Authora, et al., 2000'))

    def test_publication_ama_commas(self):  # AMA Style, comma-separated authors/initials
        self.assertEqual(('Authora AB, 2000', ['A. B. Authora'], '2000', 'A.B. Authora, 2000', '', False),
                         functions.publication_parser('Authora AB, 2000'))
        self.assertEqual(('Authora AB, Authorb CD, 2000', ['A. B. Authora', 'C. D. Authorb'], '2000',
                          'A.B. Authora and C.D. Authorb, 2000', '', False),
                         functions.publication_parser('Authora AB, Authorb CD, 2000'))
        # self.assertEqual(('Authora AB, Authorb CD, Authorc EF, Authord GH, 2000',
        #                   ['A. B. Authora', 'C. D. Authorb', 'E. F. Authorc', 'G. H. Authord'], '2000',
        #                   'A.B. Authora et al., 2000', '', False),
        #                  functions.publication_parser('Authora AB, Authorb CD, Authorc EF, Authord GH, 2000'))

    def test_publication_asa_commas(self):  # ASA Style, comma-separated authors/initials
        self.assertEqual(('Authora, Firstnamea A., 2000', ['Firstnamea A. Authora'], '2000', 'F.A. Authora, 2000',
                          '', False),
                         functions.publication_parser('Authora, Firstnamea A., 2000'))
        self.assertEqual(('Authora, Firstnamea A., and Firstnameb B. Authorb, 2000',
                          ['Firstnamea A. Authora', 'Firstnameb B. Authorb'], '2000',
                          'F.A. Authora and F.B. Authorb, 2000', '', False),
                         functions.publication_parser('Authora, Firstnamea A., and Firstnameb B. Authorb, 2000'))
        self.assertEqual(('Authora, Firstnamea A., Firstnameb Authorb, and Firstnamec C. Authorc, 2000',
                          ['Firstnamea A. Authora', 'Firstnameb Authorb', 'Firstnamec C. Authorc'], '2000',
                          'F.A. Authora, F. Authorb, and F.C. Authorc, 2000', '', False),
                         functions.publication_parser('Authora, Firstnamea A., '
                                                      'Firstnameb Authorb, and Firstnamec C. Authorc, 2000'))
        self.assertEqual(('Authora, Firstnamea A., Firstnameb Authorb, Firstnamec Authorc, and '
                          'Firstnamed D. Authord, 2000',
                          ['Firstnamea A. Authora', 'Firstnameb Authorb', 'Firstnamec Authorc',
                           'Firstnamed D. Authord'], '2000', 'F.A. Authora et al., 2000', '', False),
                         functions.publication_parser('Authora, Firstnamea A., '
                                                      'Firstnameb Authorb, Firstnamec Authorc,'
                                                      ' and Firstnamed D. Authord, 2000'))

    def test_publication_taxonomy_commas(self):  # Taxonomy-specific Styles, comma-separated authors/initials
        self.assertEqual(('Authora in Authorb, 2000', ['Authora'], '2000', 'Authora in Authorb, 2000', '', False),
                         functions.publication_parser('Authora in Authorb, 2000'))
        self.assertEqual(('A. Authora in B. Authorb, 2000', ['A. Authora'], '2000',
                          'A. Authora in B. Authorb, 2000', '', False),
                         functions.publication_parser('A. Authora in B. Authorb, 2000'))
        self.assertEqual(('A. Authora in Authorb and Authorc, 2000', ['A. Authora'], '2000',
                          'A. Authora in Authorb and Authorc, 2000', '', False),
                         functions.publication_parser('A. Authora in Authorb and Authorc, 2000'))
        self.assertEqual(('A. Authora in Authora, Authorb, and Authorc, 2000', ['A. Authora'], '2000',
                          'A. Authora in Authora, Authorb, and Authorc, 2000', '', False),
                         functions.publication_parser('A. Authora in Authora, Authorb, and Authorc, 2000'))
        self.assertEqual(('A. Authora in Authora, et al., 2000', ['A. Authora'], '2000',
                          'A. Authora in Authora, et al., 2000', '', False),
                         functions.publication_parser('A. Authora in Authora, et al., 2000'))
        self.assertEqual(('A. Authora and B. Authorb in Authora, et al., 2000', ['A. Authora', 'B. Authorb'],
                          '2000', 'A. Authora and B. Authorb in Authora, et al., 2000', '', False),
                         functions.publication_parser('A. Authora and B. Authorb in Authora, et al., 2000'))
        self.assertEqual(('A. Authora & B. Authorb in Authora, et al., 2000', ['A. Authora', 'B. Authorb'],
                          '2000', 'A. Authora and B. Authorb in Authora, et al., 2000', '', False),
                         functions.publication_parser('A. Authora & B. Authorb in Authora, et al., 2000'))
        self.assertEqual(('A. Authora & B. Authorb in Authora et al., 2000', ['A. Authora', 'B. Authorb'],
                          '2000', 'A. Authora and B. Authorb in Authora, et al., 2000', '', False),
                         functions.publication_parser('A. Authora & B. Authorb in Authora et al., 2000'))
        self.assertEqual(('A. Authora & B. Authorb in Authora et al, 2000', ['A. Authora', 'B. Authorb'],
                          '2000', 'A. Authora and B. Authorb in Authora, et al., 2000', '', False),
                         functions.publication_parser('A. Authora & B. Authorb in Authora et al, 2000'))

    def test_publication_sensu(self):  # publications with 'sensu'
        self.assertEqual(('Authora sensu Authorb, 2000', ['Authora'],
                          '2000', 'Authora sensu Authorb, 2000', '', False),
                         functions.publication_parser('Authora sensu Authorb, 2000'))
        self.assertEqual(('Authora, sensu Authorb, 2000', ['Authora'],
                          '2000', 'Authora sensu Authorb, 2000', '', False),
                         functions.publication_parser('Authora, sensu Authorb, 2000'))

    def test_publication_hyphenated_names(self):  # Surnames containing hyphens, comma-separated authors/initials
        self.assertEqual(('Authora-Authora and Authorb, 2000', ['Authora-Authora', 'Authorb'],
                          '2000', 'Authora-Authora and Authorb, 2000', '', False),
                         functions.publication_parser('Authora-Authora and Authorb, 2000'))

    def test_publication_apostrophe_names(self):  # Surnames containing apostrophes, comma-separated authors/initials
        self.assertEqual(("O'Authora and d'Authorb, 2000", ["O'Authora", "d'Authorb"], '2000',
                          "O'Authora and d'Authorb, 2000", '', False),
                         functions.publication_parser("O'Authora and d'Authorb, 2000"))

    def test_publication_prefixed_names(self):  # Surnames containing prefix titles, comma-separated authors/initials
        self.assertEqual(
            ("van de Kamp, Dowdy, and de Souza, 2000", ['van de Kamp', 'Dowdy', 'de Souza'],
             '2000', 'van de Kamp, Dowdy, and de Souza, 2000', '', False),
            functions.publication_parser("van de Kamp, Dowdy, and de Souza, 2000"))
        self.assertEqual(
            ("de Villers, 2000", ['de Villers'], '2000', 'de Villers, 2000', '', False),
            functions.publication_parser("de Villers, 2000"))

    def test_publication_missing_comma_before_and(self):
        # 'surname1, surname2 and surname 3, comma-separated authors/initials
        self.assertEqual(
            ("Authora, Authorb and Authorc, 2000", ['Authora', 'Authorb', 'Authorc'], '2000',
             'Authora, Authorb, and Authorc, 2000', '', False),
            functions.publication_parser("Authora, Authorb and Authorc, 2000"))
        self.assertEqual(
            ("Authora, Vauthorb and Authorc, 2000", ['Authora', 'Vauthorb', 'Authorc'], '2000',
             'Authora, Vauthorb, and Authorc, 2000', '', False),
            functions.publication_parser("Authora, Vauthorb and Authorc, 2000"))
        self.assertEqual(
            ("Authora, Iauthorb and Authorc, 2000", ['Authora', 'Iauthorb', 'Authorc'], '2000',
             'Authora, Iauthorb, and Authorc, 2000', '', False),
            functions.publication_parser("Authora, Iauthorb and Authorc, 2000"))