import nuke

def RenderProxyExr(args):

    #Parse the passed arguments. First arg is the script name, second arg is a
    #string of comma separated arguments in the form "input,outexr,outproxy"
    args = args[1].split(',')
    inputFile = args[0].replace("\\","/")
    outExr = args[1].replace("\\","/")
    outProxy = args[2].replace("\\","/")

    #Create read nodes, write nodes, and reformat
    r = nuke.nodes.Read()
    r.knob('file').fromUserText(inputFile)

    f = nuke.nodes.Reformat(type = 'to box',
                    box_width = 1280,
                    box_height = 720,
                    box_fixed = True,
                    resize = 'fit',
                    center = True,
                    black_outside = True)

    wproxy = nuke.nodes.Write(file = outProxy,
                    create_directories = True)

    wexr = nuke.nodes.Write(file = outExr,
                    create_directories = True)

    #Connect inputs for nodes
    wexr.setInput(0,r)
    f.setInput(0,r)
    wproxy.setInput(0,f)

    #Get the frame range for rendering
    start = r.knob('first').value()
    end = r.knob('last').value()

    #Render the two outputs using the frame range of the input
    nuke.render(wexr,start,end)
    nuke.render(wproxy,start,end)

if __name__ == "__main__":
    RenderProxyExr(sys.argv)
