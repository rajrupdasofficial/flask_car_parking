import eventlet
eventlet.monkey_patch()

from flask import Flask, jsonify
from flask_cors import CORS
from controller.auth.signup import signup_bp
from controller.auth.login import login_bp
from controller.vehiclecrud.createdetails import create_bp
from controller.profilecrud.readallusers import allusers_bp
from controller.sensors.sensorssim import ultrasonicsensor
from controller.sensors.iotconnect import iotcon_bp
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from controller.sensors.infratest import infratest_bp
from controller.sensors.magnetic import magnetic_sensor_bp
from controller.sensors.allsensorsdata import allsensors_bp
from controller.sensors.trainsensormodel import trainsensormodel_bp
from controller.sensors.predict import predict_bp
from controller.profilecrud.getuserprofilebyuserid import getuserbyid_bp
from controller.profilecrud.updateuserprofile import update_bp
from controller.profilecrud.deleteuser import deleteuserdata_bp
from controller.auth.forgotpassword import passwordreset_bp
from controller.vehiclecrud.updatedetails import updatevehicle_bp
from controller.vehiclecrud.deletebyid import deleteby_bp
from controller.bookingfacility.bookingcreate import createbooking_bp
from controller.bookingfacility.getbookingbyid import getbookingbyid_bp
from controller.parkingspotops.createspot import createspot_bp
from controller.parkingspotops.getpsbyid import getpsbyid_bp
from controller.parkingspotops.updateps import updateps_bp
from controller.parkingspotops.spotdetailscreate import createspotdetails_bp
from controller.parkingspotops.getspotdetailsbyid import getspotdetailsbyid_bp
from controller.parkingspotops.spotdetailsall import spotdetailsall_bp
from controller.parkingspotops.deletepsd import deletepsd_bp
from controller.parkingspotops.updatepsd import updatepsd_bp
from flask_socketio import SocketIO,emit
from controller.parkingops.parkingopsws import register_socket_events
from controller.parkingops.cardetection import cardetectionfunc
from controller.parkingops.spotops import spotresops
from controller.parkingops.totalparkingbackend import totalparkingsol
from controller.parkingops.cardtumgs import cardtumgf
from controller.bookingfacility.updatebooking import updatebooking_bp
from controller.notificationws.notificationws import bookingconfchannel
from controller.wallet.walletcreate import walletcreate_bp
from controller.wallet.getallwallet import getwallet_bp
from controller.wallet.getwalletbyid import getwalletid_bp
from controller.wallet.updatewallet import updatewallet_bp
from controller.wallet.deletewallet import deletewallet_bp
from controller.faq.faqgetall import faqgetall_bp
from controller.faq.faqcreate import faqcreate_bp
from controller.faq.faqgetbyid import faqgetbyid_bp
from controller.faq.deletefaq import deletefaq_bp
from controller.contactops.createcontact import createcontact_bp
from controller.contactops.getallcontactlist import getallcontactlist_bp
from controller.contactops.getcontactbyid import getcontactbyid_bp
from controller.parkinghistoryops.parkinghistory import parkinghistory_bp
from controller.parkinghistoryops.getallparkinghistory import getallparkinghistory_bp
from controller.parkinghistoryops.phbyid import phbyid_bp
from controller.parkinghistoryops.deleteph import phdel_bp
from controller.parkingops.mainoperations import mainops
from controller.wallet.initwalletrecharge import initwalletrecharge_bp
from controller.razorpaycruds.verifypayment import verifypayment_bp
from controller.wallet.expenses import expenses_bp
from controller.helpandsupport.createhelpandsupport import createhps_bp
from controller.helpandsupport.getallhelpandsupport import getallhelp_bp
from controller.helpandsupport.hsdbyid import hsdbyid_bp
from controller.wallet.wrechhisforsu import wrechhisforsu_bp
from controller.helpandsupport.userspecifichs import userspecifichs_bp
from controller.vehiclecrud.getvbyuid import getvbyid_bp
from controller.survery.surveycreate import surveycreate_bp
from controller.survery.surveylist import getallsurvey_bp
from controller.survery.getsurveybyid import getsurveybyid_bp
from controller.survery.deletesurvey import deletesurvey_bp
from controller.survery.changestatus import feedbackstatus_bp
from controller.auth.admin.adminsignup import adminsignup_bp
from controller.auth.admin.adminlogin import adminlogin_bp
from controller.auth.admin.adminforgotpassword import adminpasswordreset_bp
from controller.searchapi.searchdata import search_bp
from controller.helpandsupport.fetchhsadmin import fetchhsadmin_bp
from controller.bookingfacility.fetchbookingsbyadmin import fetchbokingbyid_bp
# from controller.fasttagops.fasttagscan import fasttagbproute_bp
from controller.revenueops.dailyrevenue import today_revenue_blueprint
from controller.revenueops.monthlyrevenue import monthly_revenue_blueprint
from controller.revenueops.yearlyrevenue import yearlyrevenue_blueprint
from controller.revenueops.totalrevenue import total_revenue_bp
from controller.locationops.locationcreate import location_create_bp

