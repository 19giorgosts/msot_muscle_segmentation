# -*- coding: utf-8 -*-
"""baseline.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1E43oLfh-qXHuBilxz7mGdYM-gkZcFCDM
"""

from google.colab import drive
drive.mount('/content/gdrive')
root_path = 'gdrive/My Drive/msot_muscle_segmentation' #change dir to your project folder
# %cd /content/gdrive/My\ Drive/msot_muscle_segmentation/

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 15 11:33:01 2019

@author: nikos
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
#import h5py
import time
import keras
from keras.preprocessing import image# for RGB images
import os
from tqdm import tqdm
from numpy import ndarray as nd
from sklearn.model_selection import train_test_split
import cv2# cv2.imread() for grayscale images

import matplotlib.pyplot as plt
from mpl_toolkits import axes_grid1
def add_colorbar(im, aspect=20, pad_fraction=0.5, **kwargs):
    """
    Add a vertical color bar to an image plot.
    https://stackoverflow.com/questions/18195758/set-matplotlib-colorbar-size-to-match-graph
    """
    divider = axes_grid1.make_axes_locatable(im.axes)
    width = axes_grid1.axes_size.AxesY(im.axes, aspect=1./aspect)
    pad = axes_grid1.axes_size.Fraction(pad_fraction, width)
    current_ax = plt.gca()
    cax = divider.append_axes("right", size=width, pad=pad)
    plt.sca(current_ax)
    return im.axes.figure.colorbar(im, cax=cax, **kwargs)

#%% load the images
img_folder = './data/BBBC010_v2_images'
msk_folder = './data/BBBC010_v1_foreground'
target_height = 400
target_width = 400
Nimages = 100#100 images, each image has 2 channels

# load the filenames of all images
# Note: delete the __MACOSX folder in the img_folder first
img_filenames = np.array(sorted(os.listdir(img_folder)))#sort to alphabetical order
assert len(img_filenames)==Nimages*2#2 channels

wells = [f.split('_')[6] for f in img_filenames]
wells = np.sort(np.unique(wells))#e.g. A01, A02, ..., E04
channels = [1,2]

#%%load the images
#images, 2 channels
X = np.zeros(shape=(Nimages,target_height,target_width,2),dtype='float32')
Y = np.zeros(shape=(Nimages,target_height,target_width,1),dtype='float32')

i=0
for w in  wells:
    print('loading image ',i+1)
    for c in channels:
        key = w+'_w'+str(c)
        img_file = None
        for f in img_filenames:
            if key in f:
                img_file=f
                break;
        print(img_file)
        #cv2 is better for grayscale images, use 
        #load the image
        img = cv2.imread(img_folder+'/'+img_file,-1)
        #resize
        img=cv2.resize(img,(target_width,target_height))
        #normalize to 0-1
        img=img/img.max()
        X[i,:,:,c-1]=img
    print('loading mask')
    img = cv2.imread(msk_folder+'/'+w+'_binary.png',cv2.IMREAD_GRAYSCALE)
    #resize
    img=cv2.resize(img,(target_width,target_height))
    #normalize to 0-1
    img=img/img.max()
    #create binary image from [0,1] to {0,1}, using 0.5 as threshold
    img[img<0.5]=0
    img[img>=0.5]=1
    Y[i,:,:,0]=img
    i=i+1
    print()#add a blank line for readability

#double-check that the masks are binary
assert np.array_equal(np.unique(Y), [0,1])
    

#%% split into train, validation and test sets

ix = np.arange(len(wells))

ix_tr, ix_val_ts = train_test_split(ix,train_size=60, random_state=0)
ix_val, ix_ts = train_test_split(ix_val_ts,train_size=20, random_state=0)

#sanity check, no overlap between train, validation and test sets
assert len(np.intersect1d(ix_tr,ix_val))==0
assert len(np.intersect1d(ix_tr,ix_ts))==0
assert len(np.intersect1d(ix_val,ix_ts))==0



#X_tr = X[ix_tr,:]
#Y_tr = Y[ix_tr,:]

X_val = X[ix_val,:]
Y_val = Y[ix_val,:]

X_ts = X[ix_ts,:]
Y_ts = Y[ix_ts,:]

d={}
X_tr={}
Y_tr={}
#X_val={}
#Y_val={}
#X_ts={}
#Y_ts={}

for it in range(1,6):
    d['ix_annot'+str(it)], d['ix_unannot'+str(it)] = train_test_split(ix_tr,train_size=0.1*it, random_state=0)
    #d['ix_val'+str(it)], d['ix_unannot'+str(it)] = train_test_split(ix_val,train_size=0.1*it, random_state=0)
    #d['ix_ts'+str(it)], d['ix_unannot'+str(it)] = train_test_split(ix_ts,train_size=0.1*it, random_state=0)
    
    X_tr[str(it)]=X[d['ix_annot'+str(it)],:]
    Y_tr[str(it)]=Y[d['ix_annot'+str(it)],:]
    #X_val[str(it)]=X[d['ix_val'+str(it)],:]
    #Y_val[str(it)]=Y[d['ix_val'+str(it)],:]
    #X_ts[str(it)]=X[d['ix_ts'+str(it)],:]
    #Y_ts[str(it)]=Y[d['ix_ts'+str(it)],:]
    
    print(d['ix_annot'+str(it)])
    #print(d['ix_val'+str(it)])
    #print(d['ix_ts'+str(it)])
    fnames_tr = wells[d['ix_annot'+str(it)]].tolist()
    fnames_val = wells[ix_val].tolist()
    fnames_ts = wells[ix_ts].tolist()

    fname_split = ['train']*len(fnames_tr)+['validation']*len(fnames_val)+['test']*len(fnames_ts)
    df=pd.DataFrame({'well':fnames_tr+fnames_val+fnames_ts,
                  'split':fname_split})

    #save to disk
    df.to_csv('./data/training_validation_test_splits.csv',index=False)
    np.save('./data/X_tr'+str(it)+'.npy',X_tr[str(it)])
    np.save('./data/X_val.npy',X_val)
    np.save('./data/X_ts.npy',X_ts)

    np.save('./data/Y_tr'+str(it)+'.npy',Y_tr[str(it)])
    np.save('./data/Y_val.npy',Y_val)
    np.save('./data/Y_ts.npy',Y_ts)

