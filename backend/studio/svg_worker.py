import resource
import sys
import cairosvg

if __name__=='__main__':
    resource.setrlimit(resource.RLIMIT_CPU,(8,8))
    resource.setrlimit(resource.RLIMIT_AS,(768*1024*1024,768*1024*1024))
    sys.stdout.buffer.write(cairosvg.svg2png(bytestring=sys.stdin.buffer.read(),unsafe=False))