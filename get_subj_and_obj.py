# Tomas's script!!

def get_children_with_dep(token, dep):
    return [child for child in token.children if child.dep_ == dep]

def only(lst):
    if len(lst) == 0:
        raise Exception("List is empty.")
    if len(lst) > 1:
        raise Exception(f"List has more than one element: {lst}")
    return lst[0]

def only_safe(lst):
    if len(lst) != 1:
        return None
    return lst[0]

def get_subject(token):
    nsubj_list = get_children_with_dep(token, "nsubj")
    if nsubj_list:
        nsubj = only_safe(nsubj_list)
        if token.dep_ == "relcl" and nsubj and nsubj.tag_ in {"WP", "WDT"}:
            return token.head
        return nsubj
    if token.dep_ == "xcomp":
        parent_dobj_list = get_children_with_dep(token.head, "dobj")
        if parent_dobj_list:
            return only_safe(parent_dobj_list)
        if token.head.dep_ == "acomp":
            return get_subject(token.head.head)
        return get_subject(token.head)
    if token.dep_ in {"advcl", "conj"}:
       return get_subject(token.head)
    return None

def get_simple_subject(token):
    nsubj_list = get_children_with_dep(token, "nsubj")
    if nsubj_list:
        return only_safe(nsubj_list)
    return None

def get_direct_object(token):
    dobj_list = get_children_with_dep(token, "dobj")
    if dobj_list:
        dobj = only_safe(dobj_list)
        if token.dep_ == "relcl" and dobj and dobj.tag_ in {"WP", "WDT"}:
            return token.head
        return dobj
    return None