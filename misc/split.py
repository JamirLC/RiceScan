import splitfolders

input_folder = 'dataset'
output_folder = 'output_dataset'
splitfolders.ratio(input_folder, output = output_folder, seed = 42, ratio = (.8,.1,.1), group_prefix = None)

print("Dataset split completed, Check the 'ouput_dataset' folder.")