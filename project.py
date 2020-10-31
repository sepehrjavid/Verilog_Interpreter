from math import degrees, atan, sin, radians
import sys
sys.setrecursionlimit(60)
try:
    filename = input('Please Enter File Name:')
except:
    filename = input('Please Enter File Directory:')
file1 = open(filename,'r')
syntax = ['|','~','&','wire','module','endmodule','output','input']
delays = {'&':8 , '|':5 , '~':3}
#-------------------------------------------------------------------------------------------------------------------------
class nodes:
    def __init__(self):
        self.input = {'#':1}
        self.output = {}
    def addinput(self,name):
        self.input[name] = 0    #0 means this node has not been assigned to any of the wires
    def addoutput(self,name):
        self.output[name] = 1
    def isin(self,name):
        if name in self.input:
            self.input[name] += 1
        if name in self.output:
            self.output[name] = 1
#-------------------------------------------------------------------------------------------------------------------------
class wires:
    def __init__(self):
        self.dict = {}
    def add(self,name):
        self.dict[name] = ''
    def change(self,name,explain):
        self.dict[name] = explain
    def __add__(self, other):
        result = wires()
        for i in self.dict:
            result.add(i)
            result.change(i,self.dict[i])
        for i in other.dict:
            result.add(i)
            result.change(i,other.dict[i])
        return result
#-------------------------------------------------------------------------------------------------------------------------

def iserror(x):
    syntax = ['|','~','&','wire','module','endmodule','output','input']
    return not(x in syntax)

#-------------------------------------------------------------------------------------------------------------------------

def isname(x):
    lst = [chr(a) for a in range(97,123)]+[chr(i) for i in range(48,58)]+['_']
    result = True
    for i in x:
        if i in lst:
            continue
        else:
            result = False
    return result

#-------------------------------------------------------------------------------------------------------------------------

def space_skip(var,stri):
    while stri[var] == ' ':
        if len(stri) == var+1:
            break
        var+=1
    return var

#-------------------------------------------------------------------------------------------------------------------------

mynodes=nodes()

#-------------------------------------------------------------------------------------------------------------------------
def line_check_1(line,classname, wireclassname):         #this function uses recursie way
    def in_or_out(xs):
        result=True
        if xs == [')']:
            return result
        if xs[0] == 'input':
            if isname(xs[1]):
                classname.addinput(xs[1])
                if xs[2] == ',':
                    return in_or_out(xs[3:])
                else:
                    if len(xs)>3:
                        return 'ERROR'
                    else:
                        return result
            else:
                result='ERROR'
                return result
        elif xs[0]=='output':
            if isname(xs[1]):
                classname.addoutput(xs[1])
                wireclassname.add(xs[1])
                if xs[2]==',':
                    return in_or_out(xs[3:])
                else:
                    if len(xs)>3:
                        return 'ERROR'
                    else:
                        return result
            else:
                result='ERROR'
                return result
        else:
            result='ERROR'
            return result
    k=True
    if '(' in line and ',' in line and ')' in line:
        line=line.replace('(',' ( ')
        line=line.replace(',',' , ')
        line=line.replace(')',' ) ')
    else:
        k='ERROR'
        return k
    lst=line.split()
    lst_final=[i.replace(' ','') for i in lst]
    if 'wire' in lst or '=' in lst:
        return 'ERROR, NO ";" FOUND'
    if lst_final[0]=='module':
        if isname(lst_final[1]):
            lst_final=lst_final[3:]
        else:
            k='ERROR'
            return k
    else:
        k='ERROR'
        return k
    k=in_or_out(lst_final)
    if len(classname.input)==0 or len(classname.output)==0:
        return 'ERROR'
    else:
        return k

#-------------------------------------------------------------------------------------------------------------------------

mywires=wires()

