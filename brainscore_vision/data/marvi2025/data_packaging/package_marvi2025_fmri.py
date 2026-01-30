#!/usr/bin/env python3
"""
Package Marvi2025 fMRI data for BrainScore.

Loads video-level ROI responses (50 videos × 6 subjects × 6 visual ROIs × 2 hemispheres)
and packages them into a NeuroidAssembly with proper coordinates.

Visual ROIs (high-level category-selective regions):
- FFA (Fusiform Face Area)
- OFA (Occipital Face Area)  
- EBA (Extrastriate Body Area)
- PPA (Parahippocampal Place Area)
- OPA (Occipital Place Area)
- LOC (Lateral Occipital Complex)

Noise Ceiling:
- Computed using variance-based method (Allen et al., 2021, NSD paper)
- Treats 6 subjects as "repetitions"
- Per-voxel reliability: nc = 100 * (snr / (snr + 1/n_subjects))

Output:
- NeuroidAssembly: (50 presentations, N neuroids, 1 time_bin)
- Coordinates: stimulus_id, subject, region, hemisphere, neuroid_id, voxel_id, 
                time_bin_start, time_bin_end, noise_ceiling
"""

import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from typing import Dict, List, Tuple
from brainscore_core.supported_data_standards.brainio.assemblies import NeuroidAssembly
from scipy.stats import zscore

# Paths
MARVI_DATA_DIR = Path('/work/upschrimpf1/mehrer/code/20251030_Marvi_2025_efficient_fMRI_localizer/outputs/roi_responses/multivariate/video_level')
STIMULUS_METADATA_PATH = Path(__file__).parent / 'stimulus_metadata.csv'

# Constants
ALL_SUBJECTS = ['sub-kaneff01', 'sub-kaneff06', 'sub-kaneff07', 'sub-kaneff08', 'sub-kaneff09', 'sub-kaneff21']
VISUAL_ROIS = ['ffa', 'ofa', 'eba', 'ppa', 'opa', 'loc']
HEMISPHERES = ['lh', 'rh']
TR_MS = 2000  # TR = 2 seconds


def compute_noise_ceiling_variancebased(responses: np.ndarray) -> np.ndarray:
    """
    Variance-based noise ceiling per voxel (Allen et al., 2021, NSD paper).
    
    Treats subjects as repetitions.
    
    Parameters
    ----------
    responses : np.ndarray
        Shape (n_voxels, n_stimuli, n_subjects)
        
    Returns
    -------
    np.ndarray
        Per-voxel noise ceilings in percent, shape (n_voxels,)
    """
    n_subjects = responses.shape[-1]
    if n_subjects < 2:
        raise ValueError("Need at least 2 subjects for noise ceiling computation.")
    
    # Z-score across stimuli for each (voxel, subject)
    norm = zscore(responses, axis=1, ddof=0, nan_policy='omit')  # (n_voxels, n_stimuli, n_subjects)
    
    # Noise variance: var across subjects, averaged across stimuli
    noise_var = np.nanmean(np.nanvar(norm, axis=-1, ddof=1), axis=-1)  # (n_voxels,)
    
    # Signal variance
    signal_var = np.clip(1.0 - noise_var, 0.0, None)
    
    # SNR and reliability
    snr = signal_var / np.maximum(noise_var, 1e-12)
    nc = 100.0 * (snr / (snr + 1.0 / n_subjects))
    
    return nc


def load_roi_responses(subject: str, roi: str, hemisphere: str, 
                       csv_dir: Path) -> Tuple[pd.DataFrame, np.ndarray]:
    """
    Load ROI responses for one subject/ROI/hemisphere.
    
    Returns
    -------
    metadata : pd.DataFrame
        Video metadata (50 rows)
    responses : np.ndarray
        Response matrix (50 videos, n_voxels)
    """
    csv_file = csv_dir / f'{subject}_{hemisphere}_{roi}.csv'
    if not csv_file.exists():
        raise FileNotFoundError(f"ROI response file not found: {csv_file}")
    
    df = pd.read_csv(csv_file)
    
    # Extract video names and response matrix
    video_col = df.columns[0]  # Should be 'video'
    videos = df[video_col].values
    responses = df.iloc[:, 1:].values  # All voxel columns
    
    # Create metadata DataFrame
    metadata = pd.DataFrame({'video': videos})
    
    return metadata, responses


