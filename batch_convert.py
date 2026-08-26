import os
import glob

def batch_convert(input_folder, output_folder, converter_func, input_ext, output_ext):
    os.makedirs(output_folder, exist_ok=True)
    
    input_files = glob.glob(os.path.join(input_folder, f"*{input_ext}"))
    
    if not input_files:
        print(f"No {input_ext} files found in {input_folder}")
        return
    
    print(f"Found {len(input_files)} files to convert")
    
    for input_file in input_files:
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        output_file = os.path.join(output_folder, f"{base_name}{output_ext}")
        
        try:
            print(f"Converting: {os.path.basename(input_file)}")
            converter_func(input_file, output_file, **kwargs)
        except Exception as e:
            print(f"Error: {e}")
    