#%% set-up the UNET model
import numpy as np
from keras.models import Model
from keras.layers import Input
from keras.layers import Activation
from keras.layers import BatchNormalization
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import AveragePooling2D,GlobalAveragePooling2D
from keras.layers.convolutional import Conv2D, MaxPooling2D, UpSampling2D, AveragePooling2D, Conv2DTranspose
from keras.layers.merge import concatenate #Concatenate (capital C) not working 

def UNET(input):

	#model parameters
	bnorm_axis = -1
	#filter sizes of the original model
	nfilters = np.array([64, 128, 256, 512, 1024])

	#downsize the UNET for this example.
	#the smaller network is faster to train
	#and produces excellent results on the dataset at hand
	nfilters = (nfilters/8).astype('int')

	#input
	input_tensor = Input(shape=input.shape[1:], name='input_tensor')

	####################################
	# encoder (contracting path)
	####################################
	#encoder block 0
	e0 = Conv2D(filters=nfilters[0], kernel_size=(3,3), padding='same')(input_tensor)
	e0 = BatchNormalization(axis=bnorm_axis)(e0)
	e0 = Activation('relu')(e0)
	e0 = Conv2D(filters=nfilters[0], kernel_size=(3,3), padding='same')(e0)
	e0 = BatchNormalization(axis=bnorm_axis)(e0)
	e0 = Activation('relu')(e0)

	#encoder block 1
	e1 = MaxPooling2D((2, 2))(e0)
	e1 = Conv2D(filters=nfilters[1], kernel_size=(3,3), padding='same')(e1)
	e1 = BatchNormalization(axis=bnorm_axis)(e1)
	e1 = Activation('relu')(e1)
	e1 = Conv2D(filters=nfilters[1], kernel_size=(3,3), padding='same')(e1)
	e1 = BatchNormalization(axis=bnorm_axis)(e1)
	e1 = Activation('relu')(e1)

	#encoder block 2
	e2 = MaxPooling2D((2, 2))(e1)
	e2 = Conv2D(filters=nfilters[2], kernel_size=(3,3), padding='same')(e2)
	e2 = BatchNormalization(axis=bnorm_axis)(e2)
	e2 = Activation('relu')(e2)
	e2 = Conv2D(filters=nfilters[2], kernel_size=(3,3), padding='same')(e2)
	e2 = BatchNormalization(axis=bnorm_axis)(e2)
	e2 = Activation('relu')(e2)

	#encoder block 3
	e3 = MaxPooling2D((2, 2))(e2)
	e3 = Conv2D(filters=nfilters[3], kernel_size=(3,3), padding='same')(e3)
	e3 = BatchNormalization(axis=bnorm_axis)(e3)
	e3 = Activation('relu')(e3)
	e3 = Conv2D(filters=nfilters[3], kernel_size=(3,3), padding='same')(e3)
	e3 = BatchNormalization(axis=bnorm_axis)(e3)
	e3 = Activation('relu')(e3)

	#encoder block 4
	e4 = MaxPooling2D((2, 2))(e3)
	e4 = Conv2D(filters=nfilters[4], kernel_size=(3,3), padding='same')(e4)
	e4 = BatchNormalization(axis=bnorm_axis)(e4)
	e4 = Activation('relu')(e4)
	e4 = Conv2D(filters=nfilters[4], kernel_size=(3,3), padding='same')(e4)
	e4 = BatchNormalization(axis=bnorm_axis)(e4)
	e4 = Activation('relu')(e4)
	#e4 = MaxPooling2D((2, 2))(e4)
	####################################
	# decoder (expansive path)
	####################################

	#decoder block 3
	d3=UpSampling2D((2, 2),)(e4)
	d3=concatenate([e3,d3], axis=-1)#skip connection
	d3=Conv2DTranspose(nfilters[3], (3, 3), padding='same')(d3)
	d3=BatchNormalization(axis=bnorm_axis)(d3)
	d3=Activation('relu')(d3)
	d3=Conv2DTranspose(nfilters[3], (3, 3), padding='same')(d3)
	d3=BatchNormalization(axis=bnorm_axis)(d3)
	d3=Activation('relu')(d3)

	#decoder block 2
	d2=UpSampling2D((2, 2),)(d3)
	d2=concatenate([e2,d2], axis=-1)#skip connection
	d2=Conv2DTranspose(nfilters[2], (3, 3), padding='same')(d2)
	d2=BatchNormalization(axis=bnorm_axis)(d2)
	d2=Activation('relu')(d2)
	d2=Conv2DTranspose(nfilters[2], (3, 3), padding='same')(d2)
	d2=BatchNormalization(axis=bnorm_axis)(d2)
	d2=Activation('relu')(d2)

	#decoder block 1
	d1=UpSampling2D((2, 2),)(d2)
	d1=concatenate([e1,d1], axis=-1)#skip connection
	d1=Conv2DTranspose(nfilters[1], (3, 3), padding='same')(d1)
	d1=BatchNormalization(axis=bnorm_axis)(d1)
	d1=Activation('relu')(d1)
	d1=Conv2DTranspose(nfilters[1], (3, 3), padding='same')(d1)
	d1=BatchNormalization(axis=bnorm_axis)(d1)
	d1=Activation('relu')(d1)

	#decoder block 0
	d0=UpSampling2D((2, 2),)(d1)
	d0=concatenate([e0,d0], axis=-1)#skip connection
	d0=Conv2DTranspose(nfilters[0], (3, 3), padding='same')(d0)
	d0=BatchNormalization(axis=bnorm_axis)(d0)
	d0=Activation('relu')(d0)
	d0=Conv2DTranspose(nfilters[0], (3, 3), padding='same')(d0)
	d0=BatchNormalization(axis=bnorm_axis)(d0)
	d0=Activation('relu')(d0)

	#output
	out_class = Dense(1)(d0)
	out_class = Activation('sigmoid',name='output')(out_class)

	#create and compile the model
	model=Model(inputs=input_tensor,outputs=out_class)
	model.compile(loss={'output':'binary_crossentropy'},
				  metrics={'output':'accuracy'},
				  optimizer='adam')
	#model.summary()
	#plot_model(model, to_file='unet_model.png', show_shapes=True, show_layer_names=True)
	return model

