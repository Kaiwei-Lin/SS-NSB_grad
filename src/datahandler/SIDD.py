import os

import scipy.io
import numpy as np
import torch

from src.datahandler.denoise_dataset import DenoiseDataSet
from . import regist_dataset
import csv


@regist_dataset
class SIDD(DenoiseDataSet):
    '''
    SIDD datatset class using original images.
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _scan(self):
        dataset_path = os.path.join(self.dataset_dir, 'SIDD/SIDD_Medium_Srgb/Data')
        assert os.path.exists(dataset_path), 'There is no dataset %s'%dataset_path

        # scan all image path & info in dataset path
        for folder_name in os.listdir(dataset_path):
            # parse folder name of each shot
            parsed_name = self._parse_folder_name(folder_name)

            # add path & information of image 0
            info0 = {}
            info0['instances'] = parsed_name
            info0['clean_img_path'] = os.path.join(dataset_path, folder_name, '%s_GT_SRGB_010.PNG'%parsed_name['scene_instance_number'])
            info0['noisy_img_path'] = os.path.join(dataset_path, folder_name, '%s_NOISY_SRGB_010.PNG'%parsed_name['scene_instance_number'])
            self.img_paths.append(info0)

            # add path & information of image 1
            info1 = {}
            info1['instances'] = parsed_name
            info1['clean_img_path'] = os.path.join(dataset_path, folder_name, '%s_GT_SRGB_011.PNG'%parsed_name['scene_instance_number'])
            info1['noisy_img_path'] = os.path.join(dataset_path, folder_name, '%s_NOISY_SRGB_011.PNG'%parsed_name['scene_instance_number'])
            self.img_paths.append(info1)

    def _load_data(self, data_idx):
        info = self.img_paths[data_idx]

        clean_img = self._load_img(info['clean_img_path'])
        noisy_img = self._load_img(info['noisy_img_path'])

        return {'clean': clean_img, 'real_noisy': noisy_img, 'instances': info['instances'] }

    def _parse_folder_name(self, name):
        parsed = {}
        splited = name.split('_')
        parsed['scene_instance_number']      = splited[0]
        parsed['scene_number']               = splited[1]
        parsed['smartphone_camera_code']     = splited[2]
        parsed['ISO_speed']                  = splited[3]
        parsed['shutter_speed']              = splited[4]
        parsed['illuminant_temperature']     = splited[5]
        parsed['illuminant_brightness_code'] = splited[6]
        return parsed
    
@regist_dataset
class SIDD_NLF(SIDD):
    def _scan(self):
        predefined_nlf_path = './dataset/SIDD/noise_level_functions.csv' #FIXME: parameterize
        self.nlfs = None
        if os.path.exists(predefined_nlf_path):
            with open(predefined_nlf_path, 'r', encoding='utf-8') as f:
                rdr = csv.reader(f)
                for nlf in rdr:
                    if self.nlfs is None:
                        self.nlfs = [nlf]
                    else:
                        self.nlfs.append(nlf)
                f.close()    
        dataset_path = os.path.join(self.dataset_dir, 'SIDD/SIDD_Medium_Srgb/Data')
        assert os.path.exists(dataset_path), 'There is no dataset %s'%dataset_path

        # scan all image path & info in dataset path
        for folder_name in os.listdir(dataset_path):
            # parse folder name of each shot
            parsed_name = self._parse_folder_name(folder_name)

            # add path & information of image 0
            info0 = {}
            info0['instances'] = parsed_name
            info0['instances']['nlf'] = self._find_nlf(folder_name)
            info0['clean_img_path'] = os.path.join(dataset_path, folder_name, '%s_GT_SRGB_010.PNG'%parsed_name['scene_instance_number'])
            info0['noisy_img_path'] = os.path.join(dataset_path, folder_name, '%s_NOISY_SRGB_010.PNG'%parsed_name['scene_instance_number'])
            self.img_paths.append(info0)

            # add path & information of image 1
            info1 = {}
            info1['instances'] = parsed_name
            info1['instances']['nlf'] = self._find_nlf(folder_name)
            info1['clean_img_path'] = os.path.join(dataset_path, folder_name, '%s_GT_SRGB_011.PNG'%parsed_name['scene_instance_number'])
            info1['noisy_img_path'] = os.path.join(dataset_path, folder_name, '%s_NOISY_SRGB_011.PNG'%parsed_name['scene_instance_number'])
            self.img_paths.append(info1)
    
    def _find_nlf(self, folder_name):
        if self.nlfs is None: return None
        for nlf in self.nlfs:
            if nlf[0] == folder_name:
                return nlf[-2:]
        return None

    def _load_data(self, data_idx):
        info = self.img_paths[data_idx]

        clean_img = self._load_img(info['clean_img_path'])
        noisy_img = self._load_img(info['noisy_img_path'])

        return {'clean': clean_img, 'real_noisy': noisy_img, 'instances': info['instances']}


@regist_dataset
class prep_SIDD(DenoiseDataSet):
    '''
    dataset class for prepared SIDD dataset which is cropped with overlap.
    [using size 512x512 with 128 overlapping]
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _scan(self):
        self.dataset_path = self.dataset_dir
        assert os.path.exists(self.dataset_path), 'There is no dataset %s'%self.dataset_path
        for root, _, files in os.walk(os.path.join(self.dataset_path, 'orig')):
            self.img_paths = files

    def _load_data(self, data_idx):
        file_name = self.img_paths[data_idx]

        noisy_img = np.load(os.path.join(self.dataset_path, 'noise' , file_name))
        clean = np.load(os.path.join(self.dataset_path, 'orig' , file_name))
        clean = torch.from_numpy(clean)
        return {'clean': clean} #'instances': instance }
    
