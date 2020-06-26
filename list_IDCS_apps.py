import requests
import json
import xlrd, xlwt
from xlutils.copy import copy as xl_copy


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

def get_to_be_deactivated_oAuth_apps(deactivated_user_id_list):
        oAuth_app_ids = list()
        approle_url = IDCS_SERVICE_URL+"/admin/v1/Apps?count=1000"
        approle_headers = {
                "Authorization": "Bearer "+access_token,
            "Content-Type" : "application/scim+json"
                }
        params = {
                "attributeSets":"all"
                }
        res = requests.get(approle_url, headers = approle_headers,params = params)
        res = json.loads(res._content.decode('utf-8'))
        
        for user in deactivated_user_id_list:
                for i in res["Resources"]:
                        if i["idcsCreatedBy"]["value"]==user:
                                oAuth_app_ids.append(i["id"])

        book=xlwt.Workbook(encoding="utf-8")
        sheet=book.add_sheet("Apps data")
        sheet.write(0,0,"clientType")
        sheet.write(0,1,"id")
        sheet.write(0,2,"idcsCreatedBy")
        sheet.write(0,3,"displayName")
        sheet.write(0,4,"isManagedApp")
        sheet.write(0,5,"isOAuthClient")
        sheet.write(0,6,"active")
        count=len(res["Resources"])
        row=1
        for i in res["Resources"]:
                try:        
                        sheet.write(row,0,i["clientType"])
                except:
                        sheet.write(row,0,"null")
                sheet.write(row,1,i["id"])
                sheet.write(row,2,i["idcsCreatedBy"]["value"])
                sheet.write(row,3,i["displayName"])
                sheet.write(row,4,i["isManagedApp"])
                sheet.write(row,5,i["isOAuthClient"])
                sheet.write(row,6,i["active"])
                row +=1
        book.save("apps.xls")                
        return oAuth_app_ids
def get_user(id):

        users_url = IDCS_SERVICE_URL+"/admin/v1/Users/"+id
        users_headers = {
                "Authorization": "Bearer "+access_token,
            "Content-Type" : "application/scim+json"
                }
        params = {
                "attributeSets":"all"
                }
        res = requests.get(users_url, headers = users_headers,params = params)
        res = json.loads(res._content.decode('utf-8'))
        return res["userName"]

get_to_be_deactivated_oAuth_apps()
