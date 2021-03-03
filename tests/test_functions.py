from unittest import TestCase
from functions import functions


class Test(TestCase):
    # test names like d'Brulio
    # test names like ABC de Authora

    def test_publication_basic(self):
        self.assertEqual((['C. D. Author'], '2000', 'C.D. Author, 2000', '', False),
                         functions.publication_parser('C.D. Author, 2000'))
        self.assertEqual(
            (['Authora', 'Authorb', 'Authorc'], '2000', 'Authora, Authorb, and Authorc, 2000', 'note', False),
            functions.publication_parser('Authora Authorb and Authorc, 2000, note'))
        self.assertEqual(
            (['Authora', 'Authorb', 'Authorc', 'Authord'], '2000', 'Authora et al., 2000', 'note', False),
            functions.publication_parser('Authora Authorb Authorc Authord, 2000, note'))

    def test_publication_authorsWithInitials(self):
        self.assertEqual(
            (['A. B. C. Authora', 'D. E. Authorb'], '2000', 'A.B.C. Authora and D.E. Authorb, 2000', '', False),
            functions.publication_parser('ABC Authora and DE Authorb, 2000'))
        self.assertEqual(
            (['Authora', 'A. Authorb', 'B. Authorc'], '2000', 'Authora, A. Authorb, and B. Authorc, 2000', '', False),
            functions.publication_parser('Authora, A Authorb and B Authorc, 2000'))
        self.assertEqual(
            (['A. B. C. Authora', 'D. E. Authorb'], '2000', 'A.B.C. Authora and D.E. Authorb, 2000', '', False),
            functions.publication_parser('ABC Authora & DE Authorb, 2000'))
        self.assertEqual((['A. Authora', 'B. Authorb', 'C. Authorc'], '2000',
                          'A. Authora, B. Authorb, and C. Authorc, 2000', '', False),
                         functions.publication_parser('A Authora B Authorb C Authorc, 2000'))
        self.assertEqual((['A. B. Authora', 'C. D. Authorb', 'Nick Dowdy'], '2000',
                          'A.B. Authora, C.D. Authorb, and Nick Dowdy, 2000', 'first note; second note', False),
                         functions.publication_parser(
                             'A B Authora, CD Authorb, Nick Dowdy, 2000, first note, second note'))
        self.assertEqual((['A. B. Authora', 'C. D. Authorb', 'Nick J. Dowdy'], '2000',
                          'A.B. Authora, C.D. Authorb, and Nick J. Dowdy, 2000', 'first note; second note', False),
                         functions.publication_parser(
                             'A B Authora, CD Authorb, Nick J. Dowdy, 2000, first note, second note'))

    def test_publication_noYear(self):
        self.assertEqual(([''], '????', 'Unknown, ????', 'note', False),
                         functions.publication_parser(', note'))
        self.assertEqual((['C. D. Author'], '????', 'C.D. Author, ????', 'note', False),
                         functions.publication_parser('C.D. Author, note'))
        self.assertEqual((['C. D. Author'], '????', 'C.D. Author, ????', '', False),
                         functions.publication_parser('C.D. Author'))

    def test_publication_initialsOutOfOrder(self):
        self.assertEqual((['A. B. Lastnamea', 'C. D. Lastnameb', 'E. F. Lastnamec'], '2000',
                          'A.B. Lastnamea, C.D. Lastnameb, and E.F. Lastnamec, 2000', 'note1; note2', False),
                         functions.publication_parser(
                             'Lastnamea, AB, CD Lastnameb, and EF Lastnamec, 2000, note1, note2'))
        self.assertEqual((['A. B. Lastnamea', 'C. D. Lastnameb', 'E. F. Lastnamec'], '2000',
                          'A.B. Lastnamea, C.D. Lastnameb, and E.F. Lastnamec, 2000', 'note1; note2', False),
                         functions.publication_parser(
                             'Lastnamea, AB, Lastnameb C.D., Lastnamec E.F, 2000, note1, note2'))
        self.assertEqual((['A. B. Lastnamea', 'C. D. Lastnameb', 'E. F. Lastnamec'], '2000',
                          'A.B. Lastnamea, C.D. Lastnameb, and E.F. Lastnamec, 2000', 'note1; note2', False),
                         functions.publication_parser('Lastnamea, AB Lastnameb C.D. Lastnamec E.F, 2000, note1, note2'))
        # self.assertEqual((['A. B. Lastnamea', 'C. D. Lastnameb', 'E. F. Lastnamec', 'G. H. Lastnamed',
        #                    'I. J. Lastnamek'], '2000',
        #                   'A.B. Lastnamea, C.D. Lastnameb, E.F. Lastnamec, G.H. Lastnamed, and I.J. Lastnamek, 2000',
        #                   'note1; note2', False),
        #                  functions.publication_parser(
        #                      'Lastnamea, AB Lastnameb C.D. Lastnamec E.F, G.H.,'
        #                      ' Lastnamed I. J. Lastnamek 2000, note1, note2'))

    #def test_publication_namesWithLowercase(self):
    #     self.assertEqual((['de Bruin', 'van de Kamp', "van O'Brian"], '2000',
    #                       "de Bruin, van de Kamp, and van O'Brian, 2000", '', False),
    #                      functions.publication_parser("de Bruin, van de Kamp, van O'Brian, 2000"))
    #     self.assertEqual((['de Bruin', 'Dowdy', 'van de Kamp', "van O'Brian"], '2000',
    #                       "de Bruin, et al., [2000]", 'note', True),
    #                      functions.publication_parser("de Bruin, Dowdy, van de Kamp, van O'Brian, [2000], note"))
    #     self.assertEqual((['de Bruin', 'Dowdy', 'van de Kamp', "van O'Brian"], '2000',
    #                       "de Bruin, et al., 2000", '', False),
    #                      functions.publication_parser("de Bruin Dowdy van de Kamp van O'Brian, 2000"))
    #     self.assertEqual((['de Bruin', 'Dowdy', 'van de Kamp', "van O'Brian"], '2000',
    #                       "de Bruin, et al., [2000]", 'note', True),
    #                      functions.publication_parser("de Bruin Dowdy van de Kamp van O'Brian, [2000], note"))
    #     self.assertEqual((['de Bruin', 'Dowdy', 'van de Kamp', "van O'Brian"], '2000',
    #                       "de Bruin, et al., [2000]", 'note', True),
    #                      functions.publication_parser("de Bruin Dowdy van de Kamp van O'Brian [2000], note"))

    def test_publication_bracketedYears(self):
        self.assertEqual((['C. D. Author'], '2000', 'C.D. Author, [2000]', '', True),
                         functions.publication_parser('C.D. Author, [2000]'))
        self.assertEqual(
            (['Authora', 'Authorb', 'Authorc'], '2000', 'Authora, Authorb, and Authorc, [2000]', 'note', True),
            functions.publication_parser('Authora Authorb and Authorc, [2000], note'))
        self.assertEqual(
            (['A. B. C. Authora', 'D. E. Authorb'], '2000', 'A.B.C. Authora and D.E. Authorb, [2000]', 'note', True),
            functions.publication_parser('ABC Authora and DE Authorb, [2000], note'))
        self.assertEqual((
            ['Authora', 'A. Authorb', 'B. Authorc'], '2000', 'Authora, A. Authorb, and B. Authorc, [2000]',
            'note', True),
            functions.publication_parser('Authora, A Authorb and B Authorc, [2000], note'))
        self.assertEqual((['A. B. Authora', 'C. D. Authorb', 'Nick Dowdy'], '2000',
                          'A.B. Authora, C.D. Authorb, and Nick Dowdy, [2000]', 'first note; second note', True),
                         functions.publication_parser(
                             'A B Authora, CD Authorb, Nick Dowdy, [2000], first note, second note'))
        self.assertEqual((['A. B. Authora', 'C. D. Authorb', 'Nick J. Dowdy'], '2000',
                          'A.B. Authora, C.D. Authorb, and Nick J. Dowdy, [2000]', 'first note; second note', True),
                         functions.publication_parser(
                             'A B Authora, CD Authorb, Nick J. Dowdy, [2000], first note, second note'))
        self.assertEqual((['A. Authora', 'B. Authorb', 'C. Authorc'], '2000',
                          'A. Authora, B. Authorb, and C. Authorc, [2000]', 'note', True),
                         functions.publication_parser('A Authora B Authorb C Authorc, [2000], note'))

    def test_publication_noAuthor(self):
        self.assertEqual(([''], '1999', 'Unknown, 1999', '', False),
                         functions.publication_parser('1999'))
        self.assertEqual(([''], '1999', 'Unknown, 1999', 'note', False),
                         functions.publication_parser('1999, note'))

    def test_publication_nopub(self):
        self.assertEqual(([''], '', '', '', False),
                         functions.publication_parser(''))

    def test_encoding_fix(self):
        self.assertEqual('Rebêlo', functions.encoding_fix('Reb�lo'))
        self.assertEqual('Sepúlveda', functions.encoding_fix('Sep�lveda'))
        self.assertEqual('Quiñonez', functions.encoding_fix('Qui�onez'))
        self.assertEqual('Júnior', functions.encoding_fix('J�nior'))
        self.assertEqual('Yáñez', functions.encoding_fix('Y��ez'))
        self.assertEqual('Ordóñez', functions.encoding_fix('Ord��ez'))
