import requests, json
data = {
    'login': 'admin',
    'password': 'admin',
    'db': 'test_cl'
}
headers = {
    'content-type': 'application/x-www-form-urlencoded',
    'charset':'utf-8',
    'access-token': 		'access_token_2655480cd21af5f45ea6948f8e48ff5918148eac'
}

base_url = 'http://192.168.0.6:8069'

d = {
'content': [{
	"partner":{
		"name": "Maicol Demetrio Lastra",
		"l10n_cl_document_type_id": 81,
		"l10n_cl_document_number": "1234567-9",
		"street": "Jr. Gozooli",
		"country_id": "Chile"
		},
	"invoice":{
		"number": "F001-00001",
		"date_invoice": "2018-10-08",
		"date_due": "2018-10-08",
		"lines":[
			{
				"product":{
					"name": "Ruedecita",
					"type": "consu"				
				},
				"quantity": 10,
        "price_unit": 2.5,
        "discount": 4,
			}		
		]	
	}
}]
}

p = requests.post('%s/api/l10n_cl.account.external.api/'%base_url, headers=headers,data={'content': json.dumps(d.get('content'))})
print(p.content)
