"""
Snippet of code is taken from Dr Jingying Wang's code
- This file looks at obstaining the time, positioning, frequency band of th data for various situations.
- Noise diode pattern behaviour.
- The outputs here will be used in the following sections.
"""

import katdal
import numpy as np
import pickle
import scipy as sp
import scipy.stats as stats
import os.path

def area(fname, file_path):
    '''
    fname - Requires the file name and produces the file with that name
    file_path - path where the output file should go
    '''
    
    
    if os.path.isfile(file_path+fname+'_Time_Pos.npy'):
        print ("Time Position-File exists")
    else:
        print ("Time Position-File does not exist, conjuring")
    
        if fname in ['1551037708','1551055211', '1553966342','1554156377']:
            data = katdal.open('/idia/projects/hi_im/SCI-20180330-MS-01/'+fname+'/'+fname+'/'+fname+'_sdp_l0.full.rdb')
        if fname in ['1555775533','1555793534', '1555861810', '1556034219', '1556052116', '1556120503', '1556138397','1555879611','1561650779']:
            data = katdal.open('/idia/projects/hi_im/SCI-20190418-MS-01/'+fname+'/'+fname+'/'+fname+'_sdp_l0.full.rdb')
        if fname in['1558464584','1558472940']:
            data = katdal.open('/idia/projects/hi_im/COM-20190418-MS-01/'+fname+'/'+fname+'/'+fname+'_sdp_l0.full.rdb')

        if fname=='1562857793':
            #data = katdal.open('/idia/projects/hi_im/'+fname+'/'+fname+'/'+fname+'_sdp_l0.full.rdb')
            data = katdal.open('/idia/projects/hi_im//1562857793/1562857793/1562857793_sdp_l0.full.rdb')
            #data=katdal.open('https://archive-gw-1.kat.ac.za/1562857793/1562857793_sdp_l0.full.rdb', s3_endpoint_url='https://archive-gw-1.kat.ac.za', token='eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiJ9.eyJpc3MiOiJrYXQtYXJjaGl2ZS5rYXQuYWMuemEiLCJhdWQiOiJhcmNoaXZlLWd3LTEua2F0LmFjLnphIiwiaWF0IjoxNTY5MjQ2NjYxLCJwcmVmaXgiOlsiMTU2Mjg1Nzc5MyJdLCJleHAiOjE1Njk4NTE0NjEsInN1YiI6ImRldiIsInNjb3BlcyI6WyJyZWFkIl19.AYQXK8B8O8o65295-w9UcoIJwu6s1eKdMH-B3dN0wWO_45rRTEM03tz4_DSPSrgypzQYGw_aB2Yi9vMdcHHLzg')
        if fname=='1630519596':
            data = katdal.open('https://archive-gw-1.kat.ac.za/1630519596/1630519596_sdp_l0.full.rdb?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiJ9.eyJpc3MiOiJrYXQtYXJjaGl2ZS5rYXQuYWMuemEiLCJhdWQiOiJhcmNoaXZlLWd3LTEua2F0LmFjLnphIiwiaWF0IjoxNjMwNTk0Njc1LCJwcmVmaXgiOlsiMTYzMDUxOTU5NiJdLCJleHAiOjE2MzExOTk0NzUsInN1YiI6Im1ncnNhbnRvc0B1d2MuYWMuemEiLCJzY29wZXMiOlsicmVhZCJdfQ.dWfpPmRpQlL2ImO_a4TZ3sJ5LYNoAVFAoVKUYPn_RdgbApWJ9fKCadmAMyP1n4WcsEL99gfi2ZGvuiD9FoUCXQ')
            
    #
        ant_num_used=len(data.ants)
        nd_set=float(fname)
        nd_time=1.799235 #?
        nd_cycle=19.9915424299
        #print ant_num_used
    #
        corr_id=ant_num_used #select ant
        #print data.corr_products[corr_id]
    #
        assert(data.corr_products[corr_id][0] ==data.corr_products[corr_id][1]) #check auto-corr
        recv=data.corr_products[corr_id][0]
        #print recv
        ant=data.corr_products[corr_id][0][0:4]
        pol=data.corr_products[corr_id][0][4]
        #print ant, pol
    #
        ch_plot=800 #@1.023 # 211 @0.9 #2600 @1.399
        ch_plot_backup=ch_plot
    #
        #if target=='3C273':
        #    cc = SkyCoord(187.2779154*u.deg,  2.0523883*u.deg, frame='icrs') #3C273
        #if target=='3C237':
        #    cc = SkyCoord(152.000125*u.deg,  7.504541*u.deg, frame='icrs') #3C237
        #if target=='PictorA':
        #    cc = SkyCoord(79.9571708*u.deg,  -45.7788278*u.deg, frame='icrs') #Pictor A        
    #
        data.select(ants=ant,pol=pol,scans='track')
        scans_t=[]
        scans_tw=[]
        for s in data.scans():
            if data.shape[0]> 50:
                scans_t.append(data.scan_indices[0])
            else:
                scans_tw.append(data.scan_indices[0])
        data.select(ants=ant,pol=pol,scans=scans_t)
        dp_t=data.dumps
        #print np.shape(data)

    ##

        data.select(ants=ant,pol=pol,scans='scan')
        scans_s=[]
        scans_sw=[]
        for s in data.scans():
            if data.shape[0]> 50:
                scans_s.append(data.scan_indices[0])
            else:
                scans_sw.append(data.scan_indices[0])
        data.select(ants=ant,pol=pol,scans=scans_s)
        dp_s=data.dumps
        #print np.shape(data)
        dp_sb=data.dumps[0]
        dp_se=data.dumps[-1]

    ##

        data.select(ants=ant,pol=pol,scans=('slew','stop'))
        dp_w1=data.dumps
        #print np.shape(data)
        data.select(ants=ant,pol=pol,scans=scans_tw+scans_sw)
        dp_w2=data.dumps
        #print np.shape(data)
        dp_w=list(dp_w1)+list(dp_w2)
        dp_w.sort()
        dp_w=np.array(dp_w)

    ##

        data.select() #recover after select!!!
        data.select(ants=ant,pol=pol) 
        freqs = data.freqs
        timestamps=data.timestamps    
    #
        ra=data.ra[:,0]
        dec=data.dec[:,0]    
        az=data.az[:,0]
        el=data.el[:,0]    
    #
        if fname in ['1551037708','1551055211', '1553966342','1554156377']:
            data1 = pickle.load(open('/idia/projects/hi_im/raw_vis/SCI-20180330-MS-01/'+str(fname)+'/'+str(fname)+'_'+str(recv)+'_vis_data','rb'))
        if fname in ['1555775533','1555793534', '1555861810', '1556034219', '1556052116', '1556120503', '1556138397','1555879611','1561650779']:
            data1 = pickle.load(open('/idia/projects/hi_im/raw_vis/SCI-20190418-MS-01/'+str(fname)+'/'+str(fname)+'_'+str(recv)+'_vis_data','rb'))
        if fname in['1558464584','1558472940']:
            data1 = pickle.load(open('/idia/projects/hi_im/raw_vis/COM-20190418-MS-01/'+str(fname)+'/'+str(fname)+'_'+str(recv)+'_vis_data','rb'))
        if fname in ['1562857793']:
            data1 = pickle.load(open('/idia/projects/hi_im/raw_vis/SCI-20190418-MS-01/'+str(fname)+'_new/'+str(fname)+'_'+str(recv)+'_vis_data','rb'))

    ##
        flags=data1['flags']
        flags_1ch=flags[:,ch_plot]
    #
        dp_tt=[]
        dp_ss=[]
        dp_f=[]
    #
        for i in dp_t:
            if flags_1ch[i]==False:
                dp_tt.append(i)
            else:
                dp_f.append(i)
    #
        for i in dp_s:
            if flags_1ch[i]==False:
                dp_ss.append(i)
            else:
                dp_f.append(i)
    #
        n_times = timestamps[dp_ss]
        n_az = az[dp_ss]
        n_el = el[dp_ss]
        n_freqs = data.freqs
    #   
        saved = np.zeros((3, n_times.shape[0]))
    #
        saved[0] = n_times
        saved[1] = n_az
        saved[2] = n_el
        #saved = []
        #saved.append(n_times), saved.append(n_az), saved.append(n_el), saved.append(n_freqs), saved.append(timestamps) 
        
        np.save(file_path+fname+'_Time_Pos', saved)
        print ('Time Position file created')
        
    if os.path.isfile(file_path+fname+'_nd_S0.npy'):
        print ("Noise Diode file exists")
    else:
        print ("Noise Diode file does not exist, conjuring")
        
    ####
        vis=data1['vis']


    ###
        f=10. #this value can change the detecet jump
        if fname in ['1555793534','1551055211','1551037708','1555775533']:
            f=10

        if fname=='1556120503':
            f=2
        if fname=='1556052116':
            f=15.
    
    ####
        ch_plot0=800 #only for edge detection

        lmax=abs(np.nanmax(vis[dp_ss,ch_plot0]))
        lmin=abs(np.nanmin(vis[dp_ss,ch_plot0]))
        lim=(lmax-lmin)/f        

    # Checking noise diodes being on or off
            
        mark=[]
        #nd_0=[]
        nd_1=[]
        nd_1a=[]
        nd_1b=[]
        for i in range(1,len(timestamps)):
            if (np.abs(vis[i,ch_plot0])-np.abs(vis[i-1,ch_plot0]) >lim #have a jump
                and vis[i,ch_plot0]>0 and vis[i-1,ch_plot0]> 0
                and timestamps[i-1]-timestamps[0] -data.dump_period/2. not in mark): #not jump the one before

                m=timestamps[i]-timestamps[0]-data.dump_period/2.
                #print i,m
                mark.append(m) #for plot
                nd_1.append(i) #on
                nd_1a.append(i) #on1
                if i+1<len(timestamps):
                    nd_1.append(i+1) #on
                    nd_1b.append(i+1) #on2
            '''
            else:
                if i not in nd_1:
                    nd_0.append(i) #off
            '''
        #print mark
        
    ####
        
        def gap_list(list):
            gap_list=[]
            for i in range(1,len(list)):
                gap_list.append(list[i]-list[i-1])

            gap_list=np.array(gap_list)
            return gap_list

        def gap_mode(list):
            gap_list=[]
            for i in range(1,len(list)):
                gap_list.append(list[i]-list[i-1])

            gap_list=np.array(gap_list)
            mode=stats.mode(gap_list)[0][0]
            return mode
        
     #####
        
        nd_gap_list=gap_list(nd_1a)
        nd_gap_mode=gap_mode(nd_1a)
        nd_wro_0=np.where(nd_gap_list != nd_gap_mode)[0]
