# Molok 20141222
#
# Compiler for "txt" documents
#
import argparse
import os
import re
import sys
from datetime import date,time,datetime,timedelta
from glob import glob

currentOperation = "starting ..."

desctxt="""\
  Compile txt documents.
 
  Search and replace "variables" in a -template-file- and creates a 
  compiled "daily" version ready to print with a name like this:
                        [template name]-[YYYYMMDD].prt
  A "variable" is a tag in txt document like
                        ... #date______# ...
"""

doctxt="""\
  Use the --guide option for read a complete documentation.
"""

documentazione="""\
                                Documentation

  CTXT is a "textual document compiler".
  
  CTXT get a "textual document source", compile it and produce a 
  textual document.
  However, a "document" may be whitchever unicode textual file, so, 
  CTXT may work fine also with "technical" files, source file, etc.
  
  The "source", called also Template, can contain a set of directives
  used to set the compiler environment, this is called DEFINITION
  SECTION and haves to be at the head of file (see above), the rest
  of file is called DOCUMENT SECTION.
  
  Definition section is optional, so the simpler example for a 
  template file is:
  ,----------------------------------------------( helloworld.txt )--
  | Hello #who#!
  '------------------------------------------------------------------
  the compiling command is (with correct system configuration):
   $ ctxt helloworld who=World
  and the resulting document is:
  ,-------------------------------------( helloworld-20150101.prt )--
  | Hello World!
  '------------------------------------------------------------------
  In this example, 'who' is a variable, #who# is a placeholder.
  
  As guidelines, the replacement value for a variable will lie in the 
  number and position of characters occupied between '#' place-holders
  (both included), unless specified otherwise.
  Retaking the first example:
  ,----------------------------------------------( helloworld.txt )--
  | Hello #who#!
  '------------------------------------------------------------------
   $ ctxt helloworld who=Worldwide
  will result equally in:
  ,-------------------------------------( helloworld-20150101.prt )--
  | Hello World!
  '------------------------------------------------------------------
  Instead:
  ,----------------------------------------------( helloworld.txt )--
  | Hello #whoIsThat#!
  '------------------------------------------------------------------
  with: who=World
  will be:
  ,-------------------------------------( helloworld-20150101.prt )--
  | Hello World      !
  '------------------------------------------------------------------
  In this case we can add a number to shorten the space occupied:
  ,----------------------------------------------( helloworld.txt )--
  | Hello #whoIsThat_5#!
  '------------------------------------------------------------------
  will result in the first case.
  
  There are many options like this, so let's take a look in deeper.
  
  --- VARIABLES
  The variable entity lives in two forms: as placeholders in template
  and as values in execution.
  ** CTXT searches for the firsts and replaces them with seconds! **
  In fact, the entity is the same, but lives in three phases: it has 
  a definition phase, a value phase and a formatting phase.
    Definition is gained from command line, template's definition 
  section, internal behaviour (predefined variables) and finally from 
  placeholders in template's document section; definition sets the 
  *name*, the *type*, the *source* and eventually the *value* of a 
  variable (see VARIABLES DEFINITION).
  In case of more definitions for the same variable, by *name*, the
  first definition is the leader definition.
    Value is gained from whatever source yields it: command line, 
  definition section, internal behaviour for predefined variables, or 
  interactive request if the variable reaches the formatting phase 
  without a value.
    Formatting is settled by format-dispositions, these was gained 
  from definition section and placeholders; in definition section 
  these are optional, instead, placeholders are formatting by
  definition; format dispositions may differ from a variable type to 
  another (user can specify some options for a date and some others 
  for a number, see FORMAT DEFINITION).
  
  --- DEFINITION SECTION
  Heading the txt document, there is the definition section.
  It's optional for very simple documents and replacements.
  In definition section we found:
  ,-----------------------,
  | @@def                 | <- FIRST DOC LINE! starts section
  | # comments...         | <- Comments, they must start on new line
  | @name:value           | <- variable definitions
  | @name@type            | <- variables typization
  | @name?condition       | <- variable checkings for conditional ...
  | @name-number          | <- jumps                            
  | @name[variable ...    | <- macro definitions
  | @name|expression      |    ... and macro body
  | @@doc                 | <- END of section, doc starts next line
  | ...                   |
  As we can see, the @ sign attend entirely the definition section,
  while a second marker, bounding the variable name, defines the 
  type of definition:
  - a colon character indicates a variable definition (see 
    VARIABLES DEFINITION),
  - a @ character indicates a type assignment (see TYPES)
#  - a question mark indicates a condition, the variable is checked
#    against the <condition> and the next definition is executed only
#    if the result is True (see CONDITIONS),
#        es: @answer:?yes
#            @result:"You have replied "YES"
#  - a minus sign indicates a jump, if a number N is indicated, then 
#    the next N definitions (rows) are ignored, if there's no number,
#    the named variable is evaluated to obtain an integer N, or zero
#    if it don't provide a number, and the N-jump is executed.
#    This feature work fine after conditions, but also it can work 
#    alone.
#  - a squared bracket indicates the beginning of a macro, the macros 
#    define a sequence of definitions that will be executed at later
#    time, see MACROS.


  --- VARIABLES DEFINITION
  A variable originates when its definition occurs.
  The simplest definition is a tag in document.
  Walking backward, we can define a variable in definition section or
  in command line and, finally, at start of execution, CTXT defines 
  some default variables by itself (see PREDEFINED VARIABLES).
  
  In command line, a variable is defined adding it's name and,
  optionally, a value separate by '=' as command parameter; no more 
  options are there.
  Example:
   $ ctxt my-doc property=mine!
  
  This is usefull for start ctxt in batch scripts with values passed.
  Example for DOS scripting:
   $ ctxt %doc_name% property=%user% system=%os%
  

  In definition section we define a variable by '@' (see before)
  followed by it's name, then a colon an then the actual definition.

  Variable names are mandatory, identify the variable.
  Name cannot contains space nor underscore nor colon characters, 
  only alphanumeric chars.

  The "actual definition", mentioned before, is mainly an expression 
  from where originate the value to assign to the variable.
  It offers different possibilities and is designated by the first 
  char:
  - "   a double quotation indicates constants, 
    a constant may contain every character until the end of line
        es: @var:"this is "my" variable
        es: @var:"text that contains # character, is not a comment
  -     an empty value is treated as if it was :" (a blank constant)
        es: @var:
  - #   a hash character indicates that next string will be parsed 
    as a document row, it may contains all variables already defined
        es: @var:##user# is the owner of this document (#name>#).
  - %   a percent character indicates a system environment variable, 
        es: @var:%path
    
  - ?   a question mark indicates a requested interactive input, 
        es: ?Insert a number
#     the type of input may be checked, using regexp, where the last question mark 
#     end the regexp: ??-?[0-9]?Insert a number
#     The question will be repeated if answer is invalid.
#   - a dot indicates a COMMAND LINE ARGUMENT, es: .arg-name even if a
#     predefined variable have the same name.
#   - an exclamation mark indicates a value searched in system environment variables,
#     then, if misses, in COMMAND LINE ARGMENTS and then is asked like with '?',
#     es: !env-or-args-name!regexp!user question
#   in addiction to this:
#   - a single quotation mark indicates a format expression, this apply to already 
#     defined variables (or predefined variables) and is valid for the whole document,
#     the format validity depend on the type of variable

#  --- CONDITIONS
#  Conditions need to be robust (however I want to implement that
#  directly), so that have a generic syntax.
#  Evaluate a condition mean to compare a variable against an
#  expression, that is:
#    <expression> : <value>|<operator><expression>
#    <value>      : <none>|<constant>|<variable>
#    <none>       : (none is typed after the previous operator)
#                   True if the variable is defined
#    <constant>   : a string X
#                   True if the variable value is equal to X
#    <variable>   : a hash followed by variable name #Y
#                   True if the variable value is equal to the Y value
#    <operator>   : <negation>|<comparison>
#    <negation>   : an esclamation mark '!'
#                   True if <expression> is False and vice versa
#    <comparison> : <less then>|<more then>
#    <less then>  : a comparison character '<'
#                   True if the variable value is less then 
#                   <expression> value
#    <more then>  : a comparison character '>'
#                   True if the variable value is more then
#                   <expression> value
#  Values are compared in natural manner if they are of the same type,
#  otherwise both are stringified and then compared.
#
#  When a result is obtained, only one possible action is taken:
#  + if True execute next definition (if 'False' it will be omitted)
#
#  In association with 'jumping' and 'memorizing' it's possible to 
#  obtain very smart solutions!

  --- TYPES
  Normally a variable is defined of type TEXT, only some predefined
  variables start with a different one.
  The user can specify the type of a variable in definition section
  to take advantage of specific type features, that are obtained with
  use of format options (see FORMAT DEFINITION).
  A type definition is in the form:
  | ...
  | @name@type
  when it occurs, if variable 'name' not exists, it will be created of
  the correct type;

  Valid types are listed here:
  - text        : is the default type, a text without length constraints.
  - date        : it contains a date.
  - time        : it contains a time, namely the rappresentation of
                    a moment in the 24 hours of a day.
#   - numbers

  --- MACROS
  
  
  --- FORMAT DEFINITION
  The final format depend on default format, options, allignement and
  computed length.
  Default formats by type:
  . String          text is rendered as value is. 
            e.g. 'CocaCola' => CocaCola
  
  . Date            date is rendered in ISO compressed format.
            e.g. 1 April 2015 => 20150401
                    this is easy to split in parts with text 
                    distribution (as xxxx/xx/xx) or date separator

  . Time            time is rendered in compressed precise format.
            e.g. 13h 25' 14'' 123456 mcsec => 132514123456
                    this is easy to render in human readable format
                    with text distribution or time separators
  Options by type:
  text options:
  - text distribution       text is spread over the map where:
                    'x' stands for variable character, other chars
                    stands for them-self (except for '_' that is
                    the 'end-of-options' char), e.g.:
            "Hello World" => xxx.xxxxxx-xx! => Hel.lo Wor-ld!

  date options:
  - dot '.'         pilots the render of separators, default is a dot
                    itself, alternatives may be indicated immediately 
                    after dot, es:
            #date./___#    ===>     2015/04/21

  - position        position of folds may be changed with cheracters
                    'd', 'm', 'Y' as for day, month and (cent.)year, 
            #date:mdY#     ===>     04212015

  - shifting        the date may be anticipated and postponed, the
                    simple way is using the number of days: tomorrow
                    will be '+1', a week ago will be '-7'
            #date:-7#      ===>     20150414
                    otherwise the explicit syntax is '[+-]n[dLmY]'
                    and it is iterable:
            #date:-1m:+4d# ===>     20150325
                    where 'd' means days, 'L' means working days,
                    that are counted jumping over saturday and 
                    sunday, 'm' means months and 'Y' means years.

  time options:
  - dot '.'         pilots the render of separators, default is a
                    sequence of colon, colon, dot, as in example:
            #hour.____#    ===>     12:07:42.18
                    alternatives may be indicated immediately 
                    after dot, es:
            #date..___#    ===>     12.07.42.18
    
  - position        positioning of folds may be changed with characters
                    'H', 'M', 'S' or 'f', meaning hours, minutes, seconds 
                    and fractions of second.
                    es: #@hour:hm#

  allignement
    ...
    >
    < collassabile

  computed length
    #...# default length
    > and < margins overflow and collapse
    _[length]#
 
  --- PREDEFINED VARIABLES
  Predefined variables are a facility for often-used data.
  
    name        contains the first parameter passed in command line, if 
                present, otherwise check for @name:... or external parameter
                'name=...', if none it take the name of the template.

    user        contains the user name as in system environment variable
 
    date        contains the current date at compile time.

    hour        contains the time of the day at compile start time.

#    now!        **Particular variable** thanks to '!' formatter, the
#                value of this variable is recalculate each rendering,
#                permitting to logging compilation timing.
    
  --- PLACEHOLDER CHARACTER ESCAPING
  Some characters have specific meanings, these are 'reserved' chars, 
  this causes that users can't use these chars freely.
  Sometimes it is needed one of the reserved chars simply for its 
  canonical value (e.g. inserting a '#' char for music notation), in
  these cases it's necessary to use an escape mechanism.
""" r"""
  In CTXT the escape character is '\' (backslash) and some cases it's
  requested a char-mapping to obtain the desired char in output.
  
  + Character needing escaping and mapping requested
  | Hash         |   #   |   \+   | always               |
  | underscore   |   _   |   \-   | always               |
  | backslash    |   \   |   \\   | always               |
  | colon        |   :   |   \:   | always               |
  | letter x     |   x   |   \x   | in text distribution |
""" """
  --- COMMAND LINE ARGMENTS
  After the first argument, on command line, user can add other optional
  arguments in the form: name=value
  Other optional arguments are described above (use -h)
 
  examples:
  +++ normal compilation of "mia_scheda" template.
  > ctxt mia_scheda

  +++ compiling "mia_scheda" with extra variables.
  > ctxt mia_scheda voce=Lavoro cliente=Macellaio

.
"""

