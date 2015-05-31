##
# @file compy.py
# @brief Tool for heuristic compilation of given main file. If you have a heap of sources and you want to compile certain main c-file, this tool will try to find minimal set of sources for successful compilation of given main c-file.
# @author Centaurum
# @version v0.2
# @date 2015-05-30


import sys
import os.path
from optparse import OptionParser

COMP_MAIN_FILE = ""
MAX_ITERATIONS = 1000
LIB_NAMES_MATH = ["fabs", "ceil", "floor", "fmod", "exp", "frexp", "ldexp", "log", "log10", "modf", "pow", "sqrt", "acos", "asin", "atan", "atan2", "cos", "sin", "cosh", "sinh", "tanh"]
COMPILER = "gcc"
LANG_EXT = "c"
MAKEFILE_INFO = ["", "", ""] # format: sources, library options, executable name

##
# @brief Exit with error code -1 and given error string
#
# @param A - string to be printed
#
# @return
def Terminate(A):
    sys.stderr.write("Error: " + A + "\n")
    exit(-1)

##
# @brief Execute command
#
# @param cmd - command to be executed
#
# @return (exit code, stdout+stderr output)
def RunCommand(cmd):
    import os
    from subprocess import Popen, PIPE
    process = Popen(cmd + " 2>&1" , shell=True, stdout=PIPE )
    (output, err) = process.communicate()
    exit_code = process.wait()
    return (exit_code, output)

##
# @brief search and recognize error types from compiler output
#
# @param out - compiler output
#
# @return (error code, position)
def DetectError(out):
    import re
    error_markers = [": undefined reference to"] # TODO: extend errors
    if out != None:
        detected_error_list = sorted([(j[0].start(), j[1]) for j in [(re.search(error_markers[i], out), i) for i in range(0, len(error_markers))] if j[0] != None], key = lambda t:t[1])
        error = detected_error_list[0] if detected_error_list != [] else (-1, 0)
        return error # error: (error code, position)
    else:
        Terminate("There are invalid logs, it is impossile to detect error")

##
# @brief Try to extend source list to according to compilation errors
#
# @param out - compiling output
# @param detected_error - (error code, position)
# @param comp_line - compiling commandline
#
# @return extended commandline
def ExtendCompLine(out, detected_error, comp_line):
    import re
    def read_first_word(A):
        if A != None:
            se = re.search(' ', A)
            if se != None:
                return A[0:se.start()]
            else:
                return None
        else:
            return None
    res = comp_line
    (possition, error) = detected_error
    if error == 0:
        try:
            start_entity = re.search('`', out[possition:]).start()+1
        except:
            Terminate("There are unknown errors in compilation logs")
        try:
            end_entity = re.search('\'', out[possition:]).start()
        except:
            Terminate("Logs are corrupted")
        entity = out[possition + start_entity:possition + end_entity]
        file_name = read_first_word(RunCommand("cscope -L1 " + entity)[1])
        if file_name == None:
            # TODO: add other libraries, not only libmath; implement linking with available libraries
            if entity in LIB_NAMES_MATH: # maybe the desired entity is a standard library function
                res = res + " -lm"
                MAKEFILE_INFO[1] = MAKEFILE_INFO[1] + " -lm"
            else:
                Terminate("For value '" + entity + "' file has not been found")
        else:
            if opt.dir != "./": RunCommand("cpp %s > %s/%s"%(file_name, opt.dir, file_name)) # TODO: make copying with headers instead of preprocessing
            res = res + " " +file_name
            MAKEFILE_INFO[0] = MAKEFILE_INFO[0] + " %s"%file_name # TODO: make copying with headers instead of preprocessing
        print "File '%s' added to compilation."%file_name
        return res

