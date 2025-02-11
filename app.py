from flask import Flask, request, render_template
from flask_bootstrap import Bootstrap
from PyPDF2 import PdfReader, PdfWriter
import random
import spacy
from collections import Counter
# creating app

app = Flask(__name__)

# load english tokenizer, tagger, parser, NER, and word vectors

nlp = spacy.load("en_core_web_sm")
Bootstrap(app)

def generate_mcqs(text, num_questions=5):
    # text = clean_text(text)
    if text is None:
        return []

    # Process the text with spaCy
    doc = nlp(text)

    # Extract sentences from the text
    sentences = [sent.text for sent in doc.sents]

    # Ensure that the number of questions does not exceed the number of sentences
    num_questions = min(num_questions, len(sentences))

    # Randomly select sentences to form questions
    selected_sentences = random.sample(sentences, num_questions)

    # Initialize list to store generated MCQs
    mcqs = []

    # Generate MCQs for each selected sentence
    for sentence in selected_sentences:
        # Process the sentence with spaCy
        sent_doc = nlp(sentence)

        # Extract entities (nouns) from the sentence
        nouns = [token.text for token in sent_doc if token.pos_ == "NOUN"]

        # Ensure there are enough nouns to generate MCQs
        if len(nouns) < 2:
            continue

        # Count the occurrence of each noun
        noun_counts = Counter(nouns)

        # Select the most common noun as the subject of the question
        if noun_counts:
            subject = noun_counts.most_common(1)[0][0]

            # Generate the question stem
            question_stem = sentence.replace(subject, "______")

            # Generate answer choices
            answer_choices = [subject]

            # Add some random words from the text as distractors
            distractors = list(set(nouns) - {subject})

            # Ensure there are at least three distractors
            while len(distractors) < 3:
                distractors.append("[Distractor]")  # Placeholder for missing distractors

            random.shuffle(distractors)
            for distractor in distractors[:3]:
                answer_choices.append(distractor)

            # Shuffle the answer choices
            random.shuffle(answer_choices)

            # Append the generated MCQ to the list
            correct_answer = chr(64 + answer_choices.index(subject) + 1)  # Convert index to letter
            mcqs.append((question_stem, answer_choices, correct_answer))

    return mcqs




def process_pdf(file):
    # Initialize an empty string to store the extracted text
    text = ""

    # Create a PyPDF2 PdfReader object
    pdf_reader = PdfReader(file)

    # Loop through each page of the PDF
    for page_num in range(len(pdf_reader.pages)):
        # Extract text from the current page
        page_text = pdf_reader.pages[page_num].extract_text()
        # Append the extracted text to the overall text
        text += page_text

    return text




@app.route("/",methods=['POST','GET'])
def index():    
    if request.method == 'POST':
        text = ''  
        # check if files were uploaded
        if 'files[]' in request.files:
            files = request.files.getlist("files[]")
            # if there are more than one files
            for file in files:
                if file.filename.endswith('.pdf'):
                    # process pdf files
                    text += process_pdf(file)
                else:
                    # process text file
                    text += file.read().decode('utf-8')

        # get the selected number of questions from the dropdown menu
        num_questions = int(request.form['num_questions'])
        
        mcqs = generate_mcqs(text,num_questions=num_questions) # pass the selected numberof questions
        # print(mcqs)
        # ensure each mcq is formatted correctly as(question_stem, answer_choices, correct_answer)
        mcqs_with_index = [(i+1,mcq) for i,mcq in enumerate(mcqs)]
        # print(mcqs_with_index)
        return render_template('mcqs.html',mcqs = mcqs_with_index)

    return render_template('index.html')



# python main==
if __name__ == '__main__':
    app.run(debug=True)
