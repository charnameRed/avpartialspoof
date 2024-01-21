PATH_DATA_ORI = 'data/original'
PATH_OUTPUT = 'data/processed'
NUM_FAKE = 6
RATIO_FAKE = 0.53

from tools import *
import os,random,tqdm

num_fake = NUM_FAKE
ratio_fake = RATIO_FAKE

# for ratio_fake in tqdm.tqdm(list_ratio,position=0):


dir_out = PATH_OUTPUT+f'PartialFAVCeleb_r{ratio_fake:.2f}'

shutil.rmtree(dir_out,ignore_errors=True)

os.makedirs(dir_out)

root_data_ori_rr = PATH_DATA_ORI + '/RealVideo-RealAudio'
ids = getIDs(root_data_ori_rr)
random.shuffle(ids)

subset = ['train','dev','eval']

lst_id = {}
lst_id['train'] = ids[0:int(0.6*len(ids))]
lst_id['dev'] = ids[int(0.6*len(ids)):int(0.8*len(ids))]
lst_id['eval'] = ids[int(0.8*len(ids)):]

count_fake_clips = 0
count_all_clips = 0

for sub in tqdm.tqdm(subset,position=1,leave=False):
    lst = lst_id[sub]
    num = len(lst)
    f = open(f'{dir_out}/{sub}.csv','w')
    f.write('id\ttag\n')

    for id in tqdm.tqdm(lst,position=2,leave=False):
        fake_clips,all_clips = generateMaterial(id,ratio_fake,PATH_DATA_ORI,dir_out+'/data',1,num_fake)
        count_fake_clips += fake_clips
        count_all_clips += all_clips
        f.write(f'{id.split("/")[-1]}/real\t0\n')
        for subfolder in ([f'fake_{number}' for number in range(num_fake)]):
            f.write(f'{id.split("/")[-1]}/{subfolder}\t1\n')
ratio_count = count_fake_clips/count_all_clips
with open(f'{dir_out}/counted_ratio_{ratio_count:.3f}.txt','w') as f:
    pass
