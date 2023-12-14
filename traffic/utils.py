

def gen_seat(no):
    seats=[{"seat_number":x,"is_available":True} for x in range(1,no+1)]
    return seats