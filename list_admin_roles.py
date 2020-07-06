import requests
import json
import xlrd, xlwt
from xlutils.copy import copy as xl_copy

tenantName=""
roleNames={"Identity+Domain+Administrator":"Identity Domain Administrator","Security+Administrator":"Security Administrator","Application+Administrator":"Application Administrator","Audit+Administrator":"Audit Administrator","User+Administrator":"User Administrator"}
# roleName="Identity+Domain+Administrator"

IDCS_SERVICE_URL = ""
#IDCS_SERVICE_URL=https://<tenant_idcs_id>.identity.oraclecloud.com
BASE64ENCODED = ""
#BASE64ENCODED=base64 encoded string of "clientid:clientsecret"
def create_access_tokens():
        idcs_url = IDCS_SERVICE_URL+"/oauth2/v1/token"

        idcs_headers = {
                    "Authorization" : "Basic "+BASE64ENCODED,
                    "Content-Type" : "application/x-www-form-urlencoded;charset=UTF-8"
                        }

        idcs_data = {
                    "grant_type":"client_credentials",
                    "scope":"urn:opc:idm:__myscopes__"
                        }


        res = requests.post(idcs_url, headers = idcs_headers, data=idcs_data)

        json_data = json.loads(res.text)
        access_token = json_data['access_token']
        return access_token

access_token = create_access_tokens()

def get_approle_id(roleName):
        approle_url = IDCS_SERVICE_URL+"/admin/v1/AppRoles?filter=displayName+eq+%22"+roleName+"%22"
        approle_headers = {
                "Authorization": "Bearer "+access_token,
            "Content-Type" : "application/scim+json"
                }
        params = {
                "attributeSets":"all"
                }
        res = requests.get(approle_url, headers = approle_headers,params = params)
        res = json.loads(res._content.decode('utf-8'))
        for i in res["Resources"]:
            ID=i["id"]

        return ID

def get_allusers_with_approle(roleId):
        dict_users = dict()
        approle_url = IDCS_SERVICE_URL+"/admin/v1/Users?filter=urn:ietf:params:scim:schemas:oracle:idcs:extension:user:User:approles.value+eq+%22"+roleId+"%22&count=1000"
        approle_headers = {
                "Authorization": "Bearer "+access_token,
            "Content-Type" : "application/scim+json"
                }
        params = {
                "attributeSets":"all"
                }
        res = requests.get(approle_url, headers = approle_headers,params = params)
        res = json.loads(res._content.decode('utf-8'))
        for i in res["Resources"]:
            dict_users[i["displayName"]]=i["id"]
  
        return dict_users

def write_details_to_excel(names_list,filename,roleName):
    rb = xlrd.open_workbook(filename, formatting_info=True)
    wb = xl_copy(rb)
    sheet1=wb.add_sheet(roleName)
    row=1
    sheet1.write(0,0,"displayName")
    sheet1.write(0,1,"userId")
    for k,v in names_list.items(): 
        sheet1.write(row,0,k)
        sheet1.write(row,1,v)
        row += 1
    wb.save(filename)        

def output_in_excel(filename=tenantName+".xls"):
    book=xlwt.Workbook(encoding="utf-8")
    sheet=book.add_sheet("Monitored Roles")
    sheet.write(0,0,"Identity Domain Administrator")
    sheet.write(1,0,"Security Administrator")
    sheet.write(2,0,"Application Administrator")
    sheet.write(3,0,"Audit Administrator")
    sheet.write(4,0,"User Administrator")
    book.save(filename)
    for k,v in roleNames.items():
        role_id=get_approle_id(roleName=k)
        names_list=get_allusers_with_approle(roleId=role_id)
        write_details_to_excel(names_list=names_list,filename=filename,roleName=v)

output_in_excel()

