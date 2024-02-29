# PartialFAVCeleb

基于 [FakeAVCeleb-V1.2](https://github.com/DASH-Lab/FakeAVCeleb) 建立的音视频多模态部分伪造数据集.

数据样例参考 `data/processed` 文件夹.

数据集仅提供生成代码, 具体生成所用数据请从[FakeAVCeleb](https://github.com/DASH-Lab/FakeAVCeleb)处下载.

## 运行环境

- python=3.10
- tqdm=4.65.0
- ffmpeg=1.4
- ffmpeg-python=0.2.0
- numpy=1.23.5
- soundfile=0.12.1
- librosa==0.10

## 生成方法

在 `datasetGenerate.py`文件中, 修改`PATH_DATA_ORI`和`PATH_OUTPUT`, 设置输入数据位置和输出数据位置, 可参考`data`文件夹下内容.

修改`NUM_FAKE`和`RATIO_FAKE`两项参数,设置伪造数据片段数和伪造比例.

运行`datasetGenerate.py`.

生成数据实际伪造比例会略高于`RATIO_FAKE`, 以`counted_ratio_<real fake ratio>.txt`文件名中伪造比例为准.

## 引用信息

《多模态部分伪造数据集的构建与基准检测》(《Construction and benchmark of multimodal partial forgery
deepfake dataset》).

作者:郑盛有, 陈雁翔, 赵祖兴, 刘海洋.

第四届中国媒体取证与安全大会, 南京, 2023.

![证书](https://github.com/charnameRed/avpartialspoof/assets/54922651/2df38ccd-82d1-4071-ba1b-40f05a78ebc0)

DOI:10. 11772/j.issn.1001-9081.2023101506. 
