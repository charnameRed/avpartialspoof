import numpy as np
import random as rd
import os,shutil,math,librosa
import ffmpeg
import soundfile as sf
import json

def findFolders(root:str):
    tree = os.walk(root)
    ro,dirs,_ = next(tree)
    return dirs

def findFiles(root:str):
    tree = os.walk(root)
    ro,_,files = next(tree)
    return files

def fileListFilter(filelist:list,avstatus:str):
    '''用于滤除FakeCeleb中未使用对应真实视频做基底的视频, 其文件名特征为第二段不含"id"'''
    if avstatus in ['ff','rf']:
        for file in filelist[:]:
            try:
                if not 'id' in file.split('_')[1]:
                    filelist.remove(file)
            except:
                filelist.remove(file)
    elif avstatus == 'rr':
        for file in filelist[:]:
            if not 'mp4' in file:
                filelist.remove(file)
    return filelist

def getIDs(root_FAVceleb_RR):
    '''
    输入RR数据所在的文件
    取得所有说话人的ID
    返回列表,内容为所有说话人以'id*****'形式表示的由地区开始的文件夹路径
    '''
    folders_area = findFolders(root_FAVceleb_RR)
    lst = []
    for folder_area in folders_area:
        ro_a = root_FAVceleb_RR + '/' + folder_area
        folders_gender = findFolders(ro_a)
        for folder_gender in folders_gender:
            ro_g = ro_a + '/' + folder_gender
            folders_id = findFolders(ro_g)
            for folder_id in folders_id:
                lst.append(f'{folder_area}/{folder_gender}/{folder_id}')
    
    return lst

def _getFilelist(avstatus:str,id_path,root):

    '''
    用于根据说话人id获取备选文件列表,返回文件完整相对路径
    id_path格式为'folder_area/folder_gender/folder_id',直接使用getIDs()生成即可
    使用'fr','rf','ff','rr'设置音频与视频的真伪
    其中前者为音频,后者为视频
    f为伪造,r为真实
    '''
    folderlist = {
        'rr':f'{root}/RealVideo-RealAudio',
        'fr':f'{root}/RealVideo-FakeAudio',
        'rf':f'{root}/FakeVideo-RealAudio',
        'ff':f'{root}/FakeVideo-FakeAudio'
    }

    try:
        folder = folderlist[avstatus]
    except:
        print('check the usage of _getFilelist function')
    lst = findFiles(f'{folderlist[avstatus]}/{id_path}')
    fileListFilter(lst,avstatus)
    filepath_list = [f'{folderlist[avstatus]}/{id_path}/{ele}' for ele in lst]
    rd.shuffle(filepath_list)
    return filepath_list

def randClip(len:int,ratio:float):
    '''
    根据输入长度与概率生成片段伪造序列
    '''
    lst = [0 for i in range(len)]
    for i,_ in enumerate(lst):
        if rd.random() < ratio:
            lst[i] = 1
            
    return np.array(lst)

def getClipsFR(len:int,ratio_fake:float=0.5):
    '''
    根据输入的片段数量与伪造概率生成音频,视频,混合三个序列的分片真伪序列
    输出为二维numpy矩阵,顺序为[audio,video,mixed]
    '''

    if not (ratio_fake >=0 and ratio_fake <=1):
        print('片段真伪概率必须在0~1范围内')
        return -1
    ratio = 1-math.sqrt(1-ratio_fake)
    vid = randClip(len,ratio)
    aud = randClip(len,ratio)

    mix = vid * aud
    vid = vid - mix
    aud = aud - mix

    return np.stack((aud,vid,mix))

