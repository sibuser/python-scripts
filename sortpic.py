#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import os
import re
import shutil
import exifread
import argparse


def check_path(paths):
    [os.stat(os.path.abspath(path)) for path in paths]


def fetch_exif(path):
    exif_tags = {
        'EXIF DateTimeDigitized': '',
        'EXIF DateTimeOriginal': '',
        'EXIF ExifImageLength': '',
        'EXIF ExifImageWidth': '',
        'EXIF ExifVersion': '',
        'EXIF ExposureBiasValue': '',
        'EXIF ExposureProgram': '',
        'EXIF ExposureTime': '',
        'EXIF Flash': '',
        'EXIF FNumber': '',
        'EXIF FocalLength': '',
        'EXIF ISOSpeedRatings': '',
        'EXIF MaxApertureValue': '',
        'EXIF MeteringMode': '',
        'EXIF SceneType': '',
        'EXIF ShutterSpeedValue': '',
        'EXIF SubSecTime': '',
        'Image DateTime': '',
        'Image ImageDescription': '',
        'Image Make': '',
        'Image Model': '',
        'Image Orientation': '',
        'Image XResolution': '',
        'Image YResolution': '',
        'ImageType': '',
        'ImageNumber': '',
        'OwnerName': '',
        'SerialNumber': '',
        'FirmwareVersion': '',
        'InternalSerialNumber': '',
    }

    exif_keys = exif_tags.keys()

    with open(path, 'rb') as image_file:
        # image_tags = exifread.process_file(image_file, details=False)
        image_tags = exifread.process_file(image_file)
        image_keys = image_tags.keys()
        for key_name in exif_keys:
            if key_name in image_keys:
                exif_tags[key_name] = image_tags[key_name]
    return exif_tags


months = {
    '01': '01 January',
    '02': '02 February',
    '03': '03 March',
    '04': '04 April',
    '05': '05 May',
    '06': '06 June',
    '07': '07 July',
    '08': '08 August',
    '09': '09 September',
    '10': '10 October',
    '11': '11 November',
    '12': '12 December'
}


def proceed_sort(path, is_dry):
    for root, dirs, files in os.walk(path):
        for file in files:
            date_time = fetch_exif(os.path.join(root, file)).get('Image DateTime', '')
            # print(date_time)
            if date_time != '':
                m = re.match('(\d+):(\d+):(\d+)\s\w+', str(date_time))
            else:
                m = re.match('(\d+)-(\d+)-(\d+)\s\w+', str(file))
            if m is None:
                m = re.match('IMG-(\d\d\d\d)(\d\d)(\d\d)-\w+', str(file))
            if m is None:
                m = re.match('video-(\d+)-(\d+)-(\d+)-.*', str(file))
            if m is None:
                m = re.match('Screenshot at (\d+)-(\d+)-(\d+).*', str(file))

            if m is not None:
                year = m.group(1)
                month = months[str(m.group(2))]
                day = m.group(3)

                if not is_dry:
                    if not os.path.exists(os.path.join('target', year, month, day)):
                        os.makedirs(os.path.join('target', year, month, day))

                    if not os.path.exists(os.path.join('target', year, month, day, file)):
                        print(file, date_time)
                        shutil.move(os.path.join(root, file), os.path.join('target', year, month, day, file))
                    else:
                        print(os.path.join('target', year, month, day, file), 'exitst!!!!')
                else:
                    print(os.path.join('target', year, month, day, file))

def rename_pitctures(path, is_dry):
    for root, dirs, files in os.walk(path):
        for file in files:
            date_time = fetch_exif(os.path.join(root, file)).get('Image DateTime')
            if date_time != '':
                m = re.match('(\d+):(\d+):(\d+)\s(\d+):(\d+):(\d+)', str(date_time))
                year = m.group(1)
                month = m.group(2)
                day = m.group(3)
                hours = m.group(4)
                minutes = m.group(5)
                seconds = m.group(6)                    
                extension = file.split('.')[-1]
                new_picture_name = '{0}-{1}-{2} {3}:{4}:{5}.{6}'.format(year, month, day, hours, minutes, seconds, extension)
                print(new_picture_name)
                
                if not is_dry:
                    shutil.move(os.path.join(root, file), os.path.join(root, new_picture_name))

            # print(date_time)


def revert_sort(path):
    """
    Function will walk over all folders and move all files into a folder

    :param path: path where you have all pictures
    :return:
    """
    os.mkdir('restore')
    for root, dirs, files in os.walk(path):
        for file in files:
            print(os.path.join(root, file))
            shutil.move(os.path.join(root, file), os.path.join('restore', file))


def main(args=None):
    """
    :param args:
    :return: 0 if everything is OK
    """
    parser = argparse.ArgumentParser(
        description='Sort files.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('paths', nargs='+', metavar='PATH', help='paths from where will be taken all pictures')
    parser.add_argument('--rename', action='store_true', help='Rename pictures')
    parser.add_argument('--dry', action='store_true', help='dry run')
    parser.add_argument('-r', '--revert', action='store_true', help='revert changes')

    opts = parser.parse_args(args)
    check_path(opts.paths)
    if opts.revert:
        [revert_sort(path) for path in opts.paths]
    elif opts.rename:
        [rename_pitctures(path, opts.dry) for path in opts.paths]
    else:
        [proceed_sort(path, opts.dry) for path in opts.paths]



if __name__ == '__main__':
    main()



