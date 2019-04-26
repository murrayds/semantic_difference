def format_baseline_features_one_business_json(businessJSON):
    """
    This function will take as input a single JSON objec representing a
    business (and assumes that the `attributes_flat` field exists) and produces
    a baseline feature matrix. This function is agnostic to what the label to
    predict, and simply returns all attributes.

    Parameters
    ----------
    businessJSON: json
        JSON object representing the business to process

    Returns
    -------
    A JSON object that includes only relevant baseline features extracted from
    the businessJSON object
    """

    features = {
        'business_id': businessJSON['business_id'],
        'review_count': businessJSON['review_count'],
        'stars': businessJSON['stars']
    }

    keys = businessJSON.keys()
    if 'hours' in keys:
        features['hours'] = simplify_hours_values(businessJSON['hours'])
    if 'attributes' in keys:
        features['attributes'] = simplify_attribute_values(businessJSON['attributes'])
    if 'list_of_categories' in keys:
        cat_dict = {}
        for item in businessJSON['list_of_categories']:
            cat_dict[item] = True
        features['categories'] = cat_dict

    return(features)


def extract_baseline_features(businessJSON_list, num_miss = 500):
    """
    Extracts the baseline features for a list of JSON objects representing
    businesses in Yelp.

    Parameters
    ----------
    businessJSON_list: list
        List of JSON object representing the business from which to extract
        features

    Returns
    -------
    A pandas dataframe representing the baseline features extracted from the
    business list.
    """
    from pandas.io.json import json_normalize
    bus_list = []
    for bus in businessJSON_list:
        bus_list.append(format_baseline_features_one_business_json(bus))

    df = json_normalize(bus_list)
    for column in df.columns:
        # We will set categories as a simple presence matrix: True if category
        # exists, false otherwise.
        if column.startswith('categories'):
            df[column] = df[column].fillna(False)

    # Now remove drop features that have too many missing values, which should
    # be almost entirely the attributes
    for column in df.columns:
        num_miss = df[column].isnull().sum(axis=0)
        if (num_miss > num_miss):
            df = df.drop(column, axis = 1)
        if (column.startswith("category")):
            df = df.drop(column, axis = 1)

    return(df)

def split_training_testing(features, y_column, test_size = 100):
    """
    Selects all features for which the provided attribute exists and has a value
    of true or false. It should then randomly sample from these rows the maximum
    data sample size (if smaller than the actual data size). After this, uses
    existing python libraries, or write trivial code to perform the split.

    Parameters
    ----------
    features : pandas dataframe
        The pandas dataframe containing the extracted features of the businesses
        to use for training and testing
    y_column : string
        The name of the field in the features to predict
    test_size: double
        Size of the testing data.

    Returns
    -------
    4 dataframes containing training features and labels, and testing
    features and labels
    """
    from sklearn.model_selection import train_test_split
    import pandas as pd

    # Filter dataframe to only those rows where the attribute is present
    features = features.loc[pd.notnull(features[y_column])]

    # Get the appropriate
    y = features[y_column]
    drop_list = ['business_id', y_column]
    for to_drop in drop_list:
         features = features.drop(to_drop, axis=1)

    # Now, fill NA
    features = features.fillna('Absent')

    features = pd.get_dummies(features)
    return(train_test_split(features, y, test_size = test_size))


def simplify_attribute_values(attributes):
    """
    Simple function that simplifes some of the business attribute fields that can
    take on a variable set of values. We want to treat attributes like tags,
    so we should definintely try to convert them to things that can take on
    true or false values

    Parameters
    ----------
    attributes: json
        JSON object containing the attributes to process

    Returns
    -------
    The provided attribute JSON object but with the processed value (if any)
    """
    if attributes is None:
        return None

    for key in attributes:
        if key == 'Alcohol':
            attributes['serves_alcohol'] = attributes[key] != "none"
            attributes.pop(key, None)
        elif key == 'WiFi':
            attributes['free_wifi'] = attributes[key] == 'free'
            attributes.pop(key, None)
        elif key == 'RestaurantsAttire':
            attributes['casual_attire'] = attributes[key] == 'casual'
            attributes.pop(key, None)
        elif key == 'NoiseLevel':
            attributes['loud_noise_level'] = attributes[key] == 'loud'
            attributes.pop(key, None)
        elif key == 'RestaurantsPriceRange2' and attributes[key] is not None:
            attributes['high_price'] = attributes[key] > 2
            attributes.pop(key, None)

    return(attributes)


