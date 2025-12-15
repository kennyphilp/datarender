from django.db import models
from typing import Dict, Any, Optional
from .constants import YEARS


class SchoolRoll(models.Model):
    """Model representing school enrollment data from 1996-2018."""
    
    # Core fields
    ObjectId = models.CharField(max_length=64, primary_key=True)
    Code = models.CharField(max_length=32, null=True, blank=True)
    Name = models.CharField(max_length=512)
    LA_Code = models.CharField(max_length=32, null=True, blank=True)
    LA_Name = models.CharField(max_length=256, null=True, blank=True)
    Sector = models.CharField(max_length=128, null=True, blank=True)
    School_Type = models.CharField(max_length=128, null=True, blank=True)

    # Year columns F1996..F2018 stored as integers where present
    F1996 = models.IntegerField(null=True, blank=True)
    F1997 = models.IntegerField(null=True, blank=True)
    F1998 = models.IntegerField(null=True, blank=True)
    F1999 = models.IntegerField(null=True, blank=True)
    F2000 = models.IntegerField(null=True, blank=True)
    F2001 = models.IntegerField(null=True, blank=True)
    F2002 = models.IntegerField(null=True, blank=True)
    F2003 = models.IntegerField(null=True, blank=True)
    F2004 = models.IntegerField(null=True, blank=True)
    F2005 = models.IntegerField(null=True, blank=True)
    F2006 = models.IntegerField(null=True, blank=True)
    F2007 = models.IntegerField(null=True, blank=True)
    F2008 = models.IntegerField(null=True, blank=True)
    F2009 = models.IntegerField(null=True, blank=True)
    F2010 = models.IntegerField(null=True, blank=True)
    F2011 = models.IntegerField(null=True, blank=True)
    F2012 = models.IntegerField(null=True, blank=True)
    F2013 = models.IntegerField(null=True, blank=True)
    F2014 = models.IntegerField(null=True, blank=True)
    F2015 = models.IntegerField(null=True, blank=True)
    F2016 = models.IntegerField(null=True, blank=True)
    F2017 = models.IntegerField(null=True, blank=True)
    F2018 = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'school_rolls'
        managed = False

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model instance to dictionary for API serialization.
        
        Returns:
            dict: Dictionary with ObjectId, school metadata, and enrollment
                  data for years defined in constants.YEARS.
        """
        d = {
            'ObjectId': self.ObjectId,
            'Code': self.Code,
            'Name': self.Name,
            'LA_Code': self.LA_Code,
            'LA_Name': self.LA_Name,
            'Sector': self.Sector,
            'School_Type': self.School_Type,
        }
        for year in YEARS:
            d[f'F{year}'] = getattr(self, f'F{year}')
        return d
