_file =open("sigs.txt","r")

filesig = dict()

while 1:
    s = _file.readline()
    if s == "":
        break
    else:
        desc,sig,_,_,ext,cat = s.split(",")
        sig = sig.replace(" ","").decode("hex")
        filesig[sig] = {"description":desc,"extension":ext,"category":cat,"signature":sig}
_file.close()

def is_known(s):
    return reduce(lambda acc,sig: acc | (True if s.startswith(sig) else False), filesig.keys(), False)

def match_count(s):
    return reduce(lambda acc,sig: acc + (1 if s.startswith(sig) else 0), filesig.keys(), 0)

def get_uniq_match(s):
    return reduce(lambda acc,sig: filesig[sig] if s.startswith(sig) else acc, filesig.keys(), {})

def get_match(s):
    return reduce(lambda acc,sig: acc+[filesig[sig]] if s.startswith(sig) else acc, filesig.keys(), [])
