# お遊びでpythonでlispを実装する
#
# aやkといった変数がすでに初期化されている問題
#
# マクロ実装したい できればcommonのではなくもっとエレガントにやりたい

import os, sys, functools, traceback

def kaiseki(s, acc = [], sacc = ''):

    if s == '':
        # accに副作用があるとなぜかダメらしい
        if sacc != '':
            return acc + [sacc]
        else:
            return acc

    elif s[0] == '"':
        stmp = ''
        while 1:

            s = s[1:]

            if s == '':
                print('文字列エラー')
                return
            elif s[0] == '\\':
                stmp += '\\'
                s = s[1:]
            elif s[0] == '"':
                return kaiseki(s[1:], acc + ['"' + stmp + '"'])
            
            stmp += s[0]

    elif s[0] == "'":
        return kaiseki(s[1:], acc + ["'"], sacc)

    elif s[0] == '.':
        if sacc:
            return kaiseki(s[1:], acc + [sacc, "."])
        else:
            return kaiseki(s[1:], acc + ["."])

    elif s[0] == '$':
        if sacc:
            return kaiseki(s[1:], acc + [sacc, '$'])
        else:
            return kaiseki(s[1:], acc + ["$"])

    elif s[0] == '[':
        a = ''
        while 1:
            if s[0] == ']':
                if not s:
                    print("添字エラー")
                    return
                if sacc:
                    return kaiseki(s[1:], acc + [sacc] + [a + ']'])
                else:
                    return kaiseki(s[1:], acc + [a + ']'])
            else:
                a += s[0]
                s = s[1:]

    elif s[0] == '#' or s[0] == ';':
        while 1:
            if s[0] == '\n' or s == "":
                return kaiseki(s, acc)
            else:
                s = s[1:]

    elif s[0] == '(':
        stmp = ''
        cnt = 0

        while 1:
            s = s[1:]
            if s == '':
                print('括弧エラー')
                return
            elif s[0] == ')' and cnt == 0:
                return kaiseki(s[1:], acc + [kaiseki(stmp)])
            elif s[0] == '(':
                cnt += 1
            elif s[0] == ')':
                cnt -= 1

            stmp += s[0]

    elif s[0] == ')':
        print('括弧エラー')
        return

    elif s[0] == ' ' or s[0] == '\n':
        if sacc != '':
            return kaiseki(s[1:], acc + [sacc], '')
        else:
            return kaiseki(s[1:], acc, '')

    else:
        return kaiseki(s[1:], acc, sacc + s[0])

class GSetter:
    pass

class Sub(GSetter):
    def __init__(self, k, env):
        self.val = main(k[1], env)
        if '"' == k[2][0]:
            self.sub = main(k[2], env)
        elif ':' in k[2]:
            self.sub = slice(*[main(i if i != '' else 'None', env) for i in k[2].split(':')])
        else:
            self.sub = main(k[2], env)

    def get(self):
        if isinstance(self.val, GSetter):
            return self.val.get()[self.sub]
        else:
            return self.val[self.sub]

    def set(self, it):
        if isinstance(self.val, GSetter):
            self.val.get()[self.sub] = it
        else:
            self.val[self.sub] = it

class Nonlocal(GSetter):
    def __init__(self, k, env):
        self.k = k
        while 1:
            if env.outer is glv:
                print('nonlocal: エラー 変数が存在しません')
                0 / 0
            elif env.outer and env.outer.get(k[1]):
                self.a = env.outer
                return
            else:
                env = env.outer

    def get(self):
        return self.a[self.k[1]]

    def set(self, it):
        self.a[self.k[1]] = it

class Global(GSetter):
    def __init__(self, k, env):
        if not glv.get(k[1]):
            print('global: エラー 変数が存在しません')
            0 / 0
        else:
            self.k = k

    def get(self):
        return glv[self.k[1]]
    
    def set(self, it):
        glv[self.k[1]] = it
        

class Method(GSetter):
    def __init__(self, k, env):
        self.a = main(k[1], env)
        self.k = k
        self.env = env
        #for i in k[2:]:
        #    if type(i) == list:
        #        self.a = getattr(self.a, i[0])(*[main(j, env) for j in i[1:]])
        #    else:
        #        self.a = getattr(self.a, i)

    def get(self):
        if isinstance(self.a, GSetter):
            a = self.a.get()
        else:
            a = self.a
        if type(self.k[-1]) == list:
            return getattr(a, self.k[-1][0])(*[main(j, self.env) for j in self.k[-1][1:]])
        else:
            return getattr(a, self.k[-1])

    def set(self, it):
        if isinstance(self.a, GSetter):
            a = self.a.get()
        else:
            a = self.a

        if type(self.k[-1]) == list:
            b = getattr(a, self.k[-1][0])(*[main(j, self.env) for j in self.k[-1][1:]])
            b = it
            return it
        else:
            return setattr(a, self.k[-1], it)

