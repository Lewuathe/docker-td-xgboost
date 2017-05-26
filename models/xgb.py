#!/usr/bin/env python
import os
import xgboost as xgb
import json
import tdclient
import numpy as np
import pickle
import boto3
from optparse import OptionParser
from sklearn.externals import joblib

def load(features, target, database, table, apikey):
    '''
    Load dataset from Treasure Data
    '''
    c = tdclient.Client(apikey=apikey)
    q = "SELECT {}, {} target FROM {}.{}".format(','.join(features), target, database, table)
    print(q)
    job = c.query(database, q, type='presto')
    job.wait()
    X = []
    y = []
    for r in job.result():
        X.append([float(f) for f in r[:len(features)]])
        y.append(int(r[-1]))

    # JobID should be also used as model id
    return (job.id, np.array(X), np.array(y))

def train(args, options):
    '''
    Training API
    '''
    apikey, database, src_table = options.apikey, options.database, options.table
    features = options.features
    if not features:
        print("No features are specified")
        return
    target = options.target
    model_filename = options.model + ".pkl"

    _, X, y = load(features, target, database, src_table, apikey)

    classifier = xgb.XGBClassifier()
    print("Trainting...")
    model = classifier.fit(X, y)

    pickle.dump(model, open(model_filename, 'wb'))

    # boto3 internally checks "AWS_ACCESS_KEY_ID" and "AWS_SECRET_ACCESS_KEY"
    # http://boto3.readthedocs.io/en/latest/guide/configuration.html#environment-variables
    # Upload model file to specified S3 bucket to be used by prediction phase
    s3 = boto3.resource('s3')
    s3.Object(os.environ['AWS_BUCKET_NAME'], model_filename).put(Body=pickle.dumps(model))

    # Return model id
    print(model_filename)

def predict(args, options):
    print("Predicting...")
    apikey, database, src_table = options.apikey, options.database, options.table
    features = options.features
    if not features:
        print("No features are specified")
        return
    target = options.target
    model_filename = options.model + ".pkl"

    _, X, y = load(features, target, database, src_table, apikey)

    with open(model_filename, 'w+b') as f:
        s3 = boto3.resource('s3')
        s3.Bucket(os.environ['AWS_BUCKET_NAME']).download_fileobj(model_filename, f)
        rf = joblib.load(f)

    ret = rf.predict(X)
    os.remove(model_filename)

    print(ret)

if __name__ == '__main__':
    # python train.py <API KEY> <Database> <SrcTableName>
    parser = OptionParser()

    parser.add_option("-a", "--apikey", dest='apikey',
        help='API KEY')
    parser.add_option('-d', '--database', dest='database',
        help='Database')
    parser.add_option('-t', '--table', dest='table',
        help='Table')
    parser.add_option('-f', '--feature', dest='features',
        help='Feature Columns', action='append')
    parser.add_option('-m', '--model', dest='model',
        help='Model ID')
    parser.add_option('--target', dest='target',
        help='Target Column')

    options, args = parser.parse_args()

    print(options)

    if args[0] == 'train':
        train(args, options)
    elif args[0] == 'predict':
        predict(args, options)