# definizione di un singolo campo
campo_regexp=re.compile(r"#(?P<prefix>_*)(?P<nome>[a-zA-Z0-9]+)" \
                         "(?P<options>:?[^_#]+)??(?P<postfix>_*)" \
                         "(?P<length>\d+)?(?P<queue>(?:\.\.\.)|[><]+)?#")

### Objects definitions

class Log:
    """ A simpler log.
    
    This is intended to work as class Log, not as instance, 
    apart for 'growing messages'.
    A 'growing message' is a notification that may be 'not complete'
    and the owner process can add text ad libitum.
    I've also implemented a mechanism to switch DEBUG logging on and off
    ensuring a the best possible performance """
    err=[]      # list of errors, warnings, messages...
    
    LOG_ERROR="ERROR"
    LOG_WARNING="WARN"
    LOG_INFO="INFO"
    LOG_DEBUG="DEBUG"
    # LOG_LEVEL
    # contains the list of active log-levels.
    #
    # Use Log.changeLevel(*list) to change it.
    LOG_LEVEL=[LOG_ERROR,LOG_INFO,LOG_WARNING]

    # LOG_DEBUG_FILTER
    # allow a simple selection of what debug 'scope' must be silent.
    # Each line is used as parameter for a "startWidth" check,
    # if it matches, message is omitted.
    # String is checked before str.format is execute, so the '{}'
    # has to be inserted unchanged.
    LOG_DEBUG_FILTER = [
            "--p1ace+4o1der--", # this should silence noting, hopefully
            "Compilato.",
            "file: ",
            "Template - ",
            "TypeBase - ",
            "TypeBase - allinea",
            "TypeBase - taglia",
            "TypeBase - render",
            "partizionamento - ",
        ]
    # static 'generic' section
    def LOG(lvl, msg, *par):
        if len(par)>0:
            msg=msg.format(*par)
        Log.err.append("{:5}:{:%d%H%M%S.%f}:{}".format(lvl,datetime.now(),msg))
    def filter(msg):
        """Check if msg start with a not-allowed string."""
        for filter in Log.LOG_DEBUG_FILTER:
            if msg.startswith(filter):
                return False
        return True
    def ERROR(msg, *par):
        Log.LOG(Log.LOG_ERROR,msg,*par)
    def WARNING(msg, *par):
        Log.LOG(Log.LOG_WARNING,msg,*par)
    def INFO(msg,*par):
        Log.LOG(Log.LOG_INFO,msg,*par)
    def DEBUG(*no_mean):
        pass
    def _DEBUG(msg,*par):
        if Log.filter(msg):
            Log.LOG(Log.LOG_DEBUG,msg,*par)

    def _noLog(*no_mean):
        pass

    # level-depending definitions
    def _changeLevel(new_levels):
        new_levels.sort()
        if not ( new_levels == Log.LOG_LEVEL ):
            Log.LOG_LEVEL = new_levels
            Log.INFO("Log-level changed: {}", ":".join(Log.LOG_LEVEL))
            if Log.LOG_DEBUG in Log.LOG_LEVEL:
                Log.DEBUG = Log._DEBUG
            else:
                Log.DEBUG = Log._noLog
    def raiseLevel(new_level):
        Log._changeLevel(Log.LOG_LEVEL + [new_level])

    # GROWING MESSAGES implementation
    def startGrowingMessage(lvl, first_trunk, *par):
        log=Log(lvl)
        log.append(first_trunk, *par)
        return log
    def __init__(self, lvl):
        self._lvl=lvl
        self._idx=-1
        self._sep=" "
        # since 'append' use LOG and bypass specific methods (and so, lvl definition)
        # i have to check here the lvl
        # 'cause growings has their behaviour if logging
        self.isLogging=(lvl in Log.LOG_LEVEL)
    def append(self, msg, *par):
        if self.isLogging:
            if self._idx==-1 :
                # !!! this is not thread-safe !!!
                self._idx=len(Log.err)
                # first-trunk filtering : going to stop logging
                if Log.filter(msg):
                    Log.LOG(self._lvl, msg, *par)
                else:
                    self.isLogging = False
            else:
                if Log.filter(msg):       # GROWING MESSAGES filter each trunk
                    if len(par)>0:
                        msg=msg.format(*par)
                    Log.err[self._idx]+=self._sep+msg
    def stop(self):
        ret = None
        if self.isLogging:
            ret = Log.err[self._idx]

        self._idx=-1
        # re-check lvl because it may be stopped by filtering
        self.isLogging=(self._lvl in Log.LOG_LEVEL)

        return ret
    def setSeparator(self,sep):
        self._sep=sep
    
    # Start Log
    # Trace current date and Log status in log
    err.append("{:5}:{:%d%H%M%S.%f}:{}-lvl{}".format("START",datetime.now(),
               datetime.now().strftime("%Y-%m-%d %H:%M:%S"),":".join(LOG_LEVEL)))

