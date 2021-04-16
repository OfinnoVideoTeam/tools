#!/usr/bin/env python

import pandas as pd


SEQUENCES = ['Cactus', 'BasketballDrive', 'BQTerrace', 'BasketballDrill', 'BQMall', 'PartyScene', 'RaceHorsesC', 'BasketballPass', 'BQSquare', 'BlowingBubbles', 'RaceHorses', 'FourPeople', 'Johnny', 'KristenAndSara', 'BasketballDrillText', 'ArenaOfValor', 'SlideEditing', 'SlideShow']

QPS = [ '22', '27', '32', '37']
MODES = ['ai', 'ra', 'lb', 'lp']


JobQueue = {"executable":"EncoderAppStatic",\
"arguments":"",\
"transfer_input_files":"",\
"should_transfer_files":"YES",\
"when_to_transfer_output":"ON_EXIT",\
"transfer_output_files":"1.cfg",\
"output":"out.$(Process)",\
"error":"err.$(Process)",\
"log":"log.$(Process)",\
"request_memory":"1500M",\
"request_cpus":"1"}


VanillaJob={ "universe":"vanilla",\
    'JobQueue' : JobQueue}


DockerJobQueue = {"docker_image":"taemeon/ubuntu_dev"}
DockerJobQueue.update(JobQueue)

DockerJob={"universe":"docker",\
    'JobQueue' : DockerJobQueue}


paths = {'mode':'/home/taemeon/vod/ctc/cfg',\
         'seq':'/home/taemeon/vod/ctc/cfg/per-sequence',\
         'yuv':'/home/taemeon/vod/ctc/vvc-sdr',\
         'bin':'.'}         


def genJobQueue(job_queue: dict, ctc: str, paths: dict, yuv_dic: dict) -> str:
    """
    Generate text for one job queue. job_queue is template for job queue.
    ctc: 'RaceHorsesC.Q37.jvet10.ai' 
    paths: dictionary stores path of cfgs, yuv, output binanry
    yuv_dic: dictionary maps ctc to yuv file name
    """

    # cfg file name for encoding mode
    enc_modes = {'AI':'encoder_intra_vtm', \
             'LD':'encoder_lowdelay_vtm', \
             'LP':'encoder_lowdelay_P_vtm',\
             'RA': 'encoder_randomaccess_vtm'}

    seq_name, qp, bitdepth, enc_mode = ctc.split('.')
    qp = qp[1:]
    bitdepth=int(bitdepth[4:])
    enc_mode =  enc_mode.strip().upper()
	
    mode_cfg = f'{enc_modes[enc_mode]}.cfg' # cfg file related with encoding mode
    seq_cfg  = f'{seq_name}.cfg'            # cfg file related with input yuv
    bin_fn   = f'{ctc}.bin'                 # vvc bitstream file name
    yuv_fn_name   = '.'.join(f'{yuv_dic[seq_name]}'.split('.')[:-1]) # input yuv file name without extension
    yuv_fn   = yuv_fn_name + '.yuv' # input yuv file with .yuv extension

    rec_yuv  = f'{yuv_fn_name}_rec.yuv'     # reconstructed yuv file

    if 'docker_image' in job_queue:        
        args = f'\" -c {mode_cfg} -c {seq_cfg} -q {qp} -b {bin_fn} -i {yuv_fn} -o {rec_yuv} \"'
        change = {'transfer_input_files': f'{mode_cfg}, {seq_cfg}, {yuv_fn}'}
    else:       
        change = {}
        args = f'\" -c {paths["mode"]}/{mode_cfg} -c {paths["seq"]}/{seq_cfg} -q {qp} -b {bin_fn} -i {paths["yuv"]}/{yuv_fn} -o {rec_yuv} \"'

    output = ctc + '.log'
    log    = ctc + '.trc'
    error  = ctc + '.err' 
    
    change.update({'arguments': args, 'output': output,\
              'log': log, 'error':error,\
             'transfer_output_files':f'{bin_fn}, {rec_yuv}'})
    
    text = [f'{k} = {change[k]}' if k in change else f'{k} = {v}' for k, v in job_queue.items()]
    text.append('\nqueue\n\n')

    return '\n'.join(text)


def genJob(job: dict) -> str:
    """
    Generate text for encoding submit which can be submitted to condor_submit
    job: dict of condor job template
    """

    with open('ctc_order.csv', 'r') as f:
        ctcs_ = [ctc.strip() for ctc in f.readlines()]

    ctcs = [] 
    for ctc in ctcs_:
        seq_name, qp, _, mode = ctc.split('.')
        qp = qp[1:]
        if seq_name in SEQUENCES and qp in QPS and mode in MODES:
            ctcs.append(ctc)

    #ctcs = ['RaceHorses.Q37.jvet10.ai'] # used for test

        
    yuv_dic = pd.read_csv('ctc_yuv.csv', header=None, index_col=0)[1].to_dict()

    texts = [f"universe = {job['universe']}\n"]
    jobs = [genJobQueue(job['JobQueue'], ctc, paths, yuv_dic) for ctc in ctcs ]
    texts.extend(jobs)
    
    return '\n'.join(texts)


if __name__ == '__main__':
    print(genJob(VanillaJob)) # for stand alone machine 
    #print(genJob(DockerJob))  # for aws with docker (ubuntu)
