#!/usr/bin/env python3
"""
Load Marvi2025 fMRI assembly locally for development/testing.
"""

from pathlib import Path
import numpy as np
from brainscore_core.supported_data_standards.brainio.assemblies import NeuroidAssembly
import xarray as xr


def load_local_marvi2025_assembly() -> NeuroidAssembly:
    """
    Load the locally packaged Marvi2025 fMRI assembly.
    
    Returns
    -------
    assembly : NeuroidAssembly
        Shape (50 presentations, 71262 neuroids, 1 time_bin)
    """
    import pickle
    
    assembly_path = Path(__file__).parent / 'marvi2025_assembly.pkl'
    
    if not assembly_path.exists():
        raise FileNotFoundError(
            f"Assembly not found: {assembly_path}\n"
            f"Run package_marvi2025_fmri.py first to create it."
        )
    
    # Load pickled assembly
    with open(assembly_path, 'rb') as f:
        assembly = pickle.load(f)
    
    return assembly


if __name__ == '__main__':
    """Quick test of local assembly loading."""
    print("Loading Marvi2025 fMRI assembly...")
    assembly = load_local_marvi2025_assembly()
    
    print(f"\nLoaded successfully!")
    print(f"   Identifier: {assembly.attrs.get('identifier', 'N/A')}")
    print(f"   Shape: {assembly.shape}")
    print(f"   Dims: {assembly.dims}")
    
    print(f"\nCoordinates:")
    for coord in assembly.coords:
        coord_data = assembly.coords[coord]
        if len(coord_data.shape) == 1 and len(coord_data) <= 10:
            print(f"   {coord}: {list(coord_data.values)}")
        else:
            print(f"   {coord}: shape={coord_data.shape}, "
                  f"example={coord_data.values.flat[0]}")
    
    print(f"\nData:")
    print(f"   dtype: {assembly.dtype}")
    print(f"   range: [{assembly.values.min():.3f}, {assembly.values.max():.3f}]")
    print(f"   mean: {assembly.values.mean():.3f}")
    
    print(f"\nNoise Ceiling:")
    if 'noise_ceiling' in assembly.coords:
        nc = assembly.coords['noise_ceiling'].values
        print(f"   mean: {nc.mean():.2f}%")
        print(f"   median: {np.median(nc):.2f}%")
        print(f"   range: [{nc.min():.2f}%, {nc.max():.2f}%]")
    
    print(f"\nSubjects: {sorted(set(assembly.coords['subject'].values))}")
    print(f"ROIs: {sorted(set(assembly.coords['region'].values))}")
    print(f"Hemispheres: {sorted(set(assembly.coords['hemisphere'].values))}")