#         print nd_wro_0

    ###########
    
            #nd time label timestamps[0]
        nd_tb=nd_set-timestamps[0]
        nd_te=data.dump_period*len(timestamps)

        t_line=[]
        for t in np.arange(nd_tb, nd_te+data.dump_period, nd_cycle ) :
            t_line.append(t)

#         print len(t_line), len(mark)

        if fname=='1551037708':
            t_line=t_line[5:]

        if fname=='1551055211':
            t_line=t_line[6:]

        if fname=='1553966342':
            t_line=t_line[2:]

        if fname=='1556034219':
            t_line=t_line[2:]

        if fname=='1554156377':
            t_line=t_line[1:]

        if fname=='1556138397':
            t_line=t_line[2:-1]

        if fname=='1556052116':
            t_line=t_line[2:]

        if fname=='1555775533':
            t_line=t_line[2:]

        if fname=='1556120503':
            t_line=t_line[2:]

        if fname=='1555793534':
            t_line=t_line[2:]

        if fname=='1561650779':
            t_line=t_line[3:-1]

        if fname=='1562857793':
            t_line=t_line[3:]
            
    #####
        
# Note about diode injection at this first time jump. there is 10 dumps till the next one

        nd_1a_gap=10
        if fname=='1551055211':
            nd_1a0=1
        if fname=='1555793534':
            nd_1a0 =8
        if fname=='1551037708':
            nd_1a0 =4
        if fname=='1553966342':
            nd_1a0 =4
        if fname=='1554156377':
            nd_1a0 =5
        if fname=='1555775533':
            nd_1a0 =0
        if fname=='1556034219':
            nd_1a0 =-1 #to keep nd_1b in the list
        if fname=='1556120503':
            nd_1a0 =0
        if fname=='1556138397':
            nd_1a0 =2
        if fname=='1556052116':
            nd_1a0 =1
        if fname=='1561650779':
            nd_1a0 =7
        if fname=='1562857793':
            nd_1a0 =7    

    ###
        nd_1aa=[]
        l=0
        for i in range(1000):
            a=nd_1a0+i*nd_1a_gap
            if a >= 0:
                if a >= len(timestamps):
                    break
                nd_1aa.append(a)
                l+=1
        print 'nd_1aa len = '+str(l)
        print nd_1aa==nd_1a

        nd_1bb=[]
        l=0
        for i in range(1000):
            a=nd_1a0+1+i*nd_1a_gap
            if a>=0:
                if a >= len(timestamps):
                    break
                max=i
                nd_1bb.append(a)
                l+=1
        print 'nd_1bb len = '+str(l)
        print nd_1bb==nd_1b
        
    ####
        
        nd_11=list(nd_1aa)+list(nd_1bb)
        nd_11.sort()
        
    ###

        nd_1a=nd_1aa
        nd_1b=nd_1bb
        nd_1=nd_11
        nd_0=[]
        for i in range(len(timestamps)):
            if i not in nd_1:
                nd_0.append(i)
        print len(nd_0),len(nd_1)
        assert(len(nd_0)+len(nd_1)==len(timestamps))
        
        nd_s0=[]
        for i in dp_ss:
            if i in nd_0:
                nd_s0.append(i)
        print np.shape(nd_s0)       

        nd_s1=[]
        nd_s1a=[]
        nd_s1b=[]
        for i in dp_ss:
            if i in nd_1:
                nd_s1.append(i)
            if i in nd_1a:
                nd_s1a.append(i)
            if i in nd_1b:
                nd_s1b.append(i)
        print np.shape(nd_s1),np.shape(nd_s1a),np.shape(nd_s1b)
        
        nd_t0=[]
        for i in dp_tt:
            if i in nd_0:
                nd_t0.append(i)
        print np.shape(nd_t0)       

        nd_t1=[]
        nd_t1a=[]
        nd_t1b=[]
        for i in dp_tt:
            if i in nd_1:
                nd_t1.append(i)
            if i in nd_1a:
                nd_t1a.append(i)
            if i in nd_1b:
                nd_t1b.append(i)
        print np.shape(nd_t1),np.shape(nd_t1a),np.shape(nd_t1b)

        ###
        # Saving the scan with noise diode off in file
        saved = np.zeros((2, len(nd_s0)))
        
        n_az = az[nd_s0]
        n_el = el[nd_s0]

        saved[0], saved[1] = nd_s0, timestamps[nd_s0]

        np.save(file_path+fname+'_nd_S0', saved)   
        print ('Noise Diode file conjured')                                
    
    print ('Done')
