
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


# def load_classes_sql():
#     from coffeehouse.settings import PROJECT_DIR
#     import os
#     sql_statements = open(os.path.join(PROJECT_DIR,'tst/sql/load_classes.sql'), 'r').read()
#     return sql_statements
load_classes_sql='''


DROP TABLE IF EXISTS s35;
CREATE table s35(
   id int AUTO_INCREMENT PRIMARY KEY,
   domain_id char(10),
   Class int, ## Note Capital "C" is used to avoid clash with python "class()" keyword
   arch int,
   topo int,
   homsf int,
   s35  int,
   s60  int,
   s95  int,
   s100 int,
   s100_seqcnt int,
   domain_length int,
   resolution float);

#### If however you got fixed-width CATH CLF.
LOAD DATA LOCAL INFILE '/home/shouldsee/Documents/repos/cathdb/cath-domain-list-S35-v4_1_0.txt' 
INTO TABLE s35
(@row)
SET  domain_id = TRIM(SUBSTR(@row,1,7)),
    Class = TRIM(SUBSTR(@row,8,13)),
    arch  = TRIM(SUBSTR(@row,14,19)),
    topo  = TRIM(SUBSTR(@row,20,25)),
    homsf = TRIM(SUBSTR(@row,26,31)),
    s35   = TRIM(SUBSTR(@row,32,37)),
    s60   = TRIM(SUBSTR(@row,38,43)),
    s95   = TRIM(SUBSTR(@row,44,49)),
    s100  = TRIM(SUBSTR(@row,50,55)),
    s100_seqcnt= TRIM(SUBSTR(@row,56,61)),
    domain_length=TRIM(SUBSTR(@row,62,67)),
    resolution=TRIM(SUBSTR(@row,68,73));

###  !!! pay attention to the number here !!!
ALTER TABLE s35
  ADD COLUMN version_id int default 1,
  ADD COLUMN level_id int default 6;

SET FOREIGN_KEY_CHECKS=0;
DELETE from DJANGO_CATH.tst_classification;
SET FOREIGN_KEY_CHECKS=1;

UPDATE tst_classification 
  SET temp_id=NULL;

INSERT INTO DJANGO_CATH.tst_classification 
 (Class,arch,topo,homsf,s35,s60,s95,s100,version_id,level_id,temp_id)
SELECT 
 Class,arch,topo,homsf,s35,s60,s95,s100,version_id,level_id,id from s35 ;

ALTER TABLE s35
  ADD COLUMN classification_id INT;

UPDATE s35 AS s
  JOIN tst_classification AS c
  ON   s.id=c.temp_id
  SET  s.classification_id=c.id;

INSERT INTO tst_domain
  (domain_id, domain_length, resolution, classification_id)
SELECT 
  domain_id, domain_length, resolution, classification_id FROM s35 ;


# 
# 
'''

'''
INSERT INTO DJANGO_CATH.tst_classification (id,Class,arch,topo,homsf,s35,s60,s95,s100,version_id,level_id)
 select * from CATH.temp_class;
'''

unload_classes_sql='''
SET FOREIGN_KEY_CHECKS=0;
DELETE from DJANGO_CATH.tst_domain;
DELETE from DJANGO_CATH.tst_classification;
SET FOREIGN_KEY_CHECKS=1;
DROP TABLE if exists temp_class; 
# DELETE from tst_version;
# DELETE from tst_level;
'''
class Migration(migrations.Migration):

    dependencies = [
        ('tst', '0003_init_meta'),
    ]

    operations = [
        migrations.RunSQL(load_classes_sql,unload_classes_sql),
    ]
