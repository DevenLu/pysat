"""
tests the pysat utils area
"""
import os
import numpy as np
import pandas as pds
import nose.tools
from nose.tools import assert_raises, raises
import tempfile
import pysat
import pysat.instruments.pysat_testing

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



#########
## basic yrdoy tests
def test_getyrdoy_1():
    """Test the date to year, day of year code functionality"""
    date = pds.datetime(2009, 1, 1)
    yr, doy = pysat.utils.getyrdoy(date)
    assert ((yr == 2009) & (doy == 1))

def test_getyrdoy_leap_year():
    """Test the date to year, day of year code functionality (leap_year)"""
    date = pds.datetime(2008,12,31)
    yr, doy = pysat.utils.getyrdoy(date)
    assert ((yr == 2008) & (doy == 366)) 

####################3
# test netCDF fexport ile support

def prep_dir(inst=None):
    import os
    import shutil

    if inst is None:
        inst = pysat.Instrument(platform='pysat', name='testing')
    # create data directories
    try:
        os.makedirs(inst.files.data_path)
        #print ('Made Directory')
    except OSError:
        pass

def remove_files(inst):
    # remove any files
    dir = inst.files.data_path
    for the_file in os.listdir(dir):
        if (the_file[0:13] == 'pysat_testing') & (the_file[-19:] ==
                                                  '.pysat_testing_file'):
            file_path = os.path.join(dir, the_file)
            if os.path.isfile(file_path):
                os.unlink(file_path)

