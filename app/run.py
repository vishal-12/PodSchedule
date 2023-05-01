import tornado.ioloop
import tornado.web
from pod.VMware import VMware
import json
from datetime import datetime
import jsonschema
import traceback
from schema.Vcenter import schema_vcenter

def Body():
    """
     Standard Script Response Format
    :return:
    """
    return  {"timestamp": datetime.now(),"Data": "","Message": "","Error": ""}

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        """
        Welcome Message to Pod Schedule
        :return:
        """
        template = '''<html>
                        <head>
                            <title>Pod Health and Monitor Application</title>
                        </head>
                        <body>
                            <div style="text-align:center;">
                                <img src="data:image/png;base64,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" alt="VMware Logo" style="width:300px;height:100px;">
                            </div>
                            <h1>Welcome to My VMware Application!</h1>
                            <p>Our application helps you manage your virtualized infrastructure with ease. You can perform various operations such as creating, updating, and deleting virtual machines, managing clusters, and monitoring performance metrics.</p>
                            <p>We support the following job types:</p>
                            <ul>
                                <li>Job Type 1: Get Datastore</li>
                                <li>Job Type 2: Get Templates from Content Library</li>
                                <li>Job Type 3: Get DV port Group</li>
                            </ul>
                            <p>To use our application, please sign in with your VMware account credentials.</p>
                            <div style="text-align:center;">
                                <img src="data:image/jpeg;base64,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" alt="My Company Logo" style="width:300px;height:100px;">
                            </div>
                            <p>Our application is fully integrated with Rsystems, so you can easily manage your virtualized infrastructure from within our platform. We provide advanced features such as role-based access control, automation, and analytics to help you optimize your IT operations and reduce costs.</p>
                            <p>If you have any questions or feedback, please contact our support team at vishal.sharma2@rsystems.com.</p>
                        </body>
                        </html>'''
        self.write(template)

class PodScheduleJob(tornado.web.RequestHandler):
    def post(self):
        """
        List Datastore IDs
        :return:
        """
        # Get data from request body

        data = tornado.escape.json_decode(self.request.body)
        #Validate schema
        schema = schema_vcenter()
        jsonschema.validate(data, schema)
        vcenter = {"url" : data.get("url"),"username": data.get("username"),"password" : data.get("password")}
        #Headers verify
        self.set_header("Content-Type", "application/json")
        #header_value = self.request.headers.get('X-Job-Type')
        JobType =  data.get("taskIdentifier")

        #API body
        body = Body()

        #Job Identifier
        Identifier = ["Datastore","FetchTemplate","DvPortGroup"]
        if not (JobType in Identifier):
            body.update({"Message" : "X-My-Header [{}] NOT_FOUND Available Options - {}".format(JobType,Identifier)})
            self.write(json.dumps(body, default=str))
            self.set_status(400)
            self.finish()
            return
        try:
            vmware  =  VMware(vcenter=vcenter)
            if JobType == "Datastore":
                body.update({"Data": vmware.GetDatastore()})
            if JobType == "FetchTemplate":
                body.update({"Data": vmware.get_templates_softwares_from_contentlibrary()})
            if JobType == "DvPortGroup":
                body.update({"Data": vmware.get_public_switch_list(change_job_keys=True)})
            self.set_status(200)
        except Exception:
            tb = traceback.format_exc()
            self.set_status(500)
            body.update({"Error" : "Script Output - {}".format(tb)})
        finally:
            print (json.dumps(body, default=str))
            self.write(json.dumps(body, default=str))

    def options(self):
        self.set_status(204)
        self.finish()

    supported_methods = ['POST', 'OPTIONS']

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/v1/vcenter/pod/jobs", PodScheduleJob)
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()