class Template:
    """ Manager for template.
        This mean in two sections: definition and document."""
    def __init__(self, file_in):
        self.file_name = file_in.name.rpartition("\\")[2].partition(".")[0]
        self._def_src = []
        self._tpl_src = []
        is_def=False
        log=Log(Log.LOG_DEBUG)
        log.setSeparator("")
        for l in file_in :
            # remove last \n char
            l=l[:-1]
            log.append("Template - ")
            # verify definition section begin/end
            if not is_def and l[:5]=="@@def": is_def=True
            if is_def :
                log.append("D")
                # jump comments
                if len(l.strip())==0 or l.strip()[0] =="#":
                    log.append(" {}",l)
                else:
                    # valid definitions rows start with "@"
                    if l.strip()[0] =="@"  :
                        log.append("+")
                        # save the row, it will be processed later
                        self._def_src.append(l)
                    else:
                        log.append("?")
            else:
                log.append("- ")
                # not definition, then it's document/template
                # save the row, it will be processed later
                self._tpl_src.append(l)
            # the '@@doc' line must result in 'def' section, so I check it AFTER appends
            if     is_def and l[:5]=="@@doc": is_def=False
            log.append(l)
            log.stop()
        Log.DEBUG("Template - rows DEF:{}, DOC:{}".format(len(self._def_src),len(self._tpl_src)))
        Log.DEBUG("Template - DEF :\n{}","\n".join(self._def_src))
        Log.DEBUG("Template - DOC :\n{}","\n".join(self._tpl_src))
    def definition_section(self):
        return self._def_src
    def document_section(self):
        return self._tpl_src

class Compilato:
    def __init__(self, file):
        self._file=file
    def accoda(self, riga):
        if riga[:-1] != "\n":
            riga += "\n"
        Log.DEBUG("Compilato - accoda: scrivo {}", riga[:-1])
        self._file.write(riga)

