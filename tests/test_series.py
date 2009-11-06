from tests import FlexGetBase

class TestQuality(FlexGetBase):

    __yaml__ = """
        feeds:
          best_quality:
            input_mock:
              - {title: 'QTest.S01E01.HDTV.XViD-FlexGet'}
              - {title: 'QTest.S01E01.PDTV.XViD-FlexGet'}
              - {title: 'QTest.S01E01.DSR.XViD-FlexGet'}
              - {title: 'QTest.S01E01.1080p.XViD-FlexGet'}
              - {title: 'QTest.S01E01.720p.XViD-FlexGet'}
            series:
              - QTest:
                  quality: 720p

          min_quality:
            input_mock:
              - {title: 'MinQTest.S01E01.HDTV.XViD-FlexGet'}
              - {title: 'MinQTest.S01E01.PDTV.XViD-FlexGet'}
              - {title: 'MinQTest.S01E01.DSR.XViD-FlexGet'}
              - {title: 'MinQTest.S01E01.1080p.XViD-FlexGet'}
              - {title: 'MinQTest.S01E01.720p.XViD-FlexGet'}
            series:
              - MinQTest:
                  min_quality: hdtv

          max_quality:
            input_mock:
              - {title: 'MaxQTest.S01E01.HDTV.XViD-FlexGet'}
              - {title: 'MaxQTest.S01E01.PDTV.XViD-FlexGet'}
              - {title: 'MaxQTest.S01E01.DSR.XViD-FlexGet'}
              - {title: 'MaxQTest.S01E01.1080p.XViD-FlexGet'}
              - {title: 'MaxQTest.S01E01.720p.XViD-FlexGet'}
            series:
              - MaxQTest:
                  max_quality: hdtv

          min_max_quality:
            input_mock:
              - {title: 'MinMaxQTest.S01E01.HDTV.XViD-FlexGet'}
              - {title: 'MinMaxQTest.S01E01.PDTV.XViD-FlexGet'}
              - {title: 'MinMaxQTest.S01E01.DSR.XViD-FlexGet'}
              - {title: 'MinMaxQTest.S01E01.720p.XViD-FlexGet'}
              - {title: 'MinMaxQTest.S01E01.HR.XViD-FlexGet'}
              - {title: 'MinMaxQTest.S01E01.1080p.XViD-FlexGet'}
            series:
              - MinMaxQTest:
                  min_quality: pdtv
                  max_quality: hr
    """

    def test_best_quality(self):
        """Series plugin: choose by quality"""
        self.execute_feed('best_quality')
        assert self.feed.find_entry('accepted', title='QTest.S01E01.720p.XViD-FlexGet'), \
            '720p should have been accepted'
        assert len(self.feed.accepted) == 1, 'should have accepted only one'

    def test_min_quality(self):
        """Series plugin: min_quality"""
        self.execute_feed('min_quality')
        assert self.feed.find_entry('accepted', title='MinQTest.S01E01.1080p.XViD-FlexGet'), \
            'MinQTest.S01E01.1080p.XViD-FlexGet should have been accepted'
        assert len(self.feed.accepted) == 1, 'should have accepted only one'

    def test_max_quality(self):
        """Series plugin: max_quality"""
        self.execute_feed('max_quality')
        assert self.feed.find_entry('accepted', title='MaxQTest.S01E01.HDTV.XViD-FlexGet'), \
            'MaxQTest.S01E01.HDTV.XViD-FlexGet should have been accepted'
        assert len(self.feed.accepted) == 1, 'should have accepted only one'

    def test_min_max_quality(self):
        """Series plugin: min_quality with max_quality"""
        self.execute_feed('min_max_quality')
        assert self.feed.find_entry('accepted', title='MinMaxQTest.S01E01.HR.XViD-FlexGet'), \
            'MinMaxQTest.S01E01.HR.XViD-FlexGet should have been accepted'
        assert len(self.feed.accepted) == 1, 'should have accepted only one'


