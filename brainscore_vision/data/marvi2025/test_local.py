"""
Local tests for Marvi2025 data packaging (no S3 required).

These tests validate the locally packaged data before S3 upload.
"""

import pytest
from pathlib import Path
import pandas as pd


class TestStimulusMetadata:
    """Tests for stimulus metadata CSV (no S3 required)."""
    
    @pytest.fixture
    def metadata_path(self):
        return Path(__file__).parent / 'data_packaging' / 'stimulus_metadata.csv'
    
    @pytest.fixture
    def metadata(self, metadata_path):
        assert metadata_path.exists(), f"Metadata file not found: {metadata_path}"
        return pd.read_csv(metadata_path)
    
    def test_metadata_exists(self, metadata_path):
        """Test that metadata CSV exists."""
        assert metadata_path.exists()
    
    def test_correct_number_of_stimuli(self, metadata):
        """Test we have exactly 50 stimuli."""
        assert len(metadata) == 50, f"Expected 50 stimuli, found {len(metadata)}"
    
    def test_required_columns(self, metadata):
        """Test all required columns are present."""
        required_columns = ['stimulus_id', 'filename', 'run', 'block', 
                           'condition', 'task_response', 'duration_sec', 'category',
                           'degrees_width', 'degrees_height']
        for col in required_columns:
            assert col in metadata.columns, f"Missing required column: {col}"
    
    def test_stimulus_ids_unique(self, metadata):
        """Test stimulus IDs are unique."""
        assert metadata['stimulus_id'].is_unique, "Stimulus IDs are not unique"
    
    def test_stimulus_ids_format(self, metadata):
        """Test stimulus IDs follow marvi2025_XXX format."""
        for stim_id in metadata['stimulus_id']:
            assert stim_id.startswith('marvi2025_'), f"Invalid stimulus ID format: {stim_id}"
            assert len(stim_id) == len('marvi2025_001'), f"Invalid stimulus ID length: {stim_id}"
    
    def test_conditions(self, metadata):
        """Test all 5 visual conditions are present."""
        conditions = set(metadata['condition'].unique())
        expected = {'faces', 'scenes', 'bodies', 'objects', 'words'}
        assert conditions == expected, f"Expected {expected}, got {conditions}"
    
    def test_balanced_conditions(self, metadata):
        """Test 10 stimuli per condition."""
        condition_counts = metadata['condition'].value_counts()
        for condition in ['faces', 'scenes', 'bodies', 'objects', 'words']:
            assert condition_counts[condition] == 10, \
                f"Expected 10 stimuli for {condition}, got {condition_counts[condition]}"
    
    def test_runs(self, metadata):
        """Test all 5 runs are represented."""
        runs = set(metadata['run'].unique())
        assert runs == {1, 2, 3, 4, 5}, f"Expected runs 1-5, got {runs}"
    
    def test_blocks(self, metadata):
        """Test blocks are from expected set (2-6, 8-12, excluding 1,7,13 which are fixation)."""
        blocks = set(metadata['block'].unique())
        expected_blocks = {2, 3, 4, 5, 6, 8, 9, 10, 11, 12}
        assert blocks == expected_blocks, f"Unexpected blocks: {blocks}"
    
    def test_duration(self, metadata):
        """Test all videos have 3-second duration."""
        assert (metadata['duration_sec'] == 3.0).all(), "Not all videos are 3 seconds"
    
    def test_visual_degrees(self, metadata):
        """Test visual angle values are correct (confirmed by authors)."""
        assert (metadata['degrees_width'] == 6.4).all(), \
            "Expected horizontal visual angle of 6.4 degrees"
        assert (metadata['degrees_height'] == 5.2).all(), \
            "Expected vertical visual angle of 5.2 degrees"
    
    def test_filenames_exist(self, metadata, metadata_path):
        """Test all referenced video files exist."""
        data_dir = metadata_path.parent
        for filename in metadata['filename']:
            video_path = data_dir / filename
            assert video_path.exists(), f"Video file not found: {filename}"