class Variable:
    """Represents a value to insert to someware in document."""
    
    # constants for variable source
    DEF="DEF"
    EXT="EXT"
    PRE="PRE"
    UND="UND"

    # manage a singleton source for "automatic naming"
    name_number = 0
    def newName(radix):
        name_number+=1
        return "{}_{05}".format(str(radix),name_number)


    def __init__(self,name,source=None,value=None):
        """ name: string, variable identifier
            source: string, instantiation occur caused by ?
                DEF: parameter definition (definition section)
                EXT: parametro esterno
                PRE: parametro predefinito
                UND: parameter used but undefined
            value: an object representing the value, eg. a string
        """
        self.name=name
        self.is_def=bool(source==Variable.DEF)
        self.is_ext=bool(source==Variable.EXT)
        self.is_pre=bool(source==Variable.PRE)
        self.is_und=bool(source==Variable.UND or source==None)
        self.value=None if self.is_und else value
    def __str__(self):
        return "<Variable {}: [{}]\"{}\" from {}>".format(
                self.name, self.type(), self.value,
                self.source())
    def callForValue(self, value_factory):
        self.value=value_factory(self)
    def source(self):
        if self.is_def: return Variable.DEF
        if self.is_pre: return Variable.PRE
        if self.is_ext: return Variable.EXT
        if self.is_und: return Variable.UND
        return None
    def type(self):
        if isinstance(self.value,str):
            return "text"
        if isinstance(self.value,time):
            return "time"
        if isinstance(self.value,date):
            return "date"
        return "unknown"
    def cast(self, type):
        if self.value == None or type == self.type():
            return self.value
        if type == "text":
            if self.type() == "time":
                return self.value.strftime("%H%M%S%f")
            if self.type() == "date":
                return self.value.strftime("%Y%m%d")
        if self.type() == "text":
            if type == "date":
                # per ora interpreto solo il formato YYYYMMDD
                try:
                    return datetime.strptime(self.value, "%Y%m%d").date()
                except ValueError :
                    Log.WARNING("Variable.cast - invalid date value: {}",self.value)
            if type == "time":
                # per ora interpreto solo il formato HHMMSSuuuuuu
                try:
                    Log.DEBUG("Conversione text 2 time: {} ({})", self.value, datetime.strptime(self.value, "%H%M%S%f"))
                    return datetime.strptime(self.value, "%H%M%S%f").time()
                except ValueError :
                    Log.WARNING("Variable.cast - invalid time value: {}",self.value)
        # le combinazioni rimanenti non possono essere convertite, 
        # prendo il valore di default
        return typed_default_value(type)

class TypeBase:
    """Tipo base, si focalizza sul testo finale.
    
    Implementa le parti generali che vanno a lavorare 
    sul testo finale che viene prodotto.
    Non formatta un tipo specifico.
    """
    def __init__(self, formato):
        self.prefix  = formato['prefix']
        self.postfix = formato['postfix']
        self.options = formato['options']
        self.queue = formato['queue'] or ""
        self.length = formato['length']
        self.original = None             # Variabile originale in elaborazione
        self.allin_char = " "                 # TODO: gestione caratteri diversi
        self.is_on_left = (self.prefix == '')
        self.is_on_right = (self.postfix == '')
        self.is_centered = (not self.is_on_left and not self.is_on_right)
    def base(self, variable):
        """Estrae il valore base dalla variabile.
        
        Per valore base intendo quel valore che potrebbe andare 
        direttamente in output nel caso non ci fossero opzioni
        nè allineamenti o troncamenti.
        """
        return repr(variable)
    def elabora_opzioni(self, value):
        """Modifica il testo in base alle opzioni inserite."""
        # il tipo base non ha opzioni
        return value
    def allinea(self, value):
        """Aggiunge caratteri di riempimento 
        se il testo è corto rispetto al segnaposto.
        
        Non aggiunge caratteri se è indicato il collassamento.
        """
        if len(value) < self.length and not '<' in self.queue:
            diff = self.length - len(value)
            if self.is_centered:
                #aggiungo tanti caratteri a dx quanto a sx
                car_sx = int(diff / 2)
                car_dx = diff - car_sx         # al limite uno in più a destra
                value = ((self.allin_char * car_sx) + value + 
                                (self.allin_char * car_dx))
            elif self.is_on_right and not self.is_on_left:
                #allin. destra
                value = (self.allin_char * diff) + value
            else:
                #nessuna richiesta di allin. equivale ad allineare a sx
                #allin. sinistra
                value = value + (self.allin_char * diff)
        Log.DEBUG("TypeBase - allinea: esito:{}: [{},{},{}]",value,
                  self.is_on_left,self.is_centered,self.is_on_right)
        return value
    def taglia(self, value):
        """Accorcia il testo se supera la lunghezza del segnaposto."""
        if len(value) > self.length:
            if self.queue == '...':
                # mantengo la lunghezza massima, 
                # ma sostituisco l'ultimo carattere con ellipse ('…')
                # dal lato di allineamento (o entrambi)
                ellips = '\u2026'
                if self.length > 1:
                    if self.is_centered:
                        if len(value)-self.length > 1:
                            diff = len(value)-self.length +2  # 2 ellipsis
                            diff_sin = int(diff / 2)
                            diff_des = diff - diff_sin      # taglio + a destra
                            value = (ellips + 
                                value[diff_sin:-diff_des] + ellips)
                        else:
                            #solo 1 carattere da troncare
                            value = value[:-2] + ellips
                    elif self.is_on_right and not self.is_on_left:
                        value = ellips + value[-(self.length-1):]
                    else:   # a sinistra
                        value = value[:self.length-1] + ellips
            elif '>' in self.queue:
                # permette il debordaggio, non tronco
                pass
            else:
                value = value[:self.length]
        Log.DEBUG("TypeBase - taglia: esito:{}:",value)
        return value
    def render(self, variable):
        Log.DEBUG("TypeBase - render: type {}",self.__class__)
        self.original = variable
        val = self.base(variable)
        val = self.elabora_opzioni(val)
        val = self.allinea(val)
        val = self.taglia(val)
        Log.DEBUG("TypeBase - render: {} da:{}; a:{}",variable.name,variable.value,val)
        return val