def getRandSeg(clips:np.ndarray,length:int):
    seg = [[],[],[]]
    seg_s = []
    clips_new = np.zeros((3,math.ceil(length*25/10)))
    for idx,modal in enumerate(clips):
        p = modal[0]
        if p == 1:
            seg_temp = [0+rd.randint(0,10)]
        else:
            seg_temp = []
        for i,clip in enumerate(modal):
            if clip != p:
                seg_temp.append(i*25+rd.randint(-10,10))
            if len(seg_temp) == 2:
                seg_s.append(seg_temp+[idx])
                seg_temp = []
            p = clip
        
        if len(seg_temp) != 0:
            seg_temp.append(length*25+rd.randint(-10,0))
            seg_s.append(seg_temp+[idx])

    seg_s.sort(key=lambda lst:lst[0])

    # 不同模态重叠部分取中点分割
    for idx,element in enumerate(seg_s[:-1]):
        end_p = element[1]
        start_f = seg_s[idx+1][0]
        if end_p >= start_f:
            element[1] = int((end_p+start_f)/2)
            seg_s[idx+1][0] = element[1]

    for start,end,idx in seg_s:
        seg[idx].append([start,end])
        clips_new[idx][int(start/10):int(end/10)+1] = 1

    for idx,num in enumerate(clips_new[2]):
        if num == 1:
            clips_new[0][idx] = 0
            clips_new[1][idx] = 0
        elif clips_new[0][idx] == 1 and clips_new[1][idx] == 1:
            clips_new[0][idx] = 0
            clips_new[1][idx] = 0
            clips_new[2][idx] = 1

        
    return seg,clips_new

def _getLongest_info(filelist):
    file_longest = ''
    dur_max = 0
    width,height = 0,0
    for file in filelist:
        info = ffmpeg.probe(file)
        if min(int(float(info['streams'][0]['duration'])),int(float(info['streams'][1]['duration']))) > dur_max:
            dur_max = min(int(float(info['streams'][0]['duration'])),int(float(info['streams'][1]['duration'])))
            file_longest = file
            try:
                width = int(info['streams'][0]['width'])
                height = int(info['streams'][0]['height'])
            except:
                width = int(info['streams'][1]['width'])
                height = int(info['streams'][1]['height'])
    return file_longest,dur_max,width,height

def extractPicAudio(path_file,dir_out,width,height,framerate,samplerate,status):
    '''
    提取图像/声音
    '''
    os.makedirs(dir_out,exist_ok=True)
    command = f'ffmpeg -loglevel error -i {path_file} -s {width}x{height} -r {framerate} {dir_out}/%3d.png -y'
    if status != 'fr':
        os.system(command)
    command = f'ffmpeg -loglevel error -i {path_file} -ar {samplerate} -f wav {dir_out}/audio.wav -y'
    if status != 'rf':
        os.system(command)
    return 0

