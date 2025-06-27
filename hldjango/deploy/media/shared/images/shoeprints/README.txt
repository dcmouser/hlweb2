----------------- CSFID-300 DATABASE ------------------------

This footwear impression database contains original crime scene impressions and a database of
reference impressions. This data is limited to non-commercial use only.

If you use this database in your research please cite:

[1] Unsupervised Footwear Impression Analysis and Retrieval from Crime Scene Data,
Adam Kortylewski, Thomas Albrecht, Thomas Vetter. ACCV 2014, Workshop on Robust Local Descriptors


Directories and files included in the database:

references/			- Reference impressions; scaled to the mean height of 586 pixels,
				corresponding to approx. 20 pixel per centimeter

probes_original/ 		- Original probe images

probes_cropped/			- Probe images are cropped in a way that they are roughly 
				centered in the image frame; scaled to 20 pixel per centimeter

label_table.(csv|mat)		- ID of the correct reference for each probe image.

result_ACCV14.mat		- Result of the method from [1] on this dataset. For each probe image the rank of the correct reference is recorded from the final 
				ranked list. If the method was not able to find a periodic pattern, the rank is set to 1175, which corresponds to the last rank.

subsetTable_170_in_300.mat 	- The probe images from the CSFID-170 database are a subset of the probe images in this database. This table records the corresponding 					the ID correspondance between CSFID-170 and CSFID-300.

---------------
Contact

adam dot kortylewski at unibas dot ch

---------------
Acknowledgments

We thank the German State Criminal Police Offices and forensity AG for providing the data and
supporting its publication. 






