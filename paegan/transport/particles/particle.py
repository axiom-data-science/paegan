from shapely.geometry import LineString

class Particle(object):
    """
        A particle
    """
    def __init__(self):
        self._locations = []
        self._age = 0. # Age in days

    def set_location(self, location):
        self._locations.append(location)
    def get_location(self):
        return self._locations[-1]
    location = property(get_location, set_location)

    def get_locations(self):
        return self._locations
    locations = property(get_locations, None)

    def set_active(self, active):
        self._active = active
    def get_active(self):
        return self._active
    active = property(get_active, set_active)

    def get_last_movement(self):
        return LineString(list(self.locations[-2].point.coords) + list(self.locations[-1].point.coords))

    def get_age(self, **kwargs):
        """
        Returns the particlees age (how long it has been forced) in a variety of units.
        Rounded to 8 decimal places.

        Parameters:
            units (optional) = 'days' (default), 'hours', 'minutes', or 'seconds'
        """
        try:
            units = kwargs.get('units', None)
            if units is None:
                return self._age
            units = units.lower()
            if units == "days":
                z = self._age
            elif units == "hours":
                z = self._age * 24
            elif units == "minutes":
                z = self._age * 24 * 60
            elif units == "seconds":
                z = self._age * 24 * 60 * 60
            else:
                raise
            return round(z,8) 
        except:
            raise KeyError("Could not return age of particle")

    def age(self, **kwargs):
        """
        Age this particle.

        parameters (optional, only one allowed):
            days (default)
            hours
            minutes
            seconds
        """
        if kwargs.get('days', None) is not None:
            self._age += kwargs.get('days')
            return
        if kwargs.get('hours', None) is not None:
            self._age += kwargs.get('hours') / 24.
            return
        if kwargs.get('minutes', None) is not None:
            self._age += kwargs.get('minutes') / 24. / 60.
            return
        if kwargs.get('seconds', None) is not None:
            self._age += kwargs.get('seconds') / 24. / 60. / 60.
            return

        raise KeyError("Could not age particle, please specify 'days', 'hours', 'minutes', or 'seconds' parameter")

    def linestring(self):
        return LineString(map(lambda x: list(x.point.coords)[0], self.locations))
        
class LarvaParticle(Particle):
    """
        A particle for larvamap, keeps track of information
        for the behaviors component
    """
    def __init__(self):
        super(LarvaParticle,self).__init__()
        self.lifestage_progress = 0.
        self._temp = []
        self._salt = []

    def set_temp(self, temp):
        self._temp.append(temp)
    def get_temp(self):
        return self._temp[-1]
    temp = property(get_temp, set_temp)
    
    def get_temps(self):
        return self._temp
    temps = property(get_temps, None)
    
    def set_salt(self, salt):
        self._salt.append(salt)
    def get_salt(self):
        return self._salt[-1]
    salt = property(get_salt, set_salt)
    
    def get_salts(self):
        return self._salt
    salts = property(get_salts, None)
    
    def get_lifestage_index(self):
        return int(self.lifestage_progress)
    lifestage_index = property(get_lifestage_index, None)

    def grow(self, amount):
        """
        Grow a particle by a percentage value (0 < x < 1)

        When a particle grows past 1, its current lifestage is 
        complete and it moves onto the next.

        The calculation to get the current lifestage index is in get_lifestage_index()
        """
        self.lifestage_progress += amount
        
class ChemistryParticle(Particle):
    """
        A chemical particle for time and chemistry dependent
        tracers
    """
    def __init__(self):
        pass
        

class OilParticle(Particle):
    """
        An oil particle for special oil physics and chemistry
    """
    def __init__(self):
        pass
