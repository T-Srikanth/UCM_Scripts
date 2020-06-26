import oci
import xlrd, xlwt

#enter path to oci config file below
config_file_path = ""
config = oci.config.from_file(config_file_path)

IC=oci.identity.IdentityClient(config)

tenancy_name=IC.get_tenancy(tenancy_id=config["tenancy"]).data.name
admin_group_name="Administrators"

def get_admin_group_id(name=admin_group_name):
    admin_group_details=IC.list_groups(compartment_id=config["tenancy"],name=name).data
    for i in admin_group_details:
        admin_group_id=i.id
    return admin_group_id

def get_local_users():
    local_users=[]
    users_list=oci.pagination.list_call_get_all_results(IC.list_users,compartment_id=config["tenancy"]).data
    for user in users_list:
        if user.identity_provider_id==None:
            local_users.append(user)
    return local_users

def check_admin_group_membership(local_users):
    local_admins=[]
    for user in local_users:
        group_memberships=IC.list_user_group_memberships(compartment_id=config["tenancy"],user_id=user.id,group_id=admin_group_id).data
        if group_memberships != []:
            local_admins.append(user)
    return local_admins

def write_to_xls(local_admins):
    book=xlwt.Workbook(encoding="utf-8")
    sheet=book.add_sheet("OCI_LOCAL_USERS")
    sheet.write(0,0,"User name")
    sheet.write(0,1,"User Id")
    sheet.write(0,2,"Group name")
    row=1
    for detail in local_admins:
        sheet.write(row,0,detail.name)
        sheet.write(row,1,detail.id)
        sheet.write(row,2,admin_group_name)
        row +=1
    book.save(tenancy_name+"_LA.xls")

admin_group_id=get_admin_group_id()
local_users=get_local_users()
local_admins=check_admin_group_membership(local_users)
write_to_xls(local_admins)
