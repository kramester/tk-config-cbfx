import nuke

def RenderProxyExr(args):
    args = args[1].split(',')
    inputFile = args[0].replace("\\","/")
    outExr = args[1].replace("\\","/")
    outProxy = args[2].replace("\\","/")
    r = nuke.nodes.Read()
    r.knob('file').fromUserText(inputFile)
    wexr = nuke.nodes.Write(create_directories = True)
    f = nuke.nodes.Reformat(format = '3qhd')
    wproxy = nuke.nodes.Write(create_directories = True)

    wexr.setInput(0,r)
    f.setInput(0,r)
    wproxy.setInput(0,f)

    wexr.knob('file').setValue(outExr)
    wproxy.knob('file').setValue(outProxy)

    start = r.knob('first').value()
    end = r.knob('last').value()

    nuke.render(wexr,start,end)
    nuke.render(wproxy,start,end)

if __name__ == "__main__":
    RenderProxyExr(sys.argv)