#-------------------------------------------------------------------------------------------------------------------------
#this function uses cursur way
#the input string should always have ' ' at the string and there should not be any ';'
def line_check(line, wireclassname):
    lst = line.split()
    no = 0
    for i in lst:
        if i == 'wire':
            no+=1
    if no > 1:
        return 'NO ";" FOUND'
    k = True
    line=line.replace('=',' = ')
    line=line.replace(',',' , ')
    i=0
    def next_word(var):
        begin=var
        while line[var]!=' ':
            if var+1==len(line):
                k='ERROR'
                break
            var+=1
        end=var
        word=line[begin:end]
        return word,var
    while len(line)>i+1:
        i=space_skip(i,line)
        word,i=next_word(i)
        if word in syntax and word != 'module':
            if word=='wire':
                i=space_skip(i,line)
                word,i=next_word(i)
                if isname(word) and word not in wireclassname.dict:
                    wireclassname.add(word)
                    wirename = word
                else:
                    return 'ERROR'
                i=space_skip(i,line)
                if line[i]==',':
                    k=line_check('wire '+line[i+1:], wireclassname)
                    break
            if word == 'endmodule':
                break
        elif word in wireclassname.dict and wireclassname.dict[word]=='':
            wirename = word
            i=space_skip(i,line)
            word=line[i:i+1]
            i+=1
            if word=='=':
                i=space_skip(i,line)
                p=i
                i=len(line)
                wireclassname.change(wirename,line[p:-1])
            else:
                return 'ERROR'
        elif word == '=':
            exp = line[i:]
            wireclassname.change(wirename,exp.replace(' ',''))
            break
        elif word == 'module':
            if '(' in line and ')' in line:
                line = line.replace('(',' ( ')
                line = line.replace(')',' ) ')
            else:
                return 'Perentesis Problem In Next Module Entry'
            try:
                new_filename = input('Please Enter The Next Module Filename: ')
            except:
                new_filename = input('Please Enter The Next Module File Directory: ')
            temp_result, module_name, newinput, newoutput , newwires = module_in_module(new_filename)
            if temp_result != 'ok':
                return 'ERROR In Internal Module: ' + temp_result
            if ',' in line:
                line = line.replace(',',' , ')
            else:
                temp_result = 'No "," Found In Next Module Entry'
            xs = line.split()
            pran = 0
            for m in xs:
                if m == '(' or m == ')':
                    pran += 1
            if pran % 2 != 0:
                return 'Perentesis Problem In Next Module Entry'
            cot = 0
            cotb = len(newinput) + len(newoutput)
            for m in xs:
                if m == ',':
                    cot += 1
            if cot != cotb - 2:         #dalile menhaye 2 vojude "#" tuye input dictionary has
                return 'Not Enough "," In Next Module Entry'
            new_module_name = xs[1]
            if xs[2] != '(' or (2*(cotb-1)) + 2 != pran:  #dalile menhaye 1 hman alamate "#" dar input ast
                return 'Perentesis Problem In Next Module Entry'
            if module_name != new_module_name:
                return 'Wrong Filename For The Next Module'
            xs = xs[3:]
            for p in newinput:
                wireclassname.add(p)
            for m in range(0,len(xs),5):
                if xs[m] == '(' or xs[m] == ')' or xs[m] == ',':
                    continue
                elif xs[m] in newinput:
                    if xs[m+2] in mywires.dict:
                        mywires.change(xs[m],xs[m+2])
                    elif xs[m+2] == '0':
                        mywires.change(xs[m],'0')
                    elif xs[m+2] == '1':
                        mywires.change(xs[m],'1')
                    else:
                        return 'NOT A VALID WIRE IN NEXT MODULE ENTRY'
                elif xs[m] in newoutput:
                    if isname(xs[m+2]):
                        mywires.add(xs[m+2])
                        mywires.change(xs[m+2],xs[m])
                else:
                    return 'INPUTS IN MODULE ENTRY DONT MATCH'
            return k
        else:
            return 'ERROR'
    return k