class TestDatabase(FlexGetBase):

    __yaml__ = """
        global:
          series:
            - some series
            - progress

        feeds:
          test_1:
            input_mock:
              - {title: 'Some.Series.S01E20.720p.XViD-FlexGet'}
          test_2:
            input_mock:
              - {title: 'Some.Series.S01E20.720p.XViD-DoppelGanger'}
              
          progress_1:
            input_mock:
              - {title: 'Progress.S01E20.720p-FlexGet'}
              - {title: 'Progress.S01E20.HDTV-FlexGet'}
              
          progress_2:
            input_mock:
              - {title: 'Progress.S01E20.720p.Another-FlexGet'}
              - {title: 'Progress.S01E20.HDTV-Another-FlexGet'}
    """

    def test_database(self):
        self.execute_feed('test_1')
        self.execute_feed('test_2')
        assert self.feed.find_entry('rejected', title='Some.Series.S01E20.720p.XViD-DoppelGanger'), \
            'failed basic download remembering'
            
    def test_progress(self):
        self.execute_feed('progress_1')
        assert self.feed.find_entry('accepted', title='Progress.S01E20.720p-FlexGet'), \
            'best quality not accepted'
        # should not accept anything
        self.execute_feed('progress_1')
        assert not self.feed.accepted, 'repeated execution accepted'
        # introduce new doppelgangers
        self.execute_feed('progress_2')
        assert not self.feed.accepted, 'doppelgangers accepted'

class TestFilterSeries(FlexGetBase):

    __yaml__ = """
        feeds:
          test:
            input_mock:
              - {title: 'Another.Series.S01E20.720p.XViD-FlexGet'}
              - {title: 'Another.Series.S01E21.1080p.H264-FlexGet'}
              - {title: 'Date.Series.10-11-2008.XViD'}
              - {title: 'Date.Series.10.12.2008.XViD'}
              - {title: 'Date.Series.2008-10-13.XViD'}
              - {title: 'Date.Series.2008x10.14.XViD'}
              - {title: 'Useless title', filename: 'Filename.Series.S01E26.XViD'}
              - {title: 'Empty.Description.S01E22.XViD', description: ''}

            # test chaining
            regexp:
              reject:
                - 1080p

            series:
              - another series
              - date series
              - filename series
              - empty description
    """

    def test_smoke(self):
        """Series plugin: test several standard features"""
        self.execute_feed('test')

        # normal passing
        assert self.feed.find_entry(title='Another.Series.S01E20.720p.XViD-FlexGet'), \
            'Another.Series.S01E20.720p.XViD-FlexGet should have passed'

        # date formats
        df = ['Date.Series.10-11-2008.XViD','Date.Series.10.12.2008.XViD', \
              'Date.Series.2008-10-13.XViD', 'Date.Series.2008x10.14.XViD']
        for d in df:
            assert self.feed.find_entry(title=d), 'Date format did not match %s' % d

        # parse from filename
        assert self.feed.find_entry(filename='Filename.Series.S01E26.XViD'), 'Filename parsing failed'

        # empty description
        assert self.feed.find_entry(title='Empty.Description.S01E22.XViD'), 'Empty Description failed'

        # chaining with regexp plugin
        assert self.feed.find_entry('rejected', title='Another.Series.S01E21.1080p.H264-FlexGet'), \
            'regexp chaining'


class TestEpisodeAdvancement(FlexGetBase):
    __yaml__ = """
        feeds:
          test_simple:
            input_mock:
              - {title: 'foobar s01e12'}
              - {title: 'foobar s01e10'}
              - {title: 'foobar s01e01'}
            series:
              - foobar

          test_unordered:
            input_mock:
              - {title: 'zzz s01e05'}
              - {title: 'zzz s01e06'}
              - {title: 'zzz s01e07'}
              - {title: 'zzz s01e08'}
              - {title: 'zzz s01e09'}
              - {title: 'zzz s01e10'}
              - {title: 'zzz s01e15'}
              - {title: 'zzz s01e14'}
              - {title: 'zzz s01e13'}
              - {title: 'zzz s01e12'}
              - {title: 'zzz s01e11'}
              - {title: 'zzz s01e01'}
            series:
              - zzz
    """

    def test_simple(self):
        self.execute_feed('test_simple')
        assert self.feed.find_entry('accepted', title='foobar s01e12'), \
            'foobar s01e12 should have been accepted'
        assert self.feed.find_entry('accepted', title='foobar s01e10'), \
            'foobar s01e10 should have been accepted within grace margin'
        assert self.feed.find_entry('rejected', title='foobar s01e01'), \
            'foobar s01e01 should have been rejected, too old'

    def test_unordered(self):
        self.execute_feed('test_unordered')
        assert len(self.feed.accepted) == 12, \
            'not everyone was accepted'

