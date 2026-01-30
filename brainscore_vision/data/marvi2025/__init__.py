"""
Marvi2025 visual fMRI data plugin.

Dataset from: Marvi, A. I., Hutchinson, S., Fedorenko, E., Saxe, R. R., Kamps, F. S., 
Regev, T. I., Chen, E. M., & Kanwisher, N. G. (2025). An Efficient Multifunction fMRI 
Localizer for High-Level Visual, Auditory, and Cognitive Regions in Humans. 
Imaging Neuroscience, 3, 1-29.

This data plugin provides access to VISUAL ROIs ONLY:
1. StimulusSet: 50 dynamic video stimuli (3 seconds each) from the EMFL localizer
   - 10 videos per category: faces, scenes, bodies, objects, words
2. NeuroidAssembly: fMRI responses from 6 subjects across 9 VISUAL ROIs in MNI space
   - FFA-R, OFA-R, fSTS-R, PPA-R, OPA-R, RSC-R, LOC-R, EBA-R, VWFA-L

Note: Language, ToM, MD, and Speech ROIs from the paper belong in separate 
      brain-score domains (brainscore_language, etc.) and are NOT included here.
"""

from brainscore_vision import data_registry, stimulus_set_registry
# from brainscore_core.supported_data_standards.brainio.s3 import load_stimulus_set_from_s3, load_assembly_from_s3

# ===================================================================================================
# NOTE: S3 registration is COMMENTED OUT during local development
# 
# The stimulus set and assembly will be loaded from S3 after packaging and upload.
# For local testing during development, use:
#   - data_packaging/load_local_stimulus_set.py
#
# After S3 upload, uncomment below and fill in the sha1 hashes and version IDs
# ===================================================================================================

# stimulus_set_registry['Marvi2025'] = lambda: load_stimulus_set_from_s3(
#     identifier='Marvi2025',
#     bucket='brainscore-storage/brainio-brainscore',
#     csv_sha1='TO_BE_FILLED_AFTER_S3_UPLOAD',
#     zip_sha1='TO_BE_FILLED_AFTER_S3_UPLOAD',
#     csv_version_id='TO_BE_FILLED_AFTER_S3_UPLOAD',
#     zip_version_id='TO_BE_FILLED_AFTER_S3_UPLOAD'
# )

# data_registry['Marvi2025'] = lambda: load_assembly_from_s3(
#     identifier='Marvi2025',
#     bucket='brainscore-storage/brainio-brainscore',
#     sha1='TO_BE_FILLED_AFTER_S3_UPLOAD',
#     version_id='TO_BE_FILLED_AFTER_S3_UPLOAD',
#     cls=NeuroidAssembly
# )