#------------------------------------------------------------------------------------------------
#this function uses recursive function in some way
def dict_check(nodeclassname, wireclassname):
    def check_content(explain,self):
        if 'wire' in explain or '=' in explain:
            return 'ERROR, NO ";" FOUND'
        if '&' in explain:
            explain = explain.replace('&', ' & ')
        if '~' in explain:
            explain = explain.replace('~',' ~ ')
        if '|' in explain:
            explain = explain.replace('|',' | ')
        if ('(' in explain and ')' not in explain) or ('(' not in explain and ')' in explain):
            return 'SYNTAX ERROR'
        if '(' in explain and ')' in explain:
            explain = explain.replace(')',' ) ')
            explain = explain.replace('(',' ( ')
            lst=explain.split()
            lst.remove(')')
            lst.remove('(')
            return check_content(''.join(lst),'@')
        lst = explain.split()
        if self in lst:
            return 'FEEDBACK ERROR'
        for i in nodeclassname.output:
            if i in lst:
                return 'CALLED WIRE IS AN OUTPUT'
        if len(lst)<=1:
            return ''
        if ('|' in explain or '&' in explain) and '~' not in explain:
            for i in range(0,len(lst),2):
                if lst[i] in nodeclassname.input :
                    nodeclassname.isin(lst[i])
                elif lst[i] in wireclassname.dict:
                    None
                else:
                    return 'NO WIRE FOUND WITH THIS NAME OR THE CALLED WIRE MAY BE AN OUTPUT'
        elif '~' in explain and '|' not in explain and '&' not in explain:
            if lst[1] in nodeclassname.input :
                nodeclassname.isin(lst[1])
            elif lst[1] in wireclassname.dict:
                None
            else:
                return 'NO WIRE FOUND WITH THIS NAME OR THE CALLED WIRE MAY BE AN OUTPUT'
        elif '~' in explain:
            i=lst.index('~')
            if lst[i+1] in nodeclassname.input:
                nodeclassname.isin(lst[i+1])
                lst.remove(lst[i])
                lst[i] = '#'
                return check_content(''.join(lst),'@')
            elif lst[i+1] in wireclassname.dict:
                lst.remove(lst[i])
                lst[i] = '#'
                return check_content(''.join(lst),'@')
            else:
                return 'NO WIRE FOUND WITH THIS NAME OR THE CALLED WIRE MAY BE AN OUTPUT' 
        else:
            return 'SYNTAX ERROR'
        return ''
    k=''
    for i in wireclassname.dict:
        k =  k +  check_content(wireclassname.dict[i],i)
        if k != '':
            break
    return k
#-------------------------------------------------------------------------------------------------------------------------
def warning(nodeclassname, wireclassname):
    k=''
    for i in wireclassname.dict:
        if i == '#':
            continue
        if wireclassname.dict[i]=='':
            k=k+i+' IS NOT USED ANYWHERE, '
    for i in nodeclassname.input:
        if nodeclassname.input[i]==0:
            k=k+i+' IS NOT USED ANYWHERE, '
    return k

#-------------------------------------------------------------------------------------------------------------------------
def comment(line):
    begin = line.index('/')
    end = begin
    for i in line[begin:]:
        if i == '\n':
            break
        else:
            end+=1
    delete = line[begin:end]
    line = line.replace(delete,'')
    return line
#-------------------------------------------------------------------------------------------------------------------------
def output(file,nodeclassname, wireclassname):
    whole=file.read()
    lst=whole.split(';')
    line=1
    end_line=1
    if '//' in lst[0]:
        lst[0] = comment(lst[0])
    sentence = ''
    for i in lst[0]:
        if i == '\n':
            end_line+=1
        else:
            sentence = sentence + i
    k = line_check_1(sentence,nodeclassname, wireclassname)
    if k != True:
        return k,line,end_line
    lst = lst[1:]
    line = end_line
    for each in lst:
        if '//' in each:
            each = comment(each)
        sentence = ''
        for p in each:
            if p == '\n':
                end_line+=1
            else:
                sentence = sentence + p
        sentence = sentence +' '
        k = line_check(sentence, wireclassname)
        if k != True:
            return k,line,end_line
        else:
            line = end_line
    k = dict_check(nodeclassname,wireclassname)
    if k != '':
        return k,line,end_line
    last_line = lst[-1].replace('\n','')
    if last_line != 'endmodule':
        return 'NO ENDMODULE','last line','last line'
    return 'ok',0,0
