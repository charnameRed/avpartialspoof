# PartialFAVCeleb

The Multi-modal Partialy-Spoofed dataset based on [FakeAVCeleb-V1.2](https://github.com/DASH-Lab/FakeAVCeleb)

Sample in under `data/processed` folder.

## Environments

- python=3.10
- tqdm=4.65.0
- ffmpeg=1.4
- ffmpeg-python=0.2.0
- numpy=1.23.5
- soundfile=0.12.1
- librosa==0.10

## Usage

In `datasetGenerate.py`, set the `PATH_DATA_ORI` as the original FakeAVCeleb path, and the `PATH_OUTPUT` as the required output path.

The fake ratio(between 0 and 1) and the required fake video number can be adjust by editing `NUM_FAKE` and `RATIO_FAKE`.

Run `datasetGenerate.py`.

The final ratio fake will be higher than the `RATIO_FAKE`, which can be check by the text file named `counted_ratio_<real fake ratio>.txt`.

## Citation

*多模态部分伪造数据集的构建与基准检测* (*Construction and benchmark of multimodal partial forgery
deepfake dataset*). Paper accepted. 

Author:郑盛有, 陈雁翔, 赵祖兴, 刘海洋.

DOI:10. 11772/j.issn.1001-9081.2023101506. 

Further details will be added after publication.

## License

Code is released under the MIT license.
