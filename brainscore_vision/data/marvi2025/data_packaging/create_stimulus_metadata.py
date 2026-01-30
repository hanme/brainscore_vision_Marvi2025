"""
Create StimulusSet metadata CSV for Marvi2025 fMRI benchmark.

Based on the EMFL design from run_effloc.m:
- Visual conditions: 0=Fixation, 1=Faces, 2=Scenes, 3=Bodies, 4=Objects, 5=Words
- 5 runs × 13 blocks per run (blocks 1,7,13 are fixation, no stimuli)
- 50 total stimulus videos (10 per run, blocks 2-6 and 8-12)
"""

import pandas as pd
import os
from pathlib import Path

# Visual condition design from run_effloc.m lines 52-57
VIS_RUNS = [
    [0, 1, 2, 3, 4, 5, 0, 5, 4, 3, 2, 1, 0],  # run 1
    [0, 2, 3, 4, 5, 1, 0, 1, 5, 4, 3, 2, 0],  # run 2
    [0, 3, 4, 5, 1, 2, 0, 2, 1, 5, 4, 3, 0],  # run 3
    [0, 4, 5, 1, 2, 3, 0, 3, 2, 1, 5, 4, 0],  # run 4
    [0, 5, 1, 2, 3, 4, 0, 4, 3, 2, 1, 5, 0],  # run 5
]

# Condition mapping
CONDITION_MAP = {
    0: "fixation",
    1: "faces",
    2: "scenes",
    3: "bodies",
    4: "objects",
    5: "words"
}

def create_stimulus_metadata():
    """Create StimulusSet metadata from video files."""
    
    stim_dir = Path(__file__).parent
    video_files = sorted(stim_dir.glob("*.mp4"))
    
    metadata = []
    stimulus_id_counter = 1
    
    for video_file in video_files:
        # Parse filename: run{1-5}_block{2-12}_{correct|incorrect}.mp4
        filename = video_file.stem
        parts = filename.split('_')
        
        run_num = int(parts[0].replace('run', ''))
        block_num = int(parts[1].replace('block', ''))
        task_response = parts[2]  # 'correct' or 'incorrect'
        
        # Get visual condition for this run and block
        # Blocks are numbered 1-13, but array is 0-indexed
        condition_code = VIS_RUNS[run_num - 1][block_num - 1]
        condition = CONDITION_MAP[condition_code]
        
        # Skip fixation blocks (shouldn't have videos, but check)
        if condition == "fixation":
            print(f"Warning: Found video for fixation block: {filename}")
            continue
        
        metadata.append({
            'stimulus_id': f'marvi2025_{stimulus_id_counter:03d}',
            'filename': video_file.name,
            'run': run_num,
            'block': block_num,
            'condition': condition,
            'task_response': task_response,
            'duration_sec': 3.0,  # Each video clip is 3 seconds
            'category': condition if condition != 'words' else 'words_scrambled',
        })
        
        stimulus_id_counter += 1
    
    # Create DataFrame
    df = pd.DataFrame(metadata)
    
    # Verify we have 50 stimuli
    assert len(df) == 50, f"Expected 50 stimuli, found {len(df)}"
    
    # Verify 10 per condition
    condition_counts = df['condition'].value_counts()
    print("\nStimuli per condition:")
    print(condition_counts)
    
    # Save to CSV
    csv_path = stim_dir / 'stimulus_metadata.csv'
    df.to_csv(csv_path, index=False)
    print(f"\n✅ Saved stimulus metadata to: {csv_path}")
    print(f"✅ Total stimuli: {len(df)}")
    
    return df

if __name__ == '__main__':
    create_stimulus_metadata()
