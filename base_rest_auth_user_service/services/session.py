import datetime

from odoo import fields
from odoo.http import db_monodb, request, root
from odoo.service import security

from odoo.addons.base_rest import restapi
from odoo.addons.component.core import Component
import logging


_logger = logging.getLogger(__name__)



def _rotate_session(httprequest):
    if httprequest.session.rotate:
        root.session_store.delete(httprequest.session)
        httprequest.session.sid = root.session_store.generate_key()
        if httprequest.session.uid:
            httprequest.session.session_token = security.compute_session_token(
                httprequest.session, request.env
            )
        httprequest.session.modified = True

class PartnerNewApiService(Component):
    _inherit = "base.rest.service"
    _name = "partner.new_api.service"
    _usage = "partner"
    _collection = "base_rest_auth_user_service.services"
    _description = """
        Partner New API Services
        Services developed with the new api provided by base_rest
    """

    @restapi.method(
        [(["/get_employee_details", "/"], "GET")],

        auth="user",
    )
    def get_employee_details(self):
        user_id = self.env.user
        employee = self.env['hr.employee'].search([('user_id', '=', user_id.id)])
        employees_dict = list()
        if employee:
            employees_dict.append({
                'id': employee.id,
                'name': employee.name,
                'job_title ': employee.job_title,
                'work_mobile': employee.mobile_phone,
                'work_email': employee.work_email,
                'work_phone': employee.work_phone,
                'department_name': employee.department_id.name,
                'manager_name': employee.parent_id.name,
                'pan': employee.employee_pan_no,
                'work_location': employee.work_location_id.name,
                'bank_acc_num': employee.bank_account_id.acc_number,
                'joining_date': employee.date_join,
                'nationality': employee.country_id.name,
                'identification_num': employee.identification_id,
                'passport_num': employee.passport_id,
                'gender': employee.gender,
                'age': employee.age,
                'marital_status': employee.marital,
                'salary_info': employee.total_ctc,
            })
            return {'status': 'Successfully logged in', 'employees_list': employees_dict}

    @restapi.method(
        [(["/get_dashboard_details", "/"], "GET")],

        auth="user",
    )
    def get_dashboard_details(self):
        user_id = self.env.user
        employee = self.env['hr.employee'].search([('user_id', '=', user_id.id)])
        employees_dict = list()
        if employee:
            employees_dict.append({
                'id': employee.id,
                'name': employee.name,
                'job_title ': employee.job_title,
                #'work_mobile': employee.mobile_phone,
                'work_email': employee.work_email,
                'employee_photo':employee.image_1920,
            })
            return {'status': 'Successfully logged in', 'employees_list': employees_dict}


    @restapi.method(
        [(["/get_attendance_status", "/"], "GET")],
        
        auth="user",
    )
    def get_attendance(self):
        user_id = self.env.user
        emp_id = self.env['hr.employee'].search([('user_id','=',user_id.id)])
        if emp_id:
            attendance = self.env['hr.attendance'].search([('check_out','=',False)])
            if attendance:

                return {"employe_name": emp_id.name,'attendance_status':'Marked'}
            else:
                return {"employe_name": emp_id.name,'attendance_status':'Not Marked'} 
        else:
            return {"error": 'No Employee associate with this user please contact to administrator'} 

    
    @restapi.method(
        [(["/mark_employee_checkout"], "POST")],
        
        auth="user",
    )
    def mark_employee_checkout(self):
        params = request.params
        user_id = self.env.user
        emp_id = self.env['hr.employee'].search([('user_id','=',user_id.id)])
        if emp_id:
            attendance = self.env['hr.attendance'].search([('check_out','=',False),('employee_id','=',emp_id.id)])
            if attendance:
                t_date= datetime.datetime.strptime(params.get('date'), "%Y-%m-%d %H:%M:%S")

                attendance.write({'check_out':t_date,
                                  'latitude_2': params.get('latitude_2'),
                                  'longitude_2': params.get('longitude_2'),
                                  'location_2': params.get('location_2'),
                                  })
                return {"employe_name": emp_id.name,'attendance_status':'Success checkout'}
            else:
                return {"employe_name": emp_id.name,'attendance_status':'First Mark attendance'} 
        else:
            return {"error": 'No Employee associate with this user please contact to administrator'} 

        
    
    
    @restapi.method(
        [(["/mark_employee_checkin"], "POST")],
        
        auth="user",
    )
    def mark_employee_checkin(self):
        params = request.params
        user_id = self.env.user
        emp_id = self.env['hr.employee'].search([('user_id','=',user_id.id)])
        if emp_id:
            attendance = self.env['hr.attendance'].search([('check_out','=',False),('employee_id','=',emp_id.id)])
            if not attendance:
                t_date= datetime.datetime.strptime(params.get('date'), "%Y-%m-%d %H:%M:%S")
                attendance_val={
                    'employee_id':emp_id.id,
                    'check_in':t_date,
                    'latitude_1':params.get('latitude_1'),
                    'longitude_1':params.get('longitude_1'),
                    'location_1':params.get('location_1'),
                }

                attendance=self.env['hr.attendance'].create(attendance_val)
                # attendance.write({'check_out':t_date})
                return {"employe_name": emp_id.name,'attendance_status':'Success Checkin'}
            else:
                return {"employe_name": emp_id.name,'attendance_status':'First Checkout attendance'} 
        else:
            return {"error": 'No Employee associate with this user please contact to administrator'} 

    @restapi.method(
        [(["/get_payslip_id"], "GET")],
        
        auth="user",
    )
    def get_payslip_id(self):
        params = request.params
        user_id = self.env.user
        emp_id = self.env['hr.employee'].search([('user_id','=',user_id.id)])
        if emp_id:
            payslip_date=params.get('year')+'-'+params.get('month')+"-"+'1'
            t_date= datetime.datetime.strptime(payslip_date, "%Y-%m-%d").date()
            payslip_id = self.env['hr.payslip'].search([('date_from','=',t_date),('employee_id','=',emp_id.id)])
            
            if payslip_id:
                base_url = self.env['ir.config_parameter'].search([('key','=','web.base.url')])
                url=base_url.value+"/my/payslip/download/"+str(payslip_id.id)
                return_val={
                    'employee_id':emp_id.id,
                    'employee_name':emp_id.name,
                    'payslip_id':payslip_id.id,
                    'status':'success',
                    'url':url
                }

                
                return return_val
            else:
                return_val={
                    'employee_id':emp_id.id,
                    'employee_name':emp_id.name,
                    'reason':'Contact Hr for entered month payslip',
                    
                    'status':'failed'
                }

                
                return return_val
                
        else:
            return {"error": 'No Employee associate with this user please contact to administrator'} 


    @restapi.method(
        [(["/get_leave_type"], "GET")],
        
        auth="user",
    )
    def get_leave_type(self):
        params = request.params
        user_id = self.env.user
        emp_id = self.env['hr.employee'].search([('user_id','=',user_id.id)])
        if emp_id:
            leave_type = self.env['hr.leave.type'].search(['|', ('requires_allocation', '=', 'no'), '&', ('has_valid_allocation', '=', True), '&', ('virtual_remaining_leaves', '>', 0), ('max_leaves', '>', '0')])
            if leave_type:
                leave_data=[]
                for leave in leave_type:
                    leave_data.append({
                        'id':leave.id,
                        'name':leave.name
                        })
                return_val={
                    'employee_id':emp_id.id,
                    'employee_name':emp_id.name,
                    'leave_types':leave_data,
                    'status':'success',
                    
                }

            else:
                return_val={
                    'employee_id':emp_id.id,
                    'employee_name':emp_id.name,
                    'reason':'Contact Hr for allocate you leave',
                    
                    'status':'failed'
                }

                
            return return_val
                
        else:
            return {"error": 'No Employee associate with this user please contact to administrator'} 
    @restapi.method(
        [(["/apply_for_leave"], "POST")],
        
        auth="user",
    )
    def apply_for_leave(self):
        params = request.params
        user_id = self.env.user
        emp_id = self.env['hr.employee'].search([('user_id','=',user_id.id)])
        if emp_id and "start_date" in params and "date_end" in params and "leave_id" in params:
            leave_id = self.env['hr.leave.type'].search([('id', '=', int(params['leave_id']))])
            if leave_id:
                start_date= datetime.datetime.strptime(params.get('start_date'), "%Y-%m-%d").date()
                date_end= datetime.datetime.strptime(params.get('date_end'), "%Y-%m-%d").date()
                leave_vals={
                    'employee_id':emp_id.id,
                    'request_date_from':start_date,
                    'request_date_to':date_end,
                    # 'leave_type_id':leave_id.id,
                    'holiday_status_id':leave_id.id

                    }
                if 'no_of_days' in params:
                    leave_vals['number_of_days']=params['no_of_days']
                
                if 'desc' in params:
                    leave_vals['name']=params['desc']
                
                leave=self.env['hr.leave'].create(leave_vals)
                return_val={
                    'employee_id':emp_id.id,
                    'employee_name':emp_id.name,
                    
                    'status':'success',
                    
                }

            else:
                return_val={
                    'employee_id':emp_id.id,
                    'employee_name':emp_id.name,
                    'reason':'Contact Hr',
                    
                    'status':'failed'
                }

                
            return return_val
                
        else:
            return {"error": 'No Employee associate with this user please contact to administrator'} 

    
    
    


