def mandatory_inversion(best):
    return {"1_default":best,"2_inversion":"harte Gegenposition","3_resynthese":"survived/reframed","4_survival":"largely survived / partially reframed / significantly reframed / largely collapsed","5_residual":"neu bewerten"}
def check_closure_allowed(d): 
    if "torwart" not in d: raise Exception("Closure blocked")
    return True
