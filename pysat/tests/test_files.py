"""
tests the pysat meta object and code
"""
import pysat
import pandas as pds
from nose.tools import assert_raises, raises
import nose.tools
import pysat.instruments.pysat_testing
import numpy as np
import os
import tempfile
import glob

import sys
if sys.version_info[0] >= 3:
    if sys.version_info[1] < 4:
        import imp
        re_load = imp.reload
    else:
        import importlib
        re_load = importlib.reload
else:
    re_load = reload


def create_dir(inst=None, temporary_file_list=False):
    import os
    import tempfile

    if inst is None:
        # create instrument
        inst = pysat.Instrument(platform='pysat', name='testing',
                                temporary_file_list=temporary_file_list)

    # create data directories
    try:
        os.makedirs(inst.files.data_path)
    except OSError:
        pass
    return


def remove_files(inst=None):
    import os
    import shutil

    # remove any files
    dir = inst.files.data_path
    for the_file in os.listdir(dir):
        if (the_file[0:13] == 'pysat_testing') & \
                (the_file[-19:] == '.pysat_testing_file'):
            file_path = os.path.join(dir, the_file)
            if os.path.isfile(file_path):
                os.unlink(file_path)


# create year doy file set
def create_files(inst, start=None, stop=None, freq='1D', use_doy=True,
                 root_fname=None):

    # create a bunch of files
    if start is None:
        start = pysat.datetime(2009, 1, 1)
    if stop is None:
        stop = pysat.datetime(2013, 12, 31)
    dates = pysat.utils.season_date_range(start, stop, freq=freq)

    if root_fname is None:
        root_fname = 'pysat_testing_junk_{year:04d}_gold_{day:03d}_stuff.pysat_testing_file'
    # create empty file
    for date in dates:
        yr, doy = pysat.utils.getyrdoy(date)
        if use_doy:
            doy = doy
        else:
            doy = date.day

        fname = os.path.join(inst.files.data_path, root_fname.format(year=yr,
                             day=doy, month=date.month, hour=date.hour,
                             min=date.minute, sec=date.second))
        with open(fname, 'w') as f:
            pass        # f.close()


def list_year_doy_files(tag=None, data_path=None, format_str=None):
    if data_path is not None:
        return pysat.Files.from_os(data_path=data_path,
            format_str='pysat_testing_junk_{year:04d}_gold_{day:03d}_stuff.pysat_testing_file')
    else:
        raise ValueError('A directory must be passed to the loading routine.')


def list_files(tag=None, sat_id=None, data_path=None, format_str=None):
    """Return a Pandas Series of every file for chosen satellite data"""

    if format_str is None:
        format_str = 'pysat_testing_junk_{year:04d}_gold_{day:03d}_stuff_{month:02d}_{hour:02d}_{min:02d}_{sec:02d}.pysat_testing_file'

    if tag is not None:
        if tag == '':
            return pysat.Files.from_os(data_path=data_path,
                                       format_str=format_str)
        else:
            raise ValueError('Unrecognized tag name')
    else:
        raise ValueError('A tag name must be passed ')