def package_marvi2025_assembly() -> NeuroidAssembly:
    """
    Create NeuroidAssembly from Marvi2025 fMRI data.
    
    Returns
    -------
    assembly : NeuroidAssembly
        Shape (50 presentations, N neuroids, 1 time_bin)
    """
    # Load stimulus metadata
    stim_meta = pd.read_csv(STIMULUS_METADATA_PATH)
    
    # Create mapping from video filename to stimulus_id
    # Note: ROI data has video names without .mp4 extension
    video_to_stimid = dict(zip(stim_meta['filename'], stim_meta['stimulus_id']))
    # Also create mapping without extension for matching
    video_to_stimid_no_ext = {fn.replace('.mp4', ''): stimid 
                               for fn, stimid in zip(stim_meta['filename'], stim_meta['stimulus_id'])}
    
    # Find available CSV files
    csv_dir = MARVI_DATA_DIR / 'csv_20251118_070432'
    if not csv_dir.exists():
        raise FileNotFoundError(f"CSV directory not found: {csv_dir}")
    
    print(f"Loading data from {csv_dir}")
    
    # Collect all data
    all_responses = []
    neuroid_coords = []
    
    neuroid_id = 0
    
    for subject in ALL_SUBJECTS:
        for roi in VISUAL_ROIS:
            for hemi in HEMISPHERES:
                try:
                    metadata, responses = load_roi_responses(subject, roi, hemi, csv_dir)
                    n_voxels = responses.shape[1]
                    
                    print(f"  {subject} {hemi}_{roi}: {n_voxels} voxels")
                    
                    # Store responses (50 videos × n_voxels)
                    all_responses.append(responses)
                    
                    # Create neuroid coordinates for this ROI
                    for voxel_idx in range(n_voxels):
                        neuroid_coords.append({
                            'subject': subject,
                            'region': roi,
                            'hemisphere': hemi,
                            'neuroid_id': f'{subject}_{hemi}_{roi}_v{voxel_idx:04d}',
                            'voxel_id': voxel_idx
                        })
                        neuroid_id += 1
                        
                except FileNotFoundError as e:
                    print(f"  WARNING: Skipping {subject} {hemi}_{roi} - {e}")
                    continue
    
    # Concatenate all responses: (50 videos, total_voxels)
    all_responses = np.concatenate(all_responses, axis=1)
    n_videos, n_neuroids = all_responses.shape
    
    print(f"\nTotal: {n_videos} videos × {n_neuroids} neuroids")
    
    # Compute noise ceiling per ROI (across subjects)
    # Note: We compute at ROI level because voxels aren't spatially matched across subjects
    print("Computing noise ceiling (variance-based, at ROI level across subjects)...")
    
    # Group by subject, ROI, hemisphere to compute ROI-level noise ceilings
    neuroid_df = pd.DataFrame(neuroid_coords)
    nc_per_voxel = np.full(n_neuroids, np.nan)
    
    for roi in VISUAL_ROIS:
        for hemi in HEMISPHERES:
            # Find all voxels for this ROI+hemisphere across all subjects
            mask = (neuroid_df['region'] == roi) & (neuroid_df['hemisphere'] == hemi)
            roi_neuroid_indices = np.where(mask)[0]
            
            if len(roi_neuroid_indices) == 0:
                continue
            
            # Get responses for this ROI from all subjects: (n_videos, n_voxels_in_roi)
            roi_responses = all_responses[:, roi_neuroid_indices]
            
            # Group by subject and average across voxels within each subject
            # This gives us (n_videos, n_subjects) for this ROI
            subjects_in_roi = neuroid_df.loc[mask, 'subject'].values
            subject_means = []
            for subj in ALL_SUBJECTS:
                subj_mask = subjects_in_roi == subj
                if subj_mask.any():
                    subj_mean = np.nanmean(roi_responses[:, subj_mask], axis=1)  # (n_videos,)
                    subject_means.append(subj_mean)
            
            if len(subject_means) >= 2:
                # Shape: (1, n_videos, n_subjects)
                subject_means = np.stack(subject_means, axis=-1)[np.newaxis, :, :]
                roi_nc = compute_noise_ceiling_variancebased(subject_means)[0]
                
                # Assign this ROI-level noise ceiling to all voxels in this ROI
                nc_per_voxel[roi_neuroid_indices] = roi_nc
                
                print(f"  {hemi}_{roi}: {len(roi_neuroid_indices)} voxels, NC={roi_nc:.2f}%")
    
    print(f"\nOverall noise ceiling: mean={np.nanmean(nc_per_voxel):.2f}%, "
          f"median={np.nanmedian(nc_per_voxel):.2f}%, "
          f"range=[{np.nanmin(nc_per_voxel):.2f}, {np.nanmax(nc_per_voxel):.2f}]")
    
    # Create stimulus_id coordinate
    videos = metadata['video'].values
    stimulus_ids = [video_to_stimid_no_ext.get(v, video_to_stimid.get(v, f'unknown_{v}')) 
                    for v in videos]
    
    # Create xarray DataArray
    data = all_responses[:, :, np.newaxis]  # Add time_bin dimension: (50, n_neuroids, 1)
    
    # Build coordinate dictionaries
    presentation_coords = {
        'stimulus_id': ('presentation', stimulus_ids)
    }
    
    neuroid_df = pd.DataFrame(neuroid_coords)
    neuroid_coord_dict = {
        'subject': ('neuroid', neuroid_df['subject'].values),
        'region': ('neuroid', neuroid_df['region'].values),
        'hemisphere': ('neuroid', neuroid_df['hemisphere'].values),
        'neuroid_id': ('neuroid', neuroid_df['neuroid_id'].values),
        'voxel_id': ('neuroid', neuroid_df['voxel_id'].values),
        'noise_ceiling': ('neuroid', nc_per_voxel)
    }
    
    time_bin_coords = {
        'time_bin_start': ('time_bin', [0]),
        'time_bin_end': ('time_bin', [TR_MS])
    }
    
    coords = {**presentation_coords, **neuroid_coord_dict, **time_bin_coords}
    
    # Create NeuroidAssembly
    assembly = NeuroidAssembly(
        data,
        coords=coords,
        dims=['presentation', 'neuroid', 'time_bin']
    )
    
    # Set identifier
    assembly.attrs['identifier'] = 'Marvi2025'
    assembly.attrs['stimulus_set_identifier'] = 'Marvi2025'
    assembly.attrs['n_subjects'] = len(ALL_SUBJECTS)
    assembly.attrs['n_rois'] = len(VISUAL_ROIS)
    assembly.attrs['tr_ms'] = TR_MS
    
    return assembly


def main():
    """Package and save Marvi2025 fMRI assembly."""
    print("Packaging Marvi2025 fMRI data...\n")
    
    assembly = package_marvi2025_assembly()
    
    print(f"\nAssembly created!")
    print(f"   Shape: {assembly.shape}")
    print(f"   Dims: {assembly.dims}")
    print(f"   Coords: {list(assembly.coords.keys())}")
    
    # Save locally for testing (use pickle to preserve MultiIndex)
    import pickle
    output_path = Path(__file__).parent / 'marvi2025_assembly.pkl'
    with open(output_path, 'wb') as f:
        pickle.dump(assembly, f)
    print(f"\nSaved to: {output_path}")
    
    return assembly


if __name__ == '__main__':
    assembly = main()