def generateMaterial(id,ratio_fake,dir_data_ori,dir_out,clip_duration,sub_number):
    '''
    依据id、伪造片段比例生成数据集
    输出形式为图片+音频
    ratio_fake = 0 即为非伪造条目
    '''
    id_person = id.split('/')[-1]
    lst_status = ['fr','rf','ff','rr']
    num_clips = int(1/clip_duration)
    file = {
        'list':{},
        'dur':{},
        'audio':{}
    }
    framerate = 25
    num_fram_clip = int(framerate/num_clips)
    samplerate = 16000
    num_sam_clip = int(samplerate/num_clips)
    count_fake_clips = 0
    count_all_clips = 0
    for status in lst_status:
        os.makedirs(f'temp/{status}',exist_ok=True)
        file['list'][status] = _getFilelist(status,id,dir_data_ori)

    info_id = ffmpeg.probe(file['list']['rr'][0])
    length_media = min(int(float(info_id['streams'][0]['duration'])),int(float(info_id['streams'][1]['duration'])))
    try:
        width = int(info_id['streams'][0]['width'])
        height = int(info_id['streams'][0]['height'])
    except:
        width = int(info_id['streams'][1]['width'])
        height = int(info_id['streams'][1]['height'])
    extractPicAudio(file['list']['rr'][0],f'temp/rr/{id_person}',width,height,framerate,samplerate,'rr')


    # 图片复制&音频剪切
    os.makedirs(f'{dir_out}/{id_person}/real',exist_ok=True)
    for num in range(0,length_media*framerate):
        shutil.copy(f'temp/rr/{id_person}/{num+1:0>3d}.png',f'{dir_out}/{id_person}/real/{num+1:0>3d}.png')
    audio,_ = librosa.load(f'temp/rr/{id_person}/audio.wav',sr = 16000)
    audio_out = audio[0:length_media*samplerate]
    sf.write(f'{dir_out}/{id_person}/real/audio.wav',audio_out,samplerate)
    
    tags_clip = np.zeros((3,math.ceil(length_media*25/10)))
    np.save(f'{dir_out}/{id_person}/real/tag_detailed.npy',tags_clip)

    # 各个伪造视频中取最长者, 并使用四状态视频中最短者的长度作为合成视频长度

    for subfolder in [f'fake_{number}' for number in range(sub_number)]:
        length_media = float('inf')
        for status in lst_status:
            file[status],file['dur'][status],width,height= _getLongest_info(file['list'][status])
            if status in ['rf','ff']:
                file['list'][status].remove(file[status])
            length_media = min(file['dur'][status],length_media)
            extractPicAudio(file[status],f'temp/{status}/{id_person}',width,height,framerate,samplerate,status)
            if status != 'rf':
                file['audio'][status],_ = librosa.load(f'temp/{status}/{id_person}/audio.wav',sr = samplerate)
        os.makedirs(f'{dir_out}/{id_person}/{subfolder}',exist_ok=True)

        # 根据伪造占比生成概率标签并据此进行视频音频拼接
        while True:
            tags_clip = getClipsFR(length_media*num_clips,ratio_fake)
            if np.sum(tags_clip) != 0:
                break
        
        # 真伪转换点随机化, 并对标签进行更新
        seg,tags_clip = getRandSeg(tags_clip,length_media)

        # 写入记录
        with open(f'{dir_out.rstrip("/data")}/record_{subfolder}.txt','a') as f:
            f.write(f'id:{id}\n\trr:{file["rr"]}\n\tfr:{file["fr"]}\n\trf:{file["rf"]}\n\tff:{file["ff"]}\n\tout:temp/outvideo/{id_person}.mp4\n')
            f.write(f'{tags_clip}\n{"_"*100}\n\n')

        # 置入真实数据基底
        audio_out = file['audio']['rr'][0:length_media*samplerate]
        for num in range(0,length_media*framerate):
            shutil.copy(f'temp/rr/{id_person}/{num+1:0>3d}.png',f'{dir_out}/{id_person}/{subfolder}/{num+1:0>3d}.png')

        # 伪造音频插入+归一化
        for start,end in seg[0]:
            audio_temp = audio_out[start*640:end*640]
            power_tar = np.sum(audio_temp**2)
            audio_mat = file['audio']['fr'][start*640:end*640]
            power_mat = np.sum(audio_mat**2)
            if power_tar>0.0000001 and power_mat>0.0000001:
                audio_mat = audio_mat/math.sqrt(power_mat/power_tar)
            audio_out[start*640:end*640] = audio_mat

        # 伪造视频帧插入
        for start,end in seg[1]:
            for num in  range(start+1,end+1):
                shutil.copy(f'temp/rf/{id_person}/{num:0>3d}.png',f'{dir_out}/{id_person}/{subfolder}/{num:0>3d}.png')

        # 全伪造内容插入
        for start,end in seg[2]:
            for num in  range(start+1,end+1):
                shutil.copy(f'temp/ff/{id_person}/{num:0>3d}.png',f'{dir_out}/{id_person}/{subfolder}/{num:0>3d}.png')

            audio_temp = audio_out[start*640:end*640]
            power_tar = np.sum(audio_temp**2)
            audio_mat = file['audio']['fr'][start*640:end*640]
            power_mat = np.sum(audio_mat**2)
            if power_tar>0.0000001 and power_mat>0.0000001:
                audio_mat = audio_mat/math.sqrt(power_mat/power_tar)
            audio_out[start*640:end*640] = audio_mat

        # 输出声音文件
        sf.write(f'{dir_out}/{id_person}/{subfolder}/audio.wav',audio_out,samplerate)

        # 输出标签文件
        np.save(f'{dir_out}/{id_person}/{subfolder}/tag_detailed.npy',tags_clip)
        dic_seg = {}
        dic_seg['audio'] = seg[0]
        dic_seg['video'] = seg[1]
        dic_seg['both']  = seg[2]
        dic_seg['material']={}
        for status in lst_status:
            dic_seg['material'][status] = file[status]
        with open(f'{dir_out}/{id_person}/{subfolder}/segments.json','w') as f:
            json.dump(dic_seg,f,indent=4)

        for status in lst_status:
            shutil.rmtree(f'temp/{status}/{id_person}')
        
        count_fake_clips += np.sum(tags_clip)
        count_all_clips += tags_clip.shape[1]
    

    return count_fake_clips,count_all_clips