class TestFilterSeriesPriority(FlexGetBase):

    __yaml__ = """
        feeds:
          test:
            input_mock:
              - {title: 'foobar 720p s01e01'}
              - {title: 'foobar hdtv s01e01'}
            regexp:
              reject:
                - 720p
            series:
              - foobar
    """

    def test_priorities(self):
        """Series plugin: regexp plugin is able to reject before series plugin"""
        self.execute_feed('test')
        assert self.feed.find_entry('rejected', title='foobar 720p s01e01'), \
            'foobar 720p s01e01 should have been rejected'
        assert self.feed.find_entry('accepted', title='foobar hdtv s01e01'), \
            'foobar hdtv s01e01 is not accepted'


class TestPropers(FlexGetBase):

    __yaml__ = """
        global:
          # prevents seen from rejecting on second execution,
          # we want to see that series is able to reject
          disable_builtins: yes
          series:
            - test
            - foobar
            - V

        feeds:
          propers_1:
            input_mock:
              - {title: 'Test.S01E01.720p-FlexGet'}

          # introduce proper, should be accepted
          propers_2:
            input_mock:
              - {title: 'Test.S01E01.720p.Proper-FlexGet'}

          # introduce non-proper, should not be downloaded
          propers_3:
            input_mock:
              - {title: 'Test.S01E01.FlexGet'}

          # introduce proper at the same time, should nuke non-proper and get proper
          proper_at_first:
            input_mock:
              - {title: 'Foobar.S01E01.720p.FlexGet'}
              - {title: 'Foobar.S01E01.720p.proper.FlexGet'}

          # test a lot of propers at once
          lot_propers:
            input_mock:
              - {title: 'V.2009.S01E01.PROPER.HDTV.A'}
              - {title: 'V.2009.S01E01.PROPER.HDTV.B'}
              - {title: 'V.2009.S01E01.PROPER.HDTV.C'}

          diff_quality_1:
            input_mock:
              - {title: 'Test.S01E02.720p-FlexGet'}

          # low quality proper, should not be accepted
          diff_quality_2:
            input_mock:
              - {title: 'Test.S01E02.HDTV.Proper-FlexGet'}


        """

    def test_lot_propers(self):
        """Series plugin: proper flood"""
        self.execute_feed('lot_propers')
        assert len(self.feed.accepted) == 1, 'should have accepted (only) one of the propers'

    def test_diff_quality_propers(self):
        """Series plugin: proper in different/wrong quality"""
        self.execute_feed('diff_quality_1')
        assert len(self.feed.accepted) == 1
        self.execute_feed('diff_quality_2')
        assert len(self.feed.accepted) == 0, 'should not have accepted lower quality proper'

    def test_propers(self):
        """Series plugin: proper accepted after episode is downloaded"""
        # start with normal download ...
        self.execute_feed('propers_1')
        assert self.feed.find_entry('accepted', title='Test.S01E01.720p-FlexGet'), \
            'Test.S01E01-FlexGet should have been accepted'

        # rejects downloaded
        self.execute_feed('propers_1')
        assert self.feed.find_entry('rejected', title='Test.S01E01.720p-FlexGet'), \
            'Test.S01E01-FlexGet should have been rejected'

        # accepts proper
        self.execute_feed('propers_2')
        assert self.feed.find_entry('accepted', title='Test.S01E01.720p.Proper-FlexGet'), \
            'new undownloaded proper should have been accepted'

        # reject downloaded proper
        self.execute_feed('propers_2')
        #assert not self.feed.accepted, 'downloaded proper accepted'
        assert self.feed.find_entry('rejected', title='Test.S01E01.720p.Proper-FlexGet'), \
            'downloaded proper should have been rejected'

        # reject episode that has been downloaded normally and with proper
        self.execute_feed('propers_3')
        assert self.feed.find_entry('rejected', title='Test.S01E01.FlexGet'), \
            'Test.S01E01.FlexGet should have been rejected'

    def test_proper_available(self):
        """Series plugin: proper available immediately"""
        self.execute_feed('proper_at_first')
        self.dump()
        assert self.feed.find_entry('accepted', title='Foobar.S01E01.720p.proper.FlexGet'), \
            'Foobar.S01E01.720p.proper.FlexGet should have been accepted'

