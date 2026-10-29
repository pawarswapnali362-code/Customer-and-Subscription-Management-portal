from datetime import date, timedelta
from uuid import uuid4

PRODUCTS = [
    {"name": "Learning Platform", "code": "LEARN", "description": "Personalized learning journeys and course management.", "usage_unit": "learning sessions", "default_limit": 500, "active": True},
    {"name": "Assessment Platform", "code": "ASSESS", "description": "Create assessments and track learner outcomes.", "usage_unit": "assessments", "default_limit": 100, "active": True},
    {"name": "Analytics Platform", "code": "ANALYTICS", "description": "Insights and reporting for teams and organizations.", "usage_unit": "reports", "default_limit": 250, "active": True},
    {"name": "Administration Portal", "code": "ADMIN", "description": "Centralized team and access administration.", "usage_unit": "managed users", "default_limit": 100, "active": True},
    {"name": "AI Learning Assistant", "code": "AI-ASSIST", "description": "An AI-powered assistant for guided learning.", "usage_unit": "AI sessions", "default_limit": 300, "active": True},
]


def build_sample_data():
    today = date.today()
    products = [{"_id": f"prod-{i+1}", **p} for i, p in enumerate(PRODUCTS)]
    customers = [
        {"_id":"cus-b2c-1","name":"Aarav Mehta","type":"B2C","email":"aarav@example.in","phone":"+91 98765 43210","status":"Active","created_at":str(today-timedelta(days=180)),"notes":"Annual learner plan"},
        {"_id":"cus-b2c-2","name":"Diya Sharma","type":"B2C","email":"diya@example.in","phone":"+91 98765 43211","status":"Active","created_at":str(today-timedelta(days=125)),"notes":"Interested in assessment features"},
        {"_id":"cus-b2c-3","name":"Kabir Rao","type":"B2C","email":"kabir@example.in","phone":"+91 98765 43212","status":"Inactive","created_at":str(today-timedelta(days=90)),"notes":"Subscription paused"},
        {"_id":"cus-b2b-1","name":"Acme Learning Pvt Ltd","type":"B2B","email":"admin@acme.example.in","phone":"+91 22 4000 1000","contact_person":"Neha Kapoor","status":"Active","created_at":str(today-timedelta(days=210)),"notes":"Enterprise customer, Pune"},
        {"_id":"cus-b2b-2","name":"BrightPath Schools","type":"B2B","email":"it@brightpath.example.in","phone":"+91 80 4000 2000","contact_person":"Rohan Iyer","status":"Active","created_at":str(today-timedelta(days=150)),"notes":"School network"},
        {"_id":"cus-wl-1","name":"EduBridge Partners","type":"White-label Partner","email":"partners@edubridge.example.in","phone":"+91 11 4000 3000","status":"Active","created_at":str(today-timedelta(days=300)),"notes":"North region partner"},
        {"_id":"cus-wl-2","name":"LearnWorld Network","type":"White-label Partner","email":"ops@learnworld.example.in","phone":"+91 44 4000 4000","status":"Active","created_at":str(today-timedelta(days=260)),"notes":"South region partner"},
    ]
    users = [
        {"_id":"usr-1","customer_id":"cus-b2b-1","name":"Ishaan Verma","email":"ishaan@acme.example.in","status":"Active","created_at":str(today-timedelta(days=60))},
        {"_id":"usr-2","customer_id":"cus-b2b-1","name":"Mira Shah","email":"mira@acme.example.in","status":"Active","created_at":str(today-timedelta(days=48))},
        {"_id":"usr-3","customer_id":"cus-b2b-1","name":"Arjun Nair","email":"arjun@acme.example.in","status":"Inactive","created_at":str(today-timedelta(days=36))},
        {"_id":"usr-4","customer_id":"cus-b2b-2","name":"Ananya Das","email":"ananya@brightpath.example.in","status":"Active","created_at":str(today-timedelta(days=30))},
        {"_id":"usr-5","customer_id":"cus-b2b-2","name":"Vivaan Joshi","email":"vivaan@brightpath.example.in","status":"Active","created_at":str(today-timedelta(days=24))},
        {"_id":"usr-6","customer_id":"cus-b2b-2","name":"Saanvi Menon","email":"saanvi@brightpath.example.in","status":"Active","created_at":str(today-timedelta(days=18))},
    ]
    entitlements = [
        {"_id":"ent-1","customer_id":"cus-b2c-1","product_id":"prod-1","status":"Active","limit":500,"usage":182,"starts_at":str(today-timedelta(days=90)),"expires_at":str(today+timedelta(days=275)),"quantity":1},
        {"_id":"ent-2","customer_id":"cus-b2c-1","product_id":"prod-5","status":"Active","limit":300,"usage":95,"starts_at":str(today-timedelta(days=90)),"expires_at":str(today+timedelta(days=275)),"quantity":1},
        {"_id":"ent-3","customer_id":"cus-b2c-2","product_id":"prod-2","status":"Active","limit":100,"usage":47,"starts_at":str(today-timedelta(days=45)),"expires_at":str(today+timedelta(days=320)),"quantity":1},
        {"_id":"ent-4","customer_id":"cus-b2c-3","product_id":"prod-1","status":"Suspended","limit":500,"usage":205,"starts_at":str(today-timedelta(days=120)),"expires_at":str(today+timedelta(days=245)),"quantity":1},
        {"_id":"ent-5","customer_id":"cus-b2b-1","product_id":"prod-1","status":"Active","limit":5000,"usage":1240,"starts_at":str(today-timedelta(days=120)),"expires_at":str(today+timedelta(days=245)),"quantity":75},
        {"_id":"ent-6","customer_id":"cus-b2b-1","product_id":"prod-2","status":"Active","limit":1500,"usage":384,"starts_at":str(today-timedelta(days=120)),"expires_at":str(today+timedelta(days=245)),"quantity":75},
        {"_id":"ent-7","customer_id":"cus-b2b-2","product_id":"prod-1","status":"Active","limit":2500,"usage":618,"starts_at":str(today-timedelta(days=80)),"expires_at":str(today+timedelta(days=285)),"quantity":40},
        {"_id":"ent-8","customer_id":"cus-wl-1","product_id":"prod-1","status":"Active","limit":1000,"usage":0,"starts_at":str(today-timedelta(days=180)),"expires_at":str(today+timedelta(days=185)),"quantity":100,"purchased":100},
        {"_id":"ent-9","customer_id":"cus-wl-1","product_id":"prod-2","status":"Active","limit":500,"usage":0,"starts_at":str(today-timedelta(days=180)),"expires_at":str(today+timedelta(days=185)),"quantity":50,"purchased":50},
        {"_id":"ent-10","customer_id":"cus-wl-1","product_id":"prod-5","status":"Active","limit":250,"usage":0,"starts_at":str(today-timedelta(days=180)),"expires_at":str(today+timedelta(days=185)),"quantity":25,"purchased":25},
        {"_id":"ent-11","customer_id":"cus-wl-2","product_id":"prod-1","status":"Active","limit":600,"usage":0,"starts_at":str(today-timedelta(days=120)),"expires_at":str(today+timedelta(days=245)),"quantity":60,"purchased":60},
        {"_id":"ent-12","customer_id":"cus-wl-2","product_id":"prod-3","status":"Active","limit":180,"usage":0,"starts_at":str(today-timedelta(days=120)),"expires_at":str(today+timedelta(days=245)),"quantity":18,"purchased":18},
    ]
    activations = [
        {"_id":"act-1","customer_id":"cus-b2c-1","product_id":"prod-1","identifier":"aarav@example.in","status":"Active","activated_at":str(today-timedelta(days=89))},
        {"_id":"act-2","customer_id":"cus-b2b-1","product_id":"prod-1","user_id":"usr-1","identifier":"ishaan@acme.example.in","status":"Active","activated_at":str(today-timedelta(days=59))},
        {"_id":"act-3","customer_id":"cus-b2b-1","product_id":"prod-1","user_id":"usr-2","identifier":"mira@acme.example.in","status":"Active","activated_at":str(today-timedelta(days=47))},
        {"_id":"act-4","customer_id":"cus-b2b-2","product_id":"prod-1","user_id":"usr-4","identifier":"ananya@brightpath.example.in","status":"Active","activated_at":str(today-timedelta(days=29))},
    ]
    # Seeded active partner account activations stay within each purchased allocation.
    activations += [
        {"_id":f"act-wl-{i}","customer_id":"cus-wl-1","product_id":"prod-1","identifier":f"EDU-{i:03d}","status":"Active","activated_at":str(today-timedelta(days=30-i))} for i in range(1, 13)
    ]
    payments = [
        {"_id":"pay-1","customer_id":"cus-b2c-1","amount":11988,"currency":"INR","status":"Paid","method":"UPI","reference":"TXN-2601-001","payment_date":str(today-timedelta(days=90)),"due_date":str(today-timedelta(days=90)),"product_id":"prod-1"},
        {"_id":"pay-2","customer_id":"cus-b2c-1","amount":5999,"currency":"INR","status":"Paid","method":"Card","reference":"TXN-2601-002","payment_date":str(today-timedelta(days=90)),"due_date":str(today-timedelta(days=90)),"product_id":"prod-5"},
        {"_id":"pay-3","customer_id":"cus-b2c-2","amount":7999,"currency":"INR","status":"Pending","method":"Bank transfer","reference":"TXN-2602-003","payment_date":"","due_date":str(today+timedelta(days=7)),"product_id":"prod-2"},
        {"_id":"pay-4","customer_id":"cus-b2c-3","amount":11988,"currency":"INR","status":"Refunded","method":"UPI","reference":"TXN-2602-004","payment_date":str(today-timedelta(days=45)),"due_date":str(today-timedelta(days=45)),"product_id":"prod-1"},
        {"_id":"pay-5","customer_id":"cus-b2b-1","amount":280000,"currency":"INR","status":"Paid","method":"Bank transfer","reference":"TXN-2601-005","payment_date":str(today-timedelta(days=120)),"due_date":str(today-timedelta(days=120)),"product_id":"prod-1"},
        {"_id":"pay-6","customer_id":"cus-b2b-1","amount":85000,"currency":"INR","status":"Partially Paid","method":"Bank transfer","reference":"TXN-2603-006","payment_date":str(today-timedelta(days=30)),"due_date":str(today-timedelta(days=15)),"product_id":"prod-2"},
        {"_id":"pay-7","customer_id":"cus-b2b-2","amount":165000,"currency":"INR","status":"Pending","method":"Bank transfer","reference":"TXN-2602-007","payment_date":"","due_date":str(today+timedelta(days=15)),"product_id":"prod-1"},
        {"_id":"pay-8","customer_id":"cus-wl-1","amount":450000,"currency":"INR","status":"Paid","method":"Bank transfer","reference":"TXN-2601-008","payment_date":str(today-timedelta(days=180)),"due_date":str(today-timedelta(days=180)),"product_id":"prod-1"},
        {"_id":"pay-9","customer_id":"cus-wl-1","amount":125000,"currency":"INR","status":"Paid","method":"Bank transfer","reference":"TXN-2601-009","payment_date":str(today-timedelta(days=180)),"due_date":str(today-timedelta(days=180)),"product_id":"prod-2"},
        {"_id":"pay-10","customer_id":"cus-wl-2","amount":320000,"currency":"INR","status":"Failed","method":"Bank transfer","reference":"TXN-2603-010","payment_date":str(today-timedelta(days=5)),"due_date":str(today-timedelta(days=5)),"product_id":"prod-1"},
    ]
    issues = [
        {"_id":f"ISS-{i:04d}","customer_id":cust,"product_id":prod,"title":title,"description":desc,"severity":sev,"status":state,"reported_at":str(today-timedelta(days=days)),"resolved_at":str(today-timedelta(days=1)) if state == "Resolved" else "","assigned_to":assignee,"notes":""}
        for i,(cust,prod,title,desc,sev,state,days,assignee) in enumerate([
            ("cus-b2c-1","prod-1","Course progress not syncing","My completed lessons are not reflected.","Medium","Open",1,"Support Team"),
            ("cus-b2c-2","prod-2","Assessment page loading slowly","Assessment start takes longer than usual.","High","In Progress",3,"Priya S."),
            ("cus-b2c-3","prod-1","Unable to sign in","Password reset link expired.","High","Resolved",9,"Support Team"),
            ("cus-b2b-1","prod-1","Bulk user import validation","Some valid employee rows are rejected.","Critical","Open",0,"Engineering"),
            ("cus-b2b-1","prod-2","Monthly report export","Export is missing the latest cohort.","Medium","In Progress",4,"Rahul K."),
            ("cus-b2b-2","prod-1","Invite email delivery","Two staff members did not receive invites.","Low","Resolved",12,"Support Team"),
            ("cus-wl-1","prod-1","Partner branding update","Partner logo appears stretched on mobile.","Medium","Open",2,"Design Team"),
            ("cus-wl-1","prod-5","Assistant response feedback","Please review an inaccurate answer.","High","Resolved",14,"AI Team"),
            ("cus-wl-2","prod-3","Analytics dashboard access","Dashboard access denied to partner admin.","Critical","In Progress",1,"Engineering"),
        ],1)
    ]
    return {"products":products,"customers":customers,"users":users,"entitlements":entitlements,"activations":activations,"payments":payments,"issues":issues}
