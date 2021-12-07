# This code demonstrates subtle crime I with Compressed sensing
# Run the *fast* experiment to see the images & NRMSE valus on top of them.
# Run the *long* experiment (10 slices x 3 samlpling mask realizations each) to get statistics.
# Then run the script CS_DL_knee_prep_NRMSE_figure.py to produce the statistics graphs

#############################################################
# calibration run - this code (1_knee_calib_CS_lada.py)


##########################################################################################
import os
import numpy as np
import h5py
import sys
# add path to functions library - when running on mikQNAP
sys.path.append("/mikQNAP/efrat/1_inverse_crimes/1_mirror_PyCharm_CS_MoDL_merged/SubtleCrimesRepo/")

import matplotlib.pyplot as plt
from functions.utils import merge_multicoil_data
import sigpy as sp
from sigpy import mri as mr
#from matplotlib import interactive
#from functions.demos_funcs import demo1_zero_pad_MAG_run_exps
from functions.utils import pad_multicoil_ksp,save_as_png
from functions.error_funcs import error_metrics
#from functions.sampling_funcs import genPDF, genSampling
from functions.sampling_funcs import gen_2D_var_dens_mask



sys.path.append("/home/efrat/anaconda3/")
sys.path.append("/home/efrat/anaconda3/lib/python3.7/site-packages/")  # path to sigpy

#################################################################################
## Experiment set-up
#################################################################################

data_type = 'val' # validation data is used for calibrating the params
im_type_str = 'full_im'  # Options: 'full_im' / 'blocks' (blocks are used for training Deep Learning models, not for CS & DictL).


R_vec = np.array([4])
#pad_ratio_vec = np.array([1,2,3])
pad_ratio_vec = np.array([1,1.25,1.5,1.75,2])


sampling_type_vec = np.array([1,2])  # 0 = random, 1 = strong var-dens, 2 = weak var-dens
sampling_flag = '2D'

# # alpha_vec = np.array([0.5,1,50])
# alpha_vec = np.array([0, 0.3, 100])
# R_vec = np.array([4])
# num_realizations = 1;  # number of sampling masks that will be generated for each case
#
# # Define the desired padding ratios here:
# pad_ratio_vec = np.arange(1, 3.1,
#                           1)  # this defines a numpy array with the desired padding ratios:  ratio=N_padded/N_original

single_slice_example_flag = 0  # turn this flag on (=1) for debugging. Use 0 for recon of multiple slices


if single_slice_example_flag ==1 :
    num_slices = 1 #100  # desired number of slices (for statistics)
else:
    num_slices = 10 #

data_filename = 'knee_lamda_calib_R{}_num_slices{}_Nsamp{}_FatSat'.format(R_vec[0],num_slices,sampling_type_vec.shape[0])

# #################################################################################
# ##                              Initialize arrays & dicts
# #################################################################################



#lamda = 1e-5  # calibrated for the FastMRI knee data
lamda_vec = np.array([1e-9,1e-8,1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1])
lamda_vec = np.sort(lamda_vec)


gold_dict = {}
recs_dict = {}
masks_dict = {}

NRMSE_arr = np.empty([num_slices, pad_ratio_vec.shape[0], R_vec.shape[0], sampling_type_vec.shape[0],lamda_vec.shape[0]])
#SSIM_arr  = np.empty([num_slices, pad_ratio_vec.shape[0], R_vec.shape[0], sampling_type_vec.shape[0]])

small_dataset_flag = 0

figs_folder = 'figs'
if not os.path.exists(figs_folder):
    os.makedirs(figs_folder)


# #################################################################################
# ##                               Experiments
# #################################################################################

