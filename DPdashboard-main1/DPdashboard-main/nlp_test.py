import argparse

from google.cloud import language_v1

def main(text):
    client = language_v1.LanguageServiceClient()
    document = language_v1.Document(
        content=text,
        type=language_v1.Document.Type.PLAIN_TEXT)
    response = client.classify_text(document=document)

    for category in response.categories:
        print(u'=' * 20)
        print(u'{:<16}: {}'.format('name', category.name))
        print(u'{:<16}: {}'.format('confidence', category.confidence))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('text', help="The text to be classified. " "The text needs to have at least 20 tokens.")
    args = parser.parse_args()
    main(args.text)