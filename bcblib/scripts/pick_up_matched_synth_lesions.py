"""
Pick up synth lesion masks matched with the given lesion set from a dataset generated by *generate_synth_lesions*

Authors: Chris Foulon & Michel Thiebaut de Scotten
"""
import os
import argparse
import random
import numpy as np
import json
import csv
import copy
import re
import shutil


import nibabel as nib


def read_simple_list_from_csv(csv_path):
    if not os.path.isfile(csv_path):
        raise ValueError('{} is not a file'.format(csv_path))
    with open(csv_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        out_list = [f[0] for f in csv_reader]
    return out_list


def list_synth_les(synth_lesion_size_dict, exclude_list, size, number, size_range=0.1, pick_up_strat='random'):
    if size_range >= 1:
        size_range = size_range / 100
    file_list = []
    for s in synth_lesion_size_dict:
        if size - size_range * size <= int(s) <= size + size_range * size:
            file_list = file_list + [f for f in synth_lesion_size_dict[s] if f not in exclude_list]
    if number > len(file_list):
        # number = len(file_list)
        raise ValueError('Cannot find {} images of {} +- {} voxels in the synth dataset. '
                         'Try to increase the size range'.format(number, size, number * size_range))
    if pick_up_strat == 'random':
        return random.sample(file_list, k=number)
    else:
        return file_list[0:number]


def filter_synth_lesion_size_dict(synth_lesion_size_dict, exclude_list):
    filtered_synth_lesion_size_dict = {}
    for k in synth_lesion_size_dict:
        ll = [v for v in synth_lesion_size_dict[k] if v not in exclude_list]
        if ll:
            filtered_synth_lesion_size_dict[k] = ll
    return filtered_synth_lesion_size_dict


def __pick_up_synth_list(synth_lesion_size_dict, size_list, number=1, size_range=0.1, pick_up_strat='random'):
    synth_list = []
    for s in size_list:
        synth_list = synth_list + list_synth_les(synth_lesion_size_dict, synth_list, s, number, size_range,
                                                 pick_up_strat)
    return synth_list


def format_filename(filepath):
    filename = os.path.basename(filepath)
    split_ext = filename.split('.')
    if len(split_ext) > 1:
        no_ext = split_ext[0]
        ext = '.' + split_ext[1]
    else:
        no_ext = filename
        ext = '.csv'
    find_number = re.findall(r'_\d+', no_ext)
    if len(find_number) >= 1:
        number = '_' + str(int(find_number[0].split('_')[-1]) + 1)
        no_ext = no_ext.replace(find_number[0], '')
    else:
        number = '_1'
    return ''.join([filepath.split(filename)[0], no_ext, number, ext])


def save_new_list(synth_list, filepath):
    new_filepath = filepath
    while os.path.exists(new_filepath):
        new_filepath = format_filename(new_filepath)
    with open(new_filepath, mode='w+') as f:
        employee_writer = csv.writer(f, delimiter='\n', quotechar='"',
                                     quoting=csv.QUOTE_MINIMAL)
        employee_writer.writerow(synth_list)
        return new_filepath


def copy_picked_up_synth(file_list, output_folder):
    if not file_list:
        raise ValueError('The file list is empty')
    os.makedirs(output_folder)
    for file in file_list:
        shutil.copyfile(file, os.path.join(output_folder, os.path.basename(file)))


def copy_picked_up_list(file_list, filepath):
    filename = os.path.basename(filepath)
    split_ext = filename.split('.')
    if len(split_ext) > 1:
        output_folder = os.path.join(os.path.dirname(filepath), split_ext[0])
    else:
        output_folder = os.path.join(os.path.dirname(filepath), filename + '_files')
    copy_picked_up_synth(file_list, output_folder)


def pick_up_synth_list(synth_lesion_size_dict, size_list, filepath,  copy_synth_files=False, number=1, size_range=0.1,
                       pick_up_strat='random', exclude_lists=None, number_pickup=1):
    filtered_synth_lesion_size_dict = copy.deepcopy(synth_lesion_size_dict)
    if exclude_lists is not None and exclude_lists != []:
        if not isinstance(exclude_lists[0], list):
            concat_list = [exclude_lists]
        else:
            concat_list = []
            for li in exclude_lists:
                concat_list = concat_list + li
        print(concat_list)
        filtered_synth_lesion_size_dict = filter_synth_lesion_size_dict(filtered_synth_lesion_size_dict, concat_list)
    synth_lists_list = []
    for i in range(number_pickup):
        synth_list = __pick_up_synth_list(synth_lesion_size_dict, size_list, number, size_range, pick_up_strat)
        synth_lists_list = synth_lists_list + synth_list
        output_list_path = save_new_list(synth_list, filepath)
        if copy_synth_files:
            copy_picked_up_list(synth_list, output_list_path)
        filtered_synth_lesion_size_dict = filter_synth_lesion_size_dict(filtered_synth_lesion_size_dict, synth_list)
    return synth_lists_list


def main():
    output_list_filename = 'synth_lesions_list.csv'
    parser = argparse.ArgumentParser(description='Pick up synth lesion masks matched with the given lesion set from '
                                                 'a dataset generated by *generate_synth_lesions*')
    paths_group = parser.add_mutually_exclusive_group(required=True)
    paths_group.add_argument('-p', '--input_path', type=str, help='Root folder of the lesion dataset')
    paths_group.add_argument('-li', '--input_list', type=str, help='Text file containing the list of lesion files')
    parser.add_argument('-sd', '--synth_dict', type=str, help='path to the json dictionary file of listing the '
                                                              'synthetic lesions generated by *generate_synth_lesions*',
                        required=True)
    parser.add_argument('-o', '--output', type=str,
                        help='Either output path or output folder. In the latter case '
                        'the list will be stored in {}'.format(output_list_filename),
                        required=True)
    parser.add_argument('-cp', '--copy_synth_files', action='store_true',
                        help='copy the picked up synth lesions in a separated folder')
    parser.add_argument('-ps', '--pickup_strat', type=str, default='random', choices=['random', 'first'],
                        help='synth lesion pick up')
    parser.add_argument('-sr', '--size_range', type=float, default=0.1, help='percentage of size difference to '
                                                                             'pick matching lesions e.g. 0.1 means '
                                                                             '+-10%% of the size is considered a match')
    parser.add_argument('-ml', '--multiple_lists', type=int, default=1, help='generate several lists of synthetic '
                                                                             'lesions without overlap between them')
    parser.add_argument('-n', '--number_per_lesion', type=int, default=1,
                        help='number of matched synthetic lesions per actual lesion in the output list')
    parser.add_argument('-ex', '--exclude_lists', nargs='*', default=None,
                        help='Exclude the paths from the list files given '
                             '(So you can pick up a set without overlap with other ones)'
                             'e.g. -ex /path/to/list1.csv /path/to/list2.txt /path/to/list3.csv')

    # parser.add_argument('-v', '--verbose', default='info', choices=['none', 'info', 'debug'], nargs='?', const='info',
    #                     type=str, help='print info or debugging messages [default is "info"] ')
    args = parser.parse_args()
    if args.input_path is not None:
        les_list = [os.path.join(args.input_path, f) for f in os.listdir(args.input_path)]
    else:
        if not os.path.exists(args.input_list):
            raise ValueError(args.input_list + ' does not exist.')
        if args.input_list.endswith('.csv'):
            les_list = read_simple_list_from_csv(args.input_list)
        else:
            # default delimiter is ' ', it might need to be changed
            les_list = np.loadtxt(args.input_list, dtype=str, delimiter=' ')

    if os.path.isdir(args.output):
        list_file_path = os.path.join(args.output, output_list_filename)
    else:
        list_file_path = args.output

    if not os.path.isfile(args.synth_dict):
        raise ValueError('[{}] is not an existing synthetic lesion dict')
    try:
        json_file = open(args.synth_dict, 'r')
        synth_lesion_size_dict = json.load(json_file)
    except ValueError as e:
        raise e
    except OSError as err:
        raise OSError("OS error with path [{0}]: {1}".format(args.synth_dict, err))

    if args.exclude_lists is not None:
        exclude_lists = [read_simple_list_from_csv(f) for f in args.exclude_lists]
    else:
        exclude_lists = None

    size_list = [len(np.where(nib.load(les).get_fdata())[0]) for les in les_list]
    print(size_list)
    print(len(size_list))

    final_list = pick_up_synth_list(synth_lesion_size_dict, size_list, list_file_path,
                                    copy_synth_files=args.copy_synth_files,
                                    number=args.number_per_lesion,
                                    size_range=args.size_range,
                                    pick_up_strat=args.pickup_strat,
                                    exclude_lists=exclude_lists,
                                    number_pickup=args.multiple_lists)
    print(len(final_list))


if __name__ == '__main__':
    main()
