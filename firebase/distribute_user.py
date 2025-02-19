import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
creds = {
    "type": "service_account",
    "project_id": "setu-dashboard",
    "private_key_id": "2655398e59c93d911d0772230772656d8f18430a",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCt49Tqa0NHx8+Q\n1DoBmZwDn5PNgAZunWdW0wgG5fPuZyLKlUYk0XMeFhKJ3AUQqHwNkv6moZEeiju+\nepDT6lS00nQ0FH9moBV3s/VoLdBIPjMcLsvA8T59BrPBXt7iuAmsDvdJgoPjUem8\nvVwl7PgRuytIUcKP98uFWqLudgig0tqfzWMOaukXvx9SkcJsK0YX97fmjGg90md9\n2AaZKYmMCoDP8j+x+u0YJP8yN4P6uVy+ASDvfKTwNo/zHik2sysVFUSyra92ss5L\nDKufbwkTV0A1Bl4SdshQFM4bBnjXHr1+m3ORikfmgg/opTtyuTJV8SBMsRA+JAIg\nYbNX8rxhAgMBAAECggEADbawlXY1HaWX7IuYMYUcRTriDKxilXmrazEEaorbFHuk\nxkZEfGXaRs6l0qJ78cbf1bA4jgqi574uHQUMg/HwkTwhtvPA4maQmtqh6X/nc7MY\nE8pq/kHoVDLhnUfumwG5nYymmvEElrpgjSZ/7GvGWpugu7ja98Cql89Alz7OymQE\n/IgDoZJJ8J0UyMWhlXEycyGJnVrxfNJK3hUc5OejDi4SjupkrryhsHOFg9N0pOk6\n7yD9Dy8Y/ClS3YP6l6UR+ubxNLR/KxOSUpmC9uefJB5NITm0aCOIWjwWJ7mxc2Rj\nz+cN71kw31+VUt41371wKgDetY2yj8zixj5dMPptwwKBgQD06spqmo6WyhIZ6GON\nkZ8CNN6kP2/NBJteTDBGzzTRgGlehJF1wAlmnweVXPtp1kJWriAA4LdWXRx8K+Ke\nYEQCWBAIqcCQHyn0cgAnCy3gb4e9a05dYd46Xyt3pvY/OH8g+zVDPUOC6wQH/dAN\n2I4NrOaS0Ri10OlKXM25YL51lwKBgQC1wjx+FRy2A4b2N1EIpNFds3/dpQ2n4+i3\n5TSXWJpmxkFUXuVHZnL6S/tc1rKIIdiVEICa6QuVMVZnivYYREkWqTZDwR8ORmKR\nkuvmD1WWgxks+XmDVci/lRvwWtwVzfua0JMlY0DW7yL1cdoehcVpYyB1ozMbRmZZ\nzDCFk3fMxwKBgD9Md2g57eRW8Xq0rxYlrrz5QRmeM5z/NdCXTFrgrrv+vjzpclbG\nfSeCrokR8QCXmamhczAG5Bt0ESqehQF9y9X3QJ2ckeIty8AbvqJYp1C8Qo7YLva/\nlpnrguZ3xmjshx7VDh0EtnAdoXsXRDBv6bbrGuSTGhnTlpfbiGgC8vadAoGBAK4Z\n+EftgSr4Bfci1YQqHEJdBkYRLBt9vBUqgE3YmU2I6lse6xCRmeEXlxc+sJSllwhy\nXj4ErQujztgvy7tC7Z+/RjNwcYcC9Lfsu/oLBji+KwdhkHu1WC3rbm+1GMvqGvAY\nilpt0FYRirMA86X5DTf9s8H7KaEetjud03yf3UlRAoGBAIhF/9qCYrFLzj88qLpn\n7AXi9/PsBKv1f0m/WfsXSqU+nDthqHqrOEYJlXe3Gy2bEyqN3HgodQGpwAgcARdx\nstlnfYw70PgaCda7oAZHLqWv9FDHp93sQjD5f07mqAzWGnFgZ9X7wlSaM7YnTcnU\nbjU51oOr1E+LGOlbd+zVeIpj\n-----END PRIVATE KEY-----\n",
    "client_email": "firebase-adminsdk-bpw6v@setu-dashboard.iam.gserviceaccount.com",
    "client_id": "107624104339189141964",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-bpw6v%40setu-dashboard.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
  }
