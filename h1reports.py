import requests
import json
import time

# GraphQL query template
graphql_query = {
    "operationName": "HacktivitySearchQuery",
    "variables": {
        "queryString": "*:*",  # Broad query string
        "size": 25,  # 25 reports per request
        "from": 0,  # Will be updated per iteration
        "sort": {
            "field": "disclosed_at",
            "direction": "DESC"
        },
        "product_area": "hacktivity",
        "product_feature": "overview"
    },
    "query": """query HacktivitySearchQuery($queryString: String!, $from: Int, $size: Int, $sort: SortInput!) {
        me {
            id
            __typename
        }
        search(
            index: CompleteHacktivityReportIndex  # Updated index name
            query_string: $queryString
            from: $from
            size: $size
            sort: $sort
        ) {
            __typename
            total_count
            nodes {
                __typename
                ... on HacktivityDocument {  # Updated type name
                    id
                    _id
                    reporter {
                        id
                        name
                        username
                        __typename
                    }
                    cve_ids
                    cwe
                    severity_rating
                    upvoted: upvoted_by_current_user
                    report {
                        id
                        databaseId: _id
                        title
                        substate
                        url
                        disclosed_at
                        report_generated_content {
                            id
                            hacktivity_summary
                            __typename
                        }
                        __typename
                    }
                    votes
                    team {
                        handle
                        name
                        medium_profile_picture: profile_picture(size: medium)
                        url
                        id
                        currency
                        __typename
                    }
                    total_awarded_amount
                    latest_disclosable_action
                    latest_disclosable_activity_at
                    submitted_at
                    __typename
                }
            }
        }
    }"""
}

# URL of the GraphQL endpoint
graphql_endpoint = 'https://hackerone.com/graphql'

# Pagination setup
start_index = 0
batch_size = 25  # Number of reports per request
max_reports = 5000  # Limit to 5000 reports
max_requests = max_reports // batch_size  # 200 requests (5000 / 25)

# Open the file to append URLs to
with open('h1reports.txt', 'a') as f:
    for j in range(max_requests):
        # Update the 'from' parameter for pagination
        graphql_query['variables']['from'] = start_index

        # Send POST request with GraphQL query
        try:
            response = requests.post(graphql_endpoint, json=graphql_query)

            if response.status_code == 200:
                data = response.json()

                # Print the full response for debugging
                # Print the entire JSON response for debugging
                # print(json.dumps(data, indent=2))  

                # Check if we got any results
                if 'data' in data and 'search' in data['data'] and 'nodes' in data['data']['search']:
                    nodes = data['data']['search']['nodes']
                    if nodes:
                        # Extract and write report URLs
                        for node in nodes:
                            if 'report' in node and 'url' in node['report']:
                                report_url = node['report']['url']
                                print(f"Found report URL: {report_url}")
                                f.write(report_url + '\n')
                    else:
                        print("No reports found in this batch.")
                        break  # Exit if no nodes are found in the response
                else:
                    print("No valid data found in the response.")
                    break  # Exit if no search results are returned
                
            else:
                print(f"Request failed with status code: {response.status_code}")

            # Increment the start index for the next batch
            start_index += batch_size

            # Optional: Sleep to avoid rate limiting
            time.sleep(1)  # Pause for 1 second between requests

        except Exception as e:
            print(f"An error occurred: {e}")
            break  # Exit the loop if an exception occurs