#UNET with dropout layers (p=0.5)
def UNET_mc(input):

	#model parameters
	bnorm_axis = -1
	#filter sizes of the original model
	nfilters = np.array([64, 128, 256, 512, 1024])

	#downsize the UNET for this example.
	#the smaller network is faster to train
	#and produces excellent results on the dataset at hand
	nfilters = (nfilters/8).astype('int')

	#input
	input_tensor = Input(shape=input.shape[1:], name='input_tensor')

	####################################
	# encoder (contracting path)
	####################################
	#encoder block 0
	e0 = Conv2D(filters=nfilters[0], kernel_size=(3,3), padding='same')(input_tensor)
	e0 = BatchNormalization(axis=bnorm_axis)(e0)
	e0 = Activation('relu')(e0)
	e0 = Conv2D(filters=nfilters[0], kernel_size=(3,3), padding='same')(e0)
	e0 = BatchNormalization(axis=bnorm_axis)(e0)
	e0 = Activation('relu')(e0)

	#encoder block 1
	e1 = MaxPooling2D((2, 2))(e0)
	e1 = Conv2D(filters=nfilters[1], kernel_size=(3,3), padding='same')(e1)
	e1 = BatchNormalization(axis=bnorm_axis)(e1)
	e1 = Activation('relu')(e1)
	e1 = Conv2D(filters=nfilters[1], kernel_size=(3,3), padding='same')(e1)
	e1 = BatchNormalization(axis=bnorm_axis)(e1)
	e1 = Activation('relu')(e1)

	#encoder block 2
	e2 = MaxPooling2D((2, 2))(e1)
	e2 = Conv2D(filters=nfilters[2], kernel_size=(3,3), padding='same')(e2)
	e2 = BatchNormalization(axis=bnorm_axis)(e2)
	e2 = Activation('relu')(e2)
	e2 = Conv2D(filters=nfilters[2], kernel_size=(3,3), padding='same')(e2)
	e2 = BatchNormalization(axis=bnorm_axis)(e2)
	e2 = Activation('relu')(e2)
	e2 = Dropout(0.5)(e2,training=True)

	#encoder block 3
	e3 = MaxPooling2D((2, 2))(e2)
	e3 = Conv2D(filters=nfilters[3], kernel_size=(3,3), padding='same')(e3)
	e3 = BatchNormalization(axis=bnorm_axis)(e3)
	e3 = Activation('relu')(e3)
	e3 = Conv2D(filters=nfilters[3], kernel_size=(3,3), padding='same')(e3)
	e3 = BatchNormalization(axis=bnorm_axis)(e3)
	e3 = Activation('relu')(e3)
	e3 = Dropout(0.5)(e3,training=True)

	#encoder block 4
	e4 = MaxPooling2D((2, 2))(e3)
	e4 = Conv2D(filters=nfilters[4], kernel_size=(3,3), padding='same')(e4)
	e4 = BatchNormalization(axis=bnorm_axis)(e4)
	e4 = Activation('relu')(e4)
	e4 = Conv2D(filters=nfilters[4], kernel_size=(3,3), padding='same')(e4)
	e4 = BatchNormalization(axis=bnorm_axis)(e4)
	e4 = Activation('relu')(e4)
	#e4 = MaxPooling2D((2, 2))(e4)
	e4 = Dropout(0.5)(e4,training=True)
    ####################################
	# decoder (expansive path)
	####################################

	#decoder block 3
	d3=UpSampling2D((2, 2),)(e4)
	d3=concatenate([e3,d3], axis=-1)#skip connection
	d3=Conv2DTranspose(nfilters[3], (3, 3), padding='same')(d3)
	d3=BatchNormalization(axis=bnorm_axis)(d3)
	d3=Activation('relu')(d3)
	d3=Conv2DTranspose(nfilters[3], (3, 3), padding='same')(d3)
	d3=BatchNormalization(axis=bnorm_axis)(d3)
	d3=Activation('relu')(d3)
	d3 = Dropout(0.5)(d3,training=True)

	#decoder block 2
	d2=UpSampling2D((2, 2),)(d3)
	d2=concatenate([e2,d2], axis=-1)#skip connection
	d2=Conv2DTranspose(nfilters[2], (3, 3), padding='same')(d2)
	d2=BatchNormalization(axis=bnorm_axis)(d2)
	d2=Activation('relu')(d2)
	d2=Conv2DTranspose(nfilters[2], (3, 3), padding='same')(d2)
	d2=BatchNormalization(axis=bnorm_axis)(d2)
	d2=Activation('relu')(d2)
	d2 = Dropout(0.5)(d2,training=True)

	#decoder block 1
	d1=UpSampling2D((2, 2),)(d2)
	d1=concatenate([e1,d1], axis=-1)#skip connection
	d1=Conv2DTranspose(nfilters[1], (3, 3), padding='same')(d1)
	d1=BatchNormalization(axis=bnorm_axis)(d1)
	d1=Activation('relu')(d1)
	d1=Conv2DTranspose(nfilters[1], (3, 3), padding='same')(d1)
	d1=BatchNormalization(axis=bnorm_axis)(d1)
	d1=Activation('relu')(d1)
	d1 = Dropout(0.5)(d1,training=True)

	#decoder block 0
	d0=UpSampling2D((2, 2),)(d1)
	d0=concatenate([e0,d0], axis=-1)#skip connection
	d0=Conv2DTranspose(nfilters[0], (3, 3), padding='same')(d0)
	d0=BatchNormalization(axis=bnorm_axis)(d0)
	d0=Activation('relu')(d0)
	d0=Conv2DTranspose(nfilters[0], (3, 3), padding='same')(d0)
	d0=BatchNormalization(axis=bnorm_axis)(d0)
	d0=Activation('relu')(d0)

	#output
	out_class = Dense(1)(d0)
	out_class = Activation('sigmoid',name='output')(out_class)

	#create and compile the model
	model=Model(inputs=input_tensor,outputs=out_class)
	model.compile(loss={'output':'binary_crossentropy'},
	              metrics={'output':'accuracy'},
	              optimizer='adam')
	#plot_model(model, to_file='unet_model.png', show_shapes=True, show_layer_names=True)
	return model