class Py(GSetter):
    def __init__(self, k):
        self.a = k[1]

    def get(self):
        return globals()[self.a]

    def set(self, it):
        globals()[self.a] = it

# 関数の引数を解釈する たぶん
def arg(parms, args, kwargs):
    d = {}

    # 括弧なしで全体リスト
    if type(parms) == str:
        d[parms] = args
        d.update(kwargs)
        return d
    
    # まずparmsのリストを作って 適用されるたびに消す
    rest = []

    for i in parms:
        # ここもよくわからん なんなんやろ
        if type(i) == list:
            rest.append(i[0])
        else:
            rest.append(i)
        
    for i in range(len(args)):
        # rest
        # (a b . c) みたいな感じ schemeっぽい
        if parms[i] == '.':
            d[parms[i + 1]] = args[i:]
            d.update(kwargs)
            return d

        # これなんのために書いてるのかよくわからん
        elif type(parms[i]) == list:
            d[parms[i][0]] = args[i]

        else:
            d[parms[i]] = args[i]
    d.update(kwargs)
    return d

class Mac:

    def __init__(self, k):
        self.k = k

    def do(self, args, env):
        args = [['quote', i] for i in args]
        print(self.k)
        a = main([['fn', self.k[1], *self.k[2:]], *args], env)
        return main(a, env)

class Env(dict):
    def __init__(self, parms=(), args=(), kwargs={}, outer=None):
        a = arg(parms, args, kwargs)
        self.update(a)
        self.outer = outer

    def find(self, var):
        if var in self:
            return self
        elif self.outer == None:
            return None
        else:
            return self.outer.find(var)

def readmacromain(k):
    
    if not type(k) == list:
        return k

    # 'hello は (quote hello) に変換される
    elif "'" in k:
        i = k.index("'")
        del k[i]
        k[i] = ['quote', k[i]]
        return readmacromain(k)

    # a$(b c) は (a b c) に変換される
    # a$b (a b)
    # a$
    elif '$' in k:
        i = k.index('$')
        a = k[i - 1]
        del k[i - 1]
        if not k[i:]:
            k[i - 1] = [a]
            return readmacromain(k)
        del k[i - 1]
        if type(k[i - 1]) != list:
            print("$引数エラー")
            0 / 0
        if k[i - 1]:
            k[i - 1] = [a, *k[i - 1]]
        else:
            k[i - 1] = [a]
        return readmacromain(k)

    # a.b は (-> a b) に変換される
    elif '.' in k:
        i = k.index('.')
        a = k[i - 1]
        del k[i - 1]
        del k[i - 1]
        k[i - 1] = ['->', a, k[i - 1]]
        return readmacromain(k)

    # a[i] は (sub a i) に変換される
    elif [i for i in k if '[' in i]:
        i = [i for i in enumerate(k) if '[' in i[1]][0]
        del k[i[0]]
        k[i[0] - 1] = ['sub', *k[i[0] - 1], *kaiseki(i[1][1:-1])]
        return readmacromain(k)

    else:
        return [readmacromain(i) for i in k]

