from django.utils.timezone import now

from booking_accounting.models import Report, AuditLog
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

def create_invoice(purpose,total,user,description):
    res=Invoice.objects.create(invoiceId=generate_activation_code("GIN"),purpose=purpose,invoice_total=total,
                               modified_by=user,created_by=user,description=description)
    return res


from datetime import date, timedelta


def last_thirtydays(d):
    end_dt = date.today()
    start_dt = end_dt

    # difference between current and previous date
    delta = timedelta(days=d)
    start_dt -= delta
    ss = start_dt.strftime("%Y-%m-%d")
    ee = end_dt.strftime("%Y-%m-%d")
    s = f"{ss} 00:00:00"
    e = f"{ee} 23:59:59"
    return {"start_dt": s, "end_dt": e}

def create_report(s,e,report_type, total,data):
    obj=Report.objects.filter(start=s, end=e, report_type=report_type)
    if obj.exists():
        res=obj[0]
        res.total=total
        res.data = data
        res.save()
        return res
    else:
        res=Report.objects.create(total=total, data=data, start=s, end=e, report_type=report_type)
        return res
def audit_log(name,desc,user):
    AuditLog.objects.create(audit_type=name, audit_description=desc, created_by=user)
    return True