"""fetch details by adminid"""
from controller.wallet.fetchwasadmin import fetchwasadmin_bp
from controller.survery.fetchsuasadmin import fetchsuasadmin_bp
from controller.vehiclecrud.fetchvasadmin import fetchvehicleadmin_bp
from controller.contactops.fetchcasadmin import fetchcasadmin_bp
# from controller.parkingops.parkingops import parking_bp

app = Flask(__name__)

# Enable CORS for all routes and methods
CORS(app, resources={r"/*": {
    "origins": "*",  # Change '*' to specific origins in production
    "allow_headers": ["Content-Type", "Authorization"],
    "methods": ["GET", "POST", "OPTIONS"]
}})


# Initialize the Limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["20000 per day", "5000 per hour"]  # Adjust limits as needed
)

socketio = SocketIO(app, cors_allowed_origins="*")

app.register_blueprint(signup_bp)
app.register_blueprint(login_bp)
app.register_blueprint(create_bp)
app.register_blueprint(allusers_bp)
app.register_blueprint(ultrasonicsensor)
app.register_blueprint(iotcon_bp)
app.register_blueprint(infratest_bp)
app.register_blueprint(magnetic_sensor_bp)
app.register_blueprint(allsensors_bp)
app.register_blueprint(trainsensormodel_bp)
app.register_blueprint(predict_bp)
app.register_blueprint(getuserbyid_bp)
app.register_blueprint(update_bp)
app.register_blueprint(deleteuserdata_bp)
app.register_blueprint(passwordreset_bp)
app.register_blueprint(updatevehicle_bp)
app.register_blueprint(deleteby_bp)
app.register_blueprint(createbooking_bp)
app.register_blueprint(getbookingbyid_bp)
app.register_blueprint(createspot_bp)
app.register_blueprint(getpsbyid_bp)
app.register_blueprint(updateps_bp)
app.register_blueprint(createspotdetails_bp)
app.register_blueprint(getspotdetailsbyid_bp)
app.register_blueprint(spotdetailsall_bp)
app.register_blueprint(deletepsd_bp)
app.register_blueprint(updatepsd_bp)
app.register_blueprint(updatebooking_bp)
app.register_blueprint(walletcreate_bp)
app.register_blueprint(getwallet_bp)
app.register_blueprint(getwalletid_bp)
app.register_blueprint(updatewallet_bp)
app.register_blueprint(deletewallet_bp)
app.register_blueprint(faqgetall_bp)
app.register_blueprint(faqcreate_bp)
app.register_blueprint(faqgetbyid_bp)
app.register_blueprint(deletefaq_bp)
app.register_blueprint(createcontact_bp)
app.register_blueprint(getallcontactlist_bp)
app.register_blueprint(getcontactbyid_bp)
app.register_blueprint(parkinghistory_bp)
app.register_blueprint(getallparkinghistory_bp)
app.register_blueprint(phbyid_bp)
app.register_blueprint(phdel_bp)
app.register_blueprint(initwalletrecharge_bp)
app.register_blueprint(verifypayment_bp)
app.register_blueprint(expenses_bp)
app.register_blueprint(createhps_bp)
app.register_blueprint(getallhelp_bp)
app.register_blueprint(hsdbyid_bp)
app.register_blueprint(wrechhisforsu_bp)
app.register_blueprint(userspecifichs_bp)
app.register_blueprint(getvbyid_bp)
app.register_blueprint(surveycreate_bp)
app.register_blueprint(getallsurvey_bp)
app.register_blueprint(getsurveybyid_bp)
app.register_blueprint(feedbackstatus_bp)
app.register_blueprint(deletesurvey_bp)
app.register_blueprint(search_bp)
app.register_blueprint(fetchhsadmin_bp)
app.register_blueprint(fetchbokingbyid_bp)
# app.register_blueprint(fasttagbproute_bp)
app.register_blueprint(today_revenue_blueprint)
app.register_blueprint(monthly_revenue_blueprint)
app.register_blueprint(yearlyrevenue_blueprint)
app.register_blueprint(total_revenue_bp)
app.register_blueprint(location_create_bp)

"""admin route groups"""
app.register_blueprint(adminsignup_bp)
app.register_blueprint(adminlogin_bp)
app.register_blueprint(adminpasswordreset_bp)
app.register_blueprint(fetchwasadmin_bp)
app.register_blueprint(fetchsuasadmin_bp)
app.register_blueprint(fetchvehicleadmin_bp)
app.register_blueprint(fetchcasadmin_bp)


@app.route("/", methods=['GET'])
def index():
    return jsonify({"message": "App access not allowed"})

# websocket events register
register_socket_events(socketio)
cardetectionfunc(socketio)
spotresops(socketio)
totalparkingsol(socketio)
cardtumgf(socketio)
bookingconfchannel(socketio)
mainops(socketio)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)  # Run the app with SocketIO support.