#-------------------------------------------------------------------------------------------------------------------------
result_file = open('result.data','w')
#-------------------------------------------------------------------------------------------------------------------------
def filecreator(codefile,out):
    out.write((49*'=') + '\n')
    out.write('*'+15*' ' + 'Syntax result' + 19*' ' + '*' + '\n')
    out.write((49*'=')+'\n')
    k = output(codefile, mynodes, mywires)
    if k[0] == 'ok':
        out.write('\n'+k[0]+'\n')
    else:
        out.write('\n'+'ERROR :'+filename+' : '+ 'from line '+str(k[1])+' to line '+str(k[2])+' - '+'SYNTAX ERROR: '+k[0]+'\n')
        out.close()
        return 'stop'
    warn = warning(mynodes,mywires)
    if warn != '':
        out.write('\n'+'WARNING: '+warn+'\n')
    graph(out)
    out.write('\n')
    return 'go'
#-------------------------------------------------------------------------------------------------------------------------
def graph(file):
    graphnodes=[]
    def make_lst(explain):
        if '&' in explain:
            explain = explain.replace('&', ' & ')
        if '~' in explain:
            explain = explain.replace('~',' ~ ')
        if '|' in explain:
            explain = explain.replace('|',' | ')
        if '(' in explain and ')' in explain:
            explain = explain.replace(')',' ) ')
            explain = explain.replace('(',' ( ')
            lst=explain.split()
            lst.remove(')')
            lst.remove('(')
            return lst
        lst = explain.split()
        return lst
    file.write('\n')
    file.write((49*'=')+'\n')
    file.write('*'+15*' '+'Circuit Graph'+19*' '+'*'+'\n')
    file.write((49*'=')+'\n')
    file.write('\n')
    numb = 1
    del mynodes.input['#']
    for i in mynodes.input:
        file.write('NODE_INPUT_'+str(numb)+': input_'+str(i)+'\n')
        numb += 1
    numb = 1
    for i in mynodes.output:
        file.write('NODE_OUTPUT_'+str(numb)+': output_'+str(i)+'\n')
        numb += 1
    numb = 1
    for i in mywires.dict:
        if '&' in mywires.dict[i]:
            t = mywires.dict[i].count('&')
            for p in range(t):
                file.write('NODE_AND_'+str(numb)+': and'+'\n')
                numb += 1
    numb = 1
    for i in mywires.dict:
        if '~' in mywires.dict[i]:
            t = mywires.dict[i].count('~')
            for p in range(t):
                file.write('NODE_NOT_'+str(numb)+': not'+'\n')
                numb += 1
    numb = 1
    for i in mywires.dict:
        if '|' in mywires.dict[i]:
            t = mywires.dict[i].count('|')
            for p in range(t):
                file.write('NODE_OR_'+str(numb)+': or'+'\n')
                numb += 1
    for i in mynodes.input:
        file.write('NODE_BRANCH_'+str(i)+': branch_'+str(i)+'\n')
    numb = 1
    for i in mynodes.input:
        file.write('VECTOR_'+str(numb)+': wire_'+i+' - NODE_INPUT_'+str(numb)+':NODE_BRANCH_'+i+'\n')
        numb += 1
    for i in mynodes.input:
        br_numb = 1
        not_numb = 0
        and_numb = 0
        or_numb = 0
        for p in mywires.dict:
            if '&' in mywires.dict[p]:
                and_numb += 1
            if '~' in mywires.dict[p]:
                not_numb += 1
            if '|' in mywires.dict[p]:
                or_numb += 1
            if i in mywires.dict[p]:
                xs = make_lst(mywires.dict[p])
                xs.append(' ')
                indx = xs.index(i)
                if xs[indx-1] == '~':
                    file.write('VECTOR_'+str(numb)+': branch_'+i+'_'+str(br_numb)+' - NODE_BRANCH_'+i+':NODE_NOT_'+str(not_numb)+'\n')
                    numb += 1
                    br_numb += 1
                elif xs[indx+1] == '&' or xs[indx-1] == '&':
                    file.write('VECTOR_'+str(numb)+': branch_'+i+'_'+str(br_numb)+' - NODE_BRANCH_'+i+':NODE_AND_'+str(and_numb)+'\n')
                    numb += 1
                    br_numb += 1
                elif xs[indx+1] == '|' or xs[indx-1]:
                    file.write('VECTOR_'+str(numb)+': branch_'+i+'_'+str(br_numb)+' - NODE_BRANCH_'+i+':NODE_OR_'+str(or_numb)+'\n')
                    numb += 1
                    br_numb += 1
    if not_numb != 0:
        x = not_numb
        not_out_numb = 1
        not_numb = 0
        and_numb = 0
        or_numb = 0
        for p in mywires.dict:
            if '&' in mywires.dict[p]:
                and_numb += 1
            if '~' in mywires.dict[p]:
                not_numb += 1
            if '|' in mywires.dict[p]:
                or_numb += 1
            if '~' in mywires.dict[p]:
                xs = make_lst(mywires.dict[p])
                xs.append(' ')
                xs.append(' ')
                indx = xs.index('~')
                if xs[indx-1] == '&' or xs[indx+2] == '&':
                    file.write('VECTOR_'+str(numb)+': not_'+str(not_out_numb)+'_out'+' - NODE_NOT_'+str(not_numb)+':NODE_AND_'+str(and_numb)+'\n')
                    numb += 1
                    not_out_numb += 1
                if xs[indx-1] == '|' or xs[indx+2] == '|':
                    file.write('VECTOR_'+str(numb)+': not_'+str(not_out_numb)+'_out'+' - NODE_NOT_'+str(not_numb)+':NODE_OR_'+str(or_numb)+'\n')
                    numb += 1
                    not_out_numb += 1
    not_numb = 0
    and_numb = 0
    or_numb = 0
    for p in mywires.dict:
        if '&' in mywires.dict[p]:
            and_numb += 1
        if '~' in mywires.dict[p]:
            not_numb += 1
        if '|' in mywires.dict[p]:
            or_numb += 1
        if p in mynodes.output:
            continue
        if '&' in mywires.dict[p]:
            file.write('VECTOR_'+str(numb)+': '+p+' - '+'NODE_AND_'+str(and_numb)+':NODE_')
            numb += 1
            for i in mywires.dict:
                if p in mywires.dict[i]:
                    if '|' in mywires.dict[i]:
                        file.write('OR_'+str(or_numb)+'\n')
                    if '&' in mywires.dict[i]:
                        file.write('AND_'+str(and_numb)+'\n')
        if '|' in mywires.dict[p]:
            file.write('VECTOR_'+str(numb)+': '+p+' - '+'NODE_OR_'+str(or_numb)+':NODE_')
            numb += 1
            for i in mywires.dict:
                if p in mywires.dict[i]:
                    if '|' in mywires.dict[i]:
                        file.write('OR_'+str(or_numb)+'\n')
                    if '&' in mywires.dict[i]:
                        file.write('AND_'+str(and_numb)+'\n')
                    if '~' in mywires.dict[i]:
                        file.write('NOT_'+str(not_numb)+'\n')                       
    output_numb = 1
    for i in mynodes.output:
        not_numb = 0
        and_numb = 0
        or_numb = 0
        if '|' in mywires.dict[i]:
            or_numb += 1
            file.write('VECTOR_'+str(numb)+': or_'+str(or_numb)+'_out'+' - NODE_OR_'+str(or_numb)+':NODE_OUTPUT_'+str(output_numb)+'\n')
            numb += 1
        if '&' in mywires.dict[i]:
            and_numb += 1
            file.write('VECTOR_'+str(numb)+': and_'+str(and_numb)+'_out'+' - NODE_AND_'+str(and_numb)+':NODE_OUTPUT_'+str(output_numb)+'\n')
            numb += 1
        if '~' in mywires.dict[i]:
            not_numb += 1
            file.write('VECTOR_'+str(numb)+': not_'+str(not_numb)+'_out'+' - NODE_NOT_'+str(not_numb)+':NODE_OUTPUT_'+str(output_numb)+'\n')
            numb += 1
        output_numb += 1
