#!/usr/bin/env python

"""Tests for imdb.py."""

import os
import unittest
import StringIO

os.environ["DJANGO_SETTINGS_MODULE"] = "menclave.settings"

from menclave.venclave import imdb


def swap_object(obj, attr, newval):
    """Monkey patch an object while a decorated function executes."""
    def decorator(real_func):
        def new_func(*args, **kwargs):
            oldval = getattr(obj, attr, None)
            setattr(obj, attr, newval)
            try:
                return real_func(*args, **kwargs)
            finally:
                setattr(obj, attr, oldval)
        return new_func
    return decorator


def mock_file_open(contents):
    def mock_open(*args, **kwargs):
        io = StringIO.StringIO(contents)
        # Hack in the context manager methods.
        def noop(*args, **kwargs):
            return io
        io.__enter__ = noop
        io.__exit__ = noop
        return io
    return swap_object(imdb, 'open', mock_open)


class ImdbParserTest(unittest.TestCase):

    @mock_file_open("""\
D (2005)						2005
D 14 (1993)						1993
D 4 Delivery (2007)					2007
D III 38 (1939)						1939
D Minus (1998)						1998
""")
    def test_gen_movies(self):
        parser = imdb.ImdbParser("")
        titles = [
            'D (2005)',
            'D 14 (1993)',
            'D 4 Delivery (2007)',
            'D III 38 (1939)',
            'D Minus (1998)',
        ]
        self.assertEqual(titles, list(parser.generate_movie_titles()))

    @mock_file_open("""\
MV: Movie A (1991)
PL: asdf
PL: asdf
BY: foo
MV: Movie B (1992)
PL: jkl;
PL: jkl;
BY: bar
PL: quux
PL: quux
BY: baz
""")
    def test_gen_plots(self):
        parser = imdb.ImdbParser("")
        plots = [
            ('Movie A (1991)', [('foo', 'asdf asdf')]),
            ('Movie B (1992)', [('bar', 'jkl; jkl;'),
                                ('baz', 'quux quux')]),
        ]
        self.assertEqual(plots, list(parser.generate_plots()))

    @mock_file_open("""\
8: THE GENRES LIST
B-17: A Mini-Epic (2007)				Short
B (1996)						Short
B (1996)						Thriller
B-1 Nuclear Bomber (1980) (VG)				Action
B 224 (1999)						Short
B-29 Flight Procedure and Combat Crew Functioning (1944)	Short
B-29 Flight Procedure and Combat Crew Functioning (1944)	Documentary
""")
    def test_gen_genres(self):
        parser = imdb.ImdbParser("")
        genres = [
            ('B-17: A Mini-Epic (2007)', 'Short'),
            ('B (1996)', 'Short'),
            ('B (1996)', 'Thriller'),
            ('B-1 Nuclear Bomber (1980) (VG)', 'Action'),
            ('B 224 (1999)', 'Short'),
            ('B-29 Flight Procedure and Combat Crew Functioning (1944)', 'Short'),
            ('B-29 Flight Procedure and Combat Crew Functioning (1944)', 'Documentary'),
        ]
        self.assertEqual(genres, list(parser.generate_genres()))


    @mock_file_open("""\
Name			Titles
----			------
13, Phoenix		Action Man (1998) (V)
			Action Man 2 (1998) (V)
			Anal Graveyard (1997) (V)

1312			Absolute Punishment: The Ultimate Death Experience Part 2 (1998) (V)

50 Cent			Before I Self Destruct (2009) (V)

Aaron, Joe (II)		Crazy Jones (2002)

Aaron, Mark (I)		Grease Monkeys (1979)
			The Rivermen (1980)
""")
    def test_gen_directors(self):
        parser = imdb.ImdbParser("")
        directors = [
            ('13, Phoenix', 'Action Man (1998) (V)'),
            ('13, Phoenix', 'Action Man 2 (1998) (V)'),
            ('13, Phoenix', 'Anal Graveyard (1997) (V)'),
            ('1312', 'Absolute Punishment: The Ultimate Death Experience Part'
             ' 2 (1998) (V)'),
            ('50 Cent', 'Before I Self Destruct (2009) (V)'),
            ('Aaron, Joe (II)', 'Crazy Jones (2002)'),
            ('Aaron, Mark (I)', 'Grease Monkeys (1979)'),
            ('Aaron, Mark (I)', 'The Rivermen (1980)'),
        ]
        self.assertEqual(directors, list(parser.generate_directors()))

    @mock_file_open("""\
      2....4...4       5   6.6  Austin Golden Hour (2008) (TV)
      0000122100   60323   6.2  Austin Powers in Goldmember (2002)
      0000012211   66721   7.1  Austin Powers: International Man of Mystery (1997)
      70000..000      92   1.8  Economix - International Trade (1996)
      0000012100    8689   6.8  The International (2009)
      1.100.1.04      26   4.0  The Interruption (2004)
""")
    def test_gen_ratings(self):
        parser = imdb.ImdbParser("")
        ratings = [
            ('Austin Golden Hour (2008) (TV)',                     66),
            ('Austin Powers in Goldmember (2002)',                 62),
            ('Austin Powers: International Man of Mystery (1997)', 71),
            ('Economix - International Trade (1996)',              18),
            ('The International (2009)',                           68),
            ('The Interruption (2004)',                            40),
        ]
        self.assertEqual(ratings, list(parser.generate_ratings()))

    @mock_file_open("""\
The Insurance Man (1986) (TV)				77
The Insurgents (2006)					82
The Intern (2007) (V)					117
The International (2009)				118
""")
    def test_gen_running_times(self):
        parser = imdb.ImdbParser("")
        times = [
            ('The Insurance Man (1986) (TV)', 77),
            ('The Insurgents (2006)',         82),
            ('The Intern (2007) (V)',         117),
            ('The International (2009)',      118),
        ]
        self.assertEqual(times, list(parser.generate_running_times()))

    @mock_file_open("""\
Name			Titles
----			------
Aalami, Ali Reza	Shenasayi (1987)

Aalami, Arash		Ansoo-ye ayene (1997)  <7>

50 Cent			13 (2010)  [Jimmy]
			2003 Radio Music Awards (2003) (TV)  [Himself]

Owen, Clive		Ambush (2001)  [The Driver]  <1>
			Bad Boy Blues (1995) (TV)  [Paul]  <1>
			Beat the Devil (2002)  [Driver]  <1>
			Shoot 'Em Up (2007)  [Smith]  <1>
			Sin City (2005)  [Dwight]  <36>

Willis, Bruce		16 Blocks (2006)  [Det. Jack Mosley]  <1>
			Apocalypse (1998) (VG)  [Trey Kincaid]  <1>
			Armageddon (1998/I)  [Harry S. Stamper]  <1>
			Die Hard (1988)  [Officer John McClane]  <1>
""")
    def test_gen_actors(self):
        parser = imdb.ImdbParser("")
        actors = [
            ('Aalami, Ali Reza', 'Shenasayi (1987)', None, None),
            ('Aalami, Arash', 'Ansoo-ye ayene (1997)', None, 7),
            ('50 Cent', '13 (2010)', 'Jimmy', None),
            ('50 Cent', '2003 Radio Music Awards (2003)', 'Himself', None),
            ('Owen, Clive', 'Ambush (2001)', 'The Driver', 1),
            ('Owen, Clive', 'Bad Boy Blues (1995)', 'Paul', 1),
            ('Owen, Clive', 'Beat the Devil (2002)', 'Driver', 1),
            ('Owen, Clive', 'Shoot \'Em Up (2007)', 'Smith', 1),
            ('Owen, Clive', 'Sin City (2005)', 'Dwight', 36),
            ('Willis, Bruce', '16 Blocks (2006)', 'Det. Jack Mosley', 1),
            ('Willis, Bruce', 'Apocalypse (1998)', 'Trey Kincaid', 1),
            ('Willis, Bruce', 'Armageddon (1998/I)', 'Harry S. Stamper', 1),
            ('Willis, Bruce', 'Die Hard (1988)', 'Officer John McClane', 1),
        ]
        self.assertEqual(actors, list(parser.generate_actors()))


if __name__ == '__main__':
    unittest.main()