def simplify_hours_values(hours):
    """
    Discretizes, and thus simplifies the values of the 'hours' field associated
    with each businesses. The default in the yelp json files is that `hours`
    maps to a dictionary, wherin each key is a day. Each day then maps to a set
    of hours embedded in a string.

    This function will create a new dictionary, where each day is mapped to a
    binary True/False value representing whethr the restaurant is open that day.
    Moreover, values are mapped to "OpenBreakfast", "OpenLunch", etc.; a
    restraunt only needs to be open for a time period once a week for the value
    to be set to true
    """

    if hours is None:
        return None
    # This template-filling style is not the most flexible, but since I don't
    # think we will be adding any new days anytime soon, we will probably be
    # fine
    template = {'Monday': False,
     'Tuesday': False,
     'Wednesday': False,
     'Thursday': False,
     'Friday': False,
     'Saturday': False,
     'Sunday': False,
     'OpenBreakfast': False,
     'OpenLunch': False,
     'OpenDinner': False,
     'OpenLate': False,
     'NumOpenDays': False}

    num_open_days = 0
    for key in hours.keys():
        num_open_days = num_open_days + 1
        template[key] = True
        open_close = hours[key].split('-')
        opening = int(open_close[0].split(":")[0])
        closing = int(open_close[1].split(":")[0])

        if opening < 11:
            template['OpenBreakfast'] = True
        # if between 11 and 4
        if closing > 16:
            template['OpenLunch'] = True
        if closing < 23:
            template['OpenDinner'] = True
        if closing < 4:
            template['OpenLate'] = True

    template['NumOpenDays'] = num_open_days

    return(template)


def get_count_of_neighbor_attribute(G, target, attribute, value):
    """
    Returns the count of a node's neighbors whose attribute is set to the
    given value

    Parameters
    ----------
    G : networkx graph object
        The networkx graph object
    target : string
        The business id mapping to the node
    attribute: String
        The name of the attribute to query
    value : Varies, usually boolean
        The value to compare against the atrtibute of the neighbor's nodes

    Returns
    -------
    The count of neighbor nodes contianing the value of the provided attributes
    """
    from .network_utils import get_neighbors_of_node
    neighbors = get_neighbors_of_node(G, target)
    accum = 0
    for neighbor in neighbors:
        node = G.nodes[neighbor]
        if attribute in node.keys():
            if node[attribute] == value:
                accum = accum + 1
    return accum / len(neighbors)


def get_network_features_for_one_node(G, target, attribute):
    """
    Returns a dictionary object containing the network-derived features for a
    single node, including proportion of neighbor nodes with the same attribute

    Parameters
    ----------
    G : networkx graph object
        The networkx graph object
    target : string
        The business id mapping to the node
    attribute: String
        The name of the attribute to query

    Returns
    -------
    The dictionary object contianing network-derived features
    """
    import networkx as nx
    features = {
        attribute: G.nodes[target][attribute],
        'business_id': target,
        'degree': G.degree(target),
        'prop.attribute.true': get_count_of_neighbor_attribute(G, target, attribute, True)
    }
    return(features)

def get_features_for_all_nodes(G,  attribute):
    """
    Returns a list of dictionaries, where each dictionary contains the network-
    derived features for a node

    Parameters
    ----------
    G : networkx graph object
        The networkx graph object
    df : pandas dataframe
        A pandas dataframe containing the
    attribute: String
        The name of the attribute to query
    value : Varies, usually boolean
        The value to compare against the atrtibute of the neighbor's nodes

    Returns
    -------
    The count of neighbor nodes contianing the value of the provided attributes
    """
    import networkx as nx
    feature_list = []
    for node in G.nodes:
        feature_list.append(get_network_features_for_one_node(G, node, attribute))

    deg_cent = nx.degree_centrality(G)
    for i in range(len(feature_list)):
        feature = feature_list[i]
        feature['degree_centrality'] = deg_cent[feature['business_id']]
        feature_list[i] = feature


    return(feature_list)