class TestSimilarNames(FlexGetBase):

    # hmm, not very good way to test this .. seriesparser should be tested alone?

    __yaml__ = """
        feeds:
          test:
            input_mock:
              - {title: 'FooBar.S03E01.DSR-FlexGet'}
              - {title: 'FooBar: FirstAlt.S02E01.DSR-FlexGet'}
              - {title: 'FooBar: SecondAlt.S01E01.DSR-FlexGet'}
            series:
              - FooBar
              - "FooBar: FirstAlt"
              - "FooBar: SecondAlt"
    """

    def setup(self):
        FlexGetBase.setUp(self)
        self.execute_feed('test')

    def test_names(self):
        assert self.feed.find_entry('accepted', title='FooBar.S03E01.DSR-FlexGet'), 'Standard failed?'
        assert self.feed.find_entry('accepted', title='FooBar: FirstAlt.S02E01.DSR-FlexGet'), 'FirstAlt failed'
        assert self.feed.find_entry('accepted', title='FooBar: SecondAlt.S01E01.DSR-FlexGet'), 'SecondAlt failed'

class TestDuplicates(FlexGetBase):

    __yaml__ = """

        global: # just cleans log a bit ..
          disable_builtins:
            - seen

        feeds:
          test_dupes:
            input_mock:
              - {title: 'Foo.2009.S02E04.HDTV.XviD-2HD[FlexGet]'}
              - {title: 'Foo.2009.S02E04.HDTV.XviD-2HD[ASDF]'}
            series:
              - Foo 2009

          test_1:
            input_mock:
              - {title: 'Foo.Bar.S02E04.HDTV.XviD-2HD[FlexGet]'}
              - {title: 'Foo.Bar.S02E04.HDTV.XviD-2HD[ASDF]'}
            series:
              - foo bar

          test_2:
            input_mock:
              - {title: 'Foo.Bar.S02E04.XviD-2HD[ASDF]'}
              - {title: 'Foo.Bar.S02E04.HDTV.720p.XviD-2HD[FlexGet]'}
              - {title: 'Foo.Bar.S02E04.DSRIP.XviD-2HD[ASDF]'}
              - {title: 'Foo.Bar.S02E04.HDTV.1080p.XviD-2HD[ASDF]'}
              - {title: 'Foo.Bar.S02E03.HDTV.XviD-FlexGet'}
              - {title: 'Foo.Bar.S02E05.HDTV.XviD-ZZZ'}
              - {title: 'Foo.Bar.S02E05.720p.HDTV.XviD-YYY'}
            series:
              - foo bar

          test_true_dupes:
            input_mock:
              - {title: 'Dupe.S02E04.HDTV.XviD-FlexGet'}
              - {title: 'Dupe.S02E04.HDTV.XviD-FlexGet'}
              - {title: 'Dupe.S02E04.HDTV.XviD-FlexGet'}
            series:
              - dupe
    """

    def test_dupes(self):
        """Series plugin: dupes with same quality"""
        self.execute_feed('test_dupes')
        assert len(self.feed.accepted) == 1, 'accepted both'


    def test_true_dupes(self):
        """Series plugin: true duplicate items"""
        self.execute_feed('test_true_dupes')
        self.dump()
        assert len(self.feed.accepted) == 1, 'should have accepted (only) one'

    def test_downloaded(self):
        """Series plugin: multiple downloaded and new episodes are handled correctly"""

        self.execute_feed('test_1')
        self.execute_feed('test_2')

        # these should be accepted
        accepted = ['Foo.Bar.S02E03.HDTV.XviD-FlexGet', 'Foo.Bar.S02E05.720p.HDTV.XviD-YYY']
        for item in accepted:
            assert self.feed.find_entry('accepted', title=item), \
                '%s should have been accepted' % item

        # these should be rejected
        rejected = ['Foo.Bar.S02E04.XviD-2HD[ASDF]', 'Foo.Bar.S02E04.HDTV.720p.XviD-2HD[FlexGet]', \
                    'Foo.Bar.S02E04.DSRIP.XviD-2HD[ASDF]', 'Foo.Bar.S02E04.HDTV.1080p.XviD-2HD[ASDF]']
        for item in rejected:
            assert self.feed.find_entry('rejected', title=item), \
                '%s should have been rejected' % item


