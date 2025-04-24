import http.client
import json
import requests

class FeiShuService(object):
    def __init__(self):
        self.app_id = 'cli_a555e81f23b9100c'
        self.app_secret = 'xY1oDMGJJsFdpVz2kMZFsgZiyvZwhJrn'
        self.conn = http.client.HTTPSConnection("open.feishu.cn")
        self.spreadsheet_token = "IGoUsqGLIhTpAGtClIncdZZOnud"

    def get_tenant_access_token(self):
       payload = json.dumps({
          "app_id": self.app_id,
          "app_secret": self.app_secret
       })

       headers = {
          'Content-Type': 'application/json'
       }
       self.conn.request("POST", "/open-apis/auth/v3/tenant_access_token/internal", payload, headers)
       res = self.conn.getresponse()
       data = res.read()
       print(data.decode("utf-8"))
    def get_sheet_data(self):
        payload = ''
        headers = {
         'Authorization': 'Bearer t-g104ckh1NDUPKQIFUCRPKVKWRYBY6S22RPT4EYE6',
        }
        self.conn.request("GET", f"/open-apis/sheets/v2/spreadsheets/{self.spreadsheet_token}/values/ca58dc", payload, headers)
        res = self.conn.getresponse()
        data = res.read()
        return data.decode("utf-8")




if __name__ == '__main__':
    fei_shu_service = FeiShuService()
    # fei_shu_service.get_tenant_access_token()
    fei_shu_service.get_sheet_data()




