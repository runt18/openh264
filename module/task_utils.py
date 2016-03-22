# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
MAX_ARGS = 15

boilerplate = "/* This Source Code Form is subject to the terms of the Mozilla Public\n\
 * License, v. 2.0. If a copy of the MPL was not distributed with this\n\
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */\n"

includes = "#include \"RefCounted.h\"\n"

refcountclass = "class RefCountTaskWrapper : public gmp_args_base {\n\
public:\n\
  RefCountTaskWrapper(GMPTask* aTask, RefCounted* aRefCounted)\n\
    : mTask(aTask)\n\
    , mRefCounted(aRefCounted)\n\
  {}\n\
  virtual void Run() {\n\
    mTask->Run();\n\
  }\n\
  virtual void Destroy() {\n\
    mTask->Destroy();\n\
    gmp_args_base::Destroy();\n\
  }\n\
private:\n\
  ~RefCountTaskWrapper() {}\n\
\n\
  GMPTask* mTask;\n\
  RefPtr<RefCounted> mRefCounted;\n\
};\n"


def gen_args_type(args, member):
    if member:
        ret = ["C o"]
    else:
        ret = []
    ret.append("M m")
    for arg in range(0, args):
        ret.append("A{0:d} a{1:d}".format(arg, arg))
    return ", ".join(ret)

def gen_args(args, member):
    if member:
        ret = ["o"]
    else:
        ret = []
    ret.append("m")
    for arg in range(0, args):
        ret.append("a{0:d}".format((arg)))
    return ", ".join(ret)

def gen_args_(args):
    ret = []
    for arg in range(0, args):
        ret.append("a{0:d}_".format((arg)))
    return ", ".join(ret)

def gen_init(args, r = False, member = False):
    if member:
        ret = ["o_ (o)"]
    else:
        ret = []
    ret.append("m_ (m)")

    if r:
        ret.append("r_ (r)")

    for arg in range(0, args):
        ret.append("a{0:d}_ (a{1:d})".format(arg, arg))
    return ", ".join(ret)

def gen_typenames(args, member):
    if member:
        ret = ["typename C"]
    else:
        ret = []
    ret.append("typename M")

    for arg in range(0, args):
        ret.append("typename A{0:d}".format((arg)))
    return ", ".join(ret)

def gen_types(args, member):
    if member:
        ret = ["C"]
    else:
        ret = []
    ret.append("M")
    for arg in range(0, args):
        ret.append("A{0:d}".format((arg)))
    return ", ".join(ret)


def generate_class_template(args, ret = False, member = True):
    print "// {0:d} arguments --".format(args)
    if member:
        nm = "m"
    else:
        nm = "nm"

    if not ret:
        print "template<"+ gen_typenames(args, member) + "> class gmp_args_{0!s}_{1:d} : public gmp_args_base {{".format(nm, args)
    else:
        print "template<"+ gen_typenames(args, member) + ", typename R> class gmp_args_{0!s}_{1:d}_ret : public gmp_args_base {{".format(nm, args)

    print " public:"

    if not ret:
        print "  gmp_args_{0!s}_{1:d} (".format(nm, args) + gen_args_type(args, member) + ") :"
        print "    " + gen_init(args, False, member) + "  {}"
    else:
        print "  gmp_args_{0!s}_{1:d}_ret (".format(nm, args) + gen_args_type(args, member) + ", R* r) :"
        print "    " + gen_init(args, True, member) + "  {}"
        print "  virtual bool returns_value() const {\n    return true;\n  }"
    print
    print "  void Run() {"
    if ret:
        print "    *r_ =",
    else:
        print "   ",
    if member:
        print "((*o_).*m_) (" + gen_args_(args) + ");"
    else:
        print "m_ (" + gen_args_(args) + ");"
    print "  }"
    print
    print " private:"
    if member:
        print "  C o_;"
    print "  M m_;"
    if ret:
        print "  R* r_;"
    for arg in range(0, args):
        print "  A{0:d} a{1:d}_;".format(arg, arg)
    print "};"
    print
    print
    print

def generate_function_template(args, member):
    if member:
        nm = "m"
        NM = "";
    else:
        nm = "nm"
        NM = "NM";

    print "// {0:d} arguments --".format(args)
    print "template<" + gen_typenames(args, member) + ">"
    print "gmp_args_{0!s}_{1:d}<".format(nm, args) + gen_types(args, member) + ">* WrapTask{0!s} (".format(NM) + gen_args_type(args, member) + ") {"
    print "  return new gmp_args_{0!s}_{1:d}<".format(nm, args) + gen_types(args, member) + ">"
    print "    (" + gen_args(args, member) + ");"
    print "}"
    print
    if member:
        print "template<" + gen_typenames(args, member) + ">"
        print "GMPTask*"
        print "WrapTaskRefCounted{0!s} (".format(NM) + gen_args_type(args, member) + ") {"
        print "  GMPTask *t = WrapTask{0!s} (".format(NM) + gen_args(args, member) + ");"
        print "  return new RefCountTaskWrapper(t, o);"
        print "}"
        print

def generate_function_template_ret(args, member):
    if member:
        nm = "m"
        NM = "";
    else:
        nm = "nm"
        NM = "NM";
    print "// {0:d} arguments --".format(args)
    print "template<" + gen_typenames(args, member) + ", typename R>"
    print "gmp_args_{0!s}_{1:d}_ret<".format(nm, args) + gen_types(args, member) + ", R>* WrapTask{0!s}Ret (".format(NM) + gen_args_type(args, member) + ", R* r) {"
    print "  return new gmp_args_{0!s}_{1:d}_ret<".format(nm, args) + gen_types(args, member) + ", R>"
    print "    (" + gen_args(args, member) + ", r);"
    print "}"
    print



print boilerplate
print
print includes
print
print refcountclass
print

for num_args in range (0, MAX_ARGS):
    generate_class_template(num_args, False, False)
    generate_class_template(num_args, True, False)
    generate_class_template(num_args, False, True)
    generate_class_template(num_args, True, True)


print
print
print

for num_args in range(0, MAX_ARGS):
    generate_function_template(num_args, False)
    generate_function_template_ret(num_args, False)
    generate_function_template(num_args, True)
    generate_function_template_ret(num_args, True)