#create vgg-style cnn for segmentation quality estimation


def DiceNet(input1):
	
	#model parameters
	bnorm_axis = -1
	#filter sizes of the original model
	nfilters = np.array([32, 64, 128, 256])

	#inputs
	input_tensor = Input(shape=input1.shape[1:], name='input')
	
		#Conv block #1
	x = Conv2D(filters=nfilters[0], kernel_size=(3,3), padding='same')(input_tensor)
	x = BatchNormalization(axis=bnorm_axis)(x)
	x = Activation('relu')(x)
	x = Conv2D(filters=nfilters[0], kernel_size=(3,3), padding='same')(x)
	x = BatchNormalization(axis=bnorm_axis)(x)
	x = Activation('relu')(x)

	#max-pooling #1 
	x = MaxPooling2D((2, 2))(x)

	#Conv block #2
	x = Conv2D(filters=nfilters[1], kernel_size=(3,3), padding='same')(x)
	x = BatchNormalization(axis=bnorm_axis)(x)
	x = Activation('relu')(x)
	x = Conv2D(filters=nfilters[1], kernel_size=(3,3), padding='same')(x)
	x = BatchNormalization(axis=bnorm_axis)(x)
	x = Activation('relu')(x)

	#max-pooling #2
	x = MaxPooling2D((2, 2))(x)

	#Conv block #3
	x = Conv2D(filters=nfilters[2], kernel_size=(3,3), padding='same')(x)
	x = BatchNormalization(axis=bnorm_axis)(x)
	x = Activation('relu')(x)
	x = Conv2D(filters=nfilters[2], kernel_size=(3,3), padding='same')(x)
	x = BatchNormalization(axis=bnorm_axis)(x)
	x = Activation('relu')(x)

	#max-pooling #3
	x = MaxPooling2D((2, 2))(x)

	#Conv block #4
	x = Conv2D(filters=nfilters[3], kernel_size=(3,3), padding='same')(x)
	x = BatchNormalization(axis=bnorm_axis)(x)
	x = Activation('relu')(x)
	x = Conv2D(filters=nfilters[3], kernel_size=(3,3), padding='same')(x)
	x = BatchNormalization(axis=bnorm_axis)(x)
	x = Activation('relu')(x)

	#global average pooling
	x = GlobalAveragePooling2D()(x)

	#output
	x = Dense(1)(x)
	output = Activation('sigmoid',name='output')(x)

	#create and compile the model
	model=Model(inputs=input_tensor,outputs=output)
	model.compile(loss={'output':'mse'}, optimizer='adam')

	return model

