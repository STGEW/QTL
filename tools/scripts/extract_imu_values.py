import re
import argparse
import numpy as np


acc_x_patt = re.compile(r'"acc_x": (?P<acc_x>-?\d+.?\d+),')
acc_y_patt = re.compile(r'"acc_y": (?P<acc_y>-?\d+.?\d+),')
acc_z_patt = re.compile(r'"acc_z": (?P<acc_z>-?\d+.?\d+),')

counters = {
    'x': 0,
    'y': 0,
    'z': 0
}


sums = {
    'x': 0,
    'y': 0,
    'z': 0
}

data = {
    'x': [],
    'y': [],
    'z': []
}

def calculate_mean_rms(arr):
    mean = np.mean(arr)  # Calculate mean using numpy
    rms = np.sqrt(np.mean(np.square(arr)))  # Calculate RMS using numpy
    return mean, rms

def extract_imu_values(input_file, output_file):
    # Open the input log file and the output file
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:

        for l in infile:
            res = acc_x_patt.search(l)
            if res:
                x = float(res.group('acc_x'))
                outfile.write("acc_x={}\n".format(x))
                sums['x'] += x
                data['x'].append(x)
                counters['x'] += 1
            res = acc_y_patt.search(l)
            if res:
                y = float(res.group('acc_y'))
                outfile.write("acc_y={}\n".format(y))
                sums['y'] += y
                data['y'].append(y)
                counters['y'] += 1
            res = acc_z_patt.search(l)
            if res:
                z = float(res.group('acc_z'))
                outfile.write("acc_z={}\n".format(z))
                sums['z'] += z
                data['z'].append(z)
                counters['z'] += 1

    print(f'Average x: {sums["x"]/counters["x"]} y: {sums["y"]/counters["y"]} z: {sums["z"]/counters["z"]}')
    mean, rms = calculate_mean_rms(data['x'])
    print(f'x mean: {mean} rms: {rms}')
    mean, rms = calculate_mean_rms(data['y'])
    print(f'y mean: {mean} rms: {rms}')
    mean, rms = calculate_mean_rms(data['z'])
    print(f'z mean: {mean} rms: {rms}')

if __name__ == '__main__':
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Extract IMU values from a log file and save them to an output file.')
    parser.add_argument('--input_file', help='Path to the input log file')
    parser.add_argument('--output_file', help='Path to the output file where IMU values will be saved')

    # Parse arguments
    args = parser.parse_args()

    # Call the function with the provided arguments
    extract_imu_values(args.input_file, args.output_file)