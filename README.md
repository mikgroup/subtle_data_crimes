# Subtle Data Crimes

Official github repository for the paper [Subtle data crimes: naively training machine learning algorithms could lead to overly-optimistic results](https://arxiv.org/abs/2109.08237).

Notice: this repo is still under construction. It will be finalized over the next couple of weeks (Dec 2021).

""


![subtle_fig_1](logo_arXiv_paper.png)




## Video

A 5-min oral presentation that explains this research is [here](https://ismrm-smrt21.us3.pathable.com/meetings/virtual/t6jwNsra7cnLEAdRZ) (this link requires registration to the ISMRM-2021 conference).


## Installation
To use this package:

1. Clone or download it.

2. Install the required python packages (tested with python 3.8 on Ubuntu 20.04 LTS) by running:
```bash
pip install -r requirements.txt
```

3. In order to fully reproduce our experiments, data should be downloaded from the FastMRI database (see details in the next section).


### Data

All the data used in this research was obtained from the [FastMRI database](https://fastmri.org/).

To download the data, you need to request access to FastMRI and follow their procedures.

---

### Pre-trained networks

The weights of our pre-trained networks are publicly available here:
https://berkeley.box.com/s/lamdqhruiwxuxtwwjiv8xly5mohshot9


### Acknowledgements

The Compressed Sensing code implemented was based on Sigpy.

The Dictionary Learning algorithm implementation is based on Jon Tamir's [ISMRM 2020 educational tutorial](https://github.com/utcsilab/dictionary_learning_ismrm_2020). 



### Terms of use

This repository may be used only for research/educational purpose, not clinical diagnosis.

When using some of our code in your future publications, please cite our paper. Thank you.



### Contact

Problems? Questions? contact efrat.s@berkeley.edu


Efrat Shimron, UC Berkeley (2021)
