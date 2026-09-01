from pathlib import Path

def scrape_trajectory(input_dir, fraction, scrape_type):
    input_dir = Path(input_dir)
    
    # Find all step files
    step_files = sorted(input_dir.glob("step_*.xyz"))
    if not step_files:
        step_files = sorted(input_dir.glob("step_*.lmpstep"))
    
    if not step_files:
        raise ValueError(f"No step_*.xyz or step_*.lmpstep files found in {input_dir}")
    
    n_files = len(step_files)
    n_remove = int(n_files * fraction)
    
    if n_remove == 0:
        print(f"No files to remove (fraction {fraction} of {n_files} files)")
        return
    
    # Determine which files to keep
    if scrape_type == "top":
        keep_files = step_files[n_remove:]
    elif scrape_type == "bottom":
        keep_files = step_files[:-n_remove] if n_remove > 0 else step_files
    else:
        raise ValueError("scrape_type must be 'top' or 'bottom'")
    
    # Get extension from first file
    extension = step_files[0].suffix
    
    # Delete removed files
    removed_files = set(step_files) - set(keep_files)
    for file in removed_files:
        file.unlink()
        print(f"Removed: {file.name}")
    
    # Renumber remaining files starting from 0
    for new_index, old_file in enumerate(keep_files):
        new_name = f"step_{new_index:03d}{extension}"
        new_path = old_file.parent / new_name
        
        if new_path != old_file:
            old_file.rename(new_path)
            print(f"Renamed: {old_file.name} -> {new_name}")
    
    print(f"\nCompleted: Kept {len(keep_files)} files (removed {n_remove} files)")
