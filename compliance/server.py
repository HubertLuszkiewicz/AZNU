from spyne import Application, rpc, ServiceBase, Unicode, Boolean
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from wsgiref.simple_server import make_server

class ComplianceService(ServiceBase):
    @rpc(Unicode, _returns=Boolean)
    def CheckWasteLegality(ctx, wasteType):
        return "radio" not in (wasteType or "").lower()

app = Application(
    [ComplianceService],
    tns="http://example.com/compliance",
    in_protocol=Soap11(validator="lxml"),
    out_protocol=Soap11()
)

wsgi_app = WsgiApplication(app)

if __name__ == "__main__":
    server = make_server("0.0.0.0", 8001, wsgi_app)
    print("SOAP server running on http://localhost:8001/?wsdl")
    server.serve_forever()