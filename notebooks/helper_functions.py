import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import cross_val_score, learning_curve, RepeatedKFold
from sklearn.metrics import classification_report, confusion_matrix, auc


def metric_evaluation(model, X, y, cv: int = 5, model_name: str = "Model",
                      print_results: bool = True, plot_results: bool = True):
    """
    The function evalutes the model on five metrics using cross validation scores for each and plots them.
    The six metrics are:
    1. Accuracy
    2. Weighted Precision
    3. Weighted Recall
    4. Weighted F1 score
    5. Area under the ROC curve
    
    Notes:
        The higher the value of the metric, the better. 
    
    Args:
        model (object): An instantiated object of a sklearn classifier.
        X (np.ndarray or pd.DataFrame): Contains the features from the dataset.
        y (np.ndarray or pd.DataFrame): Contains the target or response varible from the dataset.
        cv (int): number of folds in the cross validation score.
        model_name (str): A nickname for the model.
        print_results (bool): prints the performance dataframe if True. Default True.
    
    Returns:
        performance_df (pd.DataFrame): A dictionary containing the five performance metrics.
    """
    
    # Setting up random seed to ensure all models are evaluated on same data splits
    np.random.seed(100)

    # Creating a list of metrics
    metrics_list = ['accuracy', 'precision_weighted', 'recall_weighted', 'f1_weighted', 'roc_auc']
    performance_dict = {}

    for metric in metrics_list:
        metric_score = cross_val_score(model, X, y, cv=cv, scoring=metric)
        performance_dict.update({metric: metric_score})
        
    performance_df = pd.DataFrame(performance_dict).round(3).T
    performance_df.columns = [f"Cross Val {n}" for n in range(1, len(metric_score)+1)]
    
    if plot_results:
        # Instantiating figure
        fig, ax = plt.subplots(figsize=(10,7))

        # plotting data
        performance_df.T.plot.bar(ax=ax)

        # Formatting title and axes
        ax.set_title(f"Cross Validation scores of the {model_name}", 
                    fontdict={"fontsize":20, "fontweight":'bold'},
                    pad=30)

        ax.set_xlabel("Cross Validation Fold number", fontsize=14, fontweight='bold', labelpad=20)
        ax.set_ylabel("Cross Validated scores of the Metric", 
                    fontsize=14, fontweight='bold', labelpad=20)

        plt.xticks(fontsize=12, rotation=0)
        plt.yticks(fontsize=12)


        # Formatting legend
        leg = ax.legend(fontsize=12, loc=(1.02, 0.81), frameon=True)
        leg.get_frame().set_color("#F2F2F2")
        leg.get_frame().set_edgecolor("#000000")
        leg.set_title("Estimator", prop={"size": 14, "weight": 'bold'})

    # Displaying Results
    if print_results:
        print(f"######### {model_name}: Averaged Cross Validated Scores ##########")
        print("Accuracy score:            {accuracy: 0.2%}\n"
              "Weighted Precision score:  {precision_weighted: 0.2%}\n"
              "Weighted Recall score:     {recall_weighted: 0.2%}\n"
              "Weighted F1 score:         {f1_weighted: 0.2%}\n"
              "ROC Area Under Curve:      {roc_auc: .3f}".format(**dict(performance_df.T.mean())))
    
    # Print statement to know completion, incase of function being called multiple times in a cell.
    print(f"{model_name} Model evaluation complete.") 

    return performance_df


def plot_learning_curves(model, X, y):
    """
    The function plots the learning curve for the input model.

    Args:
        model (object): An instantiated object of a sklearn classifier.
        X (np.ndarray or pd.DataFrame): Contains the features from the dataset.
        y (np.ndarray or pd.DataFrame): Contains the target or response varible from the dataset.
    """
    train_sizes, train_scores, test_scores = learning_curve(estimator=model,
                                                            X=X, 
                                                            y=y,
                                                            train_sizes= np.linspace(0.1, 1.0, 10),
                                                            cv=10,
                                                            scoring='recall_weighted',random_state=100)
    train_mean = np.mean(train_scores, axis=1)
    train_std = np.std(train_scores, axis=1)
    test_mean = np.mean(test_scores, axis=1)
    test_std = np.std(test_scores, axis=1)
    
    plt.plot(train_sizes, train_mean,color='blue', marker='o', 
             markersize=5, label='training recall')
    plt.fill_between(train_sizes, train_mean + train_std, train_mean - train_std,
                     alpha=0.15, color='blue')

    plt.plot(train_sizes, test_mean, color='green', linestyle='--', marker='s', markersize=5,
             label='validation recall')
    plt.fill_between(train_sizes, test_mean + test_std, test_mean - test_std,
                     alpha=0.15, color='green')
    plt.grid(True)
    plt.xlabel('Number of training samples')
    plt.ylabel('Recall')
    plt.legend(loc='best')
    plt.show()
    

def plot_box_plot(model, X, y, model_name: str = "Model", scoring: str = "recall_weighted",
                  models: list = []):
    """The function plots a box plot for the scoring parameter defined.

    Args:
        model (object): An instantiated object of a sklearn classifier.
        X (np.ndarray or pd.DataFrame): Contains the features from the dataset.
        y (np.ndarray or pd.DataFrame): Contains the target or response varible from the dataset.
        model_name (str, optional): Name of the model used. If None, uses `Decision Tree`. Defaults to None.
        scoring (str, optional): The scoring parameter to be used. Defaults to "recall_weighted".
        models (list, optional): A list of `model`s. Defaults to [].
    """

    if not models:
        models.append((model_name, model))

    results =[]
    names=[]
    scoring ='recall_weighted'
    metric = scoring.replace('_', ' ').capitalize()
    print(f'Model Evaluation - {metric}')
    for name, model in models:
        rkf = RepeatedKFold(n_splits=10, n_repeats=5, random_state=100)
        cv_results = cross_val_score(model, X, y, cv=rkf, scoring=scoring)
        results.append(cv_results)
        names.append(name)
        print('{} {:.2f} +/- {:.2f}'.format(name,cv_results.mean(),cv_results.std()))
    print('\n')

    fig = plt.figure(figsize=(5,5))
    fig.suptitle('Boxplot View')
    ax = fig.add_subplot(111)
    sns.boxplot(data=results)
    ax.set_xticklabels(names)
    plt.ylabel(metric)
    plt.xlabel('Model')
    plt.show()
    pass


def full_model_evaluation(model, X, y, model_name: str = None):
    """
    The function does the following 4 things:
    1. Plot the learning curve.
    2. Plot a boxplot for weighted recall.
    3. Plot the cross validation scores of 5 metrics.
    """
    
    if model_name is None:
        model_name = "Decision Tree"

    # Plot learning curve
    print(f'{model_name} Learning Curve')
    plot_learning_curves(model, X, y)
    
    # Model Evaluation - Boxplot
    plot_box_plot(model, X, y, model_name)
    
    # Evaluate the performance
    metric_evaluation(model, X, y)