class TypeString (TypeBase):
    """Tipo base, rappresenta un testo."""
    def base(self, variable):
        return (variable.value if variable.value else "")
    def elabora_opzioni(self, value):
        """Modifica il testo in base alle opzioni inserite."""

        if self.options :
            log = Log.startGrowingMessage(Log.LOG_DEBUG,
                                          "TypeString - elabora_opzioni:")

            # text distribution
            text_distr_check = re.compile(
                r":(?:(?:[^x_#:\\]|\\[-+:x\\])*x+)+(?:[^x_#:\\]|\\[-+:x\\])*:?")
            text_distr_match = text_distr_check.search(self.options)
            if text_distr_match :
                log.append("text-distr : ")
                log.setSeparator("")

                text_distr_splitter = re.compile(
                    r"(?:[^x_#:\\]+|\\[-+:x\\]|x+)")
                # spezzetto il pattern di distribuzione
                text_distr_parts = text_distr_splitter.findall(
                                       text_distr_match.group())
                # ciclo sui pezzetti accodando o sostituendo
                # consumando il valore come consumabile
                consumabile = value
                new_value = ""
                for part in text_distr_parts:
                    log.append("p[{}]",part)

                    # se è un escape sostituisco con l'equivalente
                    if part[0] == "\\":
                    ##    part = part[1].translate(str.maketrans("-+x\\","_#x\\"))
                        part = ctxtesc(part)
                    
                    # se è una o più x sostituisco con tanti chars
                    elif part[0] == "x":
                        num_x = len(part)
                        part = consumabile[:num_x]
                        consumabile = consumabile[num_x:]

                    # se è altro accodo
                    else:
                        pass

                    new_value += part
                    log.append(":{}:,",part)
                # il nuovo valore ottenuto è questo
                value = new_value
        return value

class TypeDate (TypeBase):
    """Tipo data, rappresenta un momento, nel senso di data."""
    def base(self, variable):
        value = ""
        if isinstance(variable.value,date):
            # produco la data in formato base yyyymmdd
            value = variable.value.strftime("%Y%m%d")

            Log.DEBUG("TypeDate - base: {}",value)
        return value
    def elabora_opzioni(self, value):
        """Crea il testo dalla data in base alle opzioni inserite."""
        if self.options :
            log = Log.startGrowingMessage(Log.LOG_DEBUG,
                                          "TypeDate - elabora_opzioni:")
            elab_value = self.original.value #  -- shifting --
            schema = "Ymd"      # modificato da -- positioning --
            separator = ""      # modificato da -- separators --

            # -- shifting --
            option_check = re.compile(r"(?<!\\):([+-]\d+)([dLmY]?)(?:(?<!\\):|$)")
            option_match = option_check.search(self.options)
            match_n = 0
            while option_match:
                log.append(" shifting :" if match_n == 0 else ", ")

                # determino la modifica chiesta
                quant = option_match.group(1)
                quant = int(quant)
                misur = option_match.group(2)
                
                date_diff = timedelta()
                
                # sposto la data elaborata di quanto richiesto
                if misur == 'Y':
                    elab_value = elab_value.replace(
                                year = (elab_value.year + quant))
                elif misur == 'm':
                    # d delta
                    # m mese corrente
                    # mese ottenuto = ((m-1)+d)%12+1
                    # delta anno = int(((d+m-1)-((d+m-1)%12))/12)

                    # delta normalizzato
                    dnorm = quant + (elab_value.month-1)
                    anni = int((dnorm - (dnorm % 12)) / 12)
                    mesi = (dnorm % 12) + 1
                    elab_value = elab_value.replace(
                                year = (elab_value.year + anni),
                                month = mesi)
                elif misur == 'L':
                    # giorni lavorativi, devo individuare domenica e 
                    # se è compresa aumentare lo shift di 2 ogni 5
                    
                    # conteggio degli shift extra per saltare i w-e
                    extra = 0
                    adegua = 0

                    # prendo un riferimento sulla settimana
                    wday = elab_value.isoweekday() 
                    
                    # variabile di comodo per sapere la direzione
                    direz = (1 if quant > 0 else -1)
                    
                    # se la data corrente è nel w-e devo "uscirne"
                    if wday in [6,7]:
                        extra += int(6.5+(1.5*direz)-wday)*direz
                        adegua = -direz

                    # calcolo il giorno derivante dal superamento del week
                    # -1 e +1 portano il range nel campo di lavoro del reminder
                    wday_no_we = ((wday + extra -1) % 7 ) +1

                    # scavalla il w-e se lo shift è maggiore della
                    # distanza tra la data e il w-e successivo (in base a direz)
                    if quant > 0:
                        dista_we = 6 - wday_no_we
                    else:
                        dista_we = wday_no_we

                    # se ho extra sono uscito dal we, muovendomi già di un
                    # giorno nella direzione voluta (quant) quindi devo adeguare
                    if (quant + adegua)*direz >= dista_we:
                        
                        # verifica positiva, sicuramente scavallo un we
                        extra += 2*direz
                        
                        # quanti altri we scavalcherò? 1 ogni 5 giorni
                        settimane = int(((quant + adegua)*direz - dista_we) /5)
                        extra += settimane *2 *direz

                    elab_value = elab_value + timedelta(
                                days = (quant + adegua + extra))
                else:       # se misur è omesso oppure 'd'
                    elab_value = elab_value + timedelta(
                                days = quant)

                log.append("{}{}", quant, misur)
                
                match_n =+ 1
                option_match = option_check.search(self.options,
                                                   option_match.end()-1)
            if match_n > 0:
                log.append(" to {}", elab_value)

            # -- positioning --
            option_check = re.compile(r"(?<!\\):([dmY]+)(?:(?<!\\):|$)")
            option_match = option_check.search(self.options)
            if option_match:
                log.append(" positioning :")

                # determino la sequenza scelta
                schema = option_match.group(1)
                    
                log.append("{}", schema)

            # -- separators --
            option_check = re.compile(r"(?:^:?|(?<!\\):)(\.([^_#:\\]|\\[-+:\\])?)(?:(?<!\\):|$)")
            option_match = option_check.search(self.options)
            if option_match:
                log.append(" separator :")

                # determino il separatore scelto
                separator = "."
                if option_match.group(2):
                    separator = ctxtesc(option_match.group(2))
                    
                log.append("{}", separator)

            # costruisco lo schema finale
            fschema = separator.join(["%"+p for p in schema])
            log.append(": {}", fschema)
            value = elab_value.strftime(fschema)
        return value

