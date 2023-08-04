import pandas as pd
import json

class json2overcome2:
    # adds brackets to the beginning and end of json file because exported Webots json file had a formatting error
    def add_brackets_to_json_file(self,file_path):
        # Read the JSON file
        with open(file_path, 'r') as json_file:
            data = json_file.read()

        # Modify the content to add "[" at the beginning and "]" at the end
        modified_data = "[" + data + "]"

        # Write the modified content back to the file
        with open(file_path, 'w') as json_file:
            json_file.write(modified_data)

    # returns a converted dataset of the json file
    def openData(self, json_file_path):
        try:

            with open(json_file_path, 'r') as json_file:
                data = json.load(json_file)
                return data
            
        except FileNotFoundError:
            print(f"Error: The JSON file '{json_file_path}' was not found.")
        except json.JSONDecodeError:
            print(f"Error: Unable to parse the JSON file '{json_file_path}'.")

        return None

    # Creates a Translations collumn from the "Updates collumn"
    def getTranslationDF (self,data):
        time_list = []
        transition_list = []

        for frame in data['frames']:
            time = frame['time']
            for update in frame['updates']:
                #if update.get('id') == 224: # hard coded id, change it so the method accepts the id number and use supervisor id method to find id and pass it in
                transition = update.get('translation', None)
                if transition is not None:
                    if time> 0:
                        time_list.append(time)
                        transition_list.append(transition)

        # Create a new DataFrame with 'time' and 'translation' columns
        new_df = pd.DataFrame({'time': time_list, 'translation': transition_list})

        return new_df
    # Truncates the values after the first translation number
    def formatTranslationDF(self, dfTran):
        #formatDF = dfTran["translation"]
        if 'translation' in dfTran.columns:
            formatDF = dfTran['translation']
            translations = formatDF.copy()  # Create a copy of the Series to modify
            for num in range(len(translations)):
                extactNums = str(translations.iloc[num]).split()
                translations.iloc[num] = float(extactNums[0])
            return translations
        else:
        # Handle the case when 'translation' column is not present
            return pd.Series(dtype=float)

    # interprects the translation data and returns a tuple with how many obstacles were passed and the time stamp of the last crossing
    def obstaclePassed(self, df, column_name):

        result_3 = None
        result_2 = None
        result_1 = None
        result_0 = None

        # Traverse the column from bottom to top
        for idx in range(len(df) - 1):
            value = df.loc[idx, column_name]

            # Updates the relavent list
            if value >= 0.9:
                result_3 = (3, df.loc[idx, 'time'])
            elif value >= 0.4: 
                result_2 = (2, df.loc[idx, 'time'])

            #picking up the translation value of another id, messing up the method
            elif value >= -0.1:
                #print(value)
                result_1 = (1, df.loc[idx, 'time'])
            else:
                #print('0')
                result_0 = (0, df.loc[idx, 'time'])
        print (f'the {value}')
        return result_3 or result_2 or result_1 or result_0