class TestBasics():
    def setup(self):
        """Runs before every method to create a clean testing setup."""        
        # store current pysat directory
        self.data_path = pysat.data_dir
        
        # create temporary directory  
        dir_name = tempfile.mkdtemp()
        pysat.utils.set_data_dir(dir_name, store=False)

        self.testInst = pysat.Instrument(inst_module=pysat.instruments.pysat_testing, 
                                        clean_level='clean')
        # create testing directory
        prep_dir(self.testInst)

        # Add testing data for circular statistics
        self.test_angles = np.array([340.0, 348.0, 358.9, 0.5, 5.0, 9.87])
        self.test_nan = [340.0, 348.0, 358.9, 0.5, 5.0, 9.87, np.nan]
        self.circ_kwargs = {"high":360.0, "low":0.0}
        self.deg_units = ["deg", "degree", "degrees", "rad", "radian",
                          "radians", "h", "hr", "hrs", "hours"]
        self.dist_units = ["m", "km", "cm"]
        self.vel_units = ["m/s", "cm/s", "km/s"]

        # Add longitude to the test instrument
        ones = np.ones(shape=len(self.test_angles))
        time = pysat.utils.create_datetime_index(year=ones*2001, month=ones,
                                                 uts=np.arange(0.0, len(ones),
                                                               1.0))


        self.testInst.data = pds.DataFrame(np.array([time, self.test_angles]).transpose(), index=time, columns=["time", "longitude"])


    def teardown(self):
        """Runs after every method to clean up previous testing."""
        remove_files(self.testInst)
        try:
            pysat.utils.set_data_dir(self.data_path, store=False)
        except:
            pass
        del self.testInst, self.test_angles, self.test_nan, self.circ_kwargs
        del self.deg_units, self.dist_units, self.vel_units
    
    def test_basic_writing_and_reading_netcdf4_default_format(self):
        # create a bunch of files by year and doy
        from unittest.case import SkipTest
        try:
            import netCDF4
        except ImportError:
            raise SkipTest
  
        prep_dir(self.testInst)            
        outfile = os.path.join(self.testInst.files.data_path, 'test_ncdf.nc')
        self.testInst.load(2009,1)
        self.testInst.to_netcdf4(outfile)

        loaded_inst, meta = pysat.utils.load_netcdf4(outfile)
        self.testInst.data = self.testInst.data.reindex_axis(sorted(self.testInst.data.columns), axis=1)
        loaded_inst = loaded_inst.reindex_axis(sorted(loaded_inst.columns), axis=1)

        for key in self.testInst.data.columns:
            print('Testing Data Equality to filesystem and back ', key)
            assert(np.all(self.testInst[key] == loaded_inst[key]))
        # assert(np.all(self.testInst.data == loaded_inst))

    def test_basic_writing_and_reading_netcdf4_default_format_w_compression(self):
        # create a bunch of files by year and doy
        from unittest.case import SkipTest
        try:
            import netCDF4
        except ImportError:
            raise SkipTest

        prep_dir(self.testInst)
        outfile = os.path.join(self.testInst.files.data_path, 'test_ncdf.nc')
        self.testInst.load(2009, 1)
        self.testInst.to_netcdf4(outfile, zlib=True)

        loaded_inst, meta = pysat.utils.load_netcdf4(outfile)
        self.testInst.data = self.testInst.data.reindex_axis(sorted(self.testInst.data.columns), axis=1)
        loaded_inst = loaded_inst.reindex_axis(sorted(loaded_inst.columns), axis=1)

        for key in self.testInst.data.columns:
            print('Testing Data Equality to filesystem and back ', key)
            assert (np.all(self.testInst[key] == loaded_inst[key]))
            # assert(np.all(self.testInst.data == loaded_inst))

    def test_basic_writing_and_reading_netcdf4_default_format_w_weird_epoch_name(self):
        # create a bunch of files by year and doy
        from unittest.case import SkipTest
        try:
            import netCDF4
        except ImportError:
            raise SkipTest

        prep_dir(self.testInst)
        outfile = os.path.join(self.testInst.files.data_path, 'test_ncdf.nc')
        self.testInst.load(2009, 1)
        self.testInst.to_netcdf4(outfile, epoch_name='Santa')

        loaded_inst, meta = pysat.utils.load_netcdf4(outfile, epoch_name='Santa')
        self.testInst.data = self.testInst.data.reindex_axis(sorted(self.testInst.data.columns), axis=1)
        loaded_inst = loaded_inst.reindex_axis(sorted(loaded_inst.columns), axis=1)

        for key in self.testInst.data.columns:
            print('Testing Data Equality to filesystem and back ', key)
            assert (np.all(self.testInst[key] == loaded_inst[key]))

    def test_basic_writing_and_reading_netcdf4_default_format_higher_order(self):
        # create a bunch of files by year and doy
        from unittest.case import SkipTest
        try:
            import netCDF4
        except ImportError:
            raise SkipTest
        test_inst = pysat.Instrument('pysat', 'testing2d')    
        prep_dir(test_inst)
        outfile = os.path.join(test_inst.files.data_path, 'test_ncdf.nc')
        test_inst.load(2009,1)
        test_inst.to_netcdf4(outfile)
        loaded_inst, meta = pysat.utils.load_netcdf4(outfile)
        test_inst.data = test_inst.data.reindex_axis(sorted(test_inst.data.columns), axis=1)
        loaded_inst = loaded_inst.reindex_axis(sorted(loaded_inst.columns), axis=1)
        prep_dir(test_inst)
        
        # test Series of DataFrames
        test_list = []
        #print (loaded_inst.columns)
        for frame1, frame2 in zip(test_inst.data['profiles'],
                                  loaded_inst['profiles']):
            test_list.append(np.all((frame1 == frame2).all()))
        loaded_inst.drop('profiles', inplace=True, axis=1) 
        test_inst.data.drop('profiles', inplace=True, axis=1)   

        # second series of frames
        for frame1, frame2 in zip(test_inst.data['alt_profiles'],
                                  loaded_inst['alt_profiles']):
            test_list.append(np.all((frame1 == frame2).all()))
        loaded_inst.drop('alt_profiles', inplace=True, axis=1)
        test_inst.data.drop('alt_profiles', inplace=True, axis=1)

        # check series of series
        for frame1, frame2 in zip(test_inst.data['series_profiles'],
                                  loaded_inst['series_profiles']):
            test_list.append(np.all((frame1 == frame2).all()))

        # print (test_inst['series_profiles'][0], loaded_inst['series_profiles'][0])
        # print (type(test_inst['series_profiles'][0]), type(loaded_inst['series_profiles'][0]))
        # print ( (test_inst['series_profiles'][0]) == (loaded_inst['series_profiles'][0]) )
        loaded_inst.drop('series_profiles', inplace=True, axis=1)
        test_inst.data.drop('series_profiles', inplace=True, axis=1)
        
        assert(np.all((test_inst.data == loaded_inst).all()))
        assert np.all(test_list)

    def test_basic_writing_and_reading_netcdf4_default_format_higher_order_w_Compression(self):
        # create a bunch of files by year and doy
        from unittest.case import SkipTest
        try:
            import netCDF4
        except ImportError:
            raise SkipTest
        test_inst = pysat.Instrument('pysat', 'testing2d')
        prep_dir(test_inst)
        outfile = os.path.join(test_inst.files.data_path, 'test_ncdf.nc')
        test_inst.load(2009, 1)
        test_inst.to_netcdf4(outfile, zlib=True)
        loaded_inst, meta = pysat.utils.load_netcdf4(outfile)
        test_inst.data = test_inst.data.reindex_axis(sorted(test_inst.data.columns), axis=1)
        loaded_inst = loaded_inst.reindex_axis(sorted(loaded_inst.columns), axis=1)
        prep_dir(test_inst)

        # test Series of DataFrames
        test_list = []
        # print (loaded_inst.columns)
        # print (loaded_inst)
        for frame1, frame2 in zip(test_inst.data['profiles'],
                                  loaded_inst['profiles']):
            test_list.append(np.all((frame1 == frame2).all()))
        loaded_inst.drop('profiles', inplace=True, axis=1)
        test_inst.data.drop('profiles', inplace=True, axis=1)
        
        # second series of frames
        for frame1, frame2 in zip(test_inst.data['alt_profiles'],
                                  loaded_inst['alt_profiles']):
            test_list.append(np.all((frame1 == frame2).all()))
        loaded_inst.drop('alt_profiles', inplace=True, axis=1)
        test_inst.data.drop('alt_profiles', inplace=True, axis=1)

        # check series of series
        for frame1, frame2 in zip(test_inst.data['series_profiles'],
                                  loaded_inst['series_profiles']):
            test_list.append(np.all((frame1 == frame2).all()))
            # print frame1, frame2
        loaded_inst.drop('series_profiles', inplace=True, axis=1)
        test_inst.data.drop('series_profiles', inplace=True, axis=1)
        
        assert (np.all((test_inst.data == loaded_inst).all()))
        # print (test_list)
        assert np.all(test_list)
        
    # def test_basic_writing_and_reading_netcdf4_multiple_formats(self):
    #     # create a bunch of files by year and doy
    #     from unittest.case import SkipTest
    #     try:
    #         import netCDF4
    #     except ImportError:
    #         raise SkipTest
    #
    #     outfile = os.path.join(self.testInst.files.data_path, 'test_ncdf.nc')
    #     self.testInst.load(2009,1)
    #     check = []
    #     for format in ['NETCDF3_CLASSIC','NETCDF3_64BIT', 'NETCDF4_CLASSIC', 'NETCDF4']:
    #         self.testInst.to_netcdf4(outfile, file_format=format)
    #         loaded_inst, meta = pysat.utils.load_netcdf4(outfile, file_format=format)
    #         self.testInst.data = self.testInst.data.reindex_axis(sorted(self.testInst.data.columns), axis=1)
    #         loaded_inst = loaded_inst.reindex_axis(sorted(loaded_inst.columns), axis=1)
    #         check.append(np.all(self.testInst.data == loaded_inst))
    #         print(loaded_inst['string_dummy'])
    #
    #     assert(np.all(check))

    #######################
    ### test pysat data dir options
    def test_set_data_dir(self):
        saved_dir = self.data_path
        # update data_dir
        pysat.utils.set_data_dir('.')
        check1 = (pysat.data_dir == '.')
        if saved_dir is not '':
            pysat.utils.set_data_dir(saved_dir)
            check2 = (pysat.data_dir == saved_dir)
        else:
            check2 = True
        assert check1 & check2

    def test_set_data_dir_no_store(self):
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

        saved_dir = self.data_path #pysat.data_dir
        # update data_dir
        pysat.utils.set_data_dir('.', store=False)
        check1 = (pysat.data_dir == '.')
        pysat._files = re_load(pysat._files)
        pysat._instrument = re_load(pysat._instrument)
        re_load(pysat)

        check2 = (pysat.data_dir == saved_dir)
        if saved_dir is not '':
            pysat.utils.set_data_dir(saved_dir, store=False)
            check3 = (pysat.data_dir == saved_dir)
        else:
            check3 = True

        assert check1 & check2 & check3        
                        
    def test_initial_pysat_load(self):
        import shutil
        saved = False
        try:
            root = os.path.join(os.getenv('HOME'), '.pysat')
            new_root = os.path.join(os.getenv('HOME'), '.saved_pysat')
            shutil.move(root, new_root)
            saved = True
        except:
            pass
            
        re_load(pysat)
        
        try:
            if saved:
                # remove directory, trying to be careful
                os.remove(os.path.join(root, 'data_path.txt'))
                os.rmdir(root)
                shutil.move(new_root, root)
        except:
            pass

        assert True
    
    def test_circmean(self):
        """ Test custom circular mean."""
        from scipy import stats

        ref_mean = stats.circmean(self.test_angles, **self.circ_kwargs)
        test_mean = pysat.utils.nan_circmean(self.test_angles,
                                             **self.circ_kwargs)
        ans1 = ref_mean == test_mean

        assert ans1

    def test_circstd_nan(self):
        """ Test custom circular mean with NaN."""
        from scipy import stats

        ref_mean = stats.circmean(self.test_angles, **self.circ_kwargs)
        ref_nan = stats.circmean(self.test_nan, **self.circ_kwargs)
        test_nan = pysat.utils.nan_circmean(self.test_nan, **self.circ_kwargs)

        assert np.isnan(ref_nan)
        assert ref_mean == test_nan

    def test_circstd(self):
        """ Test custom circular std."""
        from scipy import stats

        ref_std = stats.circstd(self.test_angles, **self.circ_kwargs)
        test_std = pysat.utils.nan_circstd(self.test_angles, **self.circ_kwargs)
        ans1 = ref_std == test_std

        assert ans1

    def test_circstd_nan(self):
        """ Test custom circular std with NaN."""
        from scipy import stats

        ref_std = stats.circstd(self.test_angles, **self.circ_kwargs)
        ref_nan = stats.circstd(self.test_nan, **self.circ_kwargs)
        test_nan = pysat.utils.nan_circstd(self.test_nan, **self.circ_kwargs)

        assert np.isnan(ref_nan)
        assert ref_std == test_nan

    def test_adjust_cyclic_data_default(self):
        """ Test adjust_cyclic_data with default range """

        test_in = np.radians(self.test_angles) - np.pi
        test_angles = pysat.utils.adjust_cyclic_data(test_in)

        assert test_angles.max() < 2.0 * np.pi
        assert test_angles.min() >= 0.0

    def test_adjust_cyclic_data_custom(self):
        """ Test adjust_cyclic_data with a custom range """

        test_angles = pysat.utils.adjust_cyclic_data(self.test_angles,
                                                     high=180.0, low=-180.0)

        assert test_angles.max() < 180.0
        assert test_angles.min() >= -180.0

    def test_update_longitude(self):
        """Test update_longitude """

        pysat.utils.update_longitude(self.testInst, lon_name="longitude")

        assert np.all(self.testInst.data['longitude'] < 180.0)
        assert np.all(self.testInst.data['longitude'] >= -180.0)

    def test_bad_lon_name_update_longitude(self):
        """Test update_longitude with a bad longitude name"""

        assert_raises(ValueError, pysat.utils.update_longitude,
                      self.testInst)

    def test_scale_units_same(self):
        """ Test scale_units when both units are the same """

        scale = pysat.utils.scale_units("happy", "happy")

        assert scale == 1.0

    def test_scale_units_angles(self):
        """Test scale_units for angles """

        for out_unit in self.deg_units:
            scale = pysat.utils.scale_units(out_unit, "deg")

            if out_unit.find("deg") == 0:
                assert scale == 1.0
            elif out_unit.find("rad") == 0:
                assert scale == np.pi / 180.0
            else:
                assert scale == 1.0 / 15.0

    def test_scale_units_dist(self):
        """Test scale_units for distances """
        
        for out_unit in self.dist_units:
            scale = pysat.utils.scale_units(out_unit, "m")

            if out_unit == "m":
                assert scale == 1.0
            elif out_unit.find("km") == 0:
                assert scale == 0.001
            else:
                assert scale == 100.0

    def test_scale_units_vel(self):
        """Test scale_units for velocities """
        
        for out_unit in self.vel_units:
            scale = pysat.utils.scale_units(out_unit, "m/s")

            if out_unit == "m/s":
                assert scale == 1.0
            elif out_unit.find("km/s") == 0:
                assert scale == 0.001
            else:
                assert scale == 100.0

    def test_scale_units_bad(self):
        """Test scale_units for mismatched input"""

        assert_raises(ValueError, pysat.utils.scale_units, "happy", "m")
        assert_raises(ValueError, pysat.utils.scale_units, "m", "happy")
        assert_raises(ValueError, pysat.utils.scale_units, "m", "m/s")
        assert_raises(ValueError, pysat.utils.scale_units, "m", "deg")
        assert_raises(ValueError, pysat.utils.scale_units, "h", "km/s")