class TestBasics():

    def __init__(self, temporary_file_list=False):
        self.temporary_file_list = temporary_file_list

    def setup(self):
        """Runs before every method to create a clean testing setup."""
        # store current pysat directory
        self.data_path = pysat.data_dir

        # create temporary directory
        dir_name = tempfile.mkdtemp()
        pysat.utils.set_data_dir(dir_name, store=False)

        self.testInst = pysat.Instrument(inst_module=pysat.instruments.pysat_testing,
                                         clean_level='clean',
                                         temporary_file_list=self.temporary_file_list)
        # create testing directory
        create_dir(self.testInst)

    def teardown(self):
        """Runs after every method to clean up previous testing."""
        remove_files(self.testInst)
        try:
            pysat.utils.set_data_dir(self.data_path, store=False)
        except:
            pass
        del self.testInst

    def test_year_doy_files_direct_call_to_from_os(self):
        # create a bunch of files by year and doy
        start = pysat.datetime(2008, 1, 1)
        stop = pysat.datetime(2009, 12, 31)
        create_files(self.testInst, start, stop, freq='1D')
        # use from_os function to get pandas Series of files and dates
        files = pysat.Files.from_os(data_path=self.testInst.files.data_path,
            format_str='pysat_testing_junk_{year:04d}_gold_{day:03d}_stuff.pysat_testing_file')
        # check overall length
        check1 = len(files) == (365+366)
        # check specific dates
        check2 = pds.to_datetime(files.index[0]) == pysat.datetime(2008, 1, 1)
        check3 = pds.to_datetime(files.index[365]) == \
            pysat.datetime(2008, 12, 31)
        check4 = pds.to_datetime(files.index[-1]) == \
            pysat.datetime(2009, 12, 31)
        assert(check1 & check2 & check3 & check4)

    def test_year_doy_files_no_gap_in_name_direct_call_to_from_os(self):
        # create a bunch of files by year and doy
        start = pysat.datetime(2008, 1, 1)
        stop = pysat.datetime(2009, 12, 31)
        create_files(self.testInst, start, stop, freq='1D',
                     root_fname='pysat_testing_junk_{year:04d}{day:03d}_stuff.pysat_testing_file')
        # use from_os function to get pandas Series of files and dates
        files = pysat.Files.from_os(data_path=self.testInst.files.data_path,
            format_str='pysat_testing_junk_{year:04d}{day:03d}_stuff.pysat_testing_file')
        # check overall length
        check1 = len(files) == (365+366)
        # check specific dates
        check2 = pds.to_datetime(files.index[0]) == pysat.datetime(2008, 1, 1)
        check3 = pds.to_datetime(files.index[365]) == \
            pysat.datetime(2008, 12, 31)
        check4 = pds.to_datetime(files.index[-1]) == \
            pysat.datetime(2009, 12, 31)
        assert(check1 & check2 & check3 & check4)

    def test_year_month_day_files_direct_call_to_from_os(self):
        # create a bunch of files by year and doy
        start = pysat.datetime(2008, 1, 1)
        stop = pysat.datetime(2009, 12, 31)
        create_files(self.testInst, start, stop, freq='1D', use_doy=False,
                     root_fname='pysat_testing_junk_{year:04d}_gold_{day:03d}_stuff_{month:02d}.pysat_testing_file')
        # use from_os function to get pandas Series of files and dates
        files = pysat.Files.from_os(data_path=self.testInst.files.data_path,
            format_str='pysat_testing_junk_{year:04d}_gold_{day:03d}_stuff_{month:02d}.pysat_testing_file')
        # check overall length
        check1 = len(files) == (365+366)
        # check specific dates
        check2 = pds.to_datetime(files.index[0]) == pysat.datetime(2008, 1, 1)
        check3 = pds.to_datetime(files.index[365]) == \
            pysat.datetime(2008, 12, 31)
        check4 = pds.to_datetime(files.index[-1]) == \
            pysat.datetime(2009, 12, 31)
        assert(check1 & check2 & check3 & check4)

    def test_year_month_day_hour_files_direct_call_to_from_os(self):
        # create a bunch of files by year and doy
        start = pysat.datetime(2008, 1, 1)
        stop = pysat.datetime(2009, 12, 31)
        create_files(self.testInst, start, stop, freq='6h',
                     use_doy=False,
                     root_fname='pysat_testing_junk_{year:04d}_gold_{day:03d}_stuff_{month:02d}_{hour:02d}.pysat_testing_file')
        # use from_os function to get pandas Series of files and dates
        files = pysat.Files.from_os(data_path=self.testInst.files.data_path,
            format_str='pysat_testing_junk_{year:04d}_gold_{day:03d}_stuff_{month:02d}_{hour:02d}.pysat_testing_file')
        # check overall length
        check1 = len(files) == (365+366)*4-3
        # check specific dates
        check2 = pds.to_datetime(files.index[0]) == pysat.datetime(2008, 1, 1)
        check3 = pds.to_datetime(files.index[1460]) == \
            pysat.datetime(2008, 12, 31)
        check4 = pds.to_datetime(files.index[-1]) == \
            pysat.datetime(2009, 12, 31)
        assert(check1 & check2 & check3 & check4)

    def test_year_month_day_hour_minute_files_direct_call_to_from_os(self):
        root_fname='pysat_testing_junk_{year:04d}_gold_{day:03d}_stuff_{month:02d}_{hour:02d}{min:02d}.pysat_testing_file'
        # create a bunch of files by year and doy
        start = pysat.datetime(2008, 1, 1)
        stop = pysat.datetime(2008, 1, 4)
        create_files(self.testInst, start, stop, freq='30min',
                     use_doy=False,
                     root_fname=root_fname)
        # use from_os function to get pandas Series of files and dates
        files = pysat.Files.from_os(data_path=self.testInst.files.data_path,
            format_str=root_fname)
        # check overall length
        check1 = len(files) == 145
        # check specific dates
        check2 = pds.to_datetime(files.index[0]) == pysat.datetime(2008, 1, 1)
        check3 = pds.to_datetime(files.index[1]) == \
            pysat.datetime(2008, 1, 1, 0, 30)
        check4 = pds.to_datetime(files.index[10]) == \
            pysat.datetime(2008, 1, 1, 5, 0)
        check5 = pds.to_datetime(files.index[-1]) == pysat.datetime(2008, 1, 4)
        assert(check1 & check2 & check3 & check4 & check5)

    def test_year_month_day_hour_minute_second_files_direct_call_to_from_os(self):
        root_fname='pysat_testing_junk_{year:04d}_gold_{day:03d}_stuff_{month:02d}_{hour:02d}_{min:02d}_{sec:02d}.pysat_testing_file'
        # create a bunch of files by year and doy
        start = pysat.datetime(2008, 1, 1)
        stop = pysat.datetime(2008, 1, 3)
        create_files(self.testInst, start, stop, freq='30s',
                     use_doy=False, root_fname=root_fname)
        # use from_os function to get pandas Series of files and dates
        files = pysat.Files.from_os(data_path=self.testInst.files.data_path,
                                    format_str=root_fname)
        # check overall length
        check1 = len(files) == 5761
        # check specific dates
        check2 = pds.to_datetime(files.index[0]) == pysat.datetime(2008, 1, 1)
        check3 = pds.to_datetime(files.index[1]) == \
            pysat.datetime(2008, 1, 1, 0, 0, 30)
        check4 = pds.to_datetime(files.index[-1]) == \
            pysat.datetime(2008, 1, 3)
        assert(check1 & check2 & check3 & check4)

    def test_year_month_files_direct_call_to_from_os(self):
        # create a bunch of files by year and doy
        start = pysat.datetime(2008, 1, 1)
        stop = pysat.datetime(2009, 12, 31)
        create_files(self.testInst, start, stop, freq='1MS',
                     root_fname='pysat_testing_junk_{year:04d}_gold_stuff_{month:02d}.pysat_testing_file')
        # use from_os function to get pandas Series of files and dates
        files = pysat.Files.from_os(data_path=self.testInst.files.data_path,
            format_str='pysat_testing_junk_{year:04d}_gold_stuff_{month:02d}.pysat_testing_file')
        # check overall length
        check1 = len(files) == 24
        # check specific dates
        check2 = pds.to_datetime(files.index[0]) == pysat.datetime(2008, 1, 1)
        check3 = pds.to_datetime(files.index[11]) == \
            pysat.datetime(2008, 12, 1)
        check4 = pds.to_datetime(files.index[-1]) == \
            pysat.datetime(2009, 12, 1)
        assert(check1 & check2 & check3 & check4)

    def test_instrument_has_no_files(self):
        import pysat.instruments.pysat_testing

        pysat.instruments.pysat_testing.list_files = list_files
        inst = pysat.Instrument(platform='pysat', name='testing',
                                update_files=True)
        re_load(pysat.instruments.pysat_testing)
        assert(inst.files.files.empty)

    def test_instrument_has_files(self):
        import pysat.instruments.pysat_testing

        root_fname='pysat_testing_junk_{year:04d}_gold_{day:03d}_stuff_{month:02d}_{hour:02d}_{min:02d}_{sec:02d}.pysat_testing_file'
        # create a bunch of files by year and doy
        start = pysat.datetime(2007, 12, 31)
        stop = pysat.datetime(2008, 1, 10)
        create_files(self.testInst, start, stop, freq='100min',
                     use_doy=False, root_fname=root_fname)
        # create the same range of dates
        dates = pysat.utils.season_date_range(start, stop, freq='100min')
        pysat.instruments.pysat_testing.list_files = list_files
        inst = pysat.Instrument(platform='pysat', name='testing',
                                update_files=True)
        re_load(pysat.instruments.pysat_testing)
        assert (np.all(inst.files.files.index == dates))


