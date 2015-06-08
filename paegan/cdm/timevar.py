# encoding: utf-8

# Pulled from Octant
# http://code.google.com/p/octant/source/browse/trunk/octant/ocean/time.py
# Copyright (c) 2006 Robert Hetland & Richard Hofmeister

import numpy as np
import netCDF4, datetime
from dateutil.parser import parse
import bisect
import pytz

# Same basedate as matplotlib: http://matplotlib.org/api/dates_api.html#matplotlib.dates.num2date
timevar_units = 'days since 0001-01-01 00:00:00'


def date2num(python_datetime, tzinfo=None):
    tz = tzinfo or pytz.utc
    try:
        python_datetime[0]
    except TypeError:
        python_datetime = [python_datetime]
    return netCDF4.date2num([ d.astimezone(tz).replace(tzinfo=None) for d in python_datetime ], timevar_units, calendar='proleptic_gregorian')


def num2date(indatenum, inunits, tzinfo=None):
    tz = tzinfo or pytz.utc
    return np.vectorize(lambda x: x.replace(tzinfo=tz))(netCDF4.num2date(indatenum, inunits, calendar='proleptic_gregorian'))


class Timevar(np.ndarray):

    _unit2sec={}
    _unit2sec['seconds'] = 1.0
    _unit2sec['minutes'] = 60.0
    _unit2sec['hours'] = 3600.0
    _unit2sec['days'] = 3600.0*24.0
    _unit2sec['weeks'] = 3600.0*24.0*7.0
    _unit2sec['years'] = 3600.0*24.0*365.242198781 #ref to udunits

    _sec2unit={}
    _sec2unit['seconds'] = 1.0
    _sec2unit['minutes'] = 1.0/60.0
    _sec2unit['hours'] = 1.0/3600.0
    _sec2unit['days'] = 1.0/(24.0*3600.0)

    def __new__(self, ncfile, name='time', units=None, tzinfo=None, **kwargs):
        if type(ncfile) is str:
            ncfile = netCDF4.Dataset(ncfile)
        self._nc = ncfile

        if self._nc.variables[name].ndim > 1:
            _str_data = self._nc.variables[name][:,:]
            if units is None:
                units = timevar_units
            dates = [parse(_str_data[i, :].tostring()) for i in range(len(_str_data[:,0]))]
            data = netCDF4.date2num(dates, units)
        else:
            data = self._nc.variables[name][:]

        if units is None:
            try:
                self._units = self._nc.variables[name].units
            except StandardError:
                self._units = units
        else:
            self._units = units

        if tzinfo is None:
            self._tzinfo = pytz.utc
        else:
            self._tzinfo = tzinfo

        units_split = self._units.split(' ', 2)
        assert len(units_split) == 3 and units_split[1] == 'since', \
            'units string improperly formatted\n' + self._units
        self.origin = parse(units_split[2])

        self._units = units_split[0].lower()

        # compatibility to CF convention v1.0/udunits names:
        if self._units in ['second','sec','secs','s']:
            self._units='seconds'
        if self._units in ['min','minute','mins']:
            self._units='minutes'
        if self._units in ['h','hs','hr','hrs','hour']:
            self._units='hours'
        if self._units in ['day','d','ds']:
            self._units='days'

        return data.view(self)

    def __setstate__(self, *args, **kwargs):
        """
        Override for setstate to make sure we save local attributes out of process

        Needed for pickling a Timevar object.
        """
        state        = list(args[0])
        self._tzinfo = state.pop()
        self._units  = state.pop()
        self.origin  = state.pop()

        args         = [tuple(state)]

        super(Timevar, self).__setstate__(*args, **kwargs)

    def __reduce_ex__(self, *args, **kwargs):
        """
        Override for reduce_ex to make sure we save local attributes out of process

        Needed for pickling a Timevar object.
        """
        retval = list(super(Timevar, self).__reduce_ex__(*args, **kwargs))
        retval[2] = tuple(list(retval[2]) + [self.origin, self._units, self._tzinfo])
        return tuple(retval)

    def gettimestep(self):
        return self.seconds[1] - self.seconds[0]

    def nearest_index(self, dateo, select='nearest'):
        to = date2num(dateo)
        if select == 'nearest':
            try:
                return [np.where(abs(self.datenum-t) == np.nanmin(abs(self.datenum-t)))[0][0] for t in to]
            except TypeError:
                return [np.where(abs(self.datenum-to) == np.nanmin(abs(self.datenum-to)))[0][0]]
        elif select == 'before':
            try:
                return np.asarray([bisect.bisect(self.datenum, t)-1 for t in to])
            except TypeError:
                return np.asarray([bisect.bisect(self.datenum, to)-1])

    def nearest(self, dateo, select='nearest'):
        """
        find nearest model timestep,
        input and output are datetime objects
        """
        # one might choose the second value for
        #if len(self.nearest_index(dateo)) == 1:
        #    res=self.jd[self.nearest_index(dateo, select)][0]
        #else:
        #    res=self.jd[self.nearest_index(dateo, select)][1]
        return self.dates[self.nearest_index(dateo, select)][0]

    def get_seconds(self):
        fac = self._unit2sec[self._units] * self._sec2unit['seconds']
        return self*fac

    def get_minutes(self):
        fac = self._unit2sec[self._units] * self._sec2unit['minutes']
        return self*fac

    def get_hours(self):
        fac = self._unit2sec[self._units] * self._sec2unit['hours']
        return self*fac

    def get_days(self):
        fac = self._unit2sec[self._units] * self._sec2unit['days']
        return np.asarray(self,dtype='float64')*fac

    def get_dates(self):
        return num2date(self, self._units + " since " + self.origin.strftime('%Y-%m-%dT%H:%M:%S'), tzinfo=self._tzinfo)

    def get_datenum(self):
        return date2num(self.dates, tzinfo=self._tzinfo)

    datenum = property(get_datenum, None, doc="datenum in seconds since 1970-01-01")
    seconds = property(get_seconds, None, doc="seconds")
    minutes = property(get_minutes, None, doc="minutes")
    hours = property(get_hours, None, doc="hours")
    days = property(get_days, None, doc="days")
    dates = property(get_dates, None, doc="datetime objects")
    timestep = property(gettimestep, None)
