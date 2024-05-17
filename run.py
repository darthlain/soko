import os, sys, platform, subprocess

filename = sys.argv[1]
ext = os.path.splitext(filename)[1][1:]
com = dict()
osname = platform.system()
restargv = ' ' + ' '.join(sys.argv[2:])

if osname == 'Linux':
    tmp = '/tmp/###TEMPEST###'
elif osname == 'Windows':
    tmp = '%USERPROFILE%/AppData/Local/Temp/###TEMPEST###'
    filename = filename.replace('/', '\\')

def c(ext, co, osname = None):
    if osname == None:
        osname = ('Linux', 'Windows')
    elif not isinstance(osname, tuple):
        osname = (osname,)
    
    for i in osname:
        com[i, ext] = co

c('c',    'gcc {0} -O3 -mtune=native -march=native -mfpmath=both -o {1} && {1}')
c('d',    'dmd -m64 -i -run {}')
c('cpp',  'g++ {0} -O3 -mtune=native -march=native -mfpmath=both -std=c++20 -o {1} && {1}')
c('py',   'python3 {}')
c('py',   'python {}', 'Windows')
c('pyw',  'pythonw {}')
c('js',   'node {}')
c('pl',   'perl {}')
c('p6',   'raku {}')
c('rb',   'ruby {}')
c('sh',   'sh {}')
c('jl',   'julia {}')
c('hs',   'runghc {}')
c('ts',   'ts-node {}')
c('go',   'go run {}')
c('rs',   'rustc {0} -o {1} && {1}')
c('cs',   'mcs {0} -out:{1} && {1}')
c('cs',   'csc /nologo /out:{1}.exe {0} && {1}', 'Windows')
c('vb',   'vbc /nologo /out:{1}.exe {0} && {1}', 'Windows')
c('hy',   'hy {}')
c('php',  'php {}')
c('vim',  'vs {}') # koturn/vs
c('nim',  'nim c -o:{1} --hints:off -r {0}')
c('clj',  'clj {}')
c('lua',  'lua {}')
c('scm',  'gosh {}')
c('lisp', 'sbcl --script {}')
c('bash', 'bash {}')
c('html', 'open {}', 'Darwin')
c('html', 'start {}', 'Windows')
c('html', 'xdg-open {}', 'Linux')
c('raku', 'raku {}')
c('ahk',  'autohotkey {}')

s = com[osname, ext].format(filename, tmp) + restargv
os.system(s)