##
# @brief Initialize cscope reference database. By the way, don't forget to install cscope.
#
# @param is_recursively - search in current folder or recursively
#
# @return
def init_database(is_recursively):
    RunCommand("rm cscope.in.out cscope.out  cscope.po.out -f")
    if len(RunCommand("whereis cscope")[1]) <= 8:
        Terminate("Please, install cscope")
    if is_recursively == True:
        RunCommand("find . -iname '*.%s' > cscope.files"%LANG_EXT)
    else:
        RunCommand("ls *.%s > cscope.files"%LANG_EXT)
    RunCommand("cscope -b -k")

##
# @brief Compile iterative extending source list
#
# @param target_file_name - main c-file to be compiled
#
# @return
def iterative_compilation(target_file_name):
    comp_line = target_file_name # main file to be compiled
    i = 0
    (error, out) =  RunCommand("%s "%COMPILER + comp_line)
    while i < MAX_ITERATIONS and error == 1:
        comp_line = ExtendCompLine(out, DetectError(out), comp_line)

        if comp_line != None:
            (error, out) =  RunCommand("%s "%COMPILER + comp_line)
        else:
            Terminate("Imposible to compile...")
        i = i + 1
    if i == MAX_ITERATIONS:
        Terminate("Impossible to compile, too much iterations are unsuccessful")




# Create commandline option parser
parser = OptionParser(usage="usage: %prog [options] main_file_name", version="%prog v0.2")
parser.add_option("-o", action="store", dest="executable", type="string", default="a.out", help="Executable file name")
parser.add_option("-r", action="store_true", dest="recursively", default=False, help="Find sources recursively")
parser.add_option("-m", action="store_true", dest="makefile", default=False, help="Create makefile")
parser.add_option("-d", action="store", dest="dir", type="string", default="./", help="Create separate directory for compiled files")
parser.add_option("-l", action="store", dest="lang", type="string", default="c", help="Language: 'c' or 'cpp'")
(opt, args) = parser.parse_args()
MAKEFILE_INFO[0] = args[0]
MAKEFILE_INFO[2] = opt.executable
# Check files to be compiled
if args == []:
    Terminate("At least one file should be specified")
if len(args) > 1:
    Terminate("Only one file can be processed at a time")
if not os.path.isfile(args[0]):
    Terminate("File \"" + args[0] + "\" is not exist")

# Chose compiler
if opt.lang == "c":
    COMPILER = "gcc -w"
    LANG_EXT = "c"
elif opt.lang == "cpp": # TODO: cpp is not tested yet. Implement other languages and comilers
    COMPILER = "g++ -w"
    LANG_EXT = "cpp"
else:
    Terminate("Language is not supported")

# Initialize variable database
init_database(opt.recursively)

# Create directory for found sources
if opt.dir != "./":
    if RunCommand("mkdir %s"%(opt.dir))[0] != 0:
        Terminate("Unable to create directory \"%s\""%opt.dir)
    RunCommand("cpp %s %s/%s"%(args[0], opt.dir, args[0]))

# compiling iterations
iterative_compilation(args[0])

# Delete tmp files
RunCommand("rm cscope.files  cscope.out -f")

# Generate makefile
if opt.makefile == True:
    if os.path.isfile(opt.dir + "/Makefile") or os.path.isfile(opt.dir + "/makefile"):
        Terminate("file %s is already exists"%(opt.dir + "/Makefile"))
    open(opt.dir + "/Makefile", "w").write(
"""\
CC=%s
CFLAGS=-c -w
LDFLAGS=%s
SOURCES=%s
OBJECTS=$(SOURCES:.%s=.o)
EXECUTABLE=%s

all: $(SOURCES) $(EXECUTABLE)

$(EXECUTABLE): $(OBJECTS)
\t$(CC) $(LDFLAGS) $(OBJECTS) -o $@

.cpp.o:
\t$(CC) $(CFLAGS) $< -o $@

clean:
\trm *.o -rf
"""%(COMPILER, MAKEFILE_INFO[1], MAKEFILE_INFO[0], LANG_EXT, MAKEFILE_INFO[2]))
    print "Makefile has been created"



print "\nCompiled successfully!"
