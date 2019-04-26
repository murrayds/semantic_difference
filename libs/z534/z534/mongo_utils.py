def unwindBusinessCategories(db, verbose=False):
    """
    Performs the "unwinding" step on the Business table in the MongoDB table.
    This step involves splitting the list of business categories, represented
    as a string of concatenated categories separated by a comma, into a list
    of strings. The MongoDB database is updated to include this new separated
    list.

    Parameters
    ----------
    db : pymongo object
        The pymongo object that can be used to get the database information
    verbose: boolean
        True if progress should be printed. False otherwise

    Returns
    -------
    Nothing. This is not a strict function, as it updates the state of the
    pymongo database
    """
    import pymongo

    bus_col = db['businesses']
    busCursor = bus_col.find({})

    # These will end up not being used if verbose is not set to true, but
    # they should be initialized just in case
    running_count = 0
    num_documents = 0

    if(verbose):
        print("unwindBusinessCategories: 0% complete")
        num_documents = bus_col.count_documents({})

    for c in busCursor:
        if c['categories'] != None:
            mylist = c['categories'].split(', ')
            bus_col.update_one({'_id': c['_id']}, {'$set':{'list_of_categories' : mylist}})

        if (verbose):
            # If we have passed an increment of 5 percnet, then print
            printProgressBar(running_count, num_documents, length=50)

            # increment the running_count
            running_count = running_count + 1

def get_db(hostname='mongodb://localhost:27017/', db_name='yelp', create_index=True):
    """
    Helper function to access running pymongo client and return a reference
    to a select database

    Parameters
    ----------
    hostname : string
        String containing the hostname for the running mongodb instance. Defaults
        to localhost.
    db_name: string
        Name of the database from the running mondodb database to access. Defaults
        to 'yelp'
    create_index: boolean
        Indicates whether the business_id variable should be converted to an
        index or not

    Returns
    -------
    A reference to the database object from the running mongodb instance
    """
    import pymongo
    client = pymongo.MongoClient(hostname)
    db = client[db_name]

    if (create_index):
        db.reviews.create_index([('business_id', pymongo.ASCENDING)], unique=False)
        db.business.create_index([('business_id', pymongo.ASCENDING)], unique=True)

    return(db)


def aggregate_city_state(db, state, threshold):
    """
    Helper function to perform an aggregation over a city and state

    Parameters
    ----------
    db : pymongo object
        The pymongo object that can be used to get the database information
    state: string
        The state to match in the aggregation. Only cities in this state will
        be aggregated
    threshold: boolean
        Minimum number of businesses within a city for that city to be included
        in the final output

    Returns
    -------
    A dictionary containing the count of businesses in each city for the
    selected state.
    """
    import pymongo

    pipeline = [
        {'$match': {'state': state}},
        {'$group': {
            '_id': {'city': '$city', "state": '$state'},
            "count": { "$sum": 1 }
        }},
        {'$match': {'count': {'$gt': threshold}}},
        {'$sort' : { 'count' : -1} }
    ]

    out = list(db.businesses.aggregate(pipeline, allowDiskUse=True))
    return(out)

def process_attributes(db, verbose=False):
    """
    The attributes were not in a usable format when originally uploaded to
    MongoDd. Most values were stored as strings, rather than their actual type.
    This included sub-dictionaries, which made parsing difficult.

    This code updates the businesses table in MongoDb, replaces the existing
    mongodb attributes field with a type-parsed verison, and creates a second
    field called 'attributes_flat'. This field contians the same attribtes, but
    in a 'flattened' format, such that all sub-dictioanries are placed on the
    same level as the outer dictionary.

    Parameters
    ----------
    db : pymongo object
        The pymongo object that can be used to get the database information
    verbose: boolean
        True if progress should be printed. False otherwise

    Returns
    -------
    Nothing. This is not a strict function, as it updates the state of the
    pymongo database
    """
    import pymongo
    from ast import literal_eval

    # Ideally, we would save these as separate text fines, or find some way
    # to automatically infer them from the database. However, this is a fine
    # solution since we won't need to extend the data in the future
    nested_keys = ['BusinessParking', 'GoodForMeal', 'Ambience']
    variable_keys = ['Alcohol', 'NoiseLevel', 'RestaurantsAttire', 'WiFi']

    running_total = 0
    number_documents = 0
    if (verbose):
        number_documents = db.businesses.count_documents({})

    # Begin by iterating over all businesses
    for i in db.businesses.find({}):
        attr = i['attributes'] # select the attributes field
        if attr is not None: # Make sure that it exists
            # Iterate over all attribute keys
            keys = attr.keys()
            for one_key in keys:
                # If the sub-dictionaires have yet to be converted...
                if one_key in nested_keys and type(attr[one_key]) is str:
                    attr[one_key] = ast.literal_eval(attr[one_key])
                # These are already stirngs, and cost is minimal, so little
                # is lost by always performing this operation
                elif one_key in variable_keys:
                    str_to_fix = attr[one_key]
                    str_to_fix = str_to_fix.replace('u\'', '')
                    str_to_fix = str_to_fix.replace('\'', '')
                    str_to_fix = str_to_fix.lower()
                    attr[one_key] = str_to_fix
                else:
                    # This is not pretty—it is a try block becuase I want to
                    # convert booleans and numbers and such to their literal value,
                    # but in some cases this will try to literally eval a normal string,
                    # which will cause an error. In those cases, we just want to skip
                    # to the next row.
                    try:
                        attr[one_key] = literal_eval(attr[one_key])
                    except:
                        continue

            attr_flat = flatten_json(attr)

            db.businesses.update_one({'_id': i['_id']}, {'$set':{'attributes' : attr}})
            db.businesses.update_one({'_id': i['_id']}, {'$set':{'attributes_flat' : attr_flat}})

        if (verbose):
            printProgressBar(running_total, number_documents)
            running_total = running_total + 1