"""
class TestLaterDupes(FlexGetBase):

    __yaml__ = '''
        global:
          series:
            - Foobar:
                watched:
                  season: 2
                  episode: 1
        feeds:

          test_1:
            input_mock:
              - {title: 'FooBar.S02E02.PDTV-FlexGet'}

          test_2:
            input_mock:
              - {title: 'FooBar.S02E03.HDTV-FlexGet'}

          test_3:
            input_mock:
              - {title: 'FooBar.S02E03.HDTV-Bug'}
              - {title: 'FooBar.S02E03.HDTV-FlexGet'}
    '''

    def test_later(self):
        self.execute_feed('test_1')
        assert len(self.feed.accepted) == 1
        self.execute_feed('test_2')
        assert len(self.feed.accepted) == 1
        self.execute_feed('test_3')
        assert len(self.feed.accepted) == 0
        assert False
"""

class TestQualities(FlexGetBase):

    __yaml__ = """
        global:
          disable_builtins: yes
          series:
            - FooBar:
                qualities:
                  - PDTV
                  - 720p
                  - 1080p
        feeds:
          test_1:
            input_mock:
              - {title: 'FooBar.S01E01.PDTV-FlexGet'}
              - {title: 'FooBar.S01E01.1080p-FlexGet'}
              - {title: 'FooBar.S01E01.HR-FlexGet'}
          test_2:
            input_mock:
              - {title: 'FooBar.S01E01.720p-FlexGet'}
    """

    def test_qualities(self):
        self.execute_feed('test_1')

        assert self.feed.find_entry('accepted', title='FooBar.S01E01.PDTV-FlexGet'), \
            'Didn''t accept FooBar.S01E01.PDTV-FlexGet'
        assert self.feed.find_entry('accepted', title='FooBar.S01E01.1080p-FlexGet'), \
            'Didn''t accept FooBar.S01E01.1080p-FlexGet'

        assert not self.feed.find_entry('accepted', title='FooBar.S01E01.HR-FlexGet'), \
            'Accepted FooBar.S01E01.HR-FlexGet'

        self.execute_feed('test_2')

        assert self.feed.find_entry('accepted', title='FooBar.S01E01.720p-FlexGet'), \
            'Didn''t accept FooBar.S01E01.720p-FlexGet'

        # test that it rejects them afterwards

        self.execute_feed('test_1')

        assert self.feed.find_entry('rejected', title='FooBar.S01E01.PDTV-FlexGet'), \
            'Didn''t rehect FooBar.S01E01.PDTV-FlexGet'
        assert self.feed.find_entry('rejected', title='FooBar.S01E01.1080p-FlexGet'), \
            'Didn''t reject FooBar.S01E01.1080p-FlexGet'

        assert not self.feed.find_entry('accepted', title='FooBar.S01E01.HR-FlexGet'), \
            'Accepted FooBar.S01E01.HR-FlexGet'


