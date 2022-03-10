from flask import abort,flash
class err:
    def NotFound(target,comment:str):
        if len(target)==0:
            if comment:
                flash(comment)
            abort(404)

    def NotIn(items:list,group,comment:str):
        total= len(items)
        tick=0
        while tick<total-1: 
        #               Index[0] adjustment

            if items[tick] in group:
                tick+1
            else:
                if comment:
                    flash(comment)
                abort(422)
        
    def NotEqual(items:list,expected,comment:str):
        total= len(items)
        tick=0

        while tick<total-1: 
        #               Index[0] adjustment

            if items[tick] is expected:
                tick+1
            else:
                if comment:
                    flash(comment)
                abort(422)