class TestVideoFiles:
    """Tests for video stimulus files (no S3 required)."""
    
    @pytest.fixture
    def video_dir(self):
        return Path(__file__).parent / 'data_packaging'
    
    def test_correct_number_of_videos(self, video_dir):
        """Test we have exactly 50 video files."""
        videos = list(video_dir.glob('*.mp4'))
        assert len(videos) == 50, f"Expected 50 videos, found {len(videos)}"
    
    def test_video_naming_convention(self, video_dir):
        """Test videos follow run{X}_block{Y}_{correct|incorrect}.mp4 format."""
        import re
        pattern = re.compile(r'run[1-5]_block(2|3|4|5|6|8|9|10|11|12)_(correct|incorrect)\.mp4')
        
        videos = list(video_dir.glob('*.mp4'))
        for video in videos:
            assert pattern.match(video.name), f"Invalid video filename: {video.name}"


class TestLocalLoader:
    """Tests for local stimulus set loader (no S3 required)."""
    
    def test_local_loader_imports(self):
        """Test that local loader script imports successfully."""
        try:
            from brainscore_vision.data.marvi2025.data_packaging.load_local_stimulus_set import \
                load_local_marvi2025_stimulus_set
        except ImportError as e:
            pytest.fail(f"Could not import local loader: {e}")
    
    def test_local_loader_runs(self):
        """Test that local loader executes without errors."""
        from brainscore_vision.data.marvi2025.data_packaging.load_local_stimulus_set import \
            load_local_marvi2025_stimulus_set
        
        stimulus_set = load_local_marvi2025_stimulus_set()
        assert stimulus_set is not None
        assert len(stimulus_set) == 50
        assert stimulus_set.identifier == 'Marvi2025'
    
    def test_local_loader_stimulus_ids(self):
        """Test stimulus IDs from local loader."""
        from brainscore_vision.data.marvi2025.data_packaging.load_local_stimulus_set import \
            load_local_marvi2025_stimulus_set
        
        stimulus_set = load_local_marvi2025_stimulus_set()
        for stim_id in stimulus_set['stimulus_id']:
            assert stim_id.startswith('marvi2025_')
    
    def test_local_loader_conditions(self):
        """Test conditions from local loader."""
        from brainscore_vision.data.marvi2025.data_packaging.load_local_stimulus_set import \
            load_local_marvi2025_stimulus_set
        
        stimulus_set = load_local_marvi2025_stimulus_set()
        conditions = set(stimulus_set['condition'].values)
        expected = {'faces', 'scenes', 'bodies', 'objects', 'words'}
        assert conditions == expected
    
    def test_local_loader_visual_degrees(self):
        """Test visual angle metadata from local loader."""
        from brainscore_vision.data.marvi2025.data_packaging.load_local_stimulus_set import \
            load_local_marvi2025_stimulus_set
        
        stimulus_set = load_local_marvi2025_stimulus_set()
        assert 'degrees_width' in stimulus_set.columns, "Missing degrees_width column"
        assert 'degrees_height' in stimulus_set.columns, "Missing degrees_height column"
        assert (stimulus_set['degrees_width'] == 6.4).all(), "Incorrect horizontal visual angle"
        assert (stimulus_set['degrees_height'] == 5.2).all(), "Incorrect vertical visual angle"