for pad_i, pad_ratio in enumerate(pad_ratio_vec):
    print(f'##################### pad ratio {pad_ratio} ################################')

    t = 0 # counts loaded scans. each scan contains multiple slices.
    ns = 0 # counts loaded slices


    basic_data_folder = "/mikQNAP/NYU_knee_data/efrat/subtle_inv_crimes_zpad_data_v19_FatSatPD"

    if small_dataset_flag == 1:
        basic_data_folder = basic_data_folder + '_small/'
    else:
        basic_data_folder = basic_data_folder + '/'

    data_path = basic_data_folder + data_type + "/pad_" + str(
        int(100 * pad_ratio)) + "/" + im_type_str + "/"

    files_list = os.listdir(data_path)


    while ns<num_slices:

        print(' === loading h5 file {} === '.format(t))
        # Load k-space data
        filename_h5 = data_path + files_list[t]

        #print('t=', t)
        #print('filename_h5=', filename_h5)
        f = h5py.File(filename_h5, 'r')

        t += 1  # update the number of LOADED scans. Each scan contains multiple slices

        kspace_preprocessed_multislice = f["kspace"]
        im_RSS_multislice = f["reconstruction"]  # these are the RSS images produced from the zero-padded k-space - see fig. 1 in the paper

        n_slices_in_scan = kspace_preprocessed_multislice.shape[0]

        # if data_type=='val':
        #     # for validation data we arbitrarily choose a single slice from the preprocessed dataset, i.e. one slice per subject
        #     #slices_to_use = np.random.randint(0,n_slices_in_scan-1,1)
        #     slices_to_use = np.array([12])  # we arbitrarily choose slice 12 from each subject; only because its in the middle of the scan
        #
        # else:
        #     slices_to_use = range(n_slices_in_scan)

        print(f'pad_ratio {pad_ratio}  t={t}')

        for s_i in range(n_slices_in_scan):
        #for s_i in slices_to_use:
            print(f'slice {s_i}')

            kspace_slice = kspace_preprocessed_multislice[s_i,:,:].squeeze()
            im_RSS = im_RSS_multislice[s_i,:,:].squeeze()

            ns += 1  # number of slices
            print(f'ns={ns}')

            imSize = im_RSS.shape

            # ksp_slice_padded = pad_multicoil_ksp(ksp_slice,pad_ratio)
            #
            # # compute a single *magnitude* image from the data
            # mag_im = merge_multicoil_data(ksp_slice_padded)
            #
            # # go back to k-space - generate an artificial kspace
            # kspace_slice = np.fft.fftshift(np.fft.fft2(np.fft.fftshift(mag_im)))

            # normalize k-space
            #kspace_slice = kspace_slice / np.max(np.abs(kspace_slice))

            kspace_slice = np.expand_dims(kspace_slice, axis=0) # restore coil dimension (for Sigpy data format)
            _ , NX_padded, NY_padded = kspace_slice.shape  # get size. Notice: the first one is the coils dimension

            virtual_sens_maps = np.ones_like(kspace_slice)  # sens maps are all ones because we have a "single-coil" magnitude image.

            # ------- run recon experiment -----------------
            # gold standard recon (fully-sampled data, with the current zero padding length)
            #print('Gold standard rec from fully sampled data...')

            rec_gold = sp.ifft(kspace_slice)
            rec_gold = rec_gold[0,:,:].squeeze() # remove artificial coil dim

            # fig = plt.figure()
            # plt.imshow(np.abs(rec_gold), cmap="gray")
            # plt.title('rec_gold')
            # plt.colorbar()
            # plt.show()

            # check NaN values
            assert np.isnan(rec_gold).any() == False, 'there are NaN values in rec_gold! scan {} slice {}'.format(n,s_i)

            gold_dict[pad_i, ns-1] = rec_gold  # store the results in a dictionary (note: we use a dictionary instead of a numpy array beause
            # different images have different sizes due to the k-space zero-padding)

            img_shape = np.array([NX_padded,NY_padded])

            for r in range(R_vec.shape[0]):

                R = R_vec[r]

                for j in range(sampling_type_vec.shape[0]):

                    if sampling_type_vec[j] == 0:  # random uniform
                        samp_type = 'random'
                    elif sampling_type_vec[j] == 1:  # weak variable-density
                        samp_type = 'weak'
                    elif sampling_type_vec[j] == 2: # strong variable-density
                        samp_type = 'strong'


                    # calib is assumed to be 12 for NX=640
                    calib_x = int(12 * im_RSS.shape[0] / 640)
                    calib_y = int(12 * im_RSS.shape[1] / 640)
                    calib = np.array([calib_x, calib_y])


                    mask, pdf, poly_degree = gen_2D_var_dens_mask(R, imSize, samp_type, calib=calib)

                     # ======================

                    mask_expanded = np.expand_dims(mask, axis=0)  # add the empty coils
                    kspace_sampled = np.multiply(kspace_slice, mask_expanded)

                    for lam_i in range(lamda_vec.shape[0]):
                        lamda = lamda_vec[lam_i]

                        #print(f'CS rec; lamda {lamda}')
                        # CS recon from sampled data
                        #print('CS rec...')
                        rec = mr.app.L1WaveletRecon(kspace_sampled, virtual_sens_maps, lamda=lamda, show_pbar=False).run()

                        A = error_metrics(rec_gold, rec)
                        A.calc_NRMSE()
                        #A.calc_SSIM()

                        print(f'CS rec; lamda {lamda}; NRMSE={A.NRMSE:.3f}')

                        cmax = np.max([np.abs(rec_gold),np.abs(rec)])
                        #if ns==2:
                        fig = plt.figure()
                        plt.subplot(1,3,1)
                        plt.imshow(np.abs(np.rot90(rec_gold,2)), cmap="gray")
                        plt.title('rec_gold')
                        plt.clim(0,cmax)
                        plt.colorbar(shrink=0.25)
                        #plt.show()

                        #fig = plt.figure()
                        plt.subplot(1,3,2)
                        plt.imshow(mask, cmap="gray")
                        plt.colorbar(shrink=0.25)
                        #plt.show()

                        #fig = plt.figure()
                        plt.subplot(1,3,3)
                        plt.imshow(np.abs(np.rot90(rec,2)),cmap="gray")
                        plt.title(f'CS lamda={lamda} \n NRMSE {A.NRMSE:.3f}')
                        plt.clim(0, cmax)
                        plt.colorbar(shrink=0.25)
                        plt.suptitle(f'{data_type} data; R={R}; pad_ratio={pad_ratio}; {samp_type} VD samp; scan {t}; slice {ns}')
                        plt.show()
                        figname = figs_folder + f'/slice{ns}_pad_{pad_ratio}_{samp_type}_lamda{lamda}.png'
                        fig.savefig(figname)


                        NRMSE_arr[ns-1,pad_i,r,j,lam_i] = A.NRMSE
                        #SSIM_arr[ns-1,pad_i,r,j] = A.SSIM

                        #gold_dict[ns-1] = rec_gold
                        #recs_dict[ns-1,pad_i,r,j] = rec  # store the results in a dictionary
                        #masks_dict[ns-1,pad_i,r,j] = mask



# --------------------- save ----------------------
# save results
np.savez(data_filename,NRMSE_arr=NRMSE_arr,masks_dict=masks_dict,R_vec=R_vec,pad_ratio_vec=pad_ratio_vec,sampling_type_vec=sampling_type_vec,sampling_flag=sampling_flag,lamda_vec=lamda_vec,num_slices=num_slices)