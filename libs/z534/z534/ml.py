def preprocess_labels(y_train, y_test):
    """
    Pre-processes the label training and testing data. The main operaiton being performed
    is encoding the labels using sklearn's LabelEncoder object

    Parameters
    ----------
    y_train : list
        label trianing data
    y_test : list
        label testing data

    Returns
    -------
    y_train and y_test, updated with label encoding

    """
    from sklearn import preprocessing
    le = preprocessing.LabelEncoder()
    le.fit(y_train)
    y_train = le.transform(y_train)
    y_test = le.transform(y_test)
    return(y_train, y_test)

def train_logistic_model(X_train, y_train):
    """
    Trains a logistic regression model using provided training and testing data.

    Parameters
    ----------
    x_train : list
        feature training data
    y_train : list
        label trianing data

    Returns
    -------
    trained sklearn logistic regression model object
    """
    from sklearn.linear_model import LogisticRegression

    gnb = LogisticRegression(solver='lbfgs')

    # Train classifier
    gnb.fit(
        X_train,
        y_train
    )

    return(gnb)


def train_rf_model(X_train, y_train):
    """
    Trains a logistic regression model using provided training and testing data.

    Parameters
    ----------
    x_train : list
        feature training data
    y_train : list
        label trianing data

    Returns
    -------
    trained sklearn logistic regression model object
    """
    from sklearn.ensemble import RandomForestClassifier

    gnb = RandomForestClassifier(n_estimators=100, max_depth=2, random_state=0)

    # Train classifier
    gnb.fit(
        X_train,
        y_train
    )

    return(gnb)


def train_svm_model(X_train, y_train):
    """
    Trains a logistic regression model using provided training and testing data.

    Parameters
    ----------
    x_train : list
        feature training data
    y_train : list
        label trianing data

    Returns
    -------
    trained sklearn logistic regression model object
    """
    from sklearn import svm

    gnb = svm.SVC(gamma='scale')

    # Train classifier
    gnb.fit(
        X_train,
        y_train
    )

    return(gnb)


def get_metrics(y_true, y_pred):
    """
    Returns a set of performance metrics

    Parameters
    ----------
    y_true : list
        true labels
    y_pred : list
        predicted labels

    Returns
    -------
    A dictionary containing a set of performance metrics including accuracy, precision, recall, and F1
    """
    from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score
    metrics = {
        "Accuracy": round(accuracy_score(y_true, y_pred), 4),
        "Precision": round(precision_score(y_true, y_pred, average='macro'), 4),
        "Recall": round(recall_score(y_true, y_pred), 4),
        "F1": round(f1_score(y_true, y_pred), 4)
    }
    return(metrics)


def run_one_network_ml_iter(G, attribute, test_size = 500, type='logistic'):
    """
    Runs a single iteration of the ML pipeline with the specified attribute.

    Parameters
    ----------
    G : networkx object
        The networkx object containing the business-review network
    attribute : string
        Name of the attribute to predict
    type : string
        Type of classifier to use, either 'logistic', 'rf', or 'svm'

    Returns
    -------
    A dictionary containing a set of performance metrics including accuracy, precision, recall, and F1
    """
    from pandas.io.json import json_normalize
    from .features import get_features_for_all_nodes, split_training_testing

    features = get_features_for_all_nodes(G, attribute)
    attr_df = json_normalize(features)

    X_train, X_test, y_train, y_test = split_training_testing(attr_df, attribute, test_size = test_size)

    y_train, y_test = preprocess_labels(y_train, y_test)

    gnb = None
    if type == 'logistic':
        gnb = train_logistic_model(X_train, y_train)
    elif type == 'rf':
        gnb = train_rf_model(X_train, y_train)
    elif type == 'svm':
        gnb = train_svm_model(X_train, y_train)

    y_pred = gnb.predict(X_test)

    metrics = get_metrics(y_test, y_pred)
    metrics['attribute'] = attribute
    metrics['num_training_observations'] = len(X_train)
    return(metrics)


def run_one_baseline_ml_iter(businesses, attribute, test_size = 500, type = 'logistic'):
    """
    Runs a single iteration of the ML pipeline with the specified attribute.

    Parameters
    ----------
    businesses : list
        List of yelp businesses
    attribute : string
        Name of the attribute to predict

    Returns
    -------
    A dictionary containing a set of performance metrics including accuracy, precision, recall, and F1
    """
    from pandas.io.json import json_normalize
    from .features import extract_baseline_features, split_training_testing

    features = extract_baseline_features(businesses, num_miss = 500)


    X_train, X_test, y_train, y_test = split_training_testing(features, attribute, test_size = test_size)
    y_train, y_test = preprocess_labels(y_train, y_test)

    gnb = None
    if type == 'logistic':
        gnb = train_logistic_model(X_train, y_train)
    elif type == 'rf':
        gnb = train_rf_model(X_train, y_train)
    elif type == 'svm':
        gnb = train_svm_model(X_train, y_train)

    y_pred = gnb.predict(X_test)

    metrics = get_metrics(y_test, y_pred)
    metrics['attribute'] = attribute
    metrics['num_training_observations'] = len(X_train)
    return(metrics)

def run_one_all_features_ml_iter(businesses, G, attribute, test_size=500, type = 'logistic'):
    """
    Runs a single iteration of the ML pipeline with the specified attribute.
    Computes both baseline and network-derived features

    Parameters
    ----------
    businesses : list
        List of yelp businesses
    G : networkx object
        The networkx object containing the business-review network
    attribute : string
        Name of the attribute to predict

    Returns
    -------
    A dictionary containing a set of performance metrics including accuracy,
    precision, recall, and F1
    """
    from pandas.io.json import json_normalize
    from .features import extract_baseline_features, get_features_for_all_nodes, split_training_testing

    baseline_features = extract_baseline_features(businesses, num_miss = 500)

    graph_features = get_features_for_all_nodes(G, attribute)
    attr_df = json_normalize(graph_features)
    attr_df = attr_df.drop(attribute, axis = 1)

    all_features = baseline_features.join(attr_df.set_index('business_id'), on = 'business_id')

    X_train, X_test, y_train, y_test = split_training_testing(all_features, attribute, test_size = test_size)
    y_train, y_test = preprocess_labels(y_train, y_test)

    gnb = None
    if type == 'logistic':
        gnb = train_logistic_model(X_train, y_train)
    elif type == 'rf':
        gnb = train_rf_model(X_train, y_train)
    elif type == 'svm':
        gnb = train_svm_model(X_train, y_train)

    y_pred = gnb.predict(X_test)

    metrics = get_metrics(y_test, y_pred)
    metrics['attribute'] = attribute
    metrics['num_training_observations'] = len(X_train)
    return(metrics)
