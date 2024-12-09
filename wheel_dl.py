
# Wheel Downloader
# Check versions at https://pypi.org/project/mediapipe/#files (replace mediapipe with project name)
# https://docs.blender.org/manual/en/dev/advanced/extensions/python_wheels.html
# https://docs.blender.org/manual/en/latest/advanced/extensions/getting_started.html#manifest

import subprocess
import os
import re

target_dir = './wheels'

# MacOS builds are commented out because I don't know enough about Mac version numbers, and can't test them.
# If you uncomment them here, please make sure to change blender_manifest.toml to include a build for macs.
wheels = {
    # https://pypi.org/project/msvc-runtime/#files
    "msvc-runtime": [ # Attempting as a way to get past the Microsoft Visual C++ Redistributable requirements of Mediapipe. Not from Microsoft.
        'win_amd64',
    ],
    # https://pypi.org/project/opencv-python/#files
    'opencv-python': [
        'win_amd64',
        # 'manylinux_2_17_x86_64',
        # 'manylinux_2_17_aarch64',
        # 'macosx_12_0_x86_64',
        # 'macosx_11_0_arm64',
    ],
    # https://pypi.org/project/mediapipe/#files
    'mediapipe==0.10.14': [
        'win_amd64',
        # 'manylinux_2_17_x86_64',
        # 'manylinux_2_17_aarch64',
        # 'macosx_11_0_x86_64',
        # 'macosx_11_0_universal2', # Doesn't seem to be able to get dependencies
    ],
    # https://pypi.org/project/scikit-image/#files
    'scikit-image': [
        'win_amd64',
        # 'manylinux_2_17_x86_64',
        # 'manylinux_2_17_aarch64',
        # 'macosx_12_0_arm64',
        # 'macosx_10_9_x86_64',
    ],
    # https://pypi.org/project/numpy/1.26.4/#files
    'numpy==1.26.4': [ # When developing, numpy 2.0 had just released, and wasn't compatible with mediapipe yet.
        'win_amd64',
        # 'manylinux_2_17_x86_64',
        # 'manylinux_2_17_aarch64',
        # 'macosx_11_0_arm64',
        # 'macosx_10_9_x86_64',
    ],
}

download_files = input('Download files? (Y/n): ')
if len(download_files) == 0 or download_files[0].lower() == 'y':
    delete_old = input('Delete old wheel files? (Y/n): ')
    if len(delete_old) == 0 or delete_old[0].lower() == 'y':
        import shutil
        shutil.rmtree(target_dir, ignore_errors=True)
        os.makedirs(target_dir)

    for package in wheels.keys():
        print('Downloading %s' % package)
        for platform in wheels[package]:
            print('\t%s' % platform)
            subprocess.run(['pip', 'download', package, '--dest', target_dir, '--only-binary=:all:', '--python-version=3.11', '--platform=%s' % platform])

    # Everything should be downloaded, now print something nice and easy to copy into blender_manifest.
    print('Download complete')

# os.rename any wheel that's for a version less than cp311 (like OpenCV being cp37)
# Really, it just replaces everything with -cp311-
filenames = os.listdir(target_dir)
for file in filenames:
    new_file = re.sub('-cp3\d+-', '-cp311-', file) 
    os.rename(os.path.join(target_dir, file), os.path.join(target_dir, new_file))


filenames = os.listdir(target_dir)
# Move mediapipe to last, since it needs everything else to be installed as a dependency first
mp_name = list(filter(lambda x: 'mediapipe' in x.lower(), filenames))[0] 
mp_index = filenames.index(mp_name)
filenames.pop(mp_index)
filenames.append(mp_name)

print('Copy the following into blender_manifest.toml to update the wheel:\n')
print('wheels = [')
for file in filenames:
    print('\t"%s/%s",' % (target_dir, file))

print(']')

print('# Scroll up, you need to paste that final list into blender_manifest.toml')
print('# Run "blender --command extension build --split-platforms" afterwards to build the extension')