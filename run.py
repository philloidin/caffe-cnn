#!/usr/bin/env python
import matplotlib
matplotlib.use('Agg')
import sys,os
from time import localtime, strftime
#from train import train
from test import test
from test_eval import test_eval
from os import system,makedirs
from os.path import join,abspath,exists

def main():
    if len(sys.argv)!=3:
        print 'Usage: python run.py order'
        sys.exit(2)

    order = sys.argv[1]
    paramfile = sys.argv[2]

    with open(paramfile,'r') as f:
        paramdata = f.readlines()

    params = {}
    params['order'] = order
    for i in range(len(paramdata)):
        line = paramdata[i].strip().split()
        params.update({line[0]:line[1]})

    print '####### Parameters Input #######'
    for key in params.keys():
        print key + ': ' + params[key]
    print '################################'

    ctime = strftime("%Y-%m-%d-%H-%M-%S", localtime())
    datadir = os.path.abspath(os.path.join(params['model_topdir'],'data'))

    flag = False;
    if params['order']=='getdata':
        if os.path.exists(datadir):
            print 'data folder exists, will remove'
            os.system('rm -r '+datadir)
        os.makedirs(datadir)

        cmd = ' '.join(['scp -r ',params['data_src']+'/*',datadir])
        os.system(cmd)
        flag = True

    if params['order']=='train':
        if not 'modelname' in params.keys():
            params['model_batchname'] = ctime

        modeltopdir = abspath(join(params['model_topdir'],params['modelname'],params['model_batchname']))
        if os.path.exists(modeltopdir):
            print 'model folder exists, will remove'
            os.system('rm -r ' + modeltopdir)
        os.makedirs(modeltopdir)

        cwd = os.getcwd()
        for trial in range(int(params['trial_num'])):
            modeldir = join(modeltopdir,'trial'+str(trial))
            makedirs(modeldir)
            cmd = ' '.join(['cp ',params['solver_file'], modeldir])
            os.system(cmd)
            cmd = ' '.join(['cp ',params['trainval_file'], modeldir])
            os.system(cmd)

            os.chdir(modeldir)
            #train(os.path.basename(params['solver_file']),modeldir)
            outlog = os.path.join(modeldir,'train.out')
            errlog = os.path.join(modeldir,'train.err')
            os.system(' '.join(['python',os.path.join(params['codedir'],'train.py'),os.path.basename(params['solver_file']),modeldir,params['gpunum'],'1 >',outlog,'2>',errlog]))
            os.chdir(cwd)
        flag = True

    if params['order']=='test':
        modeltopdir = os.path.abspath(os.path.join(params['model_topdir'],params['modelname'],params['predictmodel_batch']))
        testdir = join(modeltopdir,'best_trial')
        if exists(testdir):
            print 'testdir '+testdir+' exists, will be removed'
            system('rm -r ' + testdir)
        makedirs(testdir)
        cmd = ' '.join(['cp',params['deploy_file'], testdir])
        os.system(cmd)
        os.chdir(testdir)
        test(os.path.basename(params['deploy_file']),modeltopdir,os.path.join(params['model_topdir'],params['predict_filelist']),int(params['gpunum']),int(params['trial_num']),testdir,params['optimwrt'])
        flag = True

    if params['order']=='test_eval':
        modeldir = os.path.abspath(os.path.join(params['model_topdir'],params['modelname'],params['predictmodel_batch'],'output'))
        pred_topdir = abspath(join(params['model_topdir'],params['modelname'],params['predictmodel_batch'],'best_trial'))
        pred_f = join(pred_topdir,'bestiter.pred')
        real_f = join(params['model_topdir'],params['predict_filelist'])
        outfile = join(pred_topdir,'bestiter.pred.eval')
        test_eval(pred_f,real_f,outfile)
        flag = True

    if not flag:
        print 'Cannot recognize order; Exit'
        exit(2)

if __name__ == '__main__':
    main()
