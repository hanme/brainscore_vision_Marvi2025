"""
Load Marvi2025 StimulusSet locally (for testing before S3 upload).

This is a helper script for development. Once data is uploaded to S3,
the main __init__.py will use the standard load_stimulus_set() function.
"""

import pandas as pd
from pathlib import Path
from brainscore_core.supported_data_standards.brainio.stimuli import StimulusSet


def load_local_marvi2025_stimulus_set():
    """
    Load Marvi2025 StimulusSet from local files.
    
    Returns
    -------
    StimulusSet
        Stimulus set with 50 video stimuli and metadata.
    """
    # Get paths
    data_dir = Path(__file__).parent
    metadata_path = data_dir / 'stimulus_metadata.csv'
    
    # Load metadata
    metadata_df = pd.read_csv(metadata_path)
    
    # Create StimulusSet
    stimulus_set = StimulusSet(metadata_df)
    stimulus_set.identifier = 'Marvi2025'
    
    # Add file paths
    stimulus_set['filepath'] = stimulus_set['filename'].apply(
        lambda f: str(data_dir / f)
    )
    
    return stimulus_set


if __name__ == '__main__':
    # Test loading
    stimulus_set = load_local_marvi2025_stimulus_set()
    print(f"✅ Loaded {len(stimulus_set)} stimuli")
    print(f"✅ Identifier: {stimulus_set.identifier}")
    print(f"\nColumns: {list(stimulus_set.columns)}")
    print(f"\nConditions: {stimulus_set['condition'].value_counts()}")
    print(f"\n✅ StimulusSet ready for local testing!")