#-------------------------------------------------------------------------------------------------------------------------
def truthtable(outfile,all):
    def giveval(xs):
        inputval = {}
        inputval[xs[0]] = (2**(len(xs)-1))*[0]+(2**(len(xs)-1))*[1]
        power = len(xs)-2
        power_2 = 1
        power_for_len = len(xs)-1
        for i in range(1,len(xs)):
            val = (2**power)*[0]
            for p in range((2**power_2)-1):
                val += reversed(inputval[xs[i-1]][2**power:(2**power_for_len)+(2**power)])
            val += (2**power)*[1]
            inputval[xs[i]] = val
            power = power - 1
            power_2 = power_2 + 1
            power_for_len = power_for_len -1
        return inputval
    
    inputlst = []
    outputlst = []
    for i in mynodes.input:
        inputlst.append(i)
    for i in mynodes.output:
        outputlst.append(i)
    outfile.write((49*'=')+'\n')
    outfile.write('*'+16*' '+'Truth Table'+20*' '+'*'+'\n')
    outfile.write((49*'=')+'\n')
    outfile.write('\n')
    for i in range(len(mynodes.input)):
        outfile.write('   input_'+ str(inputlst[i])+3*' '+'|')
    for i in range(len(mynodes.output)):
        outfile.write('   output_'+ str(outputlst[i])+3*' '+'|')
    outfile.write('\n')
    inputvals = giveval(inputlst)
    for i in range(2**(len(inputlst))):
        for x in inputvals:
            value = inputvals[x][i]
            if value == 0:
                outfile.write('    zero     |')
            if value == 1:
                outfile.write('    one      |')
        for h in range(len(mynodes.output)):
            sentence = all[h]
            explain = sentence.split()
            for k in range(len(explain)):
                if explain[k] == '&':
                    explain[k] = 'and'
            for k in range(len(explain)):
                if explain[k] == '|':
                    explain[k] = 'or'
            for k in range(len(explain)):
                if explain[k] == '~':
                    explain[k] = 'not'
            for x in inputvals:
                value = inputvals[x][i]
                if value == 0:
                    for k in range(len(explain)):
                        if explain[k] == x:
                            explain[k] = 'False'
                if value == 1:
                    for k in range(len(explain)):
                        if explain[k] == x:
                            explain[k] = 'True'
            result = eval(' '.join(explain))
            if result == True:
                outfile.write('     one      |')
            elif result == False:
                outfile.write('     zero     |')
        outfile.write('\n')
