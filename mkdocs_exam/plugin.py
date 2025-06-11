from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import Files
from mkdocs.structure.pages import Page
from importlib import resources as impresources
from . import css, js
import re
inp_file = (impresources.files(css) / 'exam.css')
with inp_file.open("rt") as f:
    style = f.read()

style = '<style type="text/css">{}</style>'.format(style)

js_file = (impresources.files(js) / 'exam.js')
with js_file.open("rt") as f:
    js = f.read()

js = '<script type="text/javascript" defer>{}</script>'.format(js)

# <?exam?>
# question: Are you ready?
# answer-correct: Yes!
# answer: No!
# answer: Maybe!
# content:
# <h2>Provide some additional content</h2>
# <?/exam?>

class MkDocsExamPlugin(BasePlugin):
    def __init__(self):
        self.enabled = True
        self.dirty = False

    def on_startup(self, *, command, dirty: bool) -> None:
        """Configure the plugin on startup."""
        self.dirty = dirty

    def on_page_markdown(self, markdown, page, config, **kwargs):
        if "exam" in page.meta and page.meta["exam"] == "disable":
            return markdown
        # Regex from exam_tag
        EXAM_START_TAG = "<?exam?>"
        EXAM_END_TAG = "<?/exam?>"
        REGEX = r'<\?exam\?>(.*?)<\?/exam\?>'
        matches = re.findall(REGEX, markdown, re.DOTALL)
        exam_id = 0
        for match in matches:
            exam_lines = match.splitlines()
            # Remove 0 and -1 if empty
            while exam_lines[0] == "":
                exam_lines = exam_lines[1:]
            while exam_lines[-1] == "":
                exam_lines = exam_lines[:-1]
            question = exam_lines[0].split("question: ")[1]

            answers = exam_lines[1: exam_lines.index("content:")]
            # correct_answer = list(filter(lambda x: x.startswith(
            #     "exam-answer-correct: "), answers))[0].split("exam-answer-correct: ")[1]
            multiple_correct = list(
                filter(lambda x: x.startswith("answer-correct: "), answers))
            multiple_correct = list(
                map(lambda x: x.split("answer-correct: ")[1], multiple_correct))
            as_checkboxes = len(multiple_correct) > 1
                
            answers = list(
                map(
                    lambda x: (
                        x.startswith("answer-correct: ")
                        and x.split("answer-correct: ")[1]
                        or x.startswith("answer: ")
                        and x.split("answer: ")[1]
                    ),
                    answers,
                )
            )
            full_answers = []
            for i in range(len(answers)):
                is_correct = answers[i] in multiple_correct
                input_id = "exam-{}-{}".format(exam_id, i)
                input_type = as_checkboxes and "checkbox" or "radio"
                correct = is_correct and "correct" or ""
                full_answers.append(
                    f'<div><input type="{input_type}" name="answer" value="{i}" id="{input_id}" {correct}>'
                    f'<label for="{input_id}">{answers[i]}</label></div>'
                )
            # Get the content of the exam
            content = exam_lines[exam_lines.index("content:") + 1:]
            exam_html = (
                '<div class="exam"><h3>{}</h3><form><fieldset>{}'
                '</fieldset><button type="submit" class="exam-button">Submit</button>'
                '</form><section class="content hidden">{}</section></div>'.format(
                    question,
                    "".join(full_answers),
                    "\n".join(content),
                )
            )
            # old_exam = "exam-start" + match + "exam-end"
            old_exam = EXAM_START_TAG + match + EXAM_END_TAG
            markdown = markdown.replace(old_exam, exam_html)
            exam_id += 1
        return markdown

    def on_page_content(self, html: str, *, page: Page, config: MkDocsConfig, files: Files) -> str | None:

        html = html + style + js
        return html
