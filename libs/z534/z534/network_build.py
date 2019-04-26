def buildBusinessUserList(db, business_category=None, state=None, city=None):
    """
    Constructs a list of businesses and reviews, for a given city and business
    category, which can be used to construct a final edge list for a network
    representation. Returns a long-format list of business reviews. For example,
    if one business was associated with 10 reviews, then that business would
    appear 10 times in the output list.

    Parameterss
    ----------
    db : pymongo object
        The pymongo object that can be used to query the database
    state :
        The state within which to query businesses, e.g., AZ, NC, PA
    business_category:
        The business category to query for, e.g., Restraunt, Cafe, etc.

    Returns
    -------
    out:
        A list of JSON objects, each representing a single combination of a
        business and a review.
    """
    import pymongo
    from .mongo_utils import build_filter_pipeline

    # Construct the query pipeline
    pipeline = build_filter_pipeline(business_category, state, city)

    rest_of_pipeline = [
        {'$unwind': '$list_of_categories'},
        {'$match': {'list_of_categories': business_category}},
        {'$lookup':
            {
                'localField': 'business_id',
                'from': 'reviews',
                'foreignField': 'business_id',
                'as': 'review_info'
            }
        },
        {'$unwind': '$review_info'},
        {'$project':
            {
                'business_id': '$business_id',
                'user_id': '$review_info.user_id'
            }
        },
        {'$group': {
            '_id': '$user_id',
            'businesses': {'$push': '$business_id'},
            "count": { "$sum": 1 }
        }},
        {'$match': {'count': {'$gt': 1}}}
    ]

    # add the remaining instructions
    pipeline.extend(rest_of_pipeline)

    # Execute the query on the database
    out = list(db.businesses.aggregate(pipeline, allowDiskUse=True))

    # Return the output
    return(out)

def buildCategoryCategoryList(db, business_category=None, state=None, city=None):
    """
    Constructs a list of businesses and categories, where each business is
    associated with a list of categories, which can be used to construct a
    network representation. For example, if one business is a food truck that
    serves tacos, then their associated categories might be:
    ['Restaurant', 'Food Truck', "Taco", "Mexican"]
    if one business was associated with 10 reviews, then that business would
    appear 10 times in the output list.

    Parameterss
    ----------
    db : pymongo object
        The pymongo object that can be used to query the database
    state :
        The state within which to query businesses, e.g., AZ, NC, PA

    Returns
    -------
    out:
        A list of JSON objects, each representing a single business with
        associated categories
    """
    import pymongo
    from .mongo_utils import build_filter_pipeline

    pipeline = build_filter_pipeline(business_category, state, city)

    # Construct the query pipeline
    rest_of_pipeline = [
        {'$unwind': '$list_of_categories'},
        {'$match':
            {'categories': {'$regex': 'Restaurants'},
             'list_of_categories': {'$ne': 'Restaurants'}
            }
        },
        {'$match': {'list_of_categories': {'$ne': 'Food'}}},
        {'$project':
            {
                'category': '$list_of_categories',
                'business_id': '$business_id'
            }
        },
        {'$group':
            {
                '_id': '$business_id',
                'categories': {'$push': '$category'},
            }
        }
    ]

    pipeline.extend(rest_of_pipeline)

    # Execute the query on the database
    out = list(db.businesses.aggregate(pipeline, allowDiskUse=True))

    # Return the output
    return(out)


def buildNodeDataFile(db, business_category=None, state=None, city=None):
    """
    Constructs a node datafile to complement network analysis. Each row
    correpsonds to a single business from a provided state. Each row contains
    basic information about that restraunt such as its name, rating, etc.,

    Parameterss
    ----------
    db : pymongo object
        The pymongo object that can be used to query the database
    state :
        The state within which to query businesses, e.g., AZ, NC, PA

    Returns
    -------
    out:
        A list of JSON objects, each representing a single business with
        associated information
    """
    import pymongo
    from .mongo_utils import build_filter_pipeline

    pipeline = build_filter_pipeline(business_category, state, city)

    rest_of_pipeline = [
        {'$project':
            {
                'id': '$business_id',
                'name': '$name',
                'city': '$city',
                'stars': '$stars',
                'review_count': '$review_count',
                'categories': '$categories'
            }
        }
    ]

    # add the remaining instructions
    pipeline.extend(rest_of_pipeline)

    # Execute the query on the database
    out = list(db.businesses.aggregate(pipeline, allowDiskUse=True))

    return(out)