class TypeTime (TypeBase):
    """Tipo ora, rappresenta un momento, nel senso di orario."""
    def base(self, variable):
        value = ""
        if isinstance(variable.value,time):
            #produco l'ora in formato base HHMMsscccccc
            value = variable.value.strftime("%H%M%S%f")

            Log.DEBUG("TypeTime - base: {}",value)
        return value
    def elabora_opzioni(self, value):
        """Crea il testo dalla data in base alle opzioni inserite."""
        if self.options :
            log = Log.startGrowingMessage(Log.LOG_DEBUG,
                                          "TypeTime - elabora_opzioni:")
            elab_value = self.original.value #  eventuali future
            schema = "HMSf"     # modificato da -- positioning --
            separator = ""      # modificato da -- separators --

            # -- positioning --
            option_check = re.compile(r"(?<!\\):([HMSf]+)(?:(?<!\\):|$)")
            option_match = option_check.search(self.options)
            if option_match:
                log.append(" positioning :")

                # determino la sequenza scelta
                schema = option_match.group(1)
                    
                log.append("{}", schema)

            # -- separators --
            option_check = re.compile(r"(?:^:?|(?<!\\):)(\.([^_#:\\]|\\[-+:\\])?)(?:(?<!\\):|$)")
            option_match = option_check.search(self.options)
            if option_match:
                log.append("separator :")

                # determino il separatore scelto
                separator = "::."
                if option_match.group(2):
                    separator = ctxtesc(option_match.group(2))
                    
                log.append("{}", separator)

            # costruisco lo schema finale
            if schema == "HMSf" and separator == "::.":
                log.append(": default")
                value = elab_value.strftime("%H:%M:%S.%f")
            else:
                fschema = separator.join(["%"+p for p in schema])
                log.append(": {}", fschema)
                value = elab_value.strftime(fschema)
        return value

class Formattatore:
    """Classe di controllo della formattazione."""
    # funzione di classe
    def typerFactory(variabile, formato):
        log = Log.startGrowingMessage(Log.LOG_DEBUG, 
                "Formattatore - typerFactory: var {} ",variabile.name)

        if isinstance(variabile.value, time):

            log.append(": type TIME")
            log.stop()

            return TypeTime(formato)

        if isinstance(variabile.value, date):

            log.append(": type DATE")
            log.stop()

            return TypeDate(formato)

        log.append(": type (undef) STRING")
        log.stop()

        return TypeString(formato)
    def __init__(self, variabile, formato):
        """
        variabile: Variable, 
        formato: dict(nome,prefix,postfix,options,queue,length)
        """
        self.variabile=variabile
        self.formato=formato
        self.typer=Formattatore.typerFactory(variabile, self.formato)
    def campo(self):
        _campo = "#{0[nome]}*{0[length]}+{0[options]}"
        return _campo.format(self.formato)
    def testo(self):
        return self.typer.render(self.variabile)

class Wallet:
    """ Wallet containing all objects involved in process."""
    tmp=None    # Template
    out=None    # Output
    vars={}     # Dict of Variable
    
    # methods
    def var(self, var=None, rif=None):
        """ Add, provide or update a walleted-variable.

        <var> is the Variable to use, even as 'name' if <rif> isn't provided
        <rif> is the name to use for var (value, add or update)
        Return a value, String, eventually blank.
        
        In update, this function protect PREDEFINED variables, if defined,
        against user-defined variables with the same name.
        """
        #in ogni caso non contemplato nelle catene di if restituisco una stringa vuota
        ret=""
        pre=None
        if not rif==None:
            #cerco la variabile
            if rif in self.vars:
                pre=self.vars[rif]
                #valore della variabile
                ret=pre.value
            # eseguo l'aggiunta/aggiornamento di variabile per riferimento
            if not var==None:
                if pre and pre.is_pre:
                    # PREDEFINED protection
                    Log.WARNING("Wallet - var: PRD protection for {} against {}",
                                rif, var.source())
                else:
                    if isinstance(var, Variable):
                        self.vars[rif]=var
                        Log.DEBUG("Wallet - var: {} {} = {}", 
                                  ("ADD" if pre == None else "UPD"), rif, var)
                    else:
                        Log.ERROR("Wallet - var: il valore di '{}' "
                                  "deve essere Variable", rif)
        elif not var==None:
            #aggiunta/aggiornamento di variabile diretta
            if isinstance(var, Variable) :
                ret=var.value
                Log.DEBUG("Wallet - var: {} {}", 
                          ("UPD" if var.name in self.vars else "ADD"), var)
                self.vars[var.name]=var
            else:
                Log.ERROR("Wallet - var: il tipo di var '{}' deve essere Variable",
                             (var.name if 'name' in var else var))
        else:
            Log.ERROR("Wallet - var: chiamata senza parametri non prevista")
        return ret
    def sostituzione(self, rendering_disposition):
        """ Analize rendering_disposition and operate the substitution 
        returning the resulting value."""
        #mi assicuro che la variabile sia definita
        nome=rendering_disposition['nome']
        if not nome in self.vars:
            # la variabile non è definita
            # genero una nuova variabile chiedendo all'utente il valore
            self.vars[nome]=Variable(nome)
            self.vars[nome].callForValue(richiestaValore)
        variabile=self.vars[nome]
        #applico il formato
        format=Formattatore(variabile,rendering_disposition)
        #recupero il valore
        testo = format.testo()
        Log.INFO("Wallet - sostituzione: {} da: {} a: {}",nome, format.campo(), testo)
        return testo
    def createTemplate(self, file):
        if self.tmp==None :
            self.tmp=Template(file)
        else:
            Log.ERROR("Wallet - createTemplate: template già definito, creare un nuovo Wallet per un nuovo template")
    def createOutput(self, file):
        if self.out==None :
            self.out=Compilato(file)
        else:
            Log.ERROR("Wallet - createOutput: output già definito, creare un nuovo Wallet per un nuovo output")

def ctxtesc(sequence: str) -> "str, single char":
    """Return the original character corresponding to sequence."""
    ## ATTENZIONE ##
    # usato solo da text-distribution e date.separator
    # quindi c'è di mezzo la x che in altri casi potrebbe dare anomalie
    ret = sequence
    if len(sequence) == 2 and sequence[0] == "\\":
        ret = sequence[1].translate(str.maketrans("-+x\\","_#x\\"))
    return ret

def menu(dir):
    """menu schede presenti.
    leggo la dir e salvo i nomi file scheda_*
    """
    
    file_scelto=None
    
    print("\n Compilazione schede:\n")
    
    docs = glob(dir+"*.txt")
    ## : stampo i file con indice
    docs = [f.rpartition(".")[0] for f in docs]
    [print("{:>5}: {}".format(str(i+1), docs[i])) for i in range(0, len(docs))]

    ## : chiedo all'utente quale scheda
    print("\n{:>5}: {}".format("q","Esce senza compilare alcuna scheda"))
    scelta = "0"
    while scelta != "q" and not ( scelta.isdecimal() and 0 < int(scelta) <= len(docs) ):
        scelta = input("\n => Quale scheda compilare? ")
        if scelta != "q" and not ( scelta.isdecimal() and 0 < int(scelta) <= len(docs) ):
            print (" !! Selezione '{}' non valida, "
            "indicare un numero tra quelli indicati o 'q'\n".format(scelta))
    ##gestione diversa da uscita anticipata
    if not scelta == 'q' :
        file_scelto = docs[int(scelta)-1]
    
    return file_scelto

def richiestaValore(variabile):
    global currentOperation
    valore=input("\r Variabile {:15} non definita, inserire il valore :".format(variabile.name))
    print(currentOperation, end="")
    return valore

