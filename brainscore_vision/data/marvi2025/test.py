"""
Tests for Marvi2025 visual fMRI data plugin.

NOTE: These tests are SKIPPED during local development.
They will work after data is uploaded to S3 and __init__.py is updated with sha1 hashes.

For local testing, use: data_packaging/load_local_stimulus_set.py
"""

import pytest
from brainscore_vision import load_stimulus_set


@pytest.mark.skip(reason="S3 data not uploaded yet - use data_packaging/load_local_stimulus_set.py for local testing")
class TestStimulusSet:
    """Tests for Marvi2025 StimulusSet (will work after S3 upload)."""
    
    def test_existence(self):
        """Test that the stimulus set can be loaded."""
        stimulus_set = load_stimulus_set('Marvi2025')
        assert stimulus_set is not None
        assert len(stimulus_set) == 50
    
    def test_stimulus_set_identifier(self):
        """Test stimulus set has correct identifier."""
        stimulus_set = load_stimulus_set('Marvi2025')
        assert stimulus_set.identifier == 'Marvi2025'
    
    def test_number_of_stimuli(self):
        """Test correct number of stimuli (50 videos)."""
        stimulus_set = load_stimulus_set('Marvi2025')
        assert len(stimulus_set) == 50
    
    def test_stimulus_ids(self):
        """Test stimulus IDs are properly formatted."""
        stimulus_set = load_stimulus_set('Marvi2025')
        for stimulus_id in stimulus_set['stimulus_id']:
            assert stimulus_id.startswith('marvi2025_')
            assert len(stimulus_id) == len('marvi2025_001')
    
    def test_columns(self):
        """Test that expected columns are present."""
        stimulus_set = load_stimulus_set('Marvi2025')
        expected_columns = ['stimulus_id', 'filename', 'run', 'block', 
                           'condition', 'task_response', 'duration_sec', 'category']
        for col in expected_columns:
            assert col in stimulus_set.columns, f"Missing column: {col}"
    
    def test_conditions(self):
        """Test all 5 visual conditions are present."""
        stimulus_set = load_stimulus_set('Marvi2025')
        conditions = set(stimulus_set['condition'].values)
        expected_conditions = {'faces', 'scenes', 'bodies', 'objects', 'words'}
        assert conditions == expected_conditions
    
    def test_stimuli_per_condition(self):
        """Test 10 stimuli per condition."""
        stimulus_set = load_stimulus_set('Marvi2025')
        condition_counts = stimulus_set['condition'].value_counts()
        for condition in ['faces', 'scenes', 'bodies', 'objects', 'words']:
            assert condition_counts[condition] == 10, \
                f"Expected 10 stimuli for {condition}, got {condition_counts[condition]}"
    
    def test_runs(self):
        """Test all 5 runs are represented."""
        stimulus_set = load_stimulus_set('Marvi2025')
        runs = set(stimulus_set['run'].values)
        assert runs == {1, 2, 3, 4, 5}
    
    def test_duration(self):
        """Test all videos have correct duration."""
        stimulus_set = load_stimulus_set('Marvi2025')
        durations = stimulus_set['duration_sec'].values
        assert all(d == 3.0 for d in durations), "All videos should be 3 seconds"


# TODO: Add tests for NeuroidAssembly after fMRI data packaging is complete
# class TestNeuroidAssembly:
#     def test_assembly_existence(self):
#         assembly = load_dataset('Marvi2025')
#         assert assembly is not None
