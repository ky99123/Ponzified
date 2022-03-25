import numpy as np
import pandas as pd
from joblib import dump, load
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.feature_selection import SelectFromModel
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from matplotlib import pyplot as plt
import seaborn as sns


# Getting test data


def import_data(feature_file, target_file):
    feature_df = pd.read_csv(feature_file)
    target_df = pd.read_csv(target_file)
    target_array = target_df.values.ravel()
    feature_df = feature_df.drop(columns=['s/n', 'Index'])
    feature_df = feature_df._get_numeric_data().fillna(0)
    feature_array = feature_df.values
    print(feature_df.shape)
    print(target_df.shape)

    return feature_df, feature_array, target_array


def split_dataset(feature_df, target_df):
    X_train, X_test, y_train, y_test = train_test_split(feature_df, target_df,
                                                        test_size=0.3)
    return X_train, X_test, y_train, y_test


def select_features(X_train, y_train, X_test, n_features):
    fs = SelectFromModel(RandomForestClassifier(n_estimators=1000),
                         max_features=n_features)
    fs.fit(X_train, y_train)
    print(fs.get_support(indices=True))
    X_train_fs = fs.transform(X_train)
    X_test_fs = fs.transform(X_test)
    return X_train_fs, X_test_fs, fs


def train_model(feature_df, target_df):
    X_train, X_test, y_train, y_test = split_dataset(feature_df, target_df)

    RF_model = RandomForestClassifier()
    RF_model.fit(X_train, y_train)

    y_pred = RF_model.predict(X_test)

    print("Full Feature Accuracy: %.2f%%" % (
                accuracy_score(y_test, y_pred) * 100))

    dump(RF_model, 'model.joblib')


def train_model_with_fs(feature_df, target_df, n_feature):
    X_train, X_test, y_train, y_test = split_dataset(feature_df, target_df)
    X_train_fs, X_test_fs, fs = select_features(X_train, y_train, X_test,
                                                n_feature)
    RF_model_with_fs = RandomForestClassifier()
    RF_model_with_fs.fit(X_train_fs, y_train)
    y_pred_fs = RF_model_with_fs.predict(X_test_fs)

    print("%d Feature Accuracy: %.2f%%" % (
    n_feature, (accuracy_score(y_test, y_pred_fs) * 100)))

    dump(RF_model_with_fs, 'model_fs25.joblib')

    return fs.get_support(indices=True)


def train_final_model(feature_df, target_df):
    X_train, X_test, y_train, y_test = split_dataset(feature_df, target_df)

    Fin_RF_model = RandomForestClassifier()
    Fin_RF_model.fit(X_train, y_train)

    y_pred = Fin_RF_model.predict(X_test)

    print("Final Model Accuracy: %.2f%%" % (
            accuracy_score(y_test, y_pred) * 100
    ))

    print(classification_report(y_test, y_pred))
    plot_CF(y_test, y_pred)

    return Fin_RF_model


def plot_CF(y_test, y_pred):
    # Get and reshape confusion matrix data
    matrix = confusion_matrix(y_test, y_pred)
    matrix = matrix.astype('float') / matrix.sum(axis=1)[:, np.newaxis]

    # Build the plot
    plt.figure(figsize=(16, 7))
    sns.set(font_scale=1.4)
    sns.heatmap(matrix, annot=True, annot_kws={'size': 10},
                cmap=plt.cm.Greens, linewidths=0.2)

    # Add labels to the plot
    class_names = ['No Fraud', 'Fraud']
    tick_marks = np.arange(len(class_names))
    tick_marks2 = tick_marks + 0.5
    plt.xticks(tick_marks, class_names, rotation=25)
    plt.yticks(tick_marks2, class_names, rotation=0)
    plt.xlabel('Predicted label')
    plt.ylabel('True label')
    plt.title('Confusion Matrix for Random Forest Model')
    plt.show()


def initial_training():
    feature_file = "transaction_dataset_clean.csv"
    target_file = "transaction_dataset_target.csv"

    feature_df, feature_arr, target_arr = import_data(feature_file, target_file)

    train_model(feature_arr, target_arr)
    # for i in range(40, 4, -5):
    #     train_model_with_fs(feature_df, target_df, i)

    feature_header = train_model_with_fs(feature_arr, target_arr, 25)
    for x in feature_header:
        print(list(feature_df.columns)[x])


def refined_training():
    feature_file = "transaction_dataset_clean_FS.csv"
    target_file = "transaction_dataset_target.csv"

    feature_df, feature_arr, target_arr = import_data(feature_file, target_file)
    print("Training Final Model")
    train_final_model(feature_arr, target_arr)


def refined_training_lessERC():
    feature_file = "transaction_dataset_clean_FS_lessERC.csv"
    target_file = "transaction_dataset_target.csv"

    feature_df, feature_arr, target_arr = import_data(feature_file, target_file)
    print("Training Final Model without ERC")
    Final_Model = train_final_model(feature_arr, target_arr)
    dump(Final_Model, 'Final.joblib')


def predict(predict_data_array):
    model = load('Final.joblib')
    input_data = np.array(predict_data_array)
    ret = model.predict([input_data])[0]
    print("Predicted Output: " + str(ret))
    return ret


def diagnostics():
    # feature_file = "transaction_dataset_clean_FS_lessERC.csv"
    # target_file = "transaction_dataset_target.csv"
    # feature_df, feature_arr, target_arr = import_data(feature_file, target_file)
    # i = 0
    # for wallet in feature_arr:
    #     print("Actual: " + str(target_arr[i]))
    #     predict(wallet)
    #
    #     i += 1
    wallet = [844.26, 1093.71, 704785.63, 721, 89, 40, 0, 45.80679, 6.589513, 0, 31.22, 1.200681, 810, 865.6910932, 586.4666748, -279.2244185]
    predict(wallet)


def main():
    # initial_training()
    # refined_training()
    refined_training_lessERC()
    pass


if __name__ == "__main__":
    main()
