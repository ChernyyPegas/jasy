#
# Jasy - JavaScript Tooling Refined
# Copyright 2010 Sebastian Werner
#

import logging, re, copy
from jasy.parser.Node import Node

class TranslationError(Exception):
    pass

class Translation:
    def __init__(self, table=None):
        self.__table = table
        

    def patch(self, node):
        self.__recurser(node)
    
    
    
    __methods = ("tr", "trc", "trn")
    __params = {
      "tr" : ["text"],
      "trn" : ["textSingular", "textPlural"],
      "trc" : ["textHint", "text"]
    }
    
    
    replacer = re.compile("({[a-zA-Z0-9_\.]+})")
    number = re.compile("[0-9]+")
    
    pluralNumber = 1
    

    def __rebuild(self, value, mapper):
        result = []
        splits = self.replacer.split(value)
        pair = Node(None, "plus")

        for entry in splits:
            if entry == "":
                continue
                
            if len(pair) == 2:
                newPair = Node(None, "plus")
                newPair.append(pair)
                pair = newPair

            if self.replacer.match(entry):
                pos = int(entry[1:-1])
                
                # Items might be added multiple times. Copy to protect original.
                try:
                    repl = mapper[pos]
                except KeyError:
                    raise TranslationError("Invalid positional value: %s in %s" % (entry, value))
                
                pair.append(copy.deepcopy(mapper[pos]))
                
            else:
                child = Node(None, "string")
                child.value = entry
                pair.append(child)
                
        return pair

    
    def __recurser(self, node):
        if node.type == "call":
            funcName = None
            
            if node[0].type == "identifier":
                funcName = node[0].value
            elif node[0].type == "dot" and node[0][1].type == "identifier":
                funcName = node[0][1].value
            
            if funcName in self.__methods:
                params = node[1]
                table = self.__table

                # Verify param types
                if params[0].type != "string":
                    logging.warn("Expecting translation string to be type string: %s at line %s" % (params[0].type, params[0].line))
                    
                if (funcName == "trn" or funcName == "trc") and params[1].type != "string":
                    logging.warn("Expecting translation string to be type string: %s at line %s" % (params[1].type, params[1].line))


                # Signature tr(msg, arg1, arg2, ...)
                if funcName == "tr":
                    key = params[0].value
                    if key in table:
                        params[0].value = table[key]
                        
                    if len(params) == 1:
                        # Replace the whole call with the string
                        node.parent.replace(node, params[0])
                        
                    else:
                        # Split string into plus-expression
                        mapper = { pos: value for pos, value in enumerate(params[1:]) }
                        try:
                            pair = self.__rebuild(params[0].value, mapper)
                        except TranslationError as ex:
                            raise TranslationError("Invalid translation usage in line %s. %s" % (node.line, ex))
                        node.parent.replace(node, pair)
                        
                        
                # Signature trc(hint, msg, arg1, arg2, ...)
                elif funcName == "trc":
                    key = params[0].value
                    if key in table:
                        params[1].value = table[key]

                    if len(params) == 2:
                        # Replace the whole call with the string
                        node.parent.replace(node, params[1])

                    else:
                        # Split string into plus-expression
                        mapper = { pos: value for pos, value in enumerate(params[2:]) }
                        try:
                            pair = self.__rebuild(params[1].value, mapper)
                        except TranslationError as ex:
                            raise TranslationError("Invalid translation usage in line %s. %s" % (node.line, ex))
                        node.parent.replace(node, pair)                        
                        
                        
                # Signature trn(msg, msg2, int, arg1, arg2, ...)
                elif funcName == "trn":
                    keySingular = params[0].value
                    if keySingular in table:
                        params[0].value = table[keySingular]

                    keyPlural = params[1].value
                    if keyPlural in table:
                        params[1].value = table[keyPlural]

                    # TODO: Multi plural support
                    
                    


                    #    # Replace the whole call with: int < 2 ? singularMessage : pluralMessage
                    #    
                    #    hook = Node(node.tokenizer, "hook")
                    #    hook.parenthesized = True
                    #    condition = Node(node.tokenizer, "le")
                    #    condition.append(params[2])
                    #    number = Node(node.tokenizer, "number")
                    #    number.value = 1
                    #    condition.append(number)
                    #    
                    #    hook.append(condition, "condition")
                    #    hook.append(params[1], "elsePart")
                    #    hook.append(params[0], "thenPart")
                    #    
                    #    node.parent.replace(node, hook)
                    #    





                    
                    
    
    
        for child in node:
            if child != None:
                self.__recurser(child)
                
                
                

        
       