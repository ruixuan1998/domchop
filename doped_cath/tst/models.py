# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
from django.utils import timezone
from django.db import models
from django.db.models import Avg,StdDev,Count
from django.urls import reverse
from django.templatetags.static import static
# from django.contrib.staticfiles.templatetags.staticfiles import static

import requests
# Create your models here.

from CATH_API.lib import *

class homsf_manager(models.Manager):
    def get_queryset(self):
    	homsf_qset = super(homsf_manager, self).get_queryset().filter(level_id=5);
    	homsf_qset = (homsf_qset.annotate(nDOPE_std=StdDev("classification__domain__nDOPE"))
              .annotate(nDOPE_avg=Avg("classification__domain__nDOPE"))
              .annotate(s35_count=Count("classification__parent__classification"))
             )
    	# homsf_qset.manager = "homsf_manager"
        return homsf_qset
class domain_manager(models.Manager):
    def get_queryset(self):
    	domain_set = super(domain_manager, self).get_queryset();
    	# domain_set.annotate(superfamily="")
    	return domain_set

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    def __str__(self):
        return self.question_text
    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)
    def to_values(self):
    	return self

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
    def __str__(self):
        return self.choice_text

class version(models.Model):
	name = models.CharField(default=None,max_length=10);
	def __str__(self):
		return self.name;
class level(models.Model):
	name = models.CharField(default=None,max_length=50)
	letter = models.CharField(default=None,max_length=1);
	def __str__(self):
		return self.name;

class classification(models.Model):	
	# homsf_ID = models.CharField(max_length=7, primary_key=True)

	Class = models.IntegerField(default=None,null=True,db_index=True)
	arch = models.IntegerField(default=None,null=True,db_index=True)
	topo = models.IntegerField(default=None,null=True,db_index=True)
	homsf = models.IntegerField(default=None,null=True,db_index=True)
	s35 = models.IntegerField(default=None,null=True,db_index=True)
	s60 = models.IntegerField(default=None,null=True)
	s95 = models.IntegerField(default=None,null=True)
	s100 = models.IntegerField(default=None,null=True)
	version =  models.ForeignKey(version, on_delete= models.CASCADE);
	level = models.ForeignKey(level,  on_delete=models.CASCADE)
	parent = models.ForeignKey("self", default=None,null=True, on_delete=models.CASCADE)
	
	def node_dict(self):
		return {
			'Class':self.Class,
			'arch':self.arch,
			'topo':self.topo,
			'homsf':self.homsf,
			's35':self.s35,
			's60':self.s60,
			's95':self.s95,
			's100':self.s100,
			# 'level_id':self.level_id,
			}
	def find_depth(self, depth):
		s = '';
		i = depth
		if not i:
			return('Not in any Class')
		for key in [self.Class,self.arch,self.topo,self.homsf,self.s35,self.s60,self.s95,self.s100]:
			i += -1
			s += str(key) + '.'
			if not i :
				return s.rstrip('.')
	def __str__(self):
		return self.find_depth(self.level.id)
	
	def superfamily(self):
		return self.find_depth(4)

	def superfamily_urled(self):
		sf = self.superfamily();
		url = reverse('domain_collection',args=[sf])
		htmldom = "<a href=\"{:s}\">{:s}</a>".format(url,sf)
		return htmldom
	
	def get_s35cnt(self):
		url = 'http://www.cathdb.info/version/v4_1_0/api/rest/superfamily/%s' % self.superfamily();
		cnt = fetch_cath(url)[1]["child_count_s35_code"]
		return cnt



	objects = models.Manager()
	homsf_objects = homsf_manager()
		# pass

	# 	return("Superfamily %s"%self.homsf_ID())
class domain(models.Model):
	domain_id = models.CharField(max_length=7,db_index=True)
	domain_length = models.IntegerField(default=0,null=True)
	resolution = models.FloatField(default=0,null=True)
	nDOPE = models.FloatField(default=0,null=True)
	raw_DOPE = models.FloatField(default=0,null=True)
	# version =  models.ForeignKey(version, default=None,on_delete= models.CASCADE);
	classification =  models.ForeignKey(classification, on_delete= models.CASCADE);
	def superfamily(self):
		return(self.classification.superfamily())
	def superfamily_urled(self):
		return(self.classification.superfamily_urled())
	def view_chopped(self):		
		elem = '<a href="#view_{:s}" data-toggle="collapse"><img src="{:s}" alt="chopped_pdb"/></a>'.format( self.domain_id, static("imgs/rasmol.png"))
		return elem
	def domain_id_urled(self):
		version = 'current';
		url = "http://www.cathdb.info/version/{:s}/domain/{:s}/".format(version, self.domain_id)
		elem = '<a target="_blank" href="{:s}">{:s}</a>'.format(url, self.domain_id)
		return elem
	# class_id = models.IntegerField(default=0)
	# node = models.CharField(default=None)
	# homsf = models.ManyToManyField(homsf);

class s35_rep(domain):
	# classification = models.ForeignKey(classification, default=None,on_delete= models.CASCADE);
	pass
	# rep_type = models.CharField(default='s35',max_length=4);
	# domain.rep_type='s35';
	# self.save()

