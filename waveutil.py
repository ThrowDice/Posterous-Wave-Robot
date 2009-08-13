import logging

def annotationTohtml(content,annotations):
    html = ''.join(list(convert(content,annotations)))
    html = html.replace('\n',"<br/>")
    return html
            
def convert(content,annotations):
    content = enumerate(content)
    start_idx = {}
    end_idx = {} 
    for annotation in annotations:
        start_idx[annotation.range.start] = []
        end_idx[annotation.range.end] = []
    for annotation in annotations:
        start_idx[annotation.range.start].append(annotation)
        end_idx[annotation.range.end].append(annotation)
    for idx,char in content:
        if idx in start_idx:
            for annotation in start_idx[idx]:
                start_m = start_markup(annotation)
                if start_m:
                    yield start_m
        elif idx in end_idx:
            for annotation in end_idx[idx]:
                end_m = end_markup(annotation)
                if end_m:
                    yield end_m
        yield char
        #starts.append(annotation.range.start)
        #if annotation.name=="link/manual":
            
def end_markup(annotation):
    markup = ""
    name = annotation.name
    value = annotation.value
    #logging.debug(name)
    if name == "link/manual":
        markup = "</a>"
    elif name == "style/fontWeight" or name == "style/fontStyle" or \
    name == "style/color" or name=="style/backgroundColor" or name=="style/textDecoration"\
        or name == "style/fontFamily" or name=="style/fontSize":
        markup = "</span>"
    else:
        markup = ""
    return markup

def start_markup(annotation):
    markup = ""
    name = annotation.name
    value = annotation.value
    #logging.debug(name)
    if name == "link/manual":
        markup = '<a href="%s">' % value
        #logging.debug(markup)
    elif name == "style/fontWeight":
        markup = '<span style="font-weight: %s;">' % value
    elif name == "style/fontStyle":
        markup = '<span style="font-style: %s;">' % value
    elif name == "style/color":
        markup = '<span style="color: %s;">' % value
    elif name == "style/backgroundColor":
        markup = '<span style="background-color: %s;">' % value
    elif name == "style/textDecoration":
        markup = '<span style="text-decoration: %s;">' % value
    elif name == "style/fontFamily":
        markup = '<span style="font-family: %s;">' % value 
    elif name == "style/fontSize":
        markup = '<span style="font-size: %s;">' % value
    else:
        markup = ""
    return markup

        
      
#def markup(content,annotation):
#    for inx,chr in enumerate(content):
#        if inx==range.start:
#            yield "<a href='%s'>" % value
#        elif inx==range.end:
#            yield "</a>"
#        yield inx
#        yield chr
#    
#def list_to_string(content):
#    logging.debug(content)
#    c = u""
#    for ch in content:
#        #logging.info(type(ch))
#        if type(ch) is not IntType:
#            #logging.info(ch)
#            c =c+ch
#    return c