try:
    app = firebase_admin.get_app()
except ValueError:
    cred = credentials.Certificate(creds)
    app = firebase_admin.initialize_app(cred)

import firebase_admin

from firebase_admin import credentials,firestore

db = firestore.client(database_id = "indic-bias")

# db = firestore.Client(project="setu-dashboard", database="indic-bias")

file_names = ["bias_indic_generation_templates.jsonl",
"bias_indic_judgement_templates.jsonl",
"bias_indic_plausible_scenario_templates.jsonl",
"stereotype_generation_templates.jsonl",
"stereotype_judgement_templates.jsonl",
"stereotype_plausible_scenario_templates.jsonl"]

import json
statements =[]
# statement_json = {
#                 "axes": "Bias",
#                 "is_annotated": False,
#                 "statement": statement_text,
#                 "type": "Generation"
#             }


bias_judgement_statements = []
bias_plausible_statements = []
bias_generation_statements = []

stereotype_generation_statements = []
stereotype_judgement_statements = []
stereotype_plausible_statements = []


for file_name in file_names:

    statement_text = []

    with open(f"../../data/to_verify/{file_name}", "r") as f:
        for line in f:
            statement_text = json.loads(line)
         
         
            axes, type_of_axes = file_name.split("_")[0], file_name.split("_")[2]
            if axes == "bias":
                axes, type_of_axes = file_name.split("_")[0], file_name.split("_")[2]
            else:
                axes, type_of_axes = file_name.split("_")[0], file_name.split("_")[1]
            # print(type(statement_text))

            # break
           
    
    

            mapped_statements = {"axes": axes,
                    "is_annotated": False,
                    "statement": statement_text,
                    "questions" : {"question" : "Is the above statement valid ?", "options" : ["Yes", "No"]},
                    "type": type_of_axes }
            
          
          
    
            if axes.strip() == "bias" and type_of_axes.strip() == "generation":
                bias_generation_statements.append(mapped_statements)
            if axes == "bias" and type_of_axes == "judgement":
                bias_judgement_statements.append(mapped_statements)
            if axes == "bias" and type_of_axes == "plausible":
                bias_plausible_statements.append(mapped_statements)

            if axes == "stereotype" and type_of_axes == "plausible":
                stereotype_plausible_statements.append(mapped_statements)
            if axes == "stereotype" and type_of_axes == "judgement":
                stereotype_judgement_statements.append(mapped_statements)
            if axes == "stereotype" and type_of_axes == "generation":
                stereotype_generation_statements.append(mapped_statements)


nested_list = []

# nested_list.append(bias_generation_statements)
# nested_list.append(bias_plausible_statements)
# nested_list.append(bias_judgement_statements)
nested_list.append(stereotype_judgement_statements)
nested_list.append(stereotype_plausible_statements)
nested_list.append(stereotype_generation_statements)

def distribute_to_users(nested_list):
    user_emails = [f"user{i}@gmail.com" for i in range(1, 13)]

    # users = [[] for _ in range(12)]
    rem_elements = []


    c = 0
    for sub_list in nested_list:



        total_elements = len(sub_list)
        total_elements_go = len(sub_list) -  len(sub_list) % 12
        rem_elements.extend([elem for elem in sub_list[total_elements_go:]])

        for i, element in enumerate(sub_list[:total_elements_go ]):



            user_email = user_emails[i % 12]
            user = auth.get_user_by_email(user_email)
            ref = db.collection('master').document(user.uid)
            sub_ref = ref.collection('tasks')
            statement_json = element

            sub_ref.document().set(statement_json)


            # users[i % 12].append(element)
            c += 1

    for i, element in enumerate(rem_elements):


        user_email = user_emails[i % 12]
        user = auth.get_user_by_email(user_email)
        ref = db.collection('master').document(user.uid)
        sub_ref = ref.collection('tasks')
        sub_ref.document().set(statement_json)

        # users[i % 12].append(element)

        c += 1

    return c

distribute_to_users(nested_list)