# I pulled this from code over in the Task1 directory, in the create_trec_qrel directory
# from: https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
    if iteration == total:
        print()


def flatten_json(y):
    """
    a simple function that recursively flattens a JSON obejct such that all
    sub-dictionaires are projected onto the top level. I took this code from
    the following website:

    https://towardsdatascience.com/flattening-json-objects-in-python-f5343c794b10

    Parameters
    ----------
    y: json
        JSON object to be flattened

    Returns
    -------
    Flattened version of JSON file
    """
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '_')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out


def build_filter_pipeline(business_category=None, state=None, city=None, review_count = 5):
    """
    Helper function that builds a mongodb aggregation pipeline for filtering
    data.

    Parameters
    ----------
    business_category : string
        String representing the business category to use when building the
        filter pipeline. If none, then this rule is not added
    state : string
        String representing the state to use when building the  filter pipeline.
        If none, then this rule is not added
    city : string
        String represmenting the city to use when building the  filter pipeline.
        If none, then this rule is not added

    Returns
    -------
    A list of json objects representing filter rules to use as part of a mongodb
    aggregate pipeline
    """
    pipeline = []

    # Filter by category
    if business_category is not None:
        category_match = {
            '$match': {
                'list_of_categories': business_category
            }
        }
        pipeline.append(category_match)

    # filter by state
    if state is not None:
        state_match = {
            '$match': {
                'state': state
            }
        }
        pipeline.append(state_match)

    # Filter by city
    if city is not None:
        city_match = {
            '$match': {
                'city': city
            }
        }
        pipeline.append(city_match)

    # Filter by number of reviews
    review_count_match = {
        '$match': {
            'review_count': {
                '$gt': review_count
            }
        }
    }
    pipeline.append(review_count_match)

    return(pipeline)


def get_filtered_businesses(db, business_category=None, state=None, city=None):
    """
    Queries and filters the businesses database by business category, state,
    and city. Data is returned as a list.
    """
    pipeline = build_filter_pipeline(business_category, state, city)
    return(list(db.businesses.aggregate(pipeline, allowDiskUse=True)))


def aggregate_reviews(db, business_category=None,
                          state=None,
                          city=None,
                          split=None,
                          review_count=5):
    """
    Collects the reviews for all businesses, filtered to the given category,
    state, or city optionally split on a value
    """
    import pymongo
    pipeline = build_filter_pipeline(business_category,
                                     state=state,
                                     city=city,
                                     review_count=review_count)
    pipeline.extend(
        [
            {'$lookup': {
                'from': 'reviews',
                'localField': 'business_id',
                'foreignField': 'business_id',
                'as': 'reviews'
                }
            },
            {'$unwind': '$reviews'},
            {'$project':
                {
                    'business_id': '$business_id',
                    'text': '$reviews.text',
                }
            },
        ]
    )

    if split is not None:
        pipeline[-1]['$project'][split] = '$reviews.{}'.format(split)

    cursor = db.businesses.aggregate(pipeline)

    if split is not None:
        split1_list = []
        split2_list = []
        for item in cursor:
            if int(item[split]) > 3:
                split1_list.append(item)
            elif int(item[split]) < 3:
                split2_list.append(item)
        return((split1_list, split2_list))
    else:
        bus_list = []
        for item in cursor:
            bus_list.append(item)
        return(bus_list)


def get_categories(file):
    import json

    with open(file) as json_file:
        yelp_categories = json.load(json_file)

    categories = []
    for category in yelp_categories:
        categories.append(category['title'])
    return categories


def get_business_ids_by_category(db, filename):
    import pymongo
    import json
    import re

    business_ids_by_category = []
    for category in get_categories(filename):
        business_ids_by_category.append((category,
                                         [x['business_id'] for x in db.businesses.aggregate([
            { '$match': {
                    'categories': {
                        '$regex': re.compile(category) } } },
            { '$project': {
                    '_id': 0,
                    'business_id': 1 } },
            { '$group': {
                    '_id': None,
                    'business_id': {
                        '$push': '$business_id' } } },
            { '$project': {
                    '_id': 0 } }
        ])]))
    return business_ids_by_category


def get_reviews_by_business_id_dict(db):
    import pymongo

    reviews_by_business_id = db.docs.aggregate([
        {
            '$group': {
                '_id': '$business_id',
                'reviews': {
                    '$push': '$text'
                }
            }
        }
    ], allowDiskUse=True, batchSize=128)

    reviews_by_business_id_dict = {}
    for x in reviews_by_business_id:
        reviews_by_business_id_dict[x['_id']] = x['reviews']

    return reviews_by_business_id_dict

def get_yelp_category_lookup(file):
    import json

    with open(file) as json_file:
        yelp_categories = json.load(json_file)

    yelp_category_lookup = {}
    for category in yelp_categories:
        yelp_category_lookup[category['title']] = category['alias']

    return yelp_category_lookup