def split_def_command(command):
    """Split command in parts: variable name, specific command, definition.
    
    Return None if command is invalid.
    """
    # procedo per casi
    # il che significa che dopo un '@' non posso usare un ':'
    #   perché verrebbe intercettato per primo!
    valid_commands = [":", "@"]
    specific_command = "--invalid--"
    for comm_char in valid_commands:
        comm_pos = command.find(comm_char)
        if comm_pos > -1:
            specific_command = comm_char
            break
    if "--invalid--" == specific_command:
        return None
    
    return command.partition(specific_command)

def typed_default_value(type: str):
    if type == 'text':
        return ''
    if type == 'date':
        return date.today()
    if type == 'time':
        return datetime.now().time()
    return None

def variable_with_value(name: str
                        , actual_command: str
                        , definition: str
                        , wallet: Wallet) -> Variable:
    """Create a variable and assign it a value.
    
    actual_command must be ':',
    definition can start with:
      void value -> blank string
      :  ->  constant string
      #  ->  composed string (with variables)
      %  ->  environment variables
    """
    var = None
    value=None
    value_type='"'
    # check sul nome
    if name == "":
        name = Variable.newName("undef")
    # caso particolare - def vuota
    if definition == "":
        value=""
    else:
        value_type=definition[0]
        value=definition[1:]
    Log.DEBUG("variable_with_value - cmd '{}', name: {}, "
                "type: '{}', value: {}.",
                actual_command, name, value_type, value)
    if value_type == '"':
        var = Variable(name,Variable.DEF,value)
    elif value_type == '#':
        result = sostituzione_variabili(wallet, value)
        Log.DEBUG("variable_with_value - composing '{}' in '{}'",value,result)
        var = Variable(name,Variable.DEF,result)
    elif value_type == '%':
        if value in os.environ:
            var = Variable(name,Variable.DEF,os.environ[value])
        else:
            Log.WARNING("variable_with_value - a property named '{}' "
                        "is not defined in OS environment.",value)
            var = Variable(name,Variable.DEF,'%'+value+'%')
    else:
        var = Variable(name,Variable.DEF,"####")
    return var

def interpreta_def(comando, wallet):
    """Interpreta il comando passato e riporta la modifica in wallet di conseguenza.
    
    Comandi noti:
    : => definizione di variabile con valore / assegnazione di nuovo valore
    @ => definizione di tipo
    """
    # il primo carattere è obbligato
    if comando[0]=='@':
        # individuo il nome variabile, il comando e la definizione
        com_parts = split_def_command(comando[1:])
        # elaboro il comando in base allo specifico
        if com_parts:
            if   com_parts[1]=='@':
                #definizione di tipo
                if com_parts[0] in wallet.vars:
                    new_var = Variable(com_parts[0],Variable.DEF,
                                wallet.vars[com_parts[0]].cast(com_parts[2]))
                else:
                    new_var = Variable(com_parts[0],Variable.DEF,
                                typed_default_value(com_parts[2]))

                Log.DEBUG(  "interpreta_def - cmd '@', name: {}, "
                            "type: '{}', value: {}.",
                            com_parts[0], com_parts[2], new_var.value)

            elif com_parts[1]==':':
                new_var = variable_with_value(*com_parts, wallet=wallet)
            wallet.var(new_var)
        else:
            Log.WARNING("interpreta_def - unknown command: {}",comando)
    else:
        Log.WARNING("interpreta_def - invalid first char: {}",comando)

def calcola_variabili(stringa_variabili, wallet):
    """Prepara un dizionario di variabili.
    
    Include per prime le variabili predefinite,
    quindi aggiunge le variabili definite esternamente come parametri del comando,
    quindi scansiona la scheda per elaborare le definizioni."""
    global currentOperation

    currentOperation = " ... preparazione delle variabili "
    print(currentOperation, end="")

    ## variabili predefinite (il nome documento è già nel wallet)
    # Verifico -- name --
    Log.DEBUG("calcola_variabili - PRE {:15}={}",'name',wallet.var(rif='name'))
    if wallet.var(rif='name') == '':
        wallet.var(Variable('name', Variable.PRE, wallet.tmp.file_name))
        print(".",end="")
    # -- user --
    wallet.var(Variable('user', Variable.PRE, os.environ['username']))
    Log.DEBUG("calcola_variabili - PRE {:15}={}",'user',wallet.var(rif='user'))
    # -- date --
    wallet.var(Variable('date', Variable.PRE, date.today()))
    Log.DEBUG("calcola_variabili - PRE {:15}={:%Y%m%d}",'date',wallet.var(rif='date'))
    # -- hour --
    wallet.var(Variable('hour', Variable.PRE, datetime.now().time()))
    Log.DEBUG("calcola_variabili - PRE {:15}={:%H%M%S%f}",'hour',wallet.var(rif='hour'))
    
    ## variabili esterne (il nome documento è già nel wallet)
    for vexval in stringa_variabili :
        print(".",end="")
        if "=" in vexval:
            # solo il primo carattere '=' serve per lo split
            vexlist=vexval.split("=")
            vex=vexlist.pop(0)
            val="=".join(vexlist)
        else:
            vex=vexval
            val=None
        Log.DEBUG("calcola_variabili - EXT {:15}={}",vex,val)
        wallet.var(Variable(vex,Variable.EXT,val))
    
    ## lettura dati scheda
    print(" ",end="")
    # elaboro tutti i comandi della sezione "definition"
    for cmd in wallet.tmp.definition_section():
        print(".",end="")
        interpreta_def(cmd,wallet)

    print(" OK ")

def partizionamento(testo: str, regexp: re.compile("")) -> "[ parts ... ]":
    """Suddivide il testo in token, in base alla regexp.
    
    Restituisce un array di tokens.
    Cerca la regexp, se non la trova restituisce il testo in forma
    di array con un solo elemento,
    altrimenti restituisce un array con i seguenti tokens:
    - il testo prima della corrispondenza regexp,
    - la corrispondenza di regexp, in forma di dict (vedi oltre)
    - più parti risultanti dall'esecuzione ricorsiva sul rimanente testo
    
    Il testo corrispondente alla regexp viene elaborato e restituito
    in forma di dict contenente i named-group della regexp, per es:
        regexp: /(?P<prefisso>.*)-(?P<corpo>.*)-(?P<suffisso>.*)/
    restituirà nel dict i campi 'prefisso', 'corpo', 'suffisso'.
    """
    risre=regexp.search(testo)
    ret_val=[]
    if risre==None :
        ret_val.append(testo)
        Log.DEBUG("partizionamento - parti:[{}] - end",testo)
    else:
        # testo prima
        ret_val.append(testo[:risre.start()])
        # testo regexp
        token=risre.groupdict()
        if token['length'] == None:
            token['length'] = risre.end()-risre.start()
        else:
            token['length'] = int(token['length'])
        ret_val.append(token)
        Log.DEBUG("partizionamento - parti:[{}], [{}], ...",ret_val[0],ret_val[1])
        # testo dopo
        ret_val+=partizionamento(testo[risre.end():],regexp)
    return ret_val

