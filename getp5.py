import re
p5rex =r"(p5\.[a-zA-Z]+[a-zA-Z0-9_]*)"
p = re.compile(p5rex)

def getp5(filename):
    with open(filename,"r") as f5:
        L = f5.readlines()
        P5 = []
        Lout = []
        for line in L:
            isp5 = re.findall(p, line)
            if isp5:
                for match in isp5:
                    P5.append(f"{match[3:]} = {match}\n")
                line = line.replace('p5.','')
            Lout.append(line)
        Fout = "".join(Lout[3:])
        P5 = "".join(sorted(list(set(P5))))
        return P5, Fout

def write_pyp5(P5,p5file="pyp5.py"):
    with open(p5file,"r") as f5:
        L = f5.readlines()
        L.extend(P5)
        Lout = sorted(list(set(L)))
        
    with open(p5file,"w") as w5:
        w5.write(''.join(Lout))    

def write_p5first(filename,in_place=False):
    P5, Fout = getp5(filename)
    prolog="import js\nfrom pyodide.ffi import create_proxy\np5 = js.window\n"
    
    fname = filename if in_place else (filename[:-3] + "_p5.py")
    with open(fname,"w") as w5:
        w5.write(f"{prolog}{P5}\n{Fout}")
        
   
                   
