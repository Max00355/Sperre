from bottle import *
import config
import send_message
import thread
import client
import is_online
import webbrowser

@route("/")
def index():
    my_address = config.my_data.find("data", "all")[0]["address"]
    messages = config.cache.find("messages", "all")
    if not messages:
        messages = []
    names = []
    out = []
    messages.reverse()
    for x in messages:
        if x['from'] not in names:
            names.append(x['from'])
            data = {}
            data["from"] = x['from']
            data['message'] = x['message']
            out.append(data)
    
    return jinja2_template("templates/index.html", messages=out, my_address=my_address)

@route("/conversation/<address>")
def conversation(address):
    my_address = config.my_data.find("data", "all")[0]["address"]
    return jinja2_template("templates/conversation.html", my_address=my_address, contact=address)


@route("/is_online/<address>")
def isonline(address):
    check = is_online.send(address)
    if check:
        return "Online"
    else:
        return "Offline"

@route("/messages/<address>")
def messages__(address):
    messages = config.cache.find("messages", {"from":address})
    if not messages:
        messages = []
    sent = config.cache.find("sent", {"contact":address})
    if not sent:
        sent = []
    conversation = messages + sent
    conversation = sorted(conversation, key=lambda x:x['time'])
    return jinja2_template("templates/messages.html",  messages=conversation)



@route("/conversation/<address>", method="POST")
def send_message_form(address):
    message_ = request.forms.get("message")
    if message_:
        thread.start_new_thread(send_message.send, (message_,  address))
        redirect("/conversation/"+address)


@route("/startconvo/")
def start_convo():
    my_address = config.my_data.find("data", "all")[0]["address"]
    return jinja2_template("templates/start_convo.html", my_address=my_address)

@route("/startconvo/", method="POST")
def start_convo_form():
    address = request.forms.get("address")
    check = config.nodes.find("nodes", {"address":address})
    if not check:
        return "Address does not exist."
    else:
        redirect("/conversation/"+address)

@route("/static/<static_file>")
def static_(static_file):
    return template("templates/"+static_file)

if __name__ == "__main__":
    thread.start_new_thread(client.run, ())
    webbrowser.open("http://127.0.0.1:4321")
    run(host="localhost", port="4321", debug=True)
