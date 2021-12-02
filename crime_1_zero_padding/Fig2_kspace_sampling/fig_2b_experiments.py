# This script runs the experiments for figure 2b in the Subtle Inverse Crimes paper. It computes the effective sampling
# rates and saves the results in a file named R_eff_results_R6.npz.
#
# (c) Efrat Shimron, UC Berkeley, 2021.

# TODO: change the path to mikQNAP. Add relative path to the "functions" folder


import numpy as np
import os
import sys

# add path to functions library - when running on mikQNAP
sys.path.append("/mikQNAP/efrat/1_inverse_crimes/1_mirror_PyCharm_CS_MoDL_merged/SubtleCrimesRepo/")

sys.path.append("/home/efrat/anaconda3/")
sys.path.append("/home/efrat/anaconda3/lib/python3.7/site-packages/")  # path to sigpy

from functions.sampling_funcs import genPDF, genSampling
from functions.demos_funcs import calc_pad_half
from functions.utils import calc_R_actual


#######################################################################################################

R = np.array([6])
pad_ratio_vec = np.array([1, 2,3])
poly_degree_vec = np.array([ 1000,10,4])

# ##################### brain data - load some datasets from fastMRI ##############################
ksp_all_data = np.empty([4, 320, 320, 10], dtype='complex64')  # there are currently 10 datasets.



########################### R_eff vs. zero padding #######################3
# graph of R_eff vs. zero pad
Num_realizations = 20
R_eff_vs_pad_and_poly = np.empty((poly_degree_vec.shape[0],pad_ratio_vec.shape[0],Num_realizations))



for n in range(np.asarray(Num_realizations)):
    print('realization ',n)
    for i, pad_ratio in enumerate(pad_ratio_vec):
        #print('========== padding ratio %d from %d' % (i + 1, len(pad_ratio_vec)), ' ============== ')
        for j, poly_degree in enumerate(poly_degree_vec):

            N_original_dim1 = ksp_all_data.shape[1]
            N_original_dim2 = ksp_all_data.shape[2]

            im1 = np.ones((N_original_dim1, N_original_dim2))

            pad_half_dim1, N_tot_dim1 = calc_pad_half(N_original_dim1, pad_ratio)
            pad_half_dim2, N_tot_dim2 = calc_pad_half(N_original_dim2, pad_ratio)

            # zero-pad k-space - for every coil separately
            padding_lengths_yz = ((pad_half_dim1, pad_half_dim1), (pad_half_dim2, pad_half_dim2))

            im_padded = np.pad(im1, padding_lengths_yz, mode='constant', constant_values=(0, 0))
            inds_inner_square = np.nonzero(im_padded)

            imSize = im_padded.shape

            pdf = genPDF(imSize, poly_degree, 1 / R)
            mask = genSampling(pdf, iter=10, tol=60)
            R_full_mask_actual = calc_R_actual(mask)

            mask_effective = np.multiply(im_padded, mask)

            a = im_padded
            b = mask
            inds_inner_square = np.nonzero(a)

            mask_effective_inner_square = b[inds_inner_square]
            mask_effective_vec = np.reshape(mask_effective_inner_square, (1, -1))
            R_eff = mask_effective_vec.shape[1] / np.count_nonzero(mask_effective_vec)
            R_eff_vs_pad_and_poly[j,i,n] = R_eff


R_eff_vs_pad_and_poly_av = np.mean(R_eff_vs_pad_and_poly,axis=2)


filename = 'R_eff_results_R{}'.format(R)
np.savez(filename,R_eff_vs_pad_and_poly=R_eff_vs_pad_and_poly,R_eff_vs_pad_and_poly_av=R_eff_vs_pad_and_poly_av,pad_ratio_vec=pad_ratio_vec,poly_degree_vec=poly_degree_vec)


print('data saved successfully')
