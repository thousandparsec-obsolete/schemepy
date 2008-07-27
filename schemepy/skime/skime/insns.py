# Don't edit this file. This is generated by iset_gen.py

from .ctx        import Context
from .proc       import Procedure
from .prim       import Primitive
from .types.pair import Pair
from .errors     import WrongArgType

TAG_CTRL_FLOW    = 1
TAG_CTX_SWITCH   = 2

def op_ret(ctx):
    pctx = ctx.parent
    retval = ctx.pop()
    pctx.push(retval)
    return pctx
    
def op_call(ctx):
    argc = get_param(ctx, 1)
    
    proc = ctx.pop()
    
    if isinstance(proc, Procedure):
        proc.check_arity(argc)
        nctx = Context(proc, proc.env.dup(), ctx)
    
        for i in range(proc.fixed_argc):
            nctx.env.assign_local(i, ctx.top(idx=argc-i))
        if proc.fixed_argc != proc.argc:
            rest = None
            for i in range(argc-proc.fixed_argc):
                rest = Pair(ctx.top(idx=i+1), rest)
            nctx.env.assign_local(proc.fixed_argc, rest)
        ctx.pop_n(argc)
    
    elif isinstance(proc, Primitive):
        proc.check_arity(argc)
        args = range(argc)
        for i in range(argc):
            args[i] = ctx.top(idx=argc-i)
        ctx.pop_n(argc)
        ctx.push(proc.call(ctx.vm, *args))
        nctx = ctx
    
    else:
        raise WrongArgType("Not a skime callable: %s" % proc)
    
    ctx.ip += 2
    return nctx
    
def op_tail_call(ctx):
    argc = get_param(ctx, 1)
    
    proc = ctx.pop()
    
    if isinstance(proc, Procedure):
        proc.check_arity(argc)
        nctx = Context(proc, proc.env.dup(), ctx.parent)
    
        for i in range(proc.fixed_argc):
            nctx.env.assign_local(i, ctx.top(idx=argc-i))
        if proc.fixed_argc != proc.argc:
            rest = None
            for i in range(argc-proc.fixed_argc):
                rest = Pair(ctx.top(idx=i+1), rest)
            nctx.env.assign_local(proc.fixed_argc, rest)
        ctx.pop_n(argc)
    
    elif isinstance(proc, Primitive):
        proc.check_arity(argc)
        args = range(argc)
        for i in range(argc):
            args[i] = ctx.top(idx=argc-i)
        ctx.pop_n(argc)
    
        nctx = ctx.parent
        nctx.push(proc.call(ctx.vm, *args))
    
    else:
        raise WrongArgType("Not a skime callable: %s" % proc)
    
    ctx.ip += 2
    return nctx
    
def op_pop(ctx):
    ctx.pop()
    ctx.ip += 1
    
def op_push_local(ctx):
    idx = get_param(ctx, 1)
    loc = ctx.env.read_local(idx)
    ctx.push(loc)
    ctx.ip += 2
    
def op_set_local(ctx):
    idx = get_param(ctx, 1)
    val = ctx.pop()
    ctx.env.assign_local(idx, val)
    ctx.ip += 2
    
def op_push_local_depth(ctx):
    depth = get_param(ctx, 1)
    idx = get_param(ctx, 2)
    
    penv = ctx.env
    while depth > 0:
        penv = penv.parent
        depth -= 1
    loc = penv.read_local(idx)
    ctx.push(loc)
    ctx.ip += 3
    
def op_set_local_depth(ctx):
    depth = get_param(ctx, 1)
    idx = get_param(ctx, 2)
    value = ctx.pop()
    
    penv = ctx.env
    while depth > 0:
        penv = penv.parent
        depth -= 1
    penv.assign_local(idx, value)
    ctx.ip += 3
    
def op_push_literal(ctx):
    idx = get_param(ctx, 1)
    lit = ctx.form.literals[idx]
    ctx.push(lit)
    ctx.ip += 2
    