class TestIdioticNumbering(FlexGetBase):

    __yaml__ = """
        global:
          series:
            - FooBar

        feeds:
          test_1:
            input_mock:
              - {title: 'FooBar.S01E01.PDTV-FlexGet'}
          test_2:
            input_mock:
              - {title: 'FooBar.102.PDTV-FlexGet'}
    """

    def test_idiotic(self):
        self.execute_feed('test_1')
        self.execute_feed('test_2')
        entry = self.feed.find_entry(title='FooBar.102.PDTV-FlexGet')
        assert entry, 'entry not found?'
        print entry
        assert entry['series_season'] == 1, 'season not detected'
        assert entry['series_episode'] == 2, 'episode not detected'


class TestCapitalization(FlexGetBase):

    __yaml__ = """
        feeds:
          test_1:
            input_mock:
              - {title: 'FooBar.S01E01.PDTV-FlexGet'}
            series:
              - FOOBAR
          test_2:
            input_mock:
              - {title: 'FooBar.S01E01.PDTV-FlexGet'}
            series:
              - foobar
    """

    def test_capitalization(self):
        self.execute_feed('test_1')
        assert self.feed.find_entry('accepted', title='FooBar.S01E01.PDTV-FlexGet')
        self.execute_feed('test_2')
        assert self.feed.find_entry('rejected', title='FooBar.S01E01.PDTV-FlexGet')


class TestAutoExact(FlexGetBase):

    __yaml__ = """
        feeds:
          test:
            input_mock:
              - {title: 'ABC.S01E01.PDTV-FlexGet'}
              - {title: 'ABC.LA.S01E01.PDTV-FlexGet'}
              - {title: 'ABC.MIAMI.S01E01.PDTV-FlexGet'}
            series:
              - ABC
              - ABC LA
              - ABC Miami
    """

    def test_auto(self):
        """Series plugin: auto enable exact"""
        self.execute_feed('test')
        assert self.feed.find_entry('accepted', title='ABC.S01E01.PDTV-FlexGet')
        assert self.feed.find_entry('accepted', title='ABC.LA.S01E01.PDTV-FlexGet')
        assert self.feed.find_entry('accepted', title='ABC.MIAMI.S01E01.PDTV-FlexGet')


class TestTimeframe(FlexGetBase):
    __yaml__ = """
        global:
          series:
            - test:
                timeframe: 5 hours
                quality: 720p
        feeds:
          test_no_waiting:
            input_mock:
              - {title: 'Test.S01E01.720p-FlexGet'}

          test_stop_waiting_1:
            input_mock:
              - {title: 'Test.S01E02.HDTV-FlexGet'}

          test_stop_waiting_2:
             input_mock:
               - {title: 'Test.S01E02.720p-FlexGet'}

          test_expires:
            input_mock:
              - {title: 'Test.S01E03.pdtv-FlexGet'}
    """

    def test_no_waiting(self):
        """Series plugin: no timeframe waiting needed"""
        self.execute_feed('test_no_waiting')
        assert self.feed.find_entry('accepted', title='Test.S01E01.720p-FlexGet'), \
            '720p not accepted immediattely'

    def test_stop_waiting(self):
        """Series plugin: timeframe quality appears, stop waiting"""
        self.execute_feed('test_stop_waiting_1')
        assert self.feed.rejected
        self.execute_feed('test_stop_waiting_2')
        assert self.feed.find_entry('accepted', title='Test.S01E02.720p-FlexGet'), \
            '720p should have caused stop waiting'

    def test_expires(self):
        """Series plugin: timeframe expires"""
        # first excecution should not accept anything
        self.execute_feed('test_expires')
        assert not self.feed.accepted
        
        def age(**kwargs):
            from flexget.plugins.filter_series import Series
            from flexget.manager import Session
            import datetime
            session = Session()
            for series in session.query(Series).all():
                for episode in series.episodes:
                    episode.first_seen = datetime.datetime.now() - datetime.timedelta(**kwargs)
            session.commit()
            
        # let 3 hours pass            
        age(hours=3)
        self.execute_feed('test_expires')
        assert not self.feed.accepted, 'expired too soon'
        
        # let another 3 hours pass, should expire now!
        age(hours=6)
        self.execute_feed('test_expires')
        assert self.feed.accepted, 'timeframe didn\'t expire'