def uncertainty_calc(X,model,bz,sample_times):
    #MC Dropout implementation
    
    for batch_id in tqdm(range(X.shape[0] // bz)):
        # initialize our predictions
        Y_hat = np.zeros(shape=(sample_times,X.shape[0],target_height,target_width,1),dtype='float32')
        #print(Y_ts_hat.shape) 
        
        start = time.time() # MC dropout is starting !!
        
        for sample_id in range(sample_times):
            # predict stochastic dropout model T times
            Y_hat[sample_id] = model.predict(X, bz)
        # average over all passes
        prediction = Y_hat.mean(axis=0)       
        uncertainty_mc= -(prediction*np.log2(prediction) + (1-prediction)*np.log2(1-prediction)) ## entropy = -(p*np.log2(p) + (1-p)*np.log(1-p))
        end = time.time()        
        chkpnt=(end-start) # this is how long it lasts for all images of the test set, for MC Dropout-based Uncertainty Estimation
        
        #%% convert predicted mask to binary
        threshold=0.5
        prediction[prediction<threshold]=0
        prediction[prediction>=threshold]=1
        print("\n Time needed for MC Dropout-based Uncertainty Estimation  ",chkpnt)

    return prediction,uncertainty_mc

def dice2D(a,b):
    intersection = np.sum(a[b==1])
    dice = (2*intersection)/(np.sum(a)+np.sum(b))
    if (np.sum(a)+np.sum(b))==0: #black/empty masks
        dice=1.0
    return(dice)

# -*- coding: utf-8 -*-

#if used on a non-GUI server ######
import matplotlib
matplotlib.use('Agg')
###################################

import numpy as np
#import pandas as pd
import matplotlib.pyplot as plt
#import h5py
import sys
#from model import *
#from keras.utils.vis_utils import plot_model

from keras.callbacks import EarlyStopping
from keras.callbacks import ModelCheckpoint
from keras.callbacks import CSVLogger
import time
import skimage.transform

def rotateT(X,angle):
	#rotate image tensor, TF order, single channel
	X_rot = np.zeros_like(X)
	#repeat for every channel
	for ch in np.arange(X.shape[-1]):
		#print('channel',ch)
		#repeat for every image
		for i in np.arange(X.shape[0]):
			#print('image',i)
			X_rot[i,:,:,ch] = skimage.transform.rotate(X[i,:,:,ch],angle=angle,resize=False,preserve_range=True,mode='edge')
	return(X_rot)

def shiftT(X,dx,dy):
	#rotate image tensor, TF order, single channel
	X_shift = np.zeros_like(X)
	#repeat for every image
	tform = skimage.transform.SimilarityTransform(translation=(dx, dy))
	for i in np.arange(X.shape[0]):
		#print('image',i)
		X_shift[i,:,:,:] = skimage.transform.warp(X[i,:,:,:],tform,mode='edge')
	return(X_shift)

#%%
def aug_generator(X_raw=None,Y_raw=None,
				  batch_size=4,
				  flip_axes=['x','y'],
				  rotation_angles=[5,15]):
				  #noise_gaussian_mean=0,
				  #noise_gaussian_var=1e-2):
				  #noise_snp_amount=0.05):
	
	batch_size=batch_size#recommended batch size    
	Ndatapoints = len(X_raw)
	#Naugmentations=4 #original + flip, rotation, noise_gaussian, noise_snp
	
	while(True):
		#print('start!')
		ix_randomized = np.random.choice(Ndatapoints,size=Ndatapoints,replace=False)
		ix_batches = np.array_split(ix_randomized,int(Ndatapoints/batch_size))
		for b in range(len(ix_batches)):
			#print('step',b,'of',len(ix_batches))
			ix_batch = ix_batches[b]
			current_batch_size=len(ix_batch)
			#print('size of current batch',current_batch_size)
			#print(ix_batch)
			X_batch = X_raw[ix_batch,:,:,:].copy()#.copy() to leave original unchanged
			Y_batch = Y_raw[ix_batch,:,:,:].copy()#.copy() to leave original unchanged
			
			#now do augmentation on images and masks
			#iterate over each image in the batch
			for img in range(current_batch_size):
				#print('current_image',img,': ',ix_batch[img])
				do_aug=np.random.choice([True, False],size=1)[0]#50-50 chance
				if do_aug == True:
					#print('flipping',img)
					flip_axis_selected = np.random.choice(flip_axes,1,replace=False)[0]
					if flip_axis_selected == 'x':
						flip_axis_selected = 1
					else: # 'y'
						flip_axis_selected = 0
					#flip an axis
					X_batch[img,:,:,:] = np.flip(X_batch[img,:,:,:],axis=flip_axis_selected)
					Y_batch[img,:,:,:] = np.flip(Y_batch[img,:,:,:],axis=flip_axis_selected)
					#print('Flip on axis',flip_axis_selected)
				
				do_aug=np.random.choice([True, False],size=1)[0]#50-50 chance
				if do_aug == True:
					#print('rotating',img)
					rotation_angle_selected = np.random.uniform(low=rotation_angles[0],high=rotation_angles[1],size=1)[0]
					#rotate the image
					X_batch[img,:,:,:] = rotateT(np.expand_dims(X_batch[img,:,:,:],axis=0),angle=rotation_angle_selected)
					Y_batch[img,:,:,:] = rotateT(np.expand_dims(Y_batch[img,:,:,:],axis=0),angle=rotation_angle_selected)
					#print('Rotate angle',rotation_angle_selected)
			yield(X_batch,Y_batch)
			#print('step end after',b,'of',len(ix_batches))
			
			
def train(mode,mc=False):
	  
	from keras import backend as K
	K.clear_session()
	model={}
	#load the data from already split files
	X_tr = np.load('./data/X_tr'+mode+'.npy')
	Y_tr = np.load('./data/Y_tr'+mode+'.npy')
	print('Training with '+str(X_tr.shape[0])+' images')
	X_val = np.load('./data/X_val.npy')
	Y_val = np.load('./data/Y_val.npy')
	print('Validating with '+str(X_val.shape[0])+' images')
	#%% train the model
	filepath = 'unet_div8_495K'

	#save the model when val_loss improves during training
	checkpoint = ModelCheckpoint('./trained_models/'+filepath+'_'+mode+'.hdf5', monitor='val_loss', verbose=1, save_best_only=True, mode='auto')
	#save training progress in a .csv
	csvlog = CSVLogger('./trained_models/'+filepath+'_'+mode+'_train_log.csv',append=True)
	#stop training if no improvement has been seen on val_loss for a while
	early_stopping = EarlyStopping(monitor='val_loss', min_delta=0, patience=8)
	batch_size=3
	
	#initialize the generator
	gen_train = aug_generator(X_tr,Y_tr,batch_size=batch_size,flip_axes=[1,2])
	#split the array and see how many splits there are to determine #steps
	steps_per_epoch_tr = len(np.array_split(np.zeros(len(X_tr)),int(len(X_tr)/batch_size)))
	
	## Step 1: Training UNET
	
	# Setup the model
	if (mc==False): 
		print("Training simple Unet")
		model=UNET(X_tr)
	else:
		print("Training Unet-mcdropout")
		model=UNET_mc(X_tr)
		
	#actually do the training
	model.fit_generator(gen_train,
						  steps_per_epoch=steps_per_epoch_tr,#the generator internally goes over the entire dataset in one iteration
						  validation_data=(X_val,Y_val),
						  epochs=80,
						  verbose=2,
						  initial_epoch=0,
						  callbacks=[checkpoint, csvlog, early_stopping])
	
	if mc==True:
		
		predictions,uncertainty_mc=uncertainty_calc(X_tr,model,1,sample_times=20)
		val_predictions,val_uncertainty_mc=uncertainty_calc(X_val,model,1,sample_times=20)
		## Step 2: Training DiceNet
		
		merged=np.concatenate((X_tr,predictions,uncertainty_mc),axis=-1)
		val_merged=np.concatenate((X_val,val_predictions,val_uncertainty_mc),axis=-1)

		model_dice=DiceNet(merged)
		#save the model when val_loss improves during training
		checkpoint = ModelCheckpoint('./trained_models/'+filepath+'_'+mode+'DiceNet.hdf5', monitor='val_loss', verbose=1, save_best_only=True, mode='auto')
		#save training progress in a .csv
		csvlog = CSVLogger('./trained_models/'+filepath+'_'+mode+'DiceNet_train_log.csv',append=True)
		#%% calculate dice
		dice = []
		dice_val=[]
		N=len(X_tr)
		for i in range(N):
			dice.append(dice2D(Y_tr[i,:,:,0],predictions[i,:,:,0]))
		#gen_train_diceNet = aug_generator(merged,np.median(dice),batch_size=batch_size,flip_axes=[1,2])
		d=np.array(dice)
		d = d.reshape(-1, 1)
		print(d.shape)
		N=len(X_val)
		for i in range(N):
			dice_val.append(dice2D(Y_val[i,:,:,0],val_predictions[i,:,:,0]))
		#gen_train_diceNet = aug_generator(merged,np.median(dice),batch_size=batch_size,flip_axes=[1,2])
		d_val=np.array(dice_val)
		d_val = d_val.reshape(-1, 1)
		model_dice.fit(merged,d,
						  #steps_per_epoch=steps_per_epoch_tr,#the generator internally goes over the entire dataset in one iteration
						  validation_data=(val_merged,dice_val),
						  epochs=60,
						  verbose=2,
						  initial_epoch=0,
						  callbacks=[checkpoint, csvlog, early_stopping])
		del model_dice
		#print(X_tr.shape,predictions.shape,uncertainty_mc.shape)
	del model

train('3',mc=True)

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from keras.models import load_model

  
def eval(mode):
    X_ts = np.load('./data/X_ts.npy')
    Y_ts = np.load('./data/Y_ts.npy')#.astype('float32')#to match keras predicted mask

    Ntest=len(X_ts)

    df = pd.read_csv('./data/training_validation_test_splits.csv')
    well_ts = df[df['split']=='test']['well'].tolist()
    #Y_ts is a binary mask
    #np.unique(Y_ts)
    #array([ 0.,  1.], dtype=float32)

    #%% get predicted masks for test set
    model = load_model('./trained_models/unet_div8_495K'+'_'+mode+'.hdf5')
    print("Loading model: "+'./trained_models/unet_div8_495K'+'_'+mode+'.hdf5')
    
    start = time.time()
    Y_ts_hat = model.predict(X_ts,batch_size=1)
    #print(Y_ts_hat.shape)
    #max_softmax=softmaxEquation(p_hat)
    end = time.time()
    chkpnt=(end-start) # this is how long it lasts for all images of the test set, for Maximum Softmax Probability-based Uncertainty Estimation
    print("\n Time needed for Maximum Softmax Probability-based Uncertainty Estimation  ",chkpnt)

    #%% convert predicted mask to binary
    threshold=0.5
    Y_ts_hat[Y_ts_hat<threshold]=0
    Y_ts_hat[Y_ts_hat>=threshold]=1
     
    #%% calculate dice
    dice = []
    for i in range(Ntest):
        dice.append(dice2D(Y_ts[i,:,:,0],Y_ts_hat[i,:,:,0]))
    #dice = np.array(dice)
    return Y_ts_hat,dice

def eval_mc(mode,sample_times=20):
    X_ts = np.load('./data/X_ts.npy')
    Y_ts = np.load('./data/Y_ts.npy')#.astype('float32')#to match keras predicted mask
    print(X_ts.shape,Y_ts.shape)
    batch_size=1
    Ntest=len(X_ts)
    df = pd.read_csv('./data/training_validation_test_splits.csv')
    well_ts = df[df['split']=='test']['well'].tolist()
  
    #%% get predicted masks for test set
    model = load_model('./trained_models/unet_div8_495K'+'_'+mode+'.hdf5')
    print("Loading model: "+'./trained_models/unet_div8_495K'+'_'+mode+'.hdf5')
 
    pred,uncertainty_mc=uncertainty_calc(X_ts,model,batch_size,sample_times=20)
    return pred,uncertainty_mc

def eval_DiceNet(mode):
    X_ts = np.load('./data/X_ts.npy')
    Y_ts = np.load('./data/Y_ts.npy')#.astype('float32')#to match keras predicted mask

    Ntest=len(X_ts)

    #%% get predicted masks for test set
    model = load_model('./trained_models/unet_div8_495K'+'_'+mode+'DiceNet.hdf5')
    print("Loading model: "+'./trained_models/unet_div8_495K'+'_'+mode+'DiceNet.hdf5')
    print(X_ts.shape)
    ts_predictions,ts_uncertainty_mc=uncertainty_calc(X_ts,model,1,sample_times=20)
    ts_merged=np.concatenate((X_ts,ts_predictions,ts_uncertainty_mc),axis=-1)
    print(ts_merged.shape)
    qest = model.predict(ts_merged,batch_size=1)
    return qest

dice_hat=eval_DiceNet('5')

p,uncertainty_mc = eval_mc('5')

num = 3
for i in range(num):
    #sample = np.random.randint(0,len(X_ts[i,:,:,0]))
    #image = X_predict[sample]
    #gt    = Y_predict[sample]
    
    #gt    = np.squeeze(gt)
        
    #n = np.random.randint(0,num)
    fig, ax = plt.subplots(2,2,figsize=(12,6))
    
    
    #fig.suptitle('Dice: {:.2f}'.format(np.median(dice)), y=1.0, fontsize=14)
    
    cax0 = ax[0,0].imshow(X_ts[i,:,:,0])
    plt.colorbar(cax0, ax=ax[0,0])
    ax[0,0].set_title('weight mask 1')
    
    #cax1 = ax[0,1].imshow(segm[i,:,:,0])
    #plt.colorbar(cax1, ax=ax[0,1])
    #ax[0,1].set_title('Max Probability')
    #ax[0,1].set_ylabel('Prediction')
    
    cax2 = ax[0,1].imshow(p[i,:,:,0])
    plt.colorbar(cax2, ax=ax[0,1])
    ax[0,1].set_title('MC-Dropout')
    ax[0,1].set_ylabel('Prediction')
    
    cax3 = ax[1,0].imshow(X_ts[i,:,:,1])
    plt.colorbar(cax3, ax=ax[1,0])
    ax[1,0].set_title('weight mask 2')
    
    #cax4 = ax[1,1].imshow(max_softmax[i,:,:,0])
    #plt.colorbar(cax4, ax=ax[1,1])
    #ax[1,1].set_xlabel('Max Probability')
    #ax[1,1].set_ylabel('Uncertainty')

    cax5 = ax[1,1].imshow(uncertainty_mc[i,:,:,0])
    plt.colorbar(cax5,ax=ax[1,1])
    #ax[1,1].set_title('MC-Dropout')
    ax[1,1].set_ylabel('Uncertainty')
    
    #for a in ax.flatten(): a.axis('off')
    #for a in ax.flatten(): a.xaxis.set_ticks_position('none')    
    
    fig.savefig('prediction_uncertainty_{:03d}.png'.format(i), dpi=300)
    
    plt.show()
    plt.close()
    plt.clf()

def generate_plot(X,Ndatapoints,Nmodels):
  import numpy as np
  import matplotlib.pyplot as plt
#   %matplotlib inline

  connected = True
  #connected = False

  #%%

  #Ndatapoints = 20 #number of datapoints in the test set
  #Nmodels = 5 #number of models trained

  #matrix containing the data
  #rows: test set datapoints
  #columns: models
  #each elements corresponds to the score (e.g. accuracy) of a model on a dataset
  #X = np.zeros((Ndatapoints,Nmodels),dtype='float')#initialize to zeros

  np.random.seed(1)#set random seed for repeatability

  #now generate artificial data, for the sake of plotting
  #for m in range(Ndatapoints):
  #    for d in range(Nmodels):
  #        X[m,d] = np.random.uniform(low=0,high=1)

  #%% generate a plot of boxplots whose medians are connected by a line

  figure_size = 4
  fig, ax = plt.subplots(figsize=(figure_size*Nmodels,figure_size))
  box_data = X
  md = np.median(box_data,axis=0)#median
  #ax.boxplot plots each column as a separate boxplot
  bplots = ax.boxplot(box_data)

  xticks = np.arange(Nmodels)+1

  if connected == True:
      #make the boxplots transparent
      for key in bplots.keys():
          #print(key)
          for b in bplots[key]:
              b.set_alpha(0.2)
      #add a line that connects the medians of all boxplots
      ax.plot(xticks,md,marker='o',c='black',lw=5,markersize=15,label='median')
      xlab = '%'
  else:
      xlab = 'Model '

  ax.set_ylabel('Score (test set)',{'fontsize':16})
  ax.set_xlabel('Model',{'fontsize':16})
  ax.set_title('Model Performance ',{'fontsize':16})
  ax.set_ylim(0,1)

  #generate the xtick labels
  xtick_labels = []
  for m in xticks:
      xtick_labels.append(xlab+str(m))
  ax.set_xticklabels(xtick_labels,rotation = 30, ha='center',fontsize=10)

  #save the figure to disk
  if connected == True:
      plt.savefig('model_boxplots_connected.png',dpi=200,bbox_inches='tight')
  else:
      plt.savefig('model_boxplots.png',dpi=200,bbox_inches='tight')

  #%% redo the same plot without the boxplots
  # only plot a line for the medians, along with error-bars for interquantile range

  figure_size = 4
  fig, ax = plt.subplots(figsize=(figure_size*Nmodels,figure_size))
  xticks = np.arange(Nmodels)+1
  md = np.median(box_data,axis=0)
  yerr = np.zeros((2,Nmodels))
  for m in range(Nmodels):
      #plt.errorbar needs the difference between the percentile and the median
      #lower errorbar: 25th percentile
      yerr[0,m]=md[m]-np.percentile(X[:,m],25)#lower errorbar
      #upper errorbar: 75th percentile
      yerr[1,m]=np.percentile(X[:,m],75)-md[m]

  #plot the errorbars
  ax.errorbar(xticks,md,yerr,capsize=10,fmt='none',c='black')
  #fmt='none' to only plot the errorbars

  #plot the (optional) connecting line
  if connected == True:
      ax.plot(xticks,md,marker='o',c='blue',lw=5,markersize=10,label='Random query')
      xlab = '% '
  else:
      ax.scatter(xticks,md,marker='o',c='black',s=200)
      xlab = 'Model '
  plt.axhline(y=0.92, label="Full data performance",color='r', linestyle='--')
  plt.legend()

  ax.set_ylabel('Score (test set)',{'fontsize':16})
  ax.set_xlabel('Model',{'fontsize':16})
  ax.set_title('Model Performance ',{'fontsize':16})
  ax.set_ylim(0,1)

  ax.set_xticks(xticks)
  #generate the xtick labels
  xtick_labels = []
  for m in xticks:
      xtick_labels.append(str(10*m)+xlab)
  ax.set_xticklabels(xtick_labels,rotation = 30, ha='center',fontsize=10)

  if connected == True:
      plt.savefig('model_errorbars_connected.png',dpi=200,bbox_inches='tight')
  else:
      plt.savefig('model_errorbars.png',dpi=200,bbox_inches='tight')

Nmodels = 1 #number of models trained
Ndata=2 #number of modes(percentages%)

dice={}
for mode in range(1,Ndata+1):
    print("Running mode "+str(mode))
    X_ts = np.load('./data/X_ts'+str(mode)+'.npy')
    Ndatapoints = len(X_ts) #number of datapoints in the test set e.g. 2(mode1),4(mode2).. etc.
    X = np.zeros((Ndatapoints*Nmodels,Ndata),dtype='float')#initialize to zeros
    l=[]
    for i in range (Nmodels):
        train(str(mode))
        ev,dc=eval(str(mode))
        for i in dc:
            l.append(i)
        dice[mode]=l
    for d in range(mode,len(dice)+1):
        for m in range(Ndatapoints*Nmodels):
            print(d,m)
            X[m,d] = dice[d][m]

X = np.zeros((2*Nmodels,1),dtype='float')#initialize to zeros
X[1][1]

generate_plot(X)

dic={}
for mode in range (2):
  x=[]
  for i in range (4):
    x.append(i)
    dic[mode]=x
dic[1]

#save
#np.save('dice_2.npy', dice) 
#load
#read_dictionary = np.load('dice.npy',allow_pickle=True).item()

#matrix containing the data
#rows: test set datapoints
#columns: models
#each elements corresponds to the score (e.g. accuracy) of a model on a dataset
#X = np.zeros((Ndatapoints,Nmodels),dtype='float')#initialize to zeros
#array = np.array(list(dice.items()))
arr=[]
for i in range(10):
    arr.append(dice[i]) 
#print(np.asarray(arr, dtype=np.float32).shape)
#X = np.zeros((Ndatapoints,Nmodels),dtype='float')#initialize to zeros
#print(X.shape)
for d in range(Nmodels):
  for m in range(Ndatapoints):
        X[m,d] = arr[d][m]

perc=[5,10,15,20,25,30,35,40,45,50]
# %matplotlib inline
import matplotlib.pyplot as plt
plt.axhline(y=0.92, label="Full data performance",color='r', linestyle='--')
plt.plot(perc,dice_ovr,label='Random query',marker='o')
plt.xlabel('Percentage (%) of training data used')
plt.ylabel('Dice coefficient')
plt.legend()
plt.show()


