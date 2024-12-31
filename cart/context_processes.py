from . cart import Cart

#create context processor so out cart can work on all  of the site

def cart(request):
    #return the defoult  data from our Cart
    return {'cart':Cart(request)}

    

