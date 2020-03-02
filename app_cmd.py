import os
import json
import argparse
from app import ner_trainer, pdf_extractor, config


parser = argparse.ArgumentParser()
parser.add_argument("-M", "--model", help="filepath to store model")
parser.add_argument("-f", "--file", required=True, help="Original CV filepath")
argument = parser.parse_args()


def cvparser(test_size, n_iter, early_stopping, model, dropout):

    # Invoke class
    ne = ner_trainer.NERspacy(test_size, n_iter, early_stopping, model)

    # Get training data and testing data
    train, test = ne.convert_dataturks_to_spacy(ne.data)

    # Parse content from original CV
    cv_filepath = argument.file
    content = pdf_extractor.extract_pdf_content(cv_filepath)

    with open(argument.file + '.txt', 'w') as f:
        f.write(content.replace('\n', '.'))

    if argument.model:
        model_filepath = argument.model
    else:
        model_filepath = ne.train_spacy(train, test, dropout)
    output = ner_trainer.predict_spacy(content, model_filepath)

    if 'prediction' not in os.listdir('.'):
        os.mkdir('prediction')

    with open("prediction/ner_prediction.json", "w") as f:
        json.dump(output, f)

    return output


cvparser(
    test_size=config.SpacyTraining.test_size,
    n_iter=config.SpacyTraining.n_iter,
    early_stopping=config.SpacyTraining.early_stopping,
    model=config.SpacyTraining.model,
    dropout=config.SpacyTraining.dropout,
)
if __name__ == "__main__":
    pass