def sostituzione_variabili(wallet: Wallet
                            , riga: str
                            ) -> "str, 'riga' elaborata":
    compilata = ""

    # divido la riga in testo e campi
    parti=partizionamento(riga, campo_regexp)

    # elaboro singolarmente ogni parte
    for parte in parti:
        # per ogni campo sostituisco il valore
        if isinstance(parte, dict) and 'nome' in parte:
            compilata+=wallet.sostituzione(parte)
        else:
            #solo testo, copio
            compilata+=parte
    return compilata

def compila(wallet):
    """Compilazione del testo con i valori delle variabili."""
    global currentOperation

    currentOperation = " ... compilazione della scheda "
    print(currentOperation, end="")
    Log.DEBUG("compila - INIZIO")

    # per ogni linea cerco i campi
    for l in wallet.tmp.document_section() :
        compilata=l
        # verifico il primo campo contenuto nella riga
        ris_regexp=campo_regexp.search(l)
        # elaboro se contiene almento un campo
        if ris_regexp==None :
            # nessun campo, riga invariata
            Log.DEBUG("compila - riga di sfondo   - {}",compilata)
        else:
            Log.DEBUG("compila - riga da compilare- {}",compilata)
            # la riga è da compilare
            compilata = sostituzione_variabili(wallet, l)
            print(".",end="")
            
        # accodo la linea in output
        wallet.out.accoda(compilata)

    Log.DEBUG("compila - FINE")
    print(" OK ")

def elabora(doc_name, scheda_file, doc_compilato, altri_parametri):
    """Esecuzione della completa elaborazione."""
    
    ## execution Wallet
    exe=Wallet()
    exe.var(Variable("name",Variable.PRE,doc_name))
    
    ## stream di input - caricato una volta per tutte in un oggetto consistente
    exe.createTemplate(scheda_file)
    
    ## preparazione variabili
    calcola_variabili(altri_parametri, exe)

    ## compilazione output
    exe.createOutput(doc_compilato)
    compila(exe)
    
    return exe

def apri_files(files_descr):
    """Apre tutti i files necessari.
    Se non è possibile restituisce un flag di validità falso."""

    validi=False
    fileIn=None
    fileOut=None
    
    fileIn_n=""
    if files_descr.dir :
        fileIn_n=files_descr.dir+os.sep
    if files_descr.template :
        fileIn_n+=files_descr.template
    else:
        if files_descr.name \
        and len(glob(fileIn_n+files_descr.name+".txt")) == 1 :
            fileIn_n+=files_descr.name+".txt"
        #elif len(glob(fileIn_n+"*.txt")) == 0 :
        #    # non ci sono file tra cui scegliere
        else:
            # file non definito, chiedo quale usare
            files_descr.name=menu(fileIn_n)
            if files_descr.name : fileIn_n+=files_descr.name+".txt"

    # apro fileIn
    if len(glob(fileIn_n)) == 1 :
        validi=True
        fileIn = open(fileIn_n, "r", encoding='utf-8')
    elif files_descr.template :
        print("\n Template indicato non trovato: {}\n".format(fileIn_n))
        exit(2)
 
    if validi :
        fileOut_n=""
        if files_descr.output :
            fileOut_n=files_descr.output+os.sep
        if files_descr.filename :
            fileOut_n+=files_descr.filename
        else:
            fileOut_n+=files_descr.name+"-"+date.today().strftime("%Y%m%d")+".prt"
        # apro fileOut
        if len(glob(fileOut_n)) == 1 :
            #chiedo se sovrascrivere o accodare
            #
            #           CONFERMA SOVRASCRIVERE
            #
            print("\n Documento compilato gia' esistente,\n")
            scelta = "S"
            scelta = input("\n Sovrascrivere, Accodare o annullare [S/a/*]? ")
            scelta=scelta.upper()
            if scelta=='' :
                scelta="S"
            if "S:::A".find(scelta)==-1 :
                scelta="X"
                validi=False
            #
            #
            #####################################
            if scelta=="S" :
                fileOut = open(fileOut_n, "w", encoding='utf-8')
            elif scelta=="A":
                fileOut = open(fileOut_n, "a", encoding='utf-8')
            else:
                fileOut = open(fileOut_n, "r", encoding='utf-8')
        else:
            fileOut = open(fileOut_n, "w", encoding='utf-8')
 
    return (fileIn, fileOut, validi)

def chiudi_files(fileIn, fileOut):
    """Chiude tutti i files necessari"""
    if fileIn  and not fileIn.closed  : fileIn.close()
    if fileOut and not fileOut.closed : fileOut.close()

##########################################################################################
if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                        description=desctxt,
                        epilog=doctxt)
    parser.add_argument('name', metavar='NAME', nargs='?',
                        help='Internal doc name. '
                        'If axists NAME.txt it will be the template file.')
    parser.add_argument('-d','--dir', metavar='DIR', 
                        help='sources directory.')
    parser.add_argument('-o','--output', metavar='DIR',
                        help='directory for compiled file.')
    parser.add_argument('-f','--filename', metavar='FILE',
                        help='prt compiled file name.')
    parser.add_argument('-t','--template', metavar='FILE',
                        help='txt source file name. '
                        'If it not exists a blank output is produced, '
                        'script ends with RC 2 (file not found). ')
    parser.add_argument('queue', metavar='var-def', nargs='*',
                        help='optionals variables definitions and values'
                        '\nin form: var-name=value')
    parser.add_argument('--guide', action='store_true',
                        help='print internal documentation.')
    parser.add_argument('-y','--overwrite', action='store_true',
                        help='If already exists output file,'
                        ' overwrite it without interaction.')
    parser.add_argument('-D','--debug', action='store_true',
                        help='Forces debug messages.')

    args = parser.parse_args()
    
    if args.debug:
        Log.raiseLevel(Log.LOG_DEBUG)

    # documentazione
    if args.guide:
        print(documentazione)
        exit(777)
    
    # if !ERRORS
    (template, document, validi) = apri_files(args)
    try:
        if validi :
            wallet=elabora(args.name, template, document, args.queue)
    except Exception as e:
        raise e
    finally:
        chiudi_files(template, document)
        if args.debug:
            print(*[err.encode("utf-8") for err in Log.err],sep="\n")
    
    
