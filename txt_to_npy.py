import argparse
import os
import shutil
import dataload


"""_summary_
Convert annotated files(.txt) to train/val or test files for Stratified-Transformer(.npy) .
"""
def parse_args():
    '''PARAMETERS'''
    parser = argparse.ArgumentParser(description = "Convert annotated files(.txt) to rgbxyzl(.npy). ")
    parser.add_argument('-i','--input_dir',  type=str, required=True,   help='input_directory')
    parser.add_argument('-o','--output_dir', type=str, required=False, help='output_directory')
    parser.add_argument('--is_annotated',    action = "store_true")
    parser.add_argument('--separator',       default = ',',    choices=[',', 't'], help='separator of input data.')
    parser.add_argument('--no_color',        action = "store_true")
    return parser.parse_args()



def main(args):
    directories = [os.path.join(args.input_dir, d) for d in os.listdir(args.input_dir) if
                   os.path.isdir(os.path.join(args.input_dir, d))]
    output_path = os.path.join(os.path.dirname(args.input_dir), f"{os.path.basename(args.input_dir)}_txt_to_npy")
    # os.makedirs(output_path,exist_ok=True)
    for directory in directories:
        dataload.convert_files(directory,
                                   output_path,
                                   args.is_annotated,
                                   args.separator,
                                   args.no_color)
    print(f"Converted files saved to {output_path}")
    return 

if __name__=="__main__":
    args = parse_args()
    main(args)