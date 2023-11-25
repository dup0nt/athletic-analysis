import requests
import pandas as pd
import os
import json

activities_url = "https://www.strava.com/api/v3/athlete/activities"

JSON_FILE_PATH = 'data/{}.csv'


def update_tokens(request):
    user = request.user # Pulls in the Strava User data
    strava_login = user.social_auth.get(provider='strava') # Strava login
    access_token = strava_login.extra_data['access_token'] # Strava Access token

    header = {'Authorization': 'Bearer ' + str(access_token)}
    return header


def get_database(header, data_type):
    #data_type:
    #   activities
    #   gear

    json_file_path = JSON_FILE_PATH.format(data_type)

    # Check if the JSON file exists
    if os.path.isfile(json_file_path):
        print("There a File")
        # JSON file exists
        #with open(json_file_path, 'r') as json_file:
        #    data = json.load(json_file)
        data = pd.read_csv(json_file_path)
        #last_saved = pd.to_datetime(data['start_date'].iloc[0])
        updated_data = update_data(header,data)

        save_json_data(data_type, updated_data)

        return updated_data
        
  
    # JSON file does not exist, fetch data from API and save it
    os.makedirs(os.path.dirname(json_file_path), exist_ok=True)

    data = fetch_data_from_api(header)
    save_json_data(data_type, data)
    
    # Now you have the data either from the existing JSON or newly fetched data
    return data


def update_data(header, old_data):

    print(type(old_data))
    old_data = pd.DataFrame(old_data)
    latest_id = old_data['id'].iloc[0]
    all_updated_activities = [old_data]

    #Verify if data is up to date
    first_page = 1
    num_pages = 1
    not_updated = True

    while not_updated:
        new_data =  fetch_data_from_api(header, 
                                        first_page,
                                        num_pages)
        
        #index_false = 200-(new_data['start_date'].isin(last).sum() + 1)#o sum dá me o numero do index do True!

        if latest_id in new_data['id'].values:
            index_to_exclude = new_data[new_data['id'] == latest_id].index[0]
            filtered_data = new_data.loc[:index_to_exclude - 1]
            all_updated_activities.append(filtered_data)
            not_updated = False
            print("Added {} activities".format(len(filtered_data)))

            break
        
        else:
            all_updated_activities.append(new_data)
        """

        index_false = 200-(new_data['start_date'].isin(old_data['start_date']).sum() + 1)#o sum dá me o numero do index do True!
        print("value of index_false: {}".format(index_false))

        if index_false == 200:
            return old_data

        elif index_false != 0:
            index_true = 200-index_false
            real_new_data = new_data[0:index_true+1]
            print("real_new_data {}".format(real_new_data))

            all_updated_activities.append(real_new_data)

            not_updated=True
            return pd.concat(all_updated_activities, axis=0, ignore_index=True)
        """
        #all_updated_activities.append(new_data)
        first_page+=1

    #all_updated_activities.append(old_data)
    print("Updated with {} activites".format(len(all_updated_activities)-len(old_data)))
    return pd.concat(all_updated_activities, axis=0, ignore_index=True)





def fetch_data_from_api(header, first_page=1,num_pages=-1):
    print("Requesting pages (200 activites per full page)... ")

    new_activities_df = []

    page = first_page #=1
    
    page_non_empty = True

    while page_non_empty:  # Change this to be higher if you have more than 1000 activities
        param = {'per_page': 200, 'page': page}
        
        activities_json = requests.get(activities_url, headers=header, params=param).json()
        print("my activities {}".format(len(activities_json)))

        new_activities_df.append(pd.json_normalize(activities_json))

        if not activities_json or num_pages==1:
            page_non_empty=False
            break

        
        page+=1

    
    new_activities_df = pd.concat(new_activities_df,axis=0, ignore_index=True)
    print("\n", len(new_activities_df), "activties downloaded!")
    #new_activities_df = pd.DataFrame(new_activities_df)

    return new_activities_df

def save_json_data(data_type, data):
    # Save the data to the JSON file
    #data = pd.DataFrame(data)
    #data['start_time'] = pd.to_datetime(data['start_date'])  # Ensure 'start_time' is in datetime format
    data = data.sort_values(by='start_date', ascending=False)
    json_file_path = JSON_FILE_PATH.format(data_type)
    data.to_csv(json_file_path, index=False)
    #with open(json_file_path, 'w') as json_file:
    #    json.dump(data, json_file)


