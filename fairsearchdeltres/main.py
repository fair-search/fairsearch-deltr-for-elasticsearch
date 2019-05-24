from fairsearchdeltr import Deltr

if __name__ == "__main__":
    import pandas as pd
    from io import StringIO

    # load some train data (this is just a sample - more is better)
    train_data_raw = """q_id,doc_id,gender,score,judgment
        1,1,1,0.962650646167003,1
        1,2,0,0.940172822166108,0.98
        1,3,0,0.925288002880488,0.96
        1,4,1,0.896143226020877,0.94
        1,5,0,0.89180775633204,0.92
        1,6,0,0.838704766545679,0.9
        """
    train_data = pd.read_csv(StringIO(train_data_raw))

    # setup the DELTR object
    protected_feature = 0  # column number of the protected attribute (index after query and document id)
    gamma = 1  # value of the gamma parameter
    number_of_iteraions = 10000  # number of iterations the training should run
    standardize = True  # let's apply standardization to the features

    # create the Deltr object
    dtr = Deltr(protected_feature, gamma, number_of_iteraions, standardize=standardize)

    # train the model
    dtr.train(train_data)