def main(k, env):
    global nowenv, escapep, coescapep, foriters, loopnest
    nowenv = env

    if escapep:
        return None

    if coescapep:
        return None

    # ()は[]と解釈される
    if k == []:
        return []

    # 文字列
    if k[0] == '"':
        return eval(k)

    elif type(k[0]) != list and isinstance(env.find(k[0]) != None and env.find(k[0])[k[0]], Mac):
        return env.find(k[0])[k[0]].do(k[1:], env)

    elif k[0] == 'mac':
        return Mac(k)

    elif type(k) != list:
        a = env.find(k)
        if a == None:
            return eval(k)
        elif a:
            return a[k]

    elif k[0] == 'quote':
        return k[-1]

    elif k[0] == 'import':
        _from = k.index(':from') if ':from' in k else -1
        _import = k[1]
        _as = k.index(':as') if ':as' in k else -1
        s = ''

        if _from != -1:
            s = 'from %s ' % k[_from + 1]
        s += 'import ' + _import
        if _as != -1:
            s += ' as %s' % k[_as + 1]
        exec(s, globals())

    elif k[0] == 'if':
        for i in range(1, len(k), 2):
            if i == len(k) - 1:
                return main(k[i], env)
            elif main(k[i], env):
                return main(k[i + 1], env)

    elif k[0] == 'and':
        for i in k[1:]:
            a = main(i, env)
            if not a:
                return a
        return a

    elif k[0] == 'or':
        for i in k[1:]:
            a = main(i, env)
            if a:
                return a
        return a

    elif k[0] == 'loop':
        loopnest += 1
        while escapep == False:
            main(['do', *k[1:]], env)
            if coescapep:
                coescapep = False
                continue
        escapep = False
        loopnest -= 1
        return None

    elif k[0] == 'break':
        if loopnest >= 1:
            escapep = True
        else:
            print('break: ループ内ではありません')

    elif k[0] == 'continue':
        if loopnest >= 1:
            coescapep = True
        else:
            print('continue: ループ内ではありません')

    elif k[0] == 'while':
        loopnest += 1
        while escapep == False and main(k[1], env):
            main(['do', *k[2:]], env)
            if coescapep:
                coescapep = False
                continue
        escapep = False
        loopnest -= 1
        return None

    elif k[0] == 'for':
        loopnest += 1
        foriters.append(iter(main(k[2], env)))
        while escapep == False:
            try:
                env[k[1]] = next(foriters[-1])
                main(['do', *k[3:]], env)
                if coescapep:
                    coescapep = False
                    continue
            except StopIteration:
                escapep = True
                foriters = foriters[:-1]
        escapep = False
        loopnest -= 1
        return None
                
    elif k[0] == '=':
        if type(k[1]) == list or env.get(k[1]):
            # SET
            # a, b = c, dのようなやつ
            if type(k[1]) == list and type(k[2]) == list:
                #for i in range(len(k[2])):
                #    main(['=', k[1][i], k[2][i]], env)

                temp = []
                for i in range(len(k[2])):
                    b = main(k[2][i], env)

                    if isinstance(b, GSetter):
                        b = b.get()

                    temp.append(b)

                for i in range(len(k[1])):
                    a = main(k[1][i], env)

                    if isinstance(a, GSetter):
                        a.set(temp[i])
                    else:
                        env.find(k[1][i])[k[1][i]] = temp[i]
                return None

            # (SET a b)
            a = main(k[1], env)
            b = main(k[2], env)
            if isinstance(b, GSetter):
                b = b.get()

            if isinstance(a, GSetter):
                a.set(b)
            else:
                env.find(k[1])[k[1]] = b
            return None

        else:
            # DEFINE
            val = main(k[2], env)
            if isinstance(val, GSetter):
                val = val.get()

            # 変数として使える名前かどうか検査する
            # ここをコメントアウトすると3=4見たいな面白いものが見れる
            if (k[1][0] == '"' or k[1].isdigit() or k[1][0] == '*'):
                print('変数に使えない名前です')
                return None

            elif (k[1] in primitives):
                print('この名前はプリミティブとして登録されています')
                return None

            try:
                env[k[1]] = val
                return None
            except TypeError:
                print('=エラー')
                return None

    elif k[0] == 'defn':
        return main(['=', k[1], ['fn', k[2], *k[3:]]], env)

    elif k[0] == 'fn' or k[0] == 'lambda':
        return lambda *args, **kwargs: \
                main(['do', *k[2:]], Env(k[1], args, kwargs, env))
    
    elif k[0] == 'do':
        if len(k) == 1:
            return None
        for i in k[1:-1]:
            a = main(i, env)
            if isinstance(a, GSetter):
                a.get()
        a = main(k[-1], env)
        if isinstance(a, GSetter):
            return a.get()
        else:
            return a

    elif k[0] == '->':
        return Method(k, env)

    elif k[0] == 'py':
        return Py(k)

    elif k[0] == 'nonlocal':
        env[k[1]] = Nonlocal(k, env)
        return None

    elif k[0] == 'nlc':
        return Nonlocal(k, env)

    elif k[0] == 'global':
        env[k[1]] = Global(k, env)
        return None

    elif k[0] == 'glv':
        return Global(k, env)

    elif k[0] == '+=':
        a = main(['=', k[1], ['+', k[1], k[2]]], env)
        return a

    elif k[0] == '-=':
        a = main(['=', k[1], ['-', k[1], k[2]]], env)
        return a

    elif k[0] == '*=':
        a = main(['=', k[1], ['*', k[1], k[2]]], env)
        return a

    elif k[0] == '/=':
        a = main(['=', k[1], ['/', k[1], k[2]]], env)
        return a

    elif k[0] == '//=':
        a = main(['=', k[1], ['//', k[1], k[2]]], env)
        return a

    elif k[0] == '%=':
        a = main(['=', k[1], ['%', k[1], k[2]]], env)
        return a

    # 添字
    elif k[0] == 'sub':
        return Sub(k, env)

    # type()を使用した動的クラス生成
    # (class A () :greeding (fn () (print "hello")))
    # (= a (A))
    # (-> a (greeding))
    elif k[0] == 'class0':
        if k[2]:
            parent = ['TUPLE', *k[2]]
        else:
            parent = ['TUPLE', 'object']
        if len(k) <= 3:
            args = ['dict']
        else:
            args = ['DICT', *k[3:]]
        a = main(['=', k[1], ['type', '"%s"' % k[1], parent, args]], env)
        return a

    elif k[0] == 'class':
        if k[2]:
            parent = ['TUPLE', *k[2]]
        else:
            parent = ['TUPLE', 'object']
        if len(k) <= 3:
            args = ['dict']
        else:
            args = ['DICT']
            for i in k[3:]:
                if i[0] == 'defn':
                    args.append(':' + i[1])
                    args.append(['fn', *i[2:]])
                elif i[0] == '=':
                    args.append(':' + i[1])
                    args.append(i[2])
                else:
                    print('class 無効なパラメーターです')
                    0 / 0
        main(['=', k[1], ['type', '"%s"' % k[1], parent, args]], env)
        return None

    # 関数実行 たぶん キーワード (print "hello" :end "") のような感じで
    else:
        acc = []
        key = {}
        keyacc = None
        for i in k:
            if type(i) == str and i[0] == ':':
                keyacc = i[1:]
            else:
                a = main(i, env)
                if isinstance(a, GSetter):
                    a = a.get()
                if keyacc:
                    key[keyacc] = a
                    keyacc = None
                else:
                    acc.append(a)
        return acc[0](*acc[1:], **key)

