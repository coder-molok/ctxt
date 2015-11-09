# ctxt

## DEVELOPERS REFERENCE

  CTXT get a template file in input, compile it depending on included
  directives and produce a document file (text plain) in output.

  The simplest directive is text, text is copyed from input to output. 

  The second simpler directive is a placeholder, it resides in text
  and it marks a space in the text (a number of chars) that will be 
  substituted in output with some other chars from some processing.

  Other and more complex directives stays in DEFINITION SECTION.
  
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
