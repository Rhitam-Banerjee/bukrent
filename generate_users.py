from app import create_app, db
from app.models.admin import Admin
from app.models.deliverer import Deliverer
from app.models.user import User
import xlsxwriter

app = create_app()
db.init_app(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/bukrent'

with app.app_context():
    iterator = 0
    workbook = xlsxwriter.Workbook("/home/ubuntu/bukrent/All_users.xlsx")
    worksheet = workbook.add_worksheet("All")
    worksheet.write(iterator, 0, "Mobile-Number/Username")
    worksheet.write(iterator, 1, "Password")
    worksheet.write(iterator, 2, "Database")
    admins = Admin.query.all()
    for x in admins:
        iterator += 1
        worksheet.write(iterator, 0, x.username)
        worksheet.write(iterator, 1, x.password)
        worksheet.write(iterator, 2, "Admin")
    users = User.query.all()
    for u in users:
        iterator += 1
        worksheet.write(iterator, 0, u.mobile_number)
        worksheet.write(iterator, 1, u.password)
        worksheet.write(iterator, 2, "Users")
    deliverers = Deliverer.query.all()
    for d in deliverers:
        iterator += 1
        worksheet.write(iterator, 0, d.username)
        worksheet.write(iterator, 1, d.password)
        worksheet.write(iterator, 3, "Deliverers")

    workbook.close()