def build_attribute_co_occurence_list(db, business_category=None, state=None, city=None):
    """
    Takes as input a list of businesses, and outputs a co occurence list of
    attributes that can be used in the buildEdgeList function.

    Parameterss
    ----------
    businesses : JSON
        A list of JSON objects representing each business

    Returns
    -------
    out:
        A list of lists that can be used in the buildEdgeList functions
    """
    from .mongo_utils import build_filter_pipeline
    from .features import simplify_attribute_values
    import pymongo

    pipeline = build_filter_pipeline(business_category, state, city)

    businesses = list(db.businesses.aggregate(pipeline, allowDiskUse=True))

    variable_keys = ['Alcohol', 'NoiseLevel', 'RestaurantsAttire', 'WiFi']
    occurence_list = []

    for item in businesses:
        if 'attributes_flat' in item.keys():
            attr_list = []
            attr = item['attributes_flat']
            for key in attr.keys():
                attr = simplify_attribute_values(attr)
            # Now repeat the loop, now that we may have added attributes
            for key in attr.keys():
                if attr[key] == True:
                    attr_list.append(key)

        occurence_list.append(attr_list)

    return(occurence_list)


def buildEdgeList(co_occurence_list, column_name=None, threshold=1):
    """
    Given a list of JSON objects, as returned from `buildBusinessUserList`,
    constructs a final edge list, where each edge contains a Source and Target
    node, and a weight that specifies the count of co-occurence reviews.

    Parameterss
    ----------
    business_review_list : list
        The list of business review JSON objects to process
    column_name : string
        If calculating on a list of dictionaries, then the column name containing
        the list. If computing on a list of lists, then leave empty
    review_count_threshold :
        The minimum weight of an edge to include in the final node set

    Returns
    -------
    out:
        A list of edges containing a column for source node, target node,
        and edge weight
    """

    import itertools

    # Create a dictionary to contain edge weights for each combination of
    # businesses.
    edges = {}
    for item in co_occurence_list:
        # generate all combinations of businesses ids reviewed by a single user
        combos = []
        if column_name is None:
            # Assuming that it is a list of lists.
            combos = list(itertools.combinations(item, 2))
        else:
            combos =list(itertools.combinations(item[column_name], 2))

        for combo in combos:
            business1 = combo[0]
            business2 = combo[1]

            # Place the businesses into a frozenset, a data structure for
            # which order doesn't matter. Out final network is not directed,
            # so we would want to discount order
            key = frozenset((business1, business2))

            # Instantiate the business pair, or increment it by 1
            edges[key] = edges.get(key, 0) + 1

    # Now convert into a usable format. THis might have made sense to place
    # in its own function, but it didn't feel useful to have the above loop
    # by itself, it only really makes sense together with the below loop.
    edgelist = []
    for item in edges.items():
        # Retreive values from the frozenset
        node_set = item[0]
        # we need this because some of the combinations were not properly formed
        if (len(node_set) == 2):
            # Extract items from the frozen set, order here doesn't matter
            val1, val2 = item[0]
            count = item[1]

            # If the weight is above the provided threshold, then add to the
            # final edge list
            if (count > threshold):
                edgelist.append({'source': val1, 'target': val2, 'weight': count})

    return(edgelist)


def build_and_save_edgefile(db,
                           filename='edges.csv',
                           business_category=None,
                           state=None,
                           city=None,
                           backbone_extract = True,
                           backbone_alpha = 0.4,
                           ):
    """

    """
    import pandas as pd
    import networkx as nx
    from .network_utils import extract_backbone

    print("Building business-review list")
    business_review_list = buildBusinessUserList(db,
                                                business_category=business_category,
                                                state = state,
                                                city=city)

    print("Building edgelist")
    edgelist = buildEdgeList(business_review_list, column_name="businesses", threshold=1)
    edge_df = pd.DataFrame(edgelist)

    G = nx.from_pandas_edgelist(edge_df, edge_attr=True)

    if (backbone_extract):
        print("Extracting backbone")
        G = extract_backbone(G, backbone_alpha)

    # Save edge list
    print('Saving the file')
    nx.write_edgelist(G, filename)
    print('Done')

    # Done, return the graph object
    return(G)


def apply_attributes_to_graph(db,
                              G,
                              business_category=None,
                              state=None,
                              city=None
                            ):
    """


    """
    import pandas as pd
    import networkx as nx
    from .mongo_utils import get_filtered_businesses
    from .features import extract_baseline_features
    from .network_utils import set_business_node_attributes

    print("Getting filtered business list")
    businesses = get_filtered_businesses(db,
                                         business_category=business_category,
                                         state=state,
                                         city=city)

    print("Extracting baseline features")
    df = extract_baseline_features(businesses, num_miss = 500)

    relevant_attributes = [
                       'hours.OpenBreakfast',
                       'hours.OpenDinner',
                       'hours.OpenLate',
                       'hours.OpenLunch',
                       'attributes.BikeParking',
                       'attributes.GoodForKids',
                       'attributes.casual_attire',
                       'attributes.free_wifi',
                       'attributes.high_price',
                       'attributes.loud_noise_level',
                       'attributes.serves_alcohol',
                       'attributes.BusinessAcceptsCreditCards',
                       'attributes.HasTV',
                       'attributes.RestaurantsTakeOut',
                       'attributes.RestaurantsReservations',
                       'attributes.OutdoorSeating',

                      ]

    print("Setting node attributes on networkx graph")
    G = set_business_node_attributes(G, df, relevant_attributes)

    print('Done')
    return(G)