class TestBasicsNoFileListStorage(TestBasics):
    def __init__(self, temporary_file_list=True):
        self.temporary_file_list = temporary_file_list


class TestInstrumentWithFiles():

    def __init__(self, temporary_file_list=False):
        self.temporary_file_list = temporary_file_list

    def setup(self):
        """Runs before every method to create a clean testing setup."""
        # store current pysat directory
        self.data_path = pysat.data_dir
        # create temporary directory
        dir_name = tempfile.mkdtemp()
        pysat.utils.set_data_dir(dir_name, store=False)
        # create testing directory
        create_dir(temporary_file_list=self.temporary_file_list)

        # create a test instrument, make sure it is getting files from
        # filesystem
        re_load(pysat.instruments.pysat_testing)
        pysat.instruments.pysat_testing.list_files = list_files
        # create a bunch of files by year and doy
        self.testInst = pysat.Instrument(inst_module=pysat.instruments.pysat_testing,
                                         clean_level='clean',
                                         temporary_file_list=self.temporary_file_list)

        self.root_fname = 'pysat_testing_junk_{year:04d}_gold_{day:03d}_stuff_{month:02d}_{hour:02d}_{min:02d}_{sec:02d}.pysat_testing_file'
        start = pysat.datetime(2007, 12, 31)
        stop = pysat.datetime(2008, 1, 10)
        create_files(self.testInst, start, stop, freq='100min',
                     use_doy=False, root_fname=self.root_fname)

        self.testInst = pysat.Instrument(inst_module=pysat.instruments.pysat_testing,
                                         clean_level='clean',
                                         update_files=True,
                                         temporary_file_list=self.temporary_file_list)

    def teardown(self):
        """Runs after every method to clean up previous testing."""
        remove_files(self.testInst)
        del self.testInst
        re_load(pysat.instruments.pysat_testing)
        re_load(pysat.instruments)
        # make sure everything about instrument state is restored
        # restore original file list, no files
        pysat.Instrument(inst_module=pysat.instruments.pysat_testing,
                         clean_level='clean',
                         update_files=True,
                         temporary_file_list=self.temporary_file_list)
        pysat.utils.set_data_dir(self.data_path, store=False)

    def test_refresh(self):
        # create new files and make sure that new files are captured
        start = pysat.datetime(2008, 1, 10)
        stop = pysat.datetime(2008, 1, 12)

        create_files(self.testInst, start, stop, freq='100min',
                     use_doy=False, root_fname=self.root_fname)
        start = pysat.datetime(2007, 12, 31)
        dates = pysat.utils.season_date_range(start, stop, freq='100min')
        self.testInst.files.refresh()
        assert (np.all(self.testInst.files.files.index == dates))

    def test_refresh_on_unchanged_files(self):
        start = pysat.datetime(2007, 12, 31)
        stop = pysat.datetime(2008, 1, 10)
        dates = pysat.utils.season_date_range(start, stop, freq='100min')
        self.testInst.files.refresh()
        assert (np.all(self.testInst.files.files.index == dates))

    def test_get_new_files_after_refresh(self):
        # create new files and make sure that new files are captured
        start = pysat.datetime(2008, 1, 11)
        stop = pysat.datetime(2008, 1, 12)

        create_files(self.testInst, start, stop, freq='100min',
                     use_doy=False, root_fname=self.root_fname)
        dates = pysat.utils.season_date_range(start, stop, freq='100min')
        self.testInst.files.refresh()
        new_files = self.testInst.files.get_new()

        assert (np.all(new_files.index == dates))

    def test_get_new_files_after_multiple_refreshes(self):
        # create new files and make sure that new files are captured
        start = pysat.datetime(2008, 1, 11)
        stop = pysat.datetime(2008, 1, 12)

        create_files(self.testInst, start, stop, freq='100min',
                     use_doy=False, root_fname=self.root_fname)
        dates = pysat.utils.season_date_range(start, stop, freq='100min')
        self.testInst.files.refresh()
        self.testInst.files.refresh()
        self.testInst.files.refresh()
        new_files = self.testInst.files.get_new()
        assert (np.all(new_files.index == dates))

    def test_get_new_files_after_adding_files(self):
        # create new files and make sure that new files are captured
        start = pysat.datetime(2008, 1, 11)
        stop = pysat.datetime(2008, 1, 12)

        create_files(self.testInst, start, stop, freq='100min',
                     use_doy=False, root_fname=self.root_fname)
        dates = pysat.utils.season_date_range(start, stop, freq='100min')
        new_files = self.testInst.files.get_new()
        assert (np.all(new_files.index == dates))

    def test_get_new_files_after_adding_files_and_adding_file(self):
        # create new files and make sure that new files are captured
        start = pysat.datetime(2008, 1, 11)
        stop = pysat.datetime(2008, 1, 12)

        create_files(self.testInst, start, stop, freq='100min',
                     use_doy=False, root_fname=self.root_fname)
        dates = pysat.utils.season_date_range(start, stop, freq='100min')
        new_files = self.testInst.files.get_new()

        start = pysat.datetime(2008, 1, 15)
        stop = pysat.datetime(2008, 1, 18)

        create_files(self.testInst, start, stop, freq='100min',
                     use_doy=False, root_fname=self.root_fname)
        dates2 = pysat.utils.season_date_range(start, stop, freq='100min')
        new_files2 = self.testInst.files.get_new()
        assert (np.all(new_files.index == dates) &
                np.all(new_files2.index == dates2))

    def test_get_new_files_after_deleting_files_and_adding_files(self):
        # create new files and make sure that new files are captured
        start = pysat.datetime(2008, 1, 11)
        stop = pysat.datetime(2008, 1, 12)
        dates = pysat.utils.season_date_range(start, stop, freq='100min')

        # remove files, same number as will be added
        to_be_removed = len(dates)
        for the_file in os.listdir(self.testInst.files.data_path):
            if (the_file[0:13] == 'pysat_testing') & \
                    (the_file[-19:] == '.pysat_testing_file'):
                file_path = os.path.join(self.testInst.files.data_path,
                                         the_file)
                if os.path.isfile(file_path) & (to_be_removed > 0):
                    # print(file_path)
                    to_be_removed -= 1
                    os.unlink(file_path)
        # add new files
        create_files(self.testInst, start, stop, freq='100min',
                     use_doy=False, root_fname=self.root_fname)
        # get new files
        new_files = self.testInst.files.get_new()

        assert (np.all(new_files.index == dates))

    def test_files_non_standard_pysat_directory(self):
        # create new files and make sure that new files are captured
        start = pysat.datetime(2008, 1, 11)
        stop = pysat.datetime(2008, 1, 15)
        dates = pysat.utils.season_date_range(start, stop, freq='100min')

        self.testInst = pysat.Instrument(inst_module=pysat.instruments.pysat_testing,
                                         clean_level='clean',
                                         sat_id='hello',
                                         directory_format='pysat_testing_{tag}_{sat_id}',
                                         update_files=True,
                                         temporary_file_list=self.temporary_file_list)
        # add new files
        create_dir(self.testInst)
        remove_files(self.testInst)
        create_files(self.testInst, start, stop, freq='100min',
                     use_doy=False, root_fname=self.root_fname)

        self.testInst = pysat.Instrument(inst_module=pysat.instruments.pysat_testing,
                                         clean_level='clean',
                                         sat_id='hello',
                                         directory_format='pysat_testing_{tag}_{sat_id}',
                                         update_files=True,
                                         temporary_file_list=self.temporary_file_list)

        # get new files
        new_files = self.testInst.files.get_new()
        assert (np.all(self.testInst.files.files.index == dates) &
                np.all(new_files.index == dates))

    def test_files_non_standard_file_format_template(self):
        # create new files and make sure that new files are captured
        start = pysat.datetime(2008, 1, 11)
        stop = pysat.datetime(2008, 1, 15)
        dates = pysat.utils.season_date_range(start, stop, freq='1D')

        # clear out old files, create new ones
        remove_files(self.testInst)
        create_files(self.testInst, start, stop, freq='1D',
                     use_doy=False,
                     root_fname='pysat_testing_unique_junk_{year:04d}_gold_{day:03d}_stuff.pysat_testing_file')

        pysat.instruments.pysat_testing.list_files = list_files
        self.testInst = pysat.Instrument(inst_module=pysat.instruments.pysat_testing,
                                         clean_level='clean',
                                         file_format='pysat_testing_unique_junk_{year:04d}_gold_{day:03d}_stuff.pysat_testing_file',
                                         update_files=True,
                                         temporary_file_list=self.temporary_file_list)

        assert (np.all(self.testInst.files.files.index == dates))

    @raises(ValueError)
    def test_files_non_standard_file_format_template_misformatted(self):

        pysat.instruments.pysat_testing.list_files = list_files
        self.testInst = pysat.Instrument(inst_module=pysat.instruments.pysat_testing,
                                         clean_level='clean',
                                         file_format='pysat_testing_unique_junk_stuff.pysat_testing_file',
                                         update_files=True,
                                         temporary_file_list=self.temporary_file_list)

    @raises(ValueError)
    def test_files_non_standard_file_format_template_misformatted_2(self):

        pysat.instruments.pysat_testing.list_files = list_files
        self.testInst = pysat.Instrument(inst_module=pysat.instruments.pysat_testing,
                                         clean_level='clean',
                                         file_format=15,
                                         update_files=True,
                                         temporary_file_list=self.temporary_file_list)


