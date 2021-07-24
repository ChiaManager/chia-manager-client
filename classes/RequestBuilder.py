import socket

class RequestBuilder:
    def wsHeaders(self, hostname, authhash, socketaction):
        reqdata = {}
        reqdata["node"] = {}
        reqdata["node"]["nodeinfo"] = {}
        reqdata["node"]["nodeinfo"]["hostname"] = hostname
        reqdata["node"]["socketaction"] = socketaction
        reqdata["request"] = {}
        reqdata["request"]["logindata"] = {}
        reqdata["request"]["logindata"]["authhash"] = authhash

        return reqdata;

    def getFormatedInfo(self, authhash, socketaction, namespace, classname, method, data):
        hostname = socket.gethostname()
        reqdata = self.wsHeaders(hostname, authhash, socketaction)


        reqdata["request"]["data"] = data
        reqdata["request"]["backendInfo"] = {}
        reqdata["request"]["backendInfo"]["namespace"] = namespace
        reqdata["request"]["backendInfo"]["class"] = classname
        reqdata["request"]["backendInfo"]["method"] = method

        return reqdata;