@regist_dataset
class prep_SIDD_NLF(prep_SIDD):
    def _scan(self):
        predefined_nlf_path = './dataset/SIDD/noise_level_functions.csv' #FIXME: parameterize
        self.nlfs = None
        if os.path.exists(predefined_nlf_path):
            with open(predefined_nlf_path, 'r', encoding='utf-8') as f:
                rdr = csv.reader(f)
                for nlf in rdr:
                    if self.nlfs is None:
                        self.nlfs = [nlf]
                    else:
                        self.nlfs.append(nlf)
                f.close() 
        super()._scan()

    def _get_nlf(self, file_name):
        scene_idx = int(file_name.split('_')[0]) //2 + 1 # ignore first row
        return self.nlfs[scene_idx][-2:]

    def _load_data(self, data_idx):
        file_name = self.img_paths[data_idx]
        nlf = self._get_nlf(file_name)
        noisy_img = self._load_img(os.path.join(self.dataset_path, 'RN' , file_name))
        clean = self._load_img(os.path.join(self.dataset_path, 'CL' , file_name))
        instance = {'nlf':nlf}
        return {'clean': clean, 'real_noisy': noisy_img, 'instances': instance}

@regist_dataset
class SIDD_val(DenoiseDataSet):
    '''
    SIDD validation dataset class 
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _scan(self):
        dataset_path = os.path.join(self.dataset_dir, 'orig')
        assert os.path.exists(dataset_path), 'There is no dataset %s'%dataset_path

        for root, _, files in os.walk(os.path.join(self.dataset_dir, 'orig')):
            self.img_paths = files


    def _load_data(self, data_idx):
        file_name = self.img_paths[data_idx]
        noisy_img = np.load(os.path.join(self.dataset_dir, 'noise', file_name))
        clean = np.load(os.path.join(self.dataset_dir, 'orig', file_name))
        clean = torch.from_numpy(clean)
        return {'clean': clean, 'idx': os.path.splitext(file_name)[0]}  # 'instances': instance }

@regist_dataset
class SIDD_benchmark(DenoiseDataSet):
    '''
    SIDD benchmark dataset class
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _scan(self):
        dataset_path = os.path.join(self.dataset_dir, 'SIDD')
        assert os.path.exists(dataset_path), 'There is no dataset %s'%dataset_path

        mat_file_path = os.path.join(dataset_path, 'BenchmarkNoisyBlocksSrgb.mat')

        self.noisy_patches = np.array(scipy.io.loadmat(mat_file_path, appendmat=False)['BenchmarkNoisyBlocksSrgb'])

        # for __len__(), make img_paths have same length
        # number of all possible patch is 1280
        for _ in range(1280):
            self.img_paths.append(None)

    def _load_data(self, data_idx):
        img_id   = data_idx // 32
        patch_id = data_idx  % 32

        noisy_img = self.noisy_patches[img_id, patch_id, :].astype(float)

        noisy_img = self._load_img_from_np(noisy_img)

        return {'real_noisy': noisy_img}

@regist_dataset
class prep_SIDD_benchmark(DenoiseDataSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _scan(self):
        self.dataset_path = os.path.join(self.dataset_dir, 'prep/SIDD_benchmark_s256_o0')
        assert os.path.exists(self.dataset_path), 'There is no dataset %s'%self.dataset_path
        for root, _, files in os.walk(os.path.join(self.dataset_path, 'RN')):
            self.img_paths = files

    def _load_data(self, data_idx):
        file_name = self.img_paths[data_idx]

        noisy_img = self._load_img(os.path.join(self.dataset_path, 'RN' , file_name))

        return {'real_noisy': noisy_img} #'instances': instance }
        