class TestInstrumentWithFilesNoFileListStorage(TestInstrumentWithFiles):
    def __init__(self, temporary_file_list=True):
        self.temporary_file_list = temporary_file_list


# create year doy file set with multiple versions
def create_versioned_files(inst, start=None, stop=None, freq='1D',
                           use_doy=True, root_fname=None):
    # create a bunch of files
    if start is None:
        start = pysat.datetime(2009, 1, 1)
    if stop is None:
        stop = pysat.datetime(2013, 12, 31)
    dates = pysat.utils.season_date_range(start, stop, freq=freq)

    versions = np.array([1, 2])
    revisions = np.array([0, 1])

    if root_fname is None:
        root_fname = 'pysat_testing_junk_{year:04d}_{month:02d}_{day:03d}{hour:02d}{min:02d}{sec:02d}_stuff_{version:02d}_{revision:03d}.pysat_testing_file'
    # create empty file
    for date in dates:
        for version in versions:
            for revision in revisions:
                yr, doy = pysat.utils.getyrdoy(date)
                if use_doy:
                    doy = doy
                else:
                    doy = date.day

                fname = os.path.join(inst.files.data_path,
                                     root_fname.format(year=yr,
                                                       day=doy,
                                                       month=date.month,
                                                       hour=date.hour,
                                                       min=date.minute,
                                                       sec=date.second,
                                                       version=version,
                                                       revision=revision))
                with open(fname, 'w') as f:
                    pass


