import json
import requests

from flask import Flask,make_response
from flask_restful import reqparse,Api,Resource
from simplexml import dumps

# creating flask app
app = Flask(__name__)

# creating an API object
api = Api(app)


# creating a class for get address details
class GetAddressDetails(Resource):

    # corresponds to post request
    def post(self):

        parser = reqparse.RequestParser()
        parser.add_argument('address', required = True)
        parser.add_argument('output_format', required = False)
        parser.add_argument('Authorization', location='headers')
        args = parser.parse_args()

        # getting all the params and authorisation key
        auth = args['Authorization']
        address = args['address']
        output_format = args['output_format']

        if not output_format:
            # making output format default to json if not present in response 
            output_format = "json"

        # if there is no authorisation key then don't allow user to use endpoint
        if not auth:
            return {"message":"unauthorised"},  401

        # getting latitude and longitude data
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address":address,
            "key": auth
        }
        response = requests.get(url=url, params=params)
        res = response.json()

        if res.get('status') == "REQUEST_DENIED":
            # if request is failed for given address or key is not right then simply return with error message
            result ={ "message": res.get("error_message")}
            status_code = 400
        else:
            # get latitude and longitude data and updated address
            result = {
                "coordinates":{
                    "lat": res['results'][0]['geometry']['location']['lat'],
                    "long": res['results'][0]['geometry']['location']['lng']
                },
                "address": res['results'][0]['formatted_address']
            }
            status_code = 200

        if output_format.lower() == "xml":
            # if output formate xml then returns xml data
            response = make_response(dumps({'root': result}), status_code)
        else:
            # if output formate is not given or json then return json data
            response = make_response(json.dumps(result),status_code)

        return response


# adding the defined resources along with their corresponding urls
api.add_resource(GetAddressDetails, '/getAddressDetails')

if __name__ == '__main__':
    app.run(debug=True)