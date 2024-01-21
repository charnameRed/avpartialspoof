# avpartialspoof

The Multi-modal Partialy-Spoofed dataset based on [FakeAVCeleb-V1.2](https://github.com/DASH-Lab/FakeAVCeleb)

``` bibtex
@misc{khalid2021fakeavceleb,
      title={FakeAVCeleb: A Novel Audio-Video Multimodal Deepfake Dataset}, 
      author={Hasam Khalid and Shahroz Tariq and Simon S. Woo},
      year={2021},
      eprint={2108.05080},
      archivePrefix={arXiv},
      primaryClass={cs.CV}
}
```

## environments

- python=3.10
- tqdm=4.65.0
- ffmpeg=1.4
- ffmpeg-python=0.2.0
- numpy=1.23.5
- soundfile=0.12.1
- librosa==0.10

## usage

In `datasetGenerate.py`, set the `PATH_DATA_ORI` as the original FakeAVCeleb path, and the `PATH_OUTPUT` as the required output path.

The fake ratio(between 0 and 1) and the required fake video number can be adjust by editing `NUM_FAKE` and `RATIO_FAKE`.

Run `datasetGenerate.py`.

The final ratio fake will be higher than the `RATIO_FAKE`, which can be check by the text file named `counted_ratio_<real fake ratio>.txt`.

## License

code is released under the MIT license.