def list_versioned_files(tag=None, sat_id=None, data_path=None,
                         format_str=None):
    """Return a Pandas Series of every file for chosen satellite data"""

    if format_str is None:
        format_str = 'pysat_testing_junk_{year:04d}_{month:02d}_{day:03d}{hour:02d}{min:02d}{sec:02d}_stuff_{version:02d}_{revision:03d}.pysat_testing_file'
    if tag is not None:
        if tag == '':
            return pysat.Files.from_os(data_path=data_path,
                                       format_str=format_str)
        else:
            raise ValueError('Unrecognized tag name')
    else:
        raise ValueError('A tag name must be passed ')


class TestInstrumentWithVersionedFiles():
    def __init__(self, temporary_file_list=False):
        self.temporary_file_list = temporary_file_list

    def setup(self):
        """Runs before every method to create a clean testing setup."""
        # store current pysat directory
        self.data_path = pysat.data_dir
        # create temporary directory
        dir_name = tempfile.gettempdir()
        pysat.utils.set_data_dir(dir_name, store=False)
        # create testing directory
        create_dir(temporary_file_list=self.temporary_file_list)

        # create a test instrument, make sure it is getting files from filesystem
        re_load(pysat.instruments.pysat_testing)
        # self.stored_files_fcn = pysat.instruments.pysat_testing.list_files
        pysat.instruments.pysat_testing.list_files = list_versioned_files
        # create a bunch of files by year and doy
        self.testInst = pysat.Instrument(inst_module=pysat.instruments.pysat_testing,
                                         clean_level='clean',
                                         temporary_file_list=self.temporary_file_list)

        self.root_fname = 'pysat_testing_junk_{year:04d}_{month:02d}_{day:03d}{hour:02d}{min:02d}{sec:02d}_stuff_{version:02d}_{revision:03d}.pysat_testing_file'
        start = pysat.datetime(2007, 12, 31)
        stop = pysat.datetime(2008, 1, 10)
        create_versioned_files(self.testInst, start, stop, freq='100min',
                               use_doy=False, root_fname=self.root_fname)

        self.testInst = pysat.Instrument(inst_module=pysat.instruments.pysat_testing,
                                         clean_level='clean',
                                         update_files=True,
                                         temporary_file_list=self.temporary_file_list)

    def teardown(self):
        """Runs after every method to clean up previous testing."""
        remove_files(self.testInst)
        del self.testInst
        re_load(pysat.instruments.pysat_testing)
        re_load(pysat.instruments)
        # make sure everything about instrument state is restored
        # restore original file list, no files
        pysat.Instrument(inst_module=pysat.instruments.pysat_testing,
                         clean_level='clean',
                         update_files=True,
                         temporary_file_list=self.temporary_file_list)
        pysat.utils.set_data_dir(self.data_path, store=False)

    def test_refresh(self):
        # create new files and make sure that new files are captured
        # files slready exist from 2007, 12, 31 through to 10th
        start = pysat.datetime(2008, 1, 10)
        stop = pysat.datetime(2008, 1, 12)
        create_versioned_files(self.testInst, start, stop, freq='100min',
                               use_doy=False,
                               root_fname=self.root_fname)
        # create list of dates for all files that should be there
        start = pysat.datetime(2007, 12, 31)
        dates = pysat.utils.season_date_range(start, stop, freq='100min')
        # update instrument file list
        self.testInst.files.refresh()
        assert (np.all(self.testInst.files.files.index == dates))

    def test_refresh_on_unchanged_files(self):

        start = pysat.datetime(2007, 12, 31)
        stop = pysat.datetime(2008, 1, 10)
        dates = pysat.utils.season_date_range(start, stop, freq='100min')
        self.testInst.files.refresh()
        assert (np.all(self.testInst.files.files.index == dates))

    def test_get_new_files_after_refresh(self):
        # create new files and make sure that new files are captured
        start = pysat.datetime(2008, 1, 11)
        stop = pysat.datetime(2008, 1, 12)

        create_versioned_files(self.testInst, start, stop, freq='100min',
                               use_doy=False, root_fname=self.root_fname)
        dates = pysat.utils.season_date_range(start, stop, freq='100min')
        self.testInst.files.refresh()
        new_files = self.testInst.files.get_new()

        assert (np.all(new_files.index == dates))

    def test_get_new_files_after_multiple_refreshes(self):
        # create new files and make sure that new files are captured
        start = pysat.datetime(2008, 1, 11)
        stop = pysat.datetime(2008, 1, 12)

        create_versioned_files(self.testInst, start, stop, freq='100min',
                               use_doy=False, root_fname=self.root_fname)
        dates = pysat.utils.season_date_range(start, stop, freq='100min')
        self.testInst.files.refresh()
        self.testInst.files.refresh()
        self.testInst.files.refresh()
        new_files = self.testInst.files.get_new()

        assert (np.all(new_files.index == dates))

    def test_get_new_files_after_adding_files(self):
        # create new files and make sure that new files are captured
        start = pysat.datetime(2008, 1, 11)
        stop = pysat.datetime(2008, 1, 12)

        create_versioned_files(self.testInst, start, stop, freq='100min',
                               use_doy=False, root_fname=self.root_fname)
        dates = pysat.utils.season_date_range(start, stop, freq='100min')
        new_files = self.testInst.files.get_new()
        assert (np.all(new_files.index == dates))

    def test_get_new_files_after_adding_files_and_adding_file(self):
        # create new files and make sure that new files are captured
        start = pysat.datetime(2008, 1, 11)
        stop = pysat.datetime(2008, 1, 12)

        create_versioned_files(self.testInst, start, stop, freq='100min',
                               use_doy=False, root_fname=self.root_fname)
        dates = pysat.utils.season_date_range(start, stop, freq='100min')
        new_files = self.testInst.files.get_new()

        start = pysat.datetime(2008, 1, 15)
        stop = pysat.datetime(2008, 1, 18)

        create_versioned_files(self.testInst, start, stop, freq='100min',
                               use_doy=False, root_fname=self.root_fname)
        dates2 = pysat.utils.season_date_range(start, stop, freq='100min')
        new_files2 = self.testInst.files.get_new()
        assert (np.all(new_files.index == dates) &
                np.all(new_files2.index == dates2))

    def test_get_new_files_after_deleting_files_and_adding_files(self):
        # create new files and make sure that new files are captured
        start = pysat.datetime(2008, 1, 11)
        stop = pysat.datetime(2008, 1, 12)
        dates = pysat.utils.season_date_range(start, stop, freq='100min')
        # remove files, same number as will be added
        to_be_removed = len(dates)
        for the_file in os.listdir(self.testInst.files.data_path):
            if (the_file[0:13] == 'pysat_testing') & \
                    (the_file[-19:] == '.pysat_testing_file'):
                file_path = os.path.join(self.testInst.files.data_path,
                                         the_file)
                if os.path.isfile(file_path) & (to_be_removed > 0):
                    to_be_removed -= 1
                    # Remove all versions of the file
                    # otherwise, previous versions will look like new files
                    pattern = '_'.join(file_path.split('_')[0:7]) + \
                        '*.pysat_testing_file'
                    map(os.unlink, glob.glob(pattern))
                    #os.unlink(file_path)
        # add new files
        create_versioned_files(self.testInst, start, stop, freq='100min',
                               use_doy=False, root_fname=self.root_fname)
        # get new files
        new_files = self.testInst.files.get_new()

        assert (np.all(new_files.index == dates))

    def test_files_non_standard_pysat_directory(self):
        # create new files and make sure that new files are captured
        start = pysat.datetime(2008, 1, 11)
        stop = pysat.datetime(2008, 1, 15)
        dates = pysat.utils.season_date_range(start, stop, freq='100min')
        pysat.instruments.pysat_testing.list_files = list_versioned_files
        self.testInst = pysat.Instrument(inst_module=pysat.instruments.pysat_testing,
                                         clean_level='clean',
                                         sat_id='hello',
                                         directory_format='pysat_testing_{tag}_{sat_id}',
                                         update_files=True,
                                         temporary_file_list=self.temporary_file_list)
        # add new files
        create_dir(self.testInst)
        remove_files(self.testInst)
        create_versioned_files(self.testInst, start, stop, freq='100min',
                               use_doy=False, root_fname=self.root_fname)

        self.testInst = pysat.Instrument(inst_module=pysat.instruments.pysat_testing,
                                         clean_level='clean',
                                         sat_id='hello',
                                         directory_format='pysat_testing_{tag}_{sat_id}',
                                         update_files=True,
                                         temporary_file_list=self.temporary_file_list)

        # get new files
        new_files = self.testInst.files.get_new()
        assert (np.all(self.testInst.files.files.index == dates) &
                np.all(new_files.index == dates))

    def test_files_non_standard_file_format_template(self):
        # create new files and make sure that new files are captured
        start = pysat.datetime(2008, 1, 11)
        stop = pysat.datetime(2008, 1, 15)
        dates = pysat.utils.season_date_range(start, stop, freq='1D')

        # clear out old files, create new ones
        remove_files(self.testInst)
        create_versioned_files(self.testInst, start, stop, freq='1D',
                               use_doy=False,
                               root_fname='pysat_testing_unique_{version:02d}_{revision:03d}_{year:04d}_g_{day:03d}_st.pysat_testing_file')

        pysat.instruments.pysat_testing.list_files = list_versioned_files
        self.testInst = pysat.Instrument(inst_module=pysat.instruments.pysat_testing,
                                         clean_level='clean',
                                         file_format='pysat_testing_unique_{version:02d}_{revision:03d}_{year:04d}_g_{day:03d}_st.pysat_testing_file',
                                         update_files=True,
                                         temporary_file_list=self.temporary_file_list)
        assert (np.all(self.testInst.files.files.index == dates))

    def test_files_when_duplicates_forced(self):
        # create new files and make sure that new files are captured
        start = pysat.datetime(2008, 1, 11)
        stop = pysat.datetime(2008, 1, 15)
        dates = pysat.utils.season_date_range(start, stop, freq='1D')

        # clear out old files, create new ones
        remove_files(self.testInst)
        create_versioned_files(self.testInst, start, stop, freq='1D',
                               use_doy=False,
                               root_fname='pysat_testing_unique_{version:02d}_{revision:03d}_{year:04d}_g_{day:03d}_st.pysat_testing_file')

        pysat.instruments.pysat_testing.list_files = list_files
        self.testInst = pysat.Instrument(inst_module=pysat.instruments.pysat_testing,
                                         clean_level='clean',
                                         file_format='pysat_testing_unique_??_???_{year:04d}_g_{day:03d}_st.pysat_testing_file',
                                         update_files=True,
                                         temporary_file_list=self.temporary_file_list)
        assert (np.all(self.testInst.files.files.index == dates))


class TestInstrumentWithVersionedFilesNoFileListStorage(TestInstrumentWithVersionedFiles):
    def __init__(self, temporary_file_list=True):
        self.temporary_file_list = temporary_file_list
