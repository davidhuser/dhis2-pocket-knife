#!/usr/bin/env python

"""
user-orgunits
~~~~~~~~~~~~~~~~~
Checks each user assigned to an organisation unit if he/she is assigned to both organisation unit
and its sub-organisation units and prints them with their UID.
"""

import argparse
import csv
import re
import sys

from core.core import Dhis


def valid_uid(uid):
    "Check if string matches DHIS2 UID pattern"
    return re.compile("[A-Za-z][A-Za-z0-9]{10}").match(uid)


parser = argparse.ArgumentParser(description="Print all users of an orgunit who also have sub-orgunits assigned")
parser.add_argument('-s', '--server', action='store', help='Server, e.g. play.dhis2.org/demo', required=True)
parser.add_argument('-o', '--orgunit', action='store', help='Root orgunit UID to check its users', required=True)
parser.add_argument('-u', '--username', action='store', help='DHIS2 username', required=True)
parser.add_argument('-p', '--password', action='store', help='DHIS2 password', required=True)
args = parser.parse_args()

dhis = Dhis(server=args.server, username=args.username, password=args.password)

if not valid_uid(args.orgunit):
    dhis.log.info("Orgunit is not a valid DHIS2 UID")
    sys.exit()

orgunit_root_uid = args.orgunit

# get root orgunit
endpoint1 = "organisationUnits/" + orgunit_root_uid
params1 = {
    "fields": "id,name,path,users"
}
root_orgunit = dhis.get(endpoint=endpoint1, params=params1)

# get path of root orgunit
path = root_orgunit['path']

# get all descendant orgunit UIDs (excluding self) via 'path' field filter
endpoint2 = "organisationUnits"
params2 = {
    "filter": [
        "path:^like:" + path,
        "id:!eq:" + orgunit_root_uid
    ],
    "fields": "id",
    "paging": False
}
resp2 = dhis.get(endpoint=endpoint2, params=params2)

no_of_users = len(root_orgunit['users'])

# put the response ids into a list
sub_uids = list(ou["id"] for ou in resp2["organisationUnits"])

dhis.log.info(
    "Checking users against sub-orgunit assignments of root orgunit " + root_orgunit['name'])

# check each user of root orgunit
# log user if: [has more than 1 orgunit associated] AND [any other user orgunit is a sub-orgunit of root orgunit]
users_export = []
counter = 0
for user in root_orgunit['users']:
    problem = False
    counter += 1
    user_uid = user['id']

    endpoint3 = "users/" + user_uid
    params3 = {
        "fields": "id,name,organisationUnits,lastUpdated"
    }
    user = dhis.get(endpoint=endpoint3, params=params3)

    print("(" + str(counter) + "/" + str(no_of_users) + ") " + user_uid + " ...")
    user_orgunits = user['organisationUnits']
    if len(user_orgunits) > 1:
        # Python2 & 3 compatibility
        try:
            xrange
        except NameError:
            xrange = range
        # find conflicting sub-orgunits
        for i in xrange(len(user_orgunits)):
            user_orgunit_uid = user_orgunits[i]['id']
            if user_orgunit_uid != orgunit_root_uid and user_orgunit_uid in sub_uids:
                problem = True

    if problem:
        users_export.append(user)
        msg = user['name'] + " - UID: " + user_uid
        dhis.log.info("Conflicting user found:  " + msg)

# write conflicting users to CSV file
if users_export:
    # remove orgunits for export
    for u in users_export:
        del u['organisationUnits']

    file_name = root_orgunit['id'] + '-user-orgunits-conflicts.csv'
    with open(file_name, 'w') as csv_file:
        # use the keys of first user as csv headers
        fieldnames = list(users_export[0].keys())

        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(users_export)

    dhis.log.info(
        "Found and exported " + str(len(users_export)) + " " + root_orgunit['name'] + " users to " + file_name)
else:
    dhis.log.info("No conflicts found.")
