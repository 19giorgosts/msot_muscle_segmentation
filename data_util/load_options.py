# --------------------------------------------------
# load options for CNN training / testing
#
# Options are loaded from a configuration file
#
# --------------------------------------------------

import configparser, os


def load_options(user_config):
    """
    map options from user input into the default config 
    """
    
    sections = user_config.sections()

    # --------------------------------------------------
    # options
    # --------------------------------------------------
    options = {}

    # experiment name (where trained weights are)
    #options['experiment'] = user_config.get('model', 'name')
    options['root_folder'] = user_config.get('database', 'root_folder')
    options['data_folder'] = user_config.get('database', 'data_folder')
    options['img_folder'] = user_config.get('database', 'img_folder')
    options['msk_folder'] = user_config.get('database', 'msk_folder')
    options['target_height'] = user_config.get('database', 'target_height')
    options['target_width'] = user_config.get('database', 'target_width')
    options['Nimages'] = user_config.get('database', 'Nimages')
    options['Ndata'] = user_config.get('database', 'Ndata')
    options['Nmodels'] = user_config.get('database', 'Nmodels')
    options['mode'] = user_config.get('model', 'mode')

    #options['output_folder'] = ''
    #options['current_scan'] = ''
    #options['t1_name'] = user_config.get('database', 't1_name')
    #options['roi_name'] = user_config.get('database', 'roi_name')
    #options['out_name'] = user_config.get('database', 'output_name')
    #options['save_tmp'] = True
    #exp_folder = None 

    # net options
    #options['mode'] = user_config.get('model', 'mode')
    #options['patch_size'] = ([user_config.getint('model', 'patch_size'),
    #options['weight_paths'] = None
    #options['train_split'] = user_config.getfloat('model', 'train_split')
    #options['max_epochs'] = user_config.getint('model', 'max_epochs')
    #options['patience'] = user_config.getint('model', 'patience')
    #options['batch_size'] = user_config.getint('model', 'batch_size')
    #options['test_batch_size'] = user_config.getint('model', 'test_batch_size')
    #options['net_verbose'] = user_config.getint('model', 'net_verbose')
    #options['load_weights'] = user_config.get('model', 'load_weights')
    #options['randomize_train'] = True
    #options['debug'] = user_config.getboolean('model', 'debug')
    #options['out_probabilities'] = user_config.getboolean('model', 'out_probabilities')
    #options['post_process'] = user_config.getboolean('model', 'post_process')
    #options['crop'] = user_config.getboolean('model', 'speedup_segmentation')

    # CUDA GPU / CPU options
    #if options['mode'].find('cuda') == -1:
    #    os.environ['THEANO_FLAGS']='mode=FAST_RUN,device=cpu,floatX=float32,optimizer=fast_compile'
    #else:
    #    os.environ['THEANO_FLAGS']='mode=FAST_RUN,device='+options['mode'] +',floatX=float32,optimizer=fast_compile'
    # Theano MKL options
    #os.environ['MKL_THREADING_LAYER']='GNU'

    return options 


def print_options(options):
    """ 
    print options 
    """

    print ("--------------------------------------------------")
    print (" ")
    keys = options.keys()
    for k in keys:
        print (k, ':', options[k])
    print ("--------------------------------------------------")
    
    
    