class TestfMRIAssembly:
    """Tests for fMRI NeuroidAssembly (no S3 required)."""
    
    def test_assembly_loader_imports(self):
        """Test that assembly loader imports successfully."""
        try:
            from brainscore_vision.data.marvi2025.data_packaging.load_local_assembly import \
                load_local_marvi2025_assembly
        except ImportError as e:
            pytest.fail(f"Could not import assembly loader: {e}")
    
    def test_assembly_loads(self):
        """Test that assembly loads successfully."""
        from brainscore_vision.data.marvi2025.data_packaging.load_local_assembly import \
            load_local_marvi2025_assembly
        
        assembly = load_local_marvi2025_assembly()
        assert assembly is not None
        assert assembly.attrs['identifier'] == 'Marvi2025'
    
    def test_assembly_shape(self):
        """Test assembly has correct shape."""
        from brainscore_vision.data.marvi2025.data_packaging.load_local_assembly import \
            load_local_marvi2025_assembly
        
        assembly = load_local_marvi2025_assembly()
        assert assembly.shape[0] == 50, "Should have 50 videos"
        assert assembly.shape[2] == 1, "Should have 1 time bin"
        assert assembly.shape[1] > 70000, "Should have >70k neuroids (6 subjects × 6 ROIs × 2 hemi)"
    
    def test_assembly_dims(self):
        """Test assembly dimensions."""
        from brainscore_vision.data.marvi2025.data_packaging.load_local_assembly import \
            load_local_marvi2025_assembly
        
        assembly = load_local_marvi2025_assembly()
        assert assembly.dims == ('presentation', 'neuroid', 'time_bin')
    
    def test_assembly_stimulus_ids(self):
        """Test stimulus IDs are properly formatted."""
        from brainscore_vision.data.marvi2025.data_packaging.load_local_assembly import \
            load_local_marvi2025_assembly
        
        assembly = load_local_marvi2025_assembly()
        stimulus_ids = assembly['presentation'].values
        
        assert len(stimulus_ids) == 50
        assert all(sid.startswith('marvi2025_') for sid in stimulus_ids)
        assert 'marvi2025_001' in stimulus_ids
        assert 'marvi2025_050' in stimulus_ids
    
    def test_assembly_subjects(self):
        """Test all 6 subjects are present."""
        from brainscore_vision.data.marvi2025.data_packaging.load_local_assembly import \
            load_local_marvi2025_assembly
        import numpy as np
        
        assembly = load_local_marvi2025_assembly()
        
        # Extract subject from neuroid MultiIndex
        neuroids = assembly['neuroid'].values
        subjects = [n[0] for n in neuroids]  # First element is subject
        unique_subjects = sorted(set(subjects))
        
        expected_subjects = ['sub-kaneff01', 'sub-kaneff06', 'sub-kaneff07',
                            'sub-kaneff08', 'sub-kaneff09', 'sub-kaneff21']
        assert unique_subjects == expected_subjects
    
    def test_assembly_rois(self):
        """Test all 6 visual ROIs are present."""
        from brainscore_vision.data.marvi2025.data_packaging.load_local_assembly import \
            load_local_marvi2025_assembly
        
        assembly = load_local_marvi2025_assembly()
        
        # Extract ROI from neuroid MultiIndex
        neuroids = assembly['neuroid'].values
        rois = [n[1] for n in neuroids]  # Second element is region
        unique_rois = sorted(set(rois))
        
        expected_rois = ['eba', 'ffa', 'loc', 'ofa', 'opa', 'ppa']
        assert unique_rois == expected_rois
    
    def test_assembly_hemispheres(self):
        """Test both hemispheres are present."""
        from brainscore_vision.data.marvi2025.data_packaging.load_local_assembly import \
            load_local_marvi2025_assembly
        
        assembly = load_local_marvi2025_assembly()
        
        # Extract hemisphere from neuroid MultiIndex  
        neuroids = assembly['neuroid'].values
        hemis = [n[2] for n in neuroids]  # Third element is hemisphere
        unique_hemis = sorted(set(hemis))
        
        assert unique_hemis == ['lh', 'rh']
    
    def test_assembly_time_bin(self):
        """Test time bin is [0, 2000] ms (TR=2s)."""
        from brainscore_vision.data.marvi2025.data_packaging.load_local_assembly import \
            load_local_marvi2025_assembly
        
        assembly = load_local_marvi2025_assembly()
        time_bins = assembly['time_bin'].values
        
        assert len(time_bins) == 1
        assert time_bins[0] == (0, 2000)
    
    def test_assembly_noise_ceiling(self):
        """Test noise ceiling coordinate exists and is reasonable."""
        from brainscore_vision.data.marvi2025.data_packaging.load_local_assembly import \
            load_local_marvi2025_assembly
        import numpy as np
        
        assembly = load_local_marvi2025_assembly()
        
        # Extract noise ceiling from neuroid MultiIndex
        neuroids = assembly['neuroid'].values
        noise_ceilings = [n[5] for n in neuroids]  # Sixth element is noise_ceiling
        
        assert len(noise_ceilings) == assembly.shape[1]
        assert all(isinstance(nc, (int, float)) for nc in noise_ceilings)
        
        # Check reasonable range (0-100%)
        valid_ncs = [nc for nc in noise_ceilings if not np.isnan(nc)]
        assert all(0 <= nc <= 100 for nc in valid_ncs)
    
    def test_assembly_data_range(self):
        """Test data values are in reasonable range for z-scores."""
        from brainscore_vision.data.marvi2025.data_packaging.load_local_assembly import \
            load_local_marvi2025_assembly
        import numpy as np
        
        assembly = load_local_marvi2025_assembly()
        
        # Z-scores typically range from -3 to +3, but can be larger
        assert assembly.values.min() > -100, "Suspiciously low values"
        assert assembly.values.max() < 100, "Suspiciously high values"
        assert np.isfinite(assembly.values).all(), "Should not have inf values"