def _eval(s):
    s = s.replace('(', ' ( ').replace(')', ' ) ')
    s = s.replace("'", " ' ")
    # m = [main(i, glv) for i in kaiseki(s)]
    m = main(readmacromain(['do'] + kaiseki(s)), glv)
    return m

# sbcl等と同じ挙動 pythonのように環境を作らない
def load(filename):
    filename = os.path.expanduser(filename)
    filename = os.path.abspath(filename)
    with open(filename, encoding = 'utf-8') as f:
        return _eval(f.read())

glv = Env()
nowenv = None
escapep = False
coescapep = False
loopnest = 0
foriters = []
macros = []
primitives = ['=', 'defn', 'fn', 'lambda', 'do', '->', 'sub', 'class', 'class0',
              'import', 'quote', 'mac', 'py', 'nlc', 'nonlocal', 'glv', 'global'
              'for', 'while', 'loop', 'break', 'continue',
              'if', 'and', 'or', '+=', '-=', '*=', '/=', '//=', '%=']

glv['True']	= True
glv['False']	= False
glv['None']	= None
glv['+']        = lambda *args: functools.reduce(lambda x, y: x + y, args[1:], args[0])
glv['-']        = lambda *args: functools.reduce(lambda x, y: x - y, args[1:], args[0])
glv['*']        = lambda *args: functools.reduce(lambda x, y: x * y, args[1:], args[0])
glv['/']        = lambda *args: functools.reduce(lambda x, y: x / y, args[1:], args[0])
glv['//']       = lambda x, y: x // y
glv['%']        = lambda x, y: x % y
glv['<']        = lambda *args: all(i[0] < i[1] for i in abbccd(args))
glv['>']        = lambda *args: all(i[0] > i[1] for i in abbccd(args))
glv['<=']       = lambda *args: all(i[0] <= i[1] for i in abbccd(args))
glv['>=']       = lambda *args: all(i[0] >= i[1] for i in abbccd(args))
glv['==']       = lambda *args: all(i == args[0] for i in args[1:])
glv['is']       = lambda *args: all(i is args[0] for i in args[1:])
glv['not']      = lambda x: not x
glv['in']       = lambda a, b: a in b
glv['EVAL']     = lambda arg: main(arg, nowenv)
glv['sprintf']  = lambda s, *args: s % args
glv['printf']   = lambda s, *args: print(s % args, end = '')
glv['LIST']     = lambda *args: list(args)
glv['TUPLE']    = lambda *args: args
glv['DICT']     = lambda **kwargs: kwargs
glv['apply']    = lambda f, lst: f(*lst)
glv['load']	= load

def abbccd(lst):
    acc = []
    for i in range(len(lst) - 1):
        acc.append((lst[i], lst[i + 1]))
    return acc

def repl():
    while 1:
        try:
            print('nolis> ', end = '')
            a = _eval(input())
            if a != None:
                print(a)
        except SystemExit:
            return
        except EOFError:
            return
        except:
            traceback.print_exc()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        repl()
    else:
        load(sys.argv[1])

#print(readmacromain(kaiseki("(for i range$(10) print$(a) =$((a b) (b +$(a b))))")))