def op_push_0(ctx):
    ctx.push(0)
    ctx.ip += 1
    
def op_push_1(ctx):
    ctx.push(1)
    ctx.ip += 1
    
def op_push_nil(ctx):
    ctx.push(None)
    ctx.ip += 1
    
def op_push_true(ctx):
    ctx.push(True)
    ctx.ip += 1
    
def op_push_false(ctx):
    ctx.push(False)
    ctx.ip += 1
    
def op_dup(ctx):
    ctx.push(ctx.top())
    ctx.ip += 1
    
def op_goto(ctx):
    ip = get_param(ctx, 1)
    ctx.ip = ip
    
def op_goto_if_not_false(ctx):
    ip = get_param(ctx, 1)
    cond = ctx.pop()
    if cond is not False:
        ctx.ip = ip
    else:
        ctx.ip += 2
    
def op_goto_if_false(ctx):
    ip = get_param(ctx, 1)
    cond = ctx.pop()
    if cond is False:
        ctx.ip = ip
    else:
        ctx.ip += 2
    
def op_fix_lexical(ctx):
    proc = ctx.top()
    proc.lexical_parent = ctx.env
    ctx.ip += 1
    
def op_fix_lexical_pop(ctx):
    proc = ctx.pop()
    proc.lexical_parent = ctx.env
    ctx.ip += 1
    
def op_fix_lexical_depth(ctx):
    depth = get_param(ctx, 1)
    proc = ctx.top()
    env = ctx.env
    while depth > 0:
        env = env.parent
        depth -= 1
    proc.lexical_parent = env
    ctx.ip += 2
    
def op_dynamic_eval(ctx):
    dc = ctx.pop()
    form = dc.form
    env = dc.lexical_parent
    ctx.push(form.eval(env, ctx.vm))
    ctx.ip += 1
    
def op_dynamic_set_local(ctx):
    idx = get_param(ctx, 1)
    sym_closure = ctx.pop()
    value = ctx.pop()
    
    env = sym_closure.lexical_parent
    env.assign_local(idx, value)
    ctx.ip += 2
    
def op_dynamic_set_local_depth(ctx):
    depth = get_param(ctx, 1)
    idx = get_param(ctx, 2)
    sym_closure = ctx.pop()
    value = ctx.pop()
    
    env = sym_closure.lexical_parent
    while depth > 0:
        env = env.parent
        depth -= 1
    env.assign_local(idx, value)
    ctx.ip += 3
    

INSN_ACTION = [
    op_ret,
    op_call,
    op_tail_call,
    op_pop,
    op_push_local,
    op_set_local,
    op_push_local_depth,
    op_set_local_depth,
    op_push_literal,
    op_push_0,
    op_push_1,
    op_push_nil,
    op_push_true,
    op_push_false,
    op_dup,
    op_goto,
    op_goto_if_not_false,
    op_goto_if_false,
    op_fix_lexical,
    op_fix_lexical_pop,
    op_fix_lexical_depth,
    op_dynamic_eval,
    op_dynamic_set_local,
    op_dynamic_set_local_depth
]


INSN_TAGS = [
    TAG_CTX_SWITCH | TAG_CTRL_FLOW,
    TAG_CTX_SWITCH | TAG_CTRL_FLOW,
    TAG_CTX_SWITCH | TAG_CTRL_FLOW,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    TAG_CTRL_FLOW,
    TAG_CTRL_FLOW,
    TAG_CTRL_FLOW,
    0,
    0,
    0,
    0,
    0,
    0
]



def has_tag(opcode, tag):
    return INSN_TAGS[opcode] & tag == tag

def get_param(ctx, n):
    return ctx.bytecode[ctx.ip+n]

def run(ctx):
    while ctx.ip < len(ctx.bytecode):
        opcode = ctx.bytecode[ctx.ip]
        nctx = INSN_ACTION[opcode](ctx)
        if has_tag(opcode, TAG_CTX_SWITCH):
            ctx = nctx