#-------------------------------------------------------------------------------------------------------------------------
def all_in_one(nodeclassname ,wireclassname, outfile = None):
    def make_lst(explain):
        if '&' in explain:
            explain = explain.replace('&', ' & ')
        if '~' in explain:
            explain = explain.replace('~',' ~ ')
        if '|' in explain:
            explain = explain.replace('|',' | ')
        if '(' in explain and ')' in explain:
            explain = explain.replace(')',' ) ')
            explain = explain.replace('(',' ( ')
        lst=explain.split()
        return lst
    
    def change(lst):
        def inside(xs):
            for i in range(len(xs)):
                if xs[i] in wireclassname.dict:
                    xs[i] = ' '.join(inside(make_lst(wireclassname.dict[xs[i]])))
                    xs.insert(i,'(')
                    xs.insert(i+2,')')
                    return inside(xs)
            return xs
        try:
            return inside(lst)
        except:
            if nodeclassname == mynodes:
                result_file.close()
                change_file = open('result.data','w')
                change_file.write((49*'=')+'\n')
                change_file.write('*'+15*' '+'Syntax result'+19*' '+'*'+'\n')
                change_file.write((49*'=')+'\n')
                change_file.write('\n'+'ERROR :'+filename+' : '+' - '+'SYNTAX ERROR: FEEDBACK'+'\n')
                return None
            else:
                return 'FEEDBACK ERROR'
    if nodeclassname == mynodes:
        outfile.write((49*'=')+'\n')
        outfile.write('*'+15*' '+'Module Result'+19*' '+'*'+'\n')
        outfile.write((49*'=')+'\n')
        outfile.write('\n')
    myexplain_lst = []
    for i in nodeclassname.output:
        xs = make_lst(wireclassname.dict[i])
        mylst = change(xs)
        if mylst == None :
            return 'stop'
        if mylst == 'FEEDBACK ERROR':
            return 'FEEDBACK ERROR'
        myexplain = ' '.join(mylst)
        myexplain_lst.append(myexplain)
        if nodeclassname == mynodes:
            outfile.write('output ' + i + ' = ' + myexplain + '\n')
    return myexplain_lst
