from django.utils.timezone import now

from userapp.utils import generate_activation_code
from vehicle_driver_app.models import Approval, Invoice


def reset_bus_util(old_sch,seat_no):
    seats = old_sch.seats
    no =old_sch.seats_available
    for s in seats:
    # print(s)
        if s['seat_number'] == seat_no and s['is_available'] == False:
            s['is_available'] = True
    old_sch.seats = seats
    old_sch.seats_available = no + 1
    old_sch.save()
    return True

def create_invoice(purpose,total,user):
    res=Invoice.objects.create(invoiceId=generate_activation_code("GIN"),purpose=purpose,invoice_total=total,
                               modified_by=user,created_by=user)
    return res


