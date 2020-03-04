import sys

def init_list_of_floats(size):
    list_of_objects = list()
    for i in range(0,size):
        list_of_objects.append( 0.0 ) 
    return list_of_objects

def get_max_val_index(z):
    max_val=-1e100
    m_v_ind=-1
    sz=len(z)
    for i in range(0,sz):
        v=z[i]
        if v>max_val:
            max_val = v
            m_v_ind=i
    return m_v_ind
    
class CountAvg:
    def __init__(self, tf, attr, attr_cnt):
        self.train_file=tf
        self.attr_to_find=attr
        self.attr_count=attr_cnt
        self.Count=0
    
    def CountMetrix(self):
        f = open(self.train_file, "r")
        attr_totals=init_list_of_floats(self.attr_count)
        for line in f:
            tmp=line.split("\t")
            v_id=tmp[0]
            attr=tmp[1].split(",")
            if attr[0]==self.attr_to_find:
                self.Count=self.Count+1
                for i in range(1,self.attr_count):
                    attr_totals[i]=attr_totals[i]+float(attr[i])
        f.close
        attr_avg=init_list_of_floats(self.attr_count)
        if self.Count>0:
            for i in range(1,self.attr_count):
                attr_avg[i] = attr_totals[i]/self.Count
        return attr_avg[1:len(attr_avg)] #excluding unused 0 item

    def GetRowsCount(self):
        return self.Count

  
class CountStdDev:
    def __init__(self, tf, attr, attr_cnt, av):
        self.train_file=tf
        self.attr_to_find=attr
        self.attr_count=attr_cnt
        self.averages=av
        self.Count=0
        
    def CountMetrix(self):   
        
        attr_avg = self.averages
        attr_disp=init_list_of_floats(self.attr_count)
        std_dev=init_list_of_floats(self.attr_count)
        f = open(self.train_file, "r")
        cnt=0
        for line in f:
            tmp=line.split("\t")
            v_id=tmp[0]
            attr=tmp[1].split(",")
            if attr[0]==self.attr_to_find:
                cnt=cnt+1
                for i in range(1,self.attr_count):
                    attr_disp[i]=attr_disp[i]+(float(attr[i])-attr_avg[i-1])**2
        f.close
        for i in range(1,self.attr_count):
            std_dev[i]=(1/cnt*attr_disp[i])**0.5
        
        return std_dev[1:len(std_dev)] #exclude unused 0 item

class ZNorm:
    def __init__(self, id, attrib, avg, stddev):
        self.id_job=id
        self.ATTR=attrib.split(",")
        self.ATTR=self.ATTR[1:len(self.ATTR)] #excluding unused item
        self.AVG=avg
        self.STDDEV=stddev
    
    def CountMetrix(self):
        cnt=len(self.ATTR)
        attr_z=init_list_of_floats(cnt)
        if cnt!=len(self.AVG):
            print("Warning! Column count not match! LENGTHS:",cnt, len(self.AVG), len(self.STDDEV))
            cnt=len(self.AVG)
        for i in range(0,cnt):
            attr_z[i]=(float(self.ATTR[i])-self.AVG[i])/self.STDDEV[i]
        return attr_z #exclude unused 0 item

#MAIN code   
#input params processing
if len(sys.argv)!=6:
    print("USAGE: test.py train_file data_file out_file attr_to_find attr_count")
    sys.exit()
    
train_file = sys.argv[1] #'train.tsv'
data_file = sys.argv[2] #'test.tsv'
out_file = sys.argv[3] #'test_proc.tsv'
attr_to_find=sys.argv[4] #"2"
attr_count=int(sys.argv[5]) #257

avgs_metrix=CountAvg(train_file, attr_to_find, attr_count)
attr_avg=avgs_metrix.CountMetrix() #get list of avg by columns
#print("AVGs:", attr_avg)
std_dev_metrix=CountStdDev(train_file,attr_to_find,attr_count,attr_avg)
std_dev=std_dev_metrix.CountMetrix()    #get std dev by columns
#print("Std_Devs:", std_dev)
f_src=open(data_file,"rt")   #data file
f_dest=open(out_file,"wt")   #output file
for line in f_src:
    tmp=line.split("\t")
    attr=tmp[1].split(",")
    if attr[0]==attr_to_find:
        #counting data to write to file
        z=ZNorm(tmp[0], tmp[1], attr_avg, std_dev).CountMetrix()
        mx_idx=get_max_val_index(z)
        #populating data row
        #to add metrix, you need to count it and append to row
        #get formatted output in str
        outline=tmp[0]+'\t'+str(z).replace("[","").replace("]","")+"\t"+str(mx_idx)+"\t"+str(float(attr[mx_idx+1])/std_dev[mx_idx+1]) 
        f_dest.write(outline+"\n")
f_dest.close
f_src.close