#-------------------------------------------------------------------------------------------------------------------------
def module_in_module(filename):
    new_wires = wires()
    new_nodes = nodes()
    mo_file = open(filename,'r')
    k = output(mo_file, new_nodes , new_wires)
    if k[0] != 'ok':
        return k[0],None,None,None,None
    mo_file.close()
    new_file = open(filename,'r')
    exp = new_file.read()
    lst = exp.split(';')
    first_line = lst[0]
    first_line = first_line.replace('(',' ( ')
    xs = first_line.split()
    modulename = xs[1]
    for o in new_nodes.output:
        if o in mywires.dict:
            return 'Output Of The Inside Module Overlaps With Outside Module', modulename, new_nodes.input, new_nodes.output, new_wires
    for q in new_nodes.input:
        if (q in mynodes.input and q!='#') or q in mywires.dict :
            return 'Input Of The Inside Module Overlaps With Outside Module' , modulename, new_nodes.input, new_nodes.output, new_wires
    conti = all_in_one(new_nodes,new_wires)
    p = 0
    for i in new_nodes.output:
        mywires.add(i)
        mywires.change(i,conti[p])
        p += 1
    return k[0] , modulename , new_nodes.input , new_nodes.output , new_wires
#-------------------------------------------------------------------------------------------------------------------------
def chart():
    def delayss(s):
        delay = 0
        for i in s:
            if i == '|' or i == '~' or i == '&':
                delay = delay + delays[i]
        return delay
    
    def proceed(xs):
        res = True
        for i in xs:
            if i in mywires.dict:
                return False
        return res

    def change(ex):
        if '&' in ex:
            ex = ex.replace('&',' & ')
        if '|' in ex:
            ex = ex.replace('|', ' | ')
        if '~' in ex:
            ex = ex.replace('~', ' ~ ')
        lst_ex = ex.split()
        if proceed(lst_ex):
            return ' '.join(lst_ex)
        for i in range(len(lst_ex)):
            if lst_ex[i] in mywires.dict:
                lst_ex[i] = ' ( ' + mywires.dict[lst_ex[i]] + ' ) '
        return change(' '.join(lst_ex))

    def draw():
        import turtle
        sep = turtle.Turtle()
        wn = turtle.Screen()
        wn.tracer(10)
        wn.bgcolor('black')
        sep.color('white')
        sep.up()
        sep.setpos(-300,-200)
        sep.down()
        sep.forward(900)
        sep.stamp()
        sep.up()
        sep.setpos(-300,-200)
        sep.left(90)
        sep.down()
        sep.forward(400)
        sep.stamp()
        sep.up()
        sep.setpos(-315,-100)
        sep.write('0')
        sep.sety(0)
        sep.write('1')
        sep.setx(-300)
        sep.sety(-100)
        sep.setheading(0)
        sep.down()
        sep.shape('blank')
        draw_node = input('Please Enter The Node You Want To Track: ')
        final_all_in_one = change(mywires.dict[draw_node])
        last = 0
        how = 0
        delay = delayss(final_all_in_one)
        for p in range(len(whole_val)):
            all_in_one_mid = final_all_in_one
            for i in whole_val[p]:
                all_in_one_mid = all_in_one_mid.replace(i,whole_val[p][i])
            if '&' in all_in_one_mid:
                all_in_one_mid = all_in_one_mid.replace('&', ' and ')
            if '|' in all_in_one_mid:
                all_in_one_mid = all_in_one_mid.replace('|', ' or ')
            if '~' in all_in_one_mid:
                all_in_one_mid = all_in_one_mid.replace('~', ' not ')
            final_result = eval(all_in_one_mid)
            if final_result == 0:
                sep.pensize(5)
                sep.color('red')
                if last == 1:
                    deg = degrees(atan(100/(3*delay)))
                    sep.right(deg)
                    sep.forward(100/sin(radians(deg)))
                    sep.left(deg)
                    sep.forward(3 * (int(howlongs[p])-delay))
                    sep.up()
                    sep.sety(-215)
                    how = how + int(howlongs[p])
                    sep.write(str(how))
                    sep.sety(-100)
                    sep.down()
                    last = 0
                else:
                    sep.setheading(0)
                    sep.forward(3 * int(howlongs[p]))
                    sep.up()
                    sep.sety(-215)
                    how = how + int(howlongs[p])
                    sep.write(str(how))
                    sep.sety(-100)
                    sep.down()
                    last = 0
            elif final_result == 1:
                sep.pensize(5)
                sep.color('green')
                if last == 0:
                    deg = degrees(atan(100/(3*delay)))
                    sep.left(deg)
                    sep.forward(100/sin(radians(deg)))
                    sep.right(deg)
                    sep.forward(3 * (int(howlongs[p])-delay))
                    sep.up()
                    sep.sety(-215)
                    how = how + int(howlongs[p])
                    sep.write(str(how))
                    sep.sety(0)
                    sep.down()
                    last = 1
                else:
                    sep.forward(3 * int(howlongs[p]))
                    sep.up()
                    sep.sety(-215)
                    how = how + int(howlongs[p])
                    sep.write(str(how))
                    sep.sety(0)
                    sep.down()
                    last = 1
        turtle.exitonclick()
                
    ins_filename = input('Please Enter The Required File To Draw The Chart:')
    instruct = open(ins_filename,'r')
    whole = instruct.read()
    whole = whole.replace('\n',' ')
    whole_lst = whole.split(';')
    for element in whole_lst:
        if element == '':
            whole_lst.remove(element)
    val = {}
    whole_val = []
    howlongs = []
    for i in whole_lst:
        if '=' in i:
            explain = i.replace('=',' = ')
            new_lst = explain.split()
            if new_lst[0] in mynodes.input:
                if new_lst[2] == '0' or new_lst[2] == '1':
                    val[new_lst[0]] = new_lst[2]
                else:
                    print('Not A Valid value')
                    return
            else:
                print('No Input Is Registered With This Name')
                return
        elif '#' in i:
            explain = i.replace('#',' # ')
            new_lst = explain.split()
            if new_lst[0] == '#' and len(new_lst) == 2:
                howlongs.append(new_lst[1])
                if len(whole_val) == 0:
                    if len(val) == len(mynodes.input):
                        whole_val.append(val)
                        val = {}
                    else:
                        print('Not Enough Values For All Inputs')
                        return
                else:
                    for k in whole_val[-1]:
                        if k not in val:
                            val[k] = whole_val[-1][k]
                    whole_val.append(val)
                    val = {}
            else:
                print('Wrong Syntax')
                return
        else:
            print('Wrong Syntax')
            return
    draw()
    return
#-------------------------------------------------------------------------------------------------------------------------
destiny = filecreator(file1,result_file)
#-------------------------------------------------------------------------------------------------------------------------
if destiny == 'go':
    continu = all_in_one(mynodes , mywires , result_file)
    if continu != 'stop':
        result_file.write('\n')
        truthtable(result_file,continu)
        chart()
#-------------------------------------------------------------------------------------------------------------------------
result_file.close()