class SessionAuthenticationService(Component):
    _inherit = "base.rest.service"
    _name = "session.authenticate.service"
    _usage = "auth"
    _collection = "session.rest.services"

    @restapi.method([(["/login"], "POST")], auth="public" , cors="*")
    def authenticate(self):
        params = request.params
        db_name = params.get("db", db_monodb())
        request.session.authenticate(db_name, params["login"], params["password"])
        result = request.env["ir.http"].session_info()
        # avoid to rotate the session outside of the scope of this method
        # to ensure that the session ID does not change after this method
        _rotate_session(request)
        request.session.rotate = False
        expiration = datetime.datetime.utcnow() + datetime.timedelta(days=90)
        result["session"] = {
            "sid": request.session.sid,
            "expires_at": fields.Datetime.to_string(expiration),

        }
        return result

    @restapi.method([(["/logout"], "POST")], auth="user" , cors="*")
    def logout(self):

        request.session.logout(keep_db=True)
        return {"message": "Successful logout"}

    @restapi.method([(["/reset_password"], "POST")], auth="user" , cors="*")
    def resetpassword(self):
        params = request.params
        user_id = self.env['res.users'].sudo().search([('login','=',params['email'])])
        user_id.sudo().write({'password':params['password']})

        #request.session.logout(keep_db=True)
        return {"message": "Successful reset password"}

    @restapi.method([(["/add_company"], "POST")], auth="user" , cors="*")
    def addcompany(self):
        params = request.params
        user_id = self.env['res.users'].sudo().search([('id','=',self.env.user.id)])
        company_id = self.env['res.partner'].sudo().create({
                'name':params['company_name'],
                'website':params['company_website'],
                'comment':params['industry'],
                'company_type':'company',
                'member_ids':[(4,user_id.id)]
            })

        
        return {"message": "Successful create company","company_id":company_id.id}


    @restapi.method([(["/add_company_with_user"], "POST")], auth="user" , cors="*")
    def addcompanywithuser(self):
        params = request.params
        user_id = self.env['res.users'].sudo().search([('login','=',params['email'])])
        if user_id:
            company_id = self.env['res.partner'].sudo().create({
                    'name':params['company_name'],
                    'website':params['company_website'],
                    'comment':params['industry'],
                    'company_type':'company',
                    'member_ids':[(4,user_id.id)]
                })
        else:
            return {"message": "User Not exist with provided email please check your email"}


        
        return {"message": "Successful create company with user","company_id":company_id.id}

    @restapi.method([(["/add_user_in_company"], "POST")], auth="user" , cors="*")
    def addcompanyuser(self):
        params = request.params
        user_id = self.env['res.users'].sudo().search([('id','=',self.env.user.id)])
        company_id = self.env['res.partner'].sudo().search([("id",'=',int(params['company_id']))])
        user_id = self.env['res.users'].sudo().search([('login','=',params['email'])])
        
        company_id.sudo().write({'member_ids':[(4,user_id.id)]})

        
        return {"message": "Successful Add Member"}

    @restapi.method([(["/delete_company"], "POST")], auth="user" , cors="*")
    def deletecompany(self):
        params = request.params
        company_id = self.env['res.partner'].sudo().search([("id",'=',int(params['company_id']))])
        
        company_id.sudo().unlink()
        
        return {"message": "Successful Remove Company"}

    @restapi.method([(["/unlink_member_from_company"], "POST")], auth="user" , cors="*")
    def unlinkmember(self):
        params = request.params
        user_id = self.env['res.users'].sudo().search([('login','=',params['email'])])
        
        company_id = self.env['res.partner'].sudo().search([("id",'=',int(params['company_id']))])
        
        company_id.sudo().write({
            'member_ids':[(3, user_id.id)]
            })
        
        return {"message": "Successful Unlink User from Company"}




    @restapi.method([(["/create_user_api"], "POST")], auth="user" , cors="*")
    def create_user(self):
        params = request.params
        user_id = self.env['res.users'].sudo()._create_user_from_template({
                'name':params['name'],
                'login':params['email'],
                'password':params['password']
            })
        #print("ggggggggggggggggggggggggggggggg",user_id)
        # group_e = self.env.ref('base.group_user', False)
        # group_e.sudo().write({'users': [(3, user_id.id)]})
        # group_e = self.env.ref('base.group_portal', False)
        # group_e.sudo().write({'users': [(4, user_id.id)]})
        course_ids = self.env['slide.channel'].sudo().search([('active','=',True)])
        course_list=[]
        user_id.partner_id.sudo().write({'email':user_id.login})
        for course in course_ids:
            if course.active:
                enrol_id=self.env['slide.channel.partner'].sudo().create({
                        'channel_id':course.id,
                        'partner_id':user_id.partner_id.id,

                    })
        if 'company_id' in params:
            company_id = self.env['res.partner'].sudo().browse(params['company_id'])
            company_id.sudo().write({'member_ids':[(4,user_id.id)]})
        return True


    @restapi.method([(["/get_active_course"], "POST")], auth="user" , cors="*")
    def active_course(self):
        params = request.params
        user_id = self.env['res.users'].sudo().search([('id','=',self.env.user.id)])
        
        course_ids = self.env['slide.channel.partner'].sudo().search([('partner_id','=',user_id.partner_id.id)])
        course_list=[]
        for course in course_ids:
            if course.channel_id.active:
                base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')

                image_url_1920 = base_url + '/web/image?' + 'model=slide.channel&id=' + str(course.channel_id.id) + '&field=image_1920'
                if course.channel_id.total_time !=0:
                    total_percentage = (course.channel_id.total_time / 100) * 100
                    total_time = round((60/100)*total_percentage,2)
                else:
                    total_time=0
                course_dict={
                    'course_name':course.channel_id.name,
                    'course_id':course.channel_id.id,
                    'description':course.channel_id.description,
                    'image':image_url_1920,
                    'steps':len(course.channel_id.slide_ids.ids),
                    'duration':total_time,
                    'progress':course.completion,
                    'is_complete':course.completed
                }
                flag_cert=0
                for lines in course.channel_id.slide_ids:
                    if lines.slide_type == 'certification':
                        flag_cert+=1
                        cetificate_id = self.env['survey.user_input'].sudo().search([('survey_id','=',lines.survey_id.id),('partner_id','=',user_id.partner_id.id)])
                        if cetificate_id:
                            course_dict['certificate_state']=cetificate_id.state
                            if cetificate_id.state in ['new','in_progress']:
                                course_dict['exam_status']="nottaken"
                            else:
                                if  cetificate_id.scoring_success:
                                    course_dict['exam_status']="passed"
                                else:
                                    course_dict['exam_status']="failed" 
                            course_dict['is_passed']=cetificate_id.scoring_success 
                            
                            course_dict['certificate_score']=cetificate_id.scoring_percentage
                        else:
                            course_dict['certificate_state']='Not attempt' 
                            course_dict['exam_status']="nottaken"
                            course_dict['certificate_score']=0
                            course_dict['is_passed']=False 
                            
                            
                if flag_cert ==0:
                    course_dict['certificate_state']='Not applicable' 
                    course_dict['certificate_score']=0
                    course_dict['is_passed']=False 
                    course_dict['exam_status']="nottaken"



                            
                tag_list=[]
                for tag in course.channel_id.tag_ids:
                    tag_dict={
                        'name':tag.name,
                        'id':tag.id
                    }
                    tag_list.append(tag_dict)
                course_dict['tags']=tag_list
                course_list.append(course_dict)
        return course_list

    @restapi.method([(["/get_child_users_progress_page"], "POST")], auth="user" , cors="*")
    def get_child_user_progress_page(self):
        params = request.params
        user_id = self.env['res.partner'].sudo().search([('id','=',params['company_id'])])
        child_data=[]
        overall_resillence_score=0
        attendance_overall=0
        overall_percent_score=0
        individual_score=0
        percent_score=0
        overall_attendance=0
        if params['search'] == 0:
            count_members=len(user_id.member_ids.ids)
            member_list=user_id.member_ids.ids
        else:
            user_ids = self.env['res.users'].sudo().search([('id','in',user_id.member_ids.ids),('name','ilike',params['args'])])
            count_members=len(user_ids.ids)
            member_list=user_ids.ids
        member_list.sort()
        filter_ids=member_list[params['start']:params['end']]
        member_ids = self.env['res.users'].sudo().browse(filter_ids)
        
        for user in member_ids:
            progress_ids = self.env['slide.channel.partner'].sudo().search([('partner_id','=',user.partner_id.id)])
            certificate_list=[]
            for progress in progress_ids:
                if progress.channel_id.active:
                    course_dict={
                    'course_name':progress.channel_id.name,
                    'course_id':progress.channel_id.id,
                    'last_update_date':str(progress.write_date),
                    'scoring_percentage':round(progress.completion),
                    'is_passed':progress.completed
                    }
                    flag_cert=0
                    for lines in progress.channel_id.slide_ids:
                        if lines.slide_type == 'certification':
                            flag_cert+=1
                            cetificate_id = self.env['survey.user_input'].sudo().search([('survey_id','=',lines.survey_id.id),('partner_id','=',user.partner_id.id)])
                            if cetificate_id:
                                # if cetificate_id.state in ['new','in_progress']:
                                #     course_dict['exam_status']="nottaken"
                                # else:
                                #     if cetificate_id.scoring_success:
                                #         course_dict['exam_status']="passed"
                                #     else:
                                #         course_dict['exam_status']="failed" 
                            
                                #course_dict['certificate_id']=cetificate_id.id 
                                course_dict['is_passed']=round(cetificate_id.scoring_success) 
                                
                                #course_dict['certificate_score']=cetificate_id.scoring_percentage
                            else:
                                #course_dict['exam_status']="nottaken"
                                #course_dict['certificate_id']=cetificate_id.id 
                                #course_dict['certificate_score']=0
                                course_dict['is_passed']=False 
                                
                    if flag_cert ==0:
                        #course_dict['exam_status']="nottaken"
                        #course_dict['certificate_score']=0
                        course_dict['is_passed']=False

                    certificate_list.append(course_dict)
            count=0
            progress_score=0
            courses_attended=0
            for certificate_data in certificate_list:
                progress_score=progress_score+certificate_data['scoring_percentage']
                if certificate_data['is_passed']==True:
                    count+=1
                if certificate_data['scoring_percentage']>0:
                    courses_attended+=1

            if len(certificate_list) != 0:
                individual_score=1000/len(certificate_list)
                percent_score=(count/len(certificate_list))*100
                overall_attendance=progress_score/len(certificate_list)

            final_score=individual_score*count
            #certificate_list['final_score']=int(final_score)
            complete_data={
            'user_name':user.name,
            'email':user.login,
            'attendance_score':round(overall_attendance),
            'resilience_score':round(final_score),
            'completion_score':round(percent_score),
            'total_no_courses':len(certificate_list),
            'courses_attended':courses_attended,
            'completed_courses':count,

            # 'data':certificate_list,

            }
            # overall_resillence_score=overall_resillence_score+round(final_score)
            # attendance_overall=attendance_overall+round(overall_attendance)
            # overall_percent_score=overall_percent_score+round(percent_score)
            child_data.append(complete_data)
        return {'data':child_data,'status':'success','no_of_users':count_members}
        

    @restapi.method([(["/get_child_users_progress"], "POST")], auth="user" , cors="*")
    def get_child_user_progress(self):
        params = request.params
        user_id = self.env['res.partner'].sudo().search([('id','=',params['company_id'])])
        child_data=[]
        overall_resillence_score=0
        attendance_overall=0
        overall_percent_score=0
        individual_score=0
        percent_score=0
        overall_attendance=0
        for user in user_id.member_ids:
            progress_ids = self.env['slide.channel.partner'].sudo().search([('partner_id','=',user.partner_id.id)])
            certificate_list=[]
            for progress in progress_ids:
                if progress.channel_id.active:
                    course_dict={
                    'course_name':progress.channel_id.name,
                    'course_id':progress.channel_id.id,
                    'last_update_date':str(progress.write_date),
                    'scoring_percentage':round(progress.completion),
                    'is_passed':progress.completed
                    }
                    flag_cert=0
                    for lines in progress.channel_id.slide_ids:
                        if lines.slide_type == 'certification':
                            flag_cert+=1
                            cetificate_id = self.env['survey.user_input'].sudo().search([('survey_id','=',lines.survey_id.id),('partner_id','=',user.partner_id.id)])
                            if cetificate_id:
                                course_dict['certificate_state']=cetificate_id.state
                                if cetificate_id.state in ['new','in_progress']:
                                    course_dict['exam_status']="nottaken"
                                else:
                                    if cetificate_id.scoring_success:
                                        course_dict['exam_status']="passed"
                                    else:
                                        course_dict['exam_status']="failed" 
                            
                                course_dict['certificate_id']=cetificate_id.id 
                                course_dict['is_passed']=round(cetificate_id.scoring_success) 
                                
                                course_dict['certificate_score']=cetificate_id.scoring_percentage
                            else:
                                course_dict['certificate_state']='Not attempt' 
                                course_dict['exam_status']="nottaken"
                                course_dict['certificate_id']=cetificate_id.id 
                                course_dict['certificate_score']=0
                                course_dict['is_passed']=False 
                                
                    if flag_cert ==0:
                        course_dict['certificate_state']='Not applicable' 
                        course_dict['exam_status']="nottaken"
                        course_dict['certificate_score']=0
                        course_dict['is_passed']=False

                    certificate_list.append(course_dict)
            count=0
            progress_score=0
            courses_attended=0
            for certificate_data in certificate_list:
                progress_score=progress_score+certificate_data['scoring_percentage']
                if certificate_data['is_passed']==True:
                    count+=1
                if certificate_data['scoring_percentage']>0:
                    courses_attended+=1

            if len(certificate_list) != 0:
                individual_score=1000/len(certificate_list)
                percent_score=(count/len(certificate_list))*100
                overall_attendance=progress_score/len(certificate_list)

            final_score=individual_score*count
            #certificate_list['final_score']=int(final_score)
            complete_data={
            'user_name':user.name,
            'attendance_score':round(overall_attendance),
            'resilience_score':round(final_score),
            'completion_score':round(percent_score),
            'total_no_courses':len(certificate_list),
            'courses_attended':courses_attended,
            'completed_courses':count,

            # 'data':certificate_list,

            }
            overall_resillence_score=overall_resillence_score+round(final_score)
            attendance_overall=attendance_overall+round(overall_attendance)
            overall_percent_score=overall_percent_score+round(percent_score)
            child_data.append(complete_data)
        if user_id.member_ids:
            overall_resillence_score=overall_resillence_score/len(user_id.member_ids.ids)
        
            attendance_overall=attendance_overall/len(user_id.member_ids.ids)
            overall_percent_score=overall_percent_score/len(user_id.member_ids.ids)


        user_id = self.env['res.partner'].sudo().search([('id','=',params['company_id'])])
        tag_ids=self.env['slide.channel.tag'].sudo().search([])
        tag_list=[]
        for tag in tag_ids:
            if tag.channel_ids:
            
                count=0
                for channel_id in tag.channel_ids:
                    if channel_id.active:
                        count+=1
                if count!=0:
                    score=1000/count
                else:
                    score=0
                count_total_score=0
                flag_cert=0
                channel_score=0
                for channel_id in tag.channel_ids:
                    if channel_id.active:
                        enrol_count=0
                        enrol_user_progree=0
                        if user_id.member_ids:
                            individual_score=round(score)/len(user_id.member_ids.ids)
                            for user in user_id.member_ids:
                                enroled_user=self.env['slide.channel.partner'].sudo().search([('partner_id','=',user.partner_id.id),('channel_id','=',channel_id.id)])
                                if enroled_user:
                                    enrol_count+=1
                                    for lines in enroled_user.channel_id.slide_ids:
                                        if lines.slide_type == 'certification':
                                            flag_cert+=1
                                            cetificate_id = self.env['survey.user_input'].sudo().search([('survey_id','=',lines.survey_id.id),('partner_id','=',user.partner_id.id)])
                                            if cetificate_id:
                                                if cetificate_id.scoring_success:
                                                    count_total_score+=1
                                                    break

                        #         enrol_user_progree=enrol_user_progree+enroled_user.completion
                        if enrol_count!=0:
                            every_user_score=score/enrol_count
                            total_score=0
                            channel_score=channel_score+(count_total_score*every_user_score)

                        #     for user in user_id.user_ids:
                        #         enroled_user=self.env['slide.channel.partner'].sudo().search([('partner_id','=',user.partner_id.id),('channel_id','=',channel_id.id)])
                        #         if enroled_user:
                        #             total_score=total_score+(enroled_user.completion/100)*every_user_score
                        #     channel_total_score=channel_total_score+total_score
                # if channel_score !=0:
                tag_dict={
                'tag_name':tag.name,
                'score':round(channel_score)
                }
                tag_list.append(tag_dict)

        return_response={
        'response':'success',
        'overall_resillence_score':round(overall_resillence_score),
        'attendance_overall':round(attendance_overall),
        'overall_percent_score':round(overall_percent_score),
        # 'data':child_data,
        'tag_data':tag_list
        }


        return return_response


    @restapi.method([(["/get_user_progress"], "POST")], auth="user" , cors="*")
    def get_certificte(self):
        params = request.params
        user_id = self.env['res.users'].sudo().search([('id','=',self.env.user.id)])
        
        progress_ids = self.env['slide.channel.partner'].sudo().search([('partner_id','=',user_id.partner_id.id)])
        certificate_list=[]
        for progress in progress_ids:
            if progress.channel_id.active:
                course_dict={
                'course_name':progress.channel_id.name,
                'course_id':progress.channel_id.id,
                'last_update_date':str(progress.write_date),
                'scoring_percentage':round(progress.completion),
                'is_passed':progress.completed
                }
                flag_cert=0
                for lines in progress.channel_id.slide_ids:
                    if lines.slide_type == 'certification':
                        flag_cert+=1
                        cetificate_id = self.env['survey.user_input'].sudo().search([('survey_id','=',lines.survey_id.id),('partner_id','=',user_id.partner_id.id)])
                        if cetificate_id:
                            course_dict['certificate_state']=cetificate_id.state
                            if cetificate_id.state in ['new','in_progress']:
                                course_dict['exam_status']="nottaken"
                            else:
                                if cetificate_id.scoring_success:
                                    course_dict['exam_status']="passed"
                                else:
                                    course_dict['exam_status']="failed"
                            course_dict['certificate_id']=cetificate_id.id 
                            course_dict['is_passed']=round(cetificate_id.scoring_success) 
                            
                            course_dict['certificate_score']=cetificate_id.scoring_percentage
                        else:
                            course_dict['certificate_state']='Not attempt' 
                            course_dict['exam_status']="nottaken"
                            course_dict['certificate_id']=cetificate_id.id 
                            course_dict['certificate_score']=0
                            course_dict['is_passed']=False 
                            
                if flag_cert ==0:
                    course_dict['certificate_state']='Not applicable' 
                    course_dict['exam_status']="nottaken"
                    course_dict['certificate_score']=0
                    course_dict['is_passed']=False

                certificate_list.append(course_dict)
        count=0
        progress_score=0
        courses_attended=0
        for certificate_data in certificate_list:
            progress_score=progress_score+certificate_data['scoring_percentage']
            if certificate_data['is_passed']==True:
                count+=1
            if certificate_data['scoring_percentage']>0:
                courses_attended+=1


        individual_score=1000/len(certificate_list)
        percent_score=(count/len(certificate_list))*100
        overall_attendance=progress_score/len(certificate_list)
        final_score=individual_score*count
        #certificate_list['final_score']=int(final_score)
        complete_data={
        'response':'sucess',
        'attendance_score':round(overall_attendance),
        'resilience_score':round(final_score),
        'completion_score':round(percent_score),
        'total_no_courses':len(certificate_list),
        'courses_attended':courses_attended,
        'completed_courses':count,

        'data':certificate_list,

        }

        return complete_data

    @restapi.method([(["/get_specific_user_progress"], "POST")], auth="user" , cors="*")
    def get_specific_user(self):
        params = request.params
        user_id = self.env['res.users'].sudo().search([('login','=',params['email'])])
        
        progress_ids = self.env['slide.channel.partner'].sudo().search([('partner_id','=',user_id.partner_id.id)])
        certificate_list=[]
        for progress in progress_ids:
            if progress.channel_id.active:
                course_dict={
                'course_name':progress.channel_id.name,
                'course_id':progress.channel_id.id,
                'last_update_date':str(progress.write_date),
                'scoring_percentage':round(progress.completion),
                'is_passed':progress.completed
                }
                flag_cert=0
                for lines in progress.channel_id.slide_ids:
                    if lines.slide_type == 'certification':
                        flag_cert+=1
                        cetificate_id = self.env['survey.user_input'].sudo().search([('survey_id','=',lines.survey_id.id),('partner_id','=',user_id.partner_id.id)])
                        if cetificate_id:
                            course_dict['certificate_state']=cetificate_id.state
                            if cetificate_id.state in ['new','in_progress']:
                                course_dict['exam_status']="nottaken"
                            else:
                                if cetificate_id.scoring_success:
                                    course_dict['exam_status']="passed"
                                else:
                                    course_dict['exam_status']="failed"
                            course_dict['certificate_id']=cetificate_id.id 
                            course_dict['is_passed']=round(cetificate_id.scoring_success) 
                            
                            course_dict['certificate_score']=cetificate_id.scoring_percentage
                        else:
                            course_dict['certificate_state']='Not attempt' 
                            course_dict['exam_status']="nottaken"
                            course_dict['certificate_id']=cetificate_id.id 
                            course_dict['certificate_score']=0
                            course_dict['is_passed']=False 
                            
                if flag_cert ==0:
                    course_dict['certificate_state']='Not applicable' 
                    course_dict['exam_status']="nottaken"
                    course_dict['certificate_score']=0
                    course_dict['is_passed']=False

                certificate_list.append(course_dict)
        count=0
        progress_score=0
        courses_attended=0
        for certificate_data in certificate_list:
            progress_score=progress_score+certificate_data['scoring_percentage']
            if certificate_data['is_passed']==True:
                count+=1
            if certificate_data['scoring_percentage']>0:
                courses_attended+=1


        individual_score=1000/len(certificate_list)
        percent_score=(count/len(certificate_list))*100
        overall_attendance=progress_score/len(certificate_list)
        final_score=individual_score*count
        #certificate_list['final_score']=int(final_score)
        complete_data={
        'response':'sucess',
        'attendance_score':round(overall_attendance),
        'resilience_score':round(final_score),
        'completion_score':round(percent_score),
        'total_no_courses':len(certificate_list),
        'courses_attended':courses_attended,
        'completed_courses':count,

        'data':certificate_list,

        }

        return complete_data


    @restapi.method([(["/get_tags_info"], "POST")], auth="user" , cors="*")
    def get_tags_info(self):
        params = request.params
        user_id = self.env['res.users'].sudo().search([('id','=',self.env.user.id)])
        
        tag_ids=self.env['slide.channel.tag'].sudo().search([])
        tag_list=[]
        for tag in tag_ids:
            if tag.channel_ids:
                count=0
                for channel_id in tag.channel_ids:
                    if channel_id.active:
                        count+=1
                if count!=0:
                    score=1000/count
                else:
                    score=0
                # score=1000/count
                count_total_score=0
                flag_cert=0
                channel_score=0
                for channel_id in tag.channel_ids:
                    if channel_id.active:
                        enrol_count=0
                        enrol_user_progree=0
                        if user_id.user_ids:
                            individual_score=round(score)/len(user_id.user_ids.ids)
                            for user in user_id.user_ids:
                                enroled_user=self.env['slide.channel.partner'].sudo().search([('partner_id','=',user.partner_id.id),('channel_id','=',channel_id.id)])
                                if enroled_user:
                                    enrol_count+=1
                                    for lines in enroled_user.channel_id.slide_ids:
                                        if lines.slide_type == 'certification':
                                            flag_cert+=1
                                            cetificate_id = self.env['survey.user_input'].sudo().search([('survey_id','=',lines.survey_id.id),('partner_id','=',user.partner_id.id)])
                                            if cetificate_id:
                                                if cetificate_id.scoring_success:
                                                    count_total_score+=1
                                                    break

                        #         enrol_user_progree=enrol_user_progree+enroled_user.completion
                        if enrol_count!=0:
                            every_user_score=score/enrol_count
                            total_score=0
                            channel_score=channel_score+(count_total_score*every_user_score)

                        #     for user in user_id.user_ids:
                        #         enroled_user=self.env['slide.channel.partner'].sudo().search([('partner_id','=',user.partner_id.id),('channel_id','=',channel_id.id)])
                        #         if enroled_user:
                        #             total_score=total_score+(enroled_user.completion/100)*every_user_score
                        #     channel_total_score=channel_total_score+total_score
                # if channel_score !=0:
                tag_dict={
                'tag_name':tag.name,
                'score':round(channel_score)
                }
                tag_list.append(tag_dict)

        return tag_list        



    @restapi.method([(["/get_employee_info"], "POST")], auth="user" , cors="*")
    def get_employee_info(self):
        params = request.params
        user_id = self.env['res.partner'].sudo().search([('id','=',params['company_id'])])
        user_list=[]
        for rec in user_id.member_ids:
            user_dict={
            'name':rec.name,
            'id':rec.id,
            'login':rec.login
            }
            user_list.append(user_dict)

        return user_list





        
    








