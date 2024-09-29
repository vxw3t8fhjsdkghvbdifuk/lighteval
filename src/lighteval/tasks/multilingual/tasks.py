# MIT License

# Copyright (c) 2024 The HuggingFace Team

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from functools import partial

from langcodes import Language as LangCodeLanguage
from langcodes import standardize_tag

from lighteval.metrics.dynamic_metrics import (
    loglikelihood_acc_metric,
    multilingual_quasi_exact_match_metric,
    multilingual_quasi_f1_score_metric,
)
from lighteval.metrics.normalizations import LogProbPMINorm, LogProbTokenNorm
from lighteval.tasks.default_prompts import LETTER_INDICES
from lighteval.tasks.lighteval_task import LightevalTaskConfig
from lighteval.tasks.multilingual.adapters import (
    agieval_prompt,
    alghafa_adapter,
    ceval_adapter,
    get_m3exam_adapter,
    thai_exams_adapter,
)
from lighteval.tasks.templates.copa import get_copa_prompt_function
from lighteval.tasks.templates.hellaswag import get_hellaswag_prompt_function
from lighteval.tasks.templates.multichoice import get_mcq_prompt_function
from lighteval.tasks.templates.nli import get_nli_prompt_function
from lighteval.tasks.templates.qa import get_qa_prompt_function
from lighteval.tasks.templates.utils.formulation import (
    CFFormulation,
    HybridFormulation,
    MCFFormulation,
)
from lighteval.utils.language import Language, iso_639_3_ind_to_iso_639_3_macro


TASKS_TABLE = []
# ------------------------------- NLI Tasks ------------------------------- #

xnli_tasks = [
    LightevalTaskConfig(
        name=f"xnli_{language.value}_{formulation.name.lower()}",
        suite=["custom"],
        metric=[loglikelihood_acc_metric(normalization=LogProbTokenNorm())],
        prompt_function=get_nli_prompt_function(
            language=language,
            adapter=lambda line: {
                "premise": line["premise"],
                "hypothesis": line["hypothesis"],
                # Since we ignore the neural label
                "gold_idx": {0: 0, 2: 1}[line["label"]],
            },
            relations=["entailment", "contradiction"],
            formulation=formulation,
        ),
        hf_filter=lambda line: line["label"] in [0, 2],
        hf_repo="facebook/xnli",
        hf_subset=standardize_tag(language.value),
        evaluation_splits=["validation"],
        few_shots_split="train",
    )
    for language in [
        Language.ARABIC,
        Language.ENGLISH,
        Language.FRENCH,
        Language.SPANISH,
        Language.BULGARIAN,
        Language.GERMAN,
        Language.GREEK,
        Language.ENGLISH,
        Language.FRENCH,
        Language.HINDI,
        Language.RUSSIAN,
        Language.SWAHILI,
        Language.THAI,
        Language.TURKISH,
        Language.URDU,
        Language.VIETNAMESE,
        Language.CHINESE,
    ]
    for formulation in [MCFFormulation(), CFFormulation(), HybridFormulation()]
]

xnli2_tasks = [
    LightevalTaskConfig(
        name=f"xnli2.0_{language.value}_{formulation.name.lower()}",
        suite=["custom"],
        metric=[loglikelihood_acc_metric(normalization=LogProbTokenNorm())],
        prompt_function=get_nli_prompt_function(
            language=language,
            adapter=lambda line: {
                "premise": line["premise"],
                "hypothesis": line["hypothesis"],
                # Since we ignore the neural label
                "gold_idx": {0: 0, 2: 1}[line["label"]],
            },
            relations=["entailment", "contradiction"],
            formulation=formulation,
        ),
        hf_filter=lambda line: line["label"] in [0, 2],
        hf_repo=f"Harsit/xnli2.0_train_{LangCodeLanguage(standardize_tag(language.value)).language_name().lower()}",
        hf_subset="default",
        evaluation_splits=["train"],
    )
    for language in [
        Language.ENGLISH,
        Language.FRENCH,
        Language.PUNJABI,
        Language.GUJARATI,
        Language.KANNADA,
        Language.ASSAMESE,
        Language.BENGALI,
        Language.MARATHI,
        Language.SANSKRIT,
        Language.TAMIL,
        Language.GERMAN,
        Language.ENGLISH,
        Language.URDU,
        Language.VIETNAMESE,
        Language.TURKISH,
        Language.THAI,
        Language.SWAHILI,
        Language.SPANISH,
        Language.RUSSIAN,
        Language.HINDI,
        Language.GREEK,
        Language.CHINESE,
        Language.BULGARIAN,
        Language.ARABIC,
        # Theoretically also: Bhojpuri, Gujarati, Odiya
    ]
    for formulation in [MCFFormulation(), CFFormulation(), HybridFormulation()]
]

xnli_indic_tasks = [
    LightevalTaskConfig(
        name=f"indicnxnli_{language.value}_{formulation.name.lower()}",
        suite=["custom"],
        prompt_function=get_nli_prompt_function(
            language=language,
            adapter=lambda line: {
                "premise": line["premise"],
                "hypothesis": line["hypothesis"],
                # Since we ignore the neural label
                "gold_idx": {0: 0, 2: 1}[line["label"]],
            },
            relations=["entailment", "contradiction"],
            formulation=formulation,
        ),
        hf_repo="Divyanshu/indicxnli",
        hf_subset=standardize_tag(language.value),
        # Ignore neutral
        hf_filter=lambda x: int(x["label"]) in [0, 2],
        evaluation_splits=["validation"],
        few_shots_split="train",
        few_shots_select=None,
        generation_size=-1,
        metric=[
            loglikelihood_acc_metric(normalization=LogProbTokenNorm()),
        ],
    )
    for language in [
        Language.ASSAMESE,
        Language.BENGALI,
        Language.GUJARATI,
        Language.HINDI,
        Language.KANNADA,
        Language.MALAYALAM,
        Language.MARATHI,
        Language.ORIYA,
        Language.PUNJABI,
        Language.TAMIL,
        Language.TELUGU,
    ]
    for formulation in [MCFFormulation(), CFFormulation(), HybridFormulation()]
]

paws_x_tasks = [
    LightevalTaskConfig(
        name=f"pawsx_{language.value}_{formulation.name.lower()}",
        suite=("custom",),
        prompt_function=get_nli_prompt_function(
            language=language,
            adapter=lambda line: {
                "premise": line["sentence1"],
                "hypothesis": line["sentence2"],
                # Since we ignore the neural label
                "gold_idx": int(line["label"]),
            },
            relations=["entailment", "contradiction"],
            formulation=formulation,
        ),
        hf_repo="google-research-datasets/paws-x",
        hf_subset=standardize_tag(language.value),
        evaluation_splits=("test",),
        few_shots_split="train",
        metric=[
            loglikelihood_acc_metric(normalization=LogProbTokenNorm()),
        ],
    )
    for language in [
        Language.GERMAN,
        Language.ENGLISH,
        Language.SPANISH,
        Language.FRENCH,
        Language.JAPANESE,
        Language.KOREAN,
        Language.CHINESE,
    ]
    for formulation in [MCFFormulation(), CFFormulation(), HybridFormulation()]
]

rcb_tasks = [
    LightevalTaskConfig(
        name=f"rcb_{Language.RUSSIAN.value}_{formulation.name.lower()}",
        prompt_function=get_nli_prompt_function(
            language=Language.RUSSIAN,
            adapter=lambda line: {
                "premise": line["inputs"]["premise"],
                "hypothesis": line["inputs"]["hypothesis"],
                # Since we ignore the neural label
                "gold_idx": int(line["outputs"]) - 1,
            },
            relations=["entailment", "contradiction"],
            formulation=formulation,
        ),
        suite=("custom",),
        hf_repo="ai-forever/MERA",
        hf_subset="rcb",
        # Ignore neutral label
        hf_filter=lambda x: int(x["outputs"] or "0") in [1, 2],
        evaluation_splits=("train", "validation"),
        metric=[
            loglikelihood_acc_metric(normalization=LogProbTokenNorm()),
        ],
    )
    for formulation in [MCFFormulation(), CFFormulation(), HybridFormulation()]
]

# Non translated chinese task
ocnli_tasks = [
    LightevalTaskConfig(
        name=f"ocnli_{Language.CHINESE.value}_{formulation.name.lower()}",
        prompt_function=get_nli_prompt_function(
            language=Language.CHINESE,
            adapter=lambda line: {
                "premise": line["sentence1"],
                "hypothesis": line["sentence2"],
                # Since we ignore the neural label
                "gold_idx": {1: 0, 2: 1}[line["label"]],
            },
            relations=["entailment", "contradiction"],
            formulation=formulation,
        ),
        suite=("custom",),
        hf_repo="clue/clue",
        hf_subset="ocnli",
        # Only keep the positive and negative examples
        hf_filter=lambda x: int(x["label"]) in [1, 2],
        evaluation_splits=("validation",),
        few_shots_split="train",
        metric=[
            loglikelihood_acc_metric(normalization=LogProbTokenNorm()),
        ],
    )
    for formulation in [MCFFormulation(), CFFormulation(), HybridFormulation()]
]

cmnli_tasks = [
    LightevalTaskConfig(
        name=f"cmnli_{Language.CHINESE.value}_{formulation.name.lower()}",
        prompt_function=get_nli_prompt_function(
            language=Language.CHINESE,
            adapter=lambda line: {
                "premise": line["sentence1"],
                "hypothesis": line["sentence2"],
                # Since we ignore the neural label
                "gold_idx": {"entailment": 0, "contradiction": 1}[line["label"]],
            },
            relations=["entailment", "contradiction"],
            formulation=formulation,
        ),
        suite=("custom",),
        hf_repo="fenffef/cmnli",
        hf_subset="default",
        hf_filter=lambda x: x["label"] in ["entailment", "contradiction"],
        # Only keep the positive and negative examples
        evaluation_splits=("validation",),
        few_shots_split="train",
        metric=[
            loglikelihood_acc_metric(normalization=LogProbTokenNorm()),
        ],
    )
    for formulation in [MCFFormulation(), CFFormulation(), HybridFormulation()]
]

TASKS_TABLE.extend(
    [*xnli_tasks, *xnli2_tasks, *xnli_indic_tasks, *paws_x_tasks, *rcb_tasks, *ocnli_tasks, *cmnli_tasks]
)
# ------------------------------- Copa Tasks ------------------------------- #

copa_tasks = [
    LightevalTaskConfig(
        name=f"xcopa_{language.value}_{formulation.name.lower()}",
        suite=["custom"],
        prompt_function=get_copa_prompt_function(
            language,
            adapter=lambda line: {
                "context": line["premise"],
                "cause_effect": line["question"],
                "continuations": [line["choice1"], line["choice2"]],
                "gold_idx": int(line["label"]),
            },
            formulation=formulation,
        ),
        hf_repo=("OALL/AlGhafa-Arabic-LLM-Benchmark-Translated" if language == Language.ARABIC else "xcopa"),
        hf_subset=("copa_ext_ar" if language == Language.ARABIC else standardize_tag(language.value)),
        hf_revision="a31ebd34ca311d7e0cfc6ad7f458b3435af280f5" if language == Language.ARABIC else None,
        evaluation_splits=["test"],
        few_shots_split="validation",
        generation_size=-1,
        metric=[
            loglikelihood_acc_metric(normalization=LogProbTokenNorm()),
        ],
    )
    for language in [
        Language.ESTONIAN,
        Language.INDONESIAN,
        Language.ITALIAN,
        Language.SWAHILI,
        Language.TAMIL,
        Language.THAI,
        Language.TURKISH,
        Language.VIETNAMESE,
        Language.CHINESE,
        # Optionally: Haitian, Quechu
    ]
    for formulation in [MCFFormulation(), CFFormulation(), HybridFormulation()]
]

copa_indic_tasks = [
    LightevalTaskConfig(
        name=f"indicxcopa_{language.value}_{formulation.name.lower()}",
        suite=["custom"],
        prompt_function=get_copa_prompt_function(
            language,
            adapter=lambda line: {
                "context": line["premise"],
                "cause_effect": line["question"],
                "continuations": [line["choice1"], line["choice2"]],
                "gold_idx": int(line["label"]),
            },
            formulation=formulation,
        ),
        hf_repo="ai4bharat/IndicCOPA",
        hf_subset=f"translation-{standardize_tag(language.value)}",
        evaluation_splits=["test"],
        metric=[
            loglikelihood_acc_metric(normalization=LogProbTokenNorm()),
        ],
        trust_dataset=True,
    )
    for language in [
        Language.ASSAMESE,
        Language.BENGALI,
        Language.GUJARATI,
        Language.HINDI,
        Language.KANNADA,
        Language.MALAYALAM,
        Language.MARATHI,
        Language.NEPALI,
        Language.ORIYA,
        Language.PUNJABI,
        Language.SANSKRIT,
        Language.SINDHI,
        Language.TAMIL,
        Language.TELUGU,
        Language.URDU,
        # Optionally: Maithili, Santali, Sindhi, Konkani
    ]
    for formulation in [MCFFormulation(), CFFormulation(), HybridFormulation()]
]

parus_tasks = [
    LightevalTaskConfig(
        name=f"parus_{Language.RUSSIAN.value}_{formulation.name.lower()}",
        suite=["custom"],
        prompt_function=get_copa_prompt_function(
            language=Language.RUSSIAN,
            adapter=lambda line: {
                "context": line["inputs"]["premise"],
                "cause_effect": line["meta"]["task"],
                "continuations": [line["inputs"]["choice1"], line["inputs"]["choice2"]],
                "gold_idx": int(line["outputs"]) - 1,
            },
            formulation=formulation,
        ),
        hf_repo="ai-forever/MERA",
        hf_subset="parus",
        evaluation_splits=["train"],
        few_shots_split="validation",
        metric=[
            loglikelihood_acc_metric(normalization=LogProbTokenNorm()),
        ],
    )
    for formulation in [MCFFormulation(), CFFormulation(), HybridFormulation()]
]


TASKS_TABLE.extend([*copa_tasks, *copa_indic_tasks, *parus_tasks])
# ------------------------------- Hellaswag Tasks ------------------------------- #

mlmm_hellaswag_tasks = [
    LightevalTaskConfig(
        name=f"hellaswag_{lang.value}_{formulation.name.lower()}",
        suite=["custom"],
        prompt_function=get_hellaswag_prompt_function(
            language=lang,
            adapter=lambda line: {
                # We don't use activity_label they are not available
                "ctx_a": line["ctx_a"],
                "ctx_b": line["ctx_b"],
                "continuations": line["endings"],
                "gold_idx": int(line["label"]),
            },
            formulation=formulation,
        ),
        hf_repo="jon-tow/okapi_hellaswag",
        hf_subset=standardize_tag(lang.value),
        hf_revision="96ed8e0dfc6172dad1d3df338d7b8ba6c1ff9d83",
        trust_dataset=True,
        evaluation_splits=["validation"],
        metric=[
            loglikelihood_acc_metric(normalization=LogProbTokenNorm()),
        ],
    )
    for lang in [
        Language.ARABIC,
        Language.BENGALI,
        Language.CATALAN,
        Language.DANISH,
        Language.GERMAN,
        Language.SPANISH,
        Language.BASQUE,
        Language.FRENCH,
        Language.GUJARATI,
        Language.HINDI,
        Language.CROATIAN,
        Language.HUNGARIAN,
        Language.ARMENIAN,
        Language.INDONESIAN,
        Language.ICELANDIC,
        Language.ITALIAN,
        Language.KANNADA,
        Language.MALAYALAM,
        Language.MARATHI,
        Language.NORWEGIAN,
        Language.NEPALI,
        Language.DUTCH,
        Language.PORTUGUESE,
        Language.ROMANIAN,
        Language.RUSSIAN,
        Language.SLOVAK,
        Language.SERBIAN,
        Language.SWEDISH,
        Language.TAMIL,
        Language.TELUGU,
        Language.UKRAINIAN,
        Language.VIETNAMESE,
        Language.CHINESE,
    ]
    for formulation in [MCFFormulation(), CFFormulation(), HybridFormulation()]
]

hellaswag_tur_tasks = [
    LightevalTaskConfig(
        name=f"hellaswag_{Language.TURKISH.value}_{formulation.name.lower()}",
        suite=["custom"],
        prompt_function=get_hellaswag_prompt_function(
            language=Language.TURKISH,
            adapter=lambda line: {
                "ctx_a": line["ctx_a"],
                "ctx_b": line["ctx_b"],
                "continuations": line["endings"],
                "gold_idx": int(line["label"]),
            },
            formulation=formulation,
            # https://github.com/malhajar17/lm-evaluation-harness_turkish/blob/main/lm_eval/tasks/hellaswag_tr-v0.2/utils.py
            dot_replacement=[" [title]", " [başlık]", " [adım]", " [header]"],
        ),
        hf_repo="malhajar/hellaswag_tr-v0.2",
        hf_subset="default",
        evaluation_splits=["validation"],
        metric=[
            loglikelihood_acc_metric(normalization=LogProbTokenNorm()),
        ],
    )
    for formulation in [MCFFormulation(), CFFormulation(), HybridFormulation()]
]

hellaswag_tha_tasks = [
    LightevalTaskConfig(
        name=f"hellaswag_{Language.THAI.value}_{formulation.name.lower()}",
        suite=["custom"],
        prompt_function=get_hellaswag_prompt_function(
            language=Language.THAI,
            adapter=lambda line: {
                "ctx_a": line["ctx_a"],
                "ctx_b": line["ctx_b"],
                "continuations": line["endings"],
                "gold_idx": int(line["label"]),
            },
            formulation=formulation,
        ),
        hf_repo="HuggingFaceFW-Dev/hellaswag_thai",
        hf_subset="default",
        evaluation_splits=["validation"],
        few_shots_split="train",
        metric=[
            loglikelihood_acc_metric(normalization=LogProbTokenNorm()),
        ],
    )
    for formulation in [MCFFormulation(), CFFormulation(), HybridFormulation()]
]

TASKS_TABLE.extend(
    [
        *mlmm_hellaswag_tasks,
        *hellaswag_tur_tasks,
        *hellaswag_tha_tasks,
    ]
)
# ------------------------------- RC Tasks ------------------------------- #

# SQuAD - like

xquad_tasks = [
    LightevalTaskConfig(
        name=f"xquad_{language.value}",
        prompt_function=get_qa_prompt_function(
            language,
            lambda line: {
                "question": line["question"],
                "context": line["context"],
                "choices": [ans for ans in line["answers"]["text"] if len(ans) > 0],
            },
        ),
        suite=("custom",),
        hf_repo="google/xquad",
        hf_subset=f"xquad.{standardize_tag(language.value)}",
        evaluation_splits=("validation",),
        few_shots_split="validation",
        generation_size=400,
        stop_sequence=("\n",),
        metric=(
            multilingual_quasi_exact_match_metric(language, "prefix"),
            multilingual_quasi_f1_score_metric(language),
        ),
    )
    for language in [
        Language.ARABIC,
        Language.GERMAN,
        Language.GREEK,
        Language.ENGLISH,
        Language.SPANISH,
        Language.HINDI,
        Language.ROMANIAN,
        Language.RUSSIAN,
        Language.THAI,
        Language.TURKISH,
        Language.VIETNAMESE,
        Language.CHINESE,
    ]
]

thaiqa_tasks = [
    LightevalTaskConfig(
        name=f"thaiqa_{Language.THAI.value}",
        prompt_function=get_qa_prompt_function(
            Language.THAI,
            lambda line: {
                "question": line["question"],
                "context": line["context"],
                "choices": [ans for ans in line["answers"]["answer"] if len(ans) > 0],
            },
        ),
        suite=("custom",),
        hf_repo="HuggingFaceFW-Dev/thaiqa_squad_fixed",
        hf_subset="default",
        evaluation_splits=("train",),
        few_shots_split="validation",
        generation_size=400,
        stop_sequence=("\n",),
        metric=(
            multilingual_quasi_exact_match_metric(Language.THAI, "prefix"),
            multilingual_quasi_f1_score_metric(Language.THAI),
        ),
    )
]

sber_squad_tasks = [
    LightevalTaskConfig(
        name=f"sber_squad_{Language.RUSSIAN.value}",
        prompt_function=get_qa_prompt_function(
            Language.RUSSIAN,
            lambda line: {
                "question": line["question"],
                "context": line["context"],
                "choices": [ans for ans in line["answers"]["text"] if len(ans) > 0],
            },
        ),
        suite=("custom",),
        hf_repo="kuznetsoffandrey/sberquad",
        hf_subset="sberquad",
        evaluation_splits=("validation",),
        few_shots_split="train",
        metric=(
            multilingual_quasi_exact_match_metric(Language.RUSSIAN, "prefix"),
            multilingual_quasi_f1_score_metric(Language.RUSSIAN),
        ),
        generation_size=400,
        stop_sequence=("\n",),
    )
]

arcd_tasks = [
    LightevalTaskConfig(
        name=f"arcd_{Language.ARABIC.value}",
        prompt_function=get_qa_prompt_function(
            Language.ARABIC,
            lambda line: {
                "question": line["question"],
                "context": line["context"],
                "choices": [ans for ans in line["answers"]["text"] if len(ans) > 0],
            },
        ),
        suite=("custom",),
        hf_repo="hsseinmz/arcd",
        hf_subset="plain_text",
        evaluation_splits=("train", "validation"),
        trust_dataset=True,
        metric=(
            multilingual_quasi_exact_match_metric(Language.ARABIC, "prefix"),
            multilingual_quasi_f1_score_metric(Language.ARABIC),
        ),
        generation_size=400,
        stop_sequence=("\n",),
    )
]

kenswquad_tasks = [
    LightevalTaskConfig(
        name=f"kenswquad_{Language.SWAHILI.value}",
        prompt_function=get_qa_prompt_function(
            Language.SWAHILI,
            lambda line: {
                "question": line["question"],
                "context": line["context"],
                "choices": [line["answer"]],
            },
        ),
        suite=("custom",),
        hf_repo="HuggingFaceFW-Dev/KenSwQuAD",
        hf_subset="default",
        evaluation_splits=("test",),
        few_shots_split="validation",
        metric=(
            multilingual_quasi_exact_match_metric(Language.SWAHILI, "prefix"),
            multilingual_quasi_f1_score_metric(Language.SWAHILI),
        ),
        generation_size=400,
        stop_sequence=("\n",),
    )
]

chinese_squad_tasks = [
    LightevalTaskConfig(
        name=f"chinese_squad_{Language.CHINESE.value}",
        prompt_function=get_qa_prompt_function(
            Language.CHINESE,
            lambda line: {
                "question": line["question"],
                "context": line["context"],
                "choices": [ans for ans in line["answers"]["text"] if len(ans) > 0],
            },
        ),
        suite=("custom",),
        hf_repo="HuggingFaceFW-Dev/ChineseSquad",
        hf_subset="default",
        evaluation_splits=("validation",),
        few_shots_split="train",
        metric=(
            multilingual_quasi_exact_match_metric(Language.CHINESE, "prefix"),
            multilingual_quasi_f1_score_metric(Language.CHINESE),
        ),
        generation_size=400,
        stop_sequence=("\n",),
    )
]

cmrc2018_tasks = [
    LightevalTaskConfig(
        name=f"cmrc2018_{Language.CHINESE.value}",
        prompt_function=get_qa_prompt_function(
            Language.CHINESE,
            lambda line: {
                "question": line["question"],
                "context": line["context"],
                "choices": [ans for ans in line["answers"]["text"] if len(ans) > 0],
            },
        ),
        suite=("custom",),
        hf_repo="clue/clue",
        hf_subset="cmrc2018",
        evaluation_splits=("trial",),
        few_shots_split="train",
        generation_size=400,
        metric=(
            multilingual_quasi_exact_match_metric(Language.CHINESE, "prefix"),
            multilingual_quasi_f1_score_metric(Language.CHINESE),
        ),
        stop_sequence=("\n",),
    )
]

indicqa_tasks = [
    LightevalTaskConfig(
        name=f"indicqa_{language.value}",
        prompt_function=get_qa_prompt_function(
            language,
            lambda line: {
                "question": line["question"],
                "context": line["context"],
                "choices": [ans for ans in line["answers"]["text"] if len(ans) > 0],
            },
        ),
        suite=("custom",),
        hf_repo="ai4bharat/IndicQA",
        hf_subset=f"indicqa.{LangCodeLanguage.get(language.value).language}",
        hf_revision="92d96092ae229950973dac3b9998f8b3a8949b0a",
        hf_filter=lambda line: any(len(ans) > 0 for ans in line["answers"]["text"]),
        trust_dataset=True,
        evaluation_splits=("test",),
        few_shots_split="test",
        generation_size=400,
        metric=(
            multilingual_quasi_exact_match_metric(language, "prefix"),
            multilingual_quasi_f1_score_metric(language),
        ),
        stop_sequence=("\n",),
    )
    for language in [
        Language.ASSAMESE,
        Language.BENGALI,
        Language.GUJARATI,
        Language.HINDI,
        Language.KANNADA,
        Language.MALAYALAM,
        Language.MARATHI,
        Language.ORIYA,
        Language.PUNJABI,
        Language.TAMIL,
        Language.TELUGU,
    ]
]


fquad_v2_tasks = [
    LightevalTaskConfig(
        name=f"fquadv2_{Language.FRENCH.value}",
        prompt_function=get_qa_prompt_function(
            Language.FRENCH,
            lambda line: {
                "question": line["question"],
                "context": line["context"],
                "choices": [ans for ans in line["answers"]["text"] if len(ans) > 0],
            },
        ),
        suite=("custom",),
        hf_repo="manu/fquad2_test",
        hf_subset="default",
        evaluation_splits=("test_hasAns",),
        few_shots_split="valid_hasAns",
        generation_size=400,
        stop_sequence=("\n",),
        metric=(
            multilingual_quasi_exact_match_metric(Language.FRENCH, "prefix"),
            multilingual_quasi_f1_score_metric(Language.FRENCH),
        ),
    )
]

tquad_v2_tasks = [
    LightevalTaskConfig(
        name=f"tquadv2_{Language.TURKISH.value}",
        prompt_function=get_qa_prompt_function(
            Language.TURKISH,
            lambda line: {
                "question": line["question"],
                "context": line["context"],
                "choices": [a["text"] for a in line["answers"]],
            },
        ),
        suite=("custom",),
        hf_repo="erdometo/tquad2",
        hf_subset="default",
        evaluation_splits=("validation",),
        few_shots_split="train",
        generation_size=400,
        stop_sequence=("\n",),
        metric=(
            multilingual_quasi_exact_match_metric(Language.TURKISH, "prefix"),
            multilingual_quasi_f1_score_metric(Language.TURKISH),
        ),
    )
]


# Other QA tasks for RC
tydiqa_tasks = [
    LightevalTaskConfig(
        name=f"tydiqa_{language.value}",
        prompt_function=get_qa_prompt_function(
            language,
            lambda line: {
                "question": line["question"],
                "context": line["context"],
                "choices": [ans for ans in line["answers"]["text"] if len(ans) > 0],
            },
        ),
        suite=("custom",),
        hf_repo="google-research-datasets/tydiqa",
        hf_subset="secondary_task",
        evaluation_splits=("validation",),
        few_shots_split="train",
        generation_size=400,
        stop_sequence=("\n",),
        metric=(
            multilingual_quasi_exact_match_metric(language, "prefix"),
            multilingual_quasi_f1_score_metric(language),
        ),
    )
    for language in [
        Language.ENGLISH,
        Language.ARABIC,
        Language.BENGALI,
        Language.FINNISH,
        Language.INDONESIAN,
        Language.JAPANESE,
        Language.KOREAN,
        Language.SWAHILI,
        Language.RUSSIAN,
        Language.TELUGU,
        Language.THAI,
    ]
]

# Other MCF tasks for RC

beleble_tasks = [
    LightevalTaskConfig(
        name=f"belebele_{language}_{formulation.name.lower()}",
        prompt_function=get_mcq_prompt_function(
            iso_639_3_ind_to_iso_639_3_macro[LangCodeLanguage.get(language).to_alpha3()],
            lambda line: {
                "question": line["question"],
                "context": line["flores_passage"],
                "choices": [line[f"mc_answer{i}"] for i in range(1, 5)],
                "gold_idx": int(line["correct_answer_num"]) - 1,
            },
        ),
        suite=("custom",),
        hf_repo="facebook/belebele",
        hf_subset=language,
        evaluation_splits=("test",),
        metric=[
            loglikelihood_acc_metric(normalization=LogProbTokenNorm()),
        ],
    )
    for formulation in [MCFFormulation(), CFFormulation(), HybridFormulation()]
    for language in [
        "acm_Arab",
        "arz_Arab",
        "ceb_Latn",
        "fin_Latn",
        "hin_Deva",
        "ita_Latn",
        "khm_Khmr",
        "lvs_Latn",
        "npi_Deva",
        "pol_Latn",
        "slv_Latn",
        "swe_Latn",
        # "tso_Latn",
        # "xho_Latn",
        "afr_Latn",
        "asm_Beng",
        "ces_Latn",
        "fra_Latn",
        "hin_Latn",
        "jav_Latn",
        # "kin_Latn",
        "mal_Mlym",
        "npi_Latn",
        "por_Latn",
        # "sna_Latn",
        "swh_Latn",
        "tur_Latn",
        "yor_Latn",
        "als_Latn",
        "azj_Latn",
        "ckb_Arab",
        # "fuv_Latn",
        "hrv_Latn",
        "jpn_Jpan",
        "kir_Cyrl",
        "mar_Deva",
        # "nso_Latn",
        "snd_Arab",
        "tam_Taml",
        "ukr_Cyrl",
        "zho_Hans",
        "amh_Ethi",
        # "bam_Latn",
        "dan_Latn",
        # "gaz_Latn",
        "hun_Latn",
        # "kac_Latn",
        "kor_Hang",
        "mkd_Cyrl",
        # "nya_Latn",
        "ron_Latn",
        "som_Latn",
        "tel_Telu",
        "urd_Arab",
        "zho_Hant",
        "apc_Arab",
        "ben_Beng",
        "deu_Latn",
        # "grn_Latn",
        "hye_Armn",
        "kan_Knda",
        "lao_Laoo",
        "mlt_Latn",
        "ory_Orya",
        "rus_Cyrl",
        # "sot_Latn",
        "tgk_Cyrl",
        "urd_Latn",
        "zsm_Latn",
        "arb_Arab",
        "ben_Latn",
        "ell_Grek",
        "guj_Gujr",
        # "ibo_Latn",
        "kat_Geor",
        # "lin_Latn",
        # "mri_Latn",
        "pan_Guru",
        # "shn_Mymr",
        "spa_Latn",
        "tgl_Latn",
        "uzn_Latn",
        # "zul_Latn",
        "arb_Latn",
        # "bod_Tibt",
        "eng_Latn",
        # "hat_Latn",
        # "ilo_Latn",
        "kaz_Cyrl",
        "lit_Latn",
        "mya_Mymr",
        "pbt_Arab",
        "sin_Latn",
        "srp_Cyrl",
        "tha_Thai",
        "vie_Latn",
        "ars_Arab",
        "bul_Cyrl",
        "est_Latn",
        # "hau_Latn",
        "ind_Latn",
        # "kea_Latn",
        # "lug_Latn",
        "nld_Latn",
        "pes_Arab",
        "sin_Sinh",
        # "ssw_Latn",
        # "tir_Ethi",
        "war_Latn",
        "ary_Arab",
        "cat_Latn",
        "eus_Latn",
        "heb_Hebr",
        "isl_Latn",
        # "khk_Cyrl",
        # "luo_Latn",
        "nob_Latn",
        "plt_Latn",
        "slk_Latn",
        # "sun_Latn",
        # "tsn_Latn",
        # "wol_Latn",
    ]
]

TASKS_TABLE.extend(
    [
        *xquad_tasks,
        *thaiqa_tasks,
        *sber_squad_tasks,
        *arcd_tasks,
        *kenswquad_tasks,
        *chinese_squad_tasks,
        *cmrc2018_tasks,
        *indicqa_tasks,
        *fquad_v2_tasks,
        *tquad_v2_tasks,
        *tydiqa_tasks,
        *beleble_tasks,
    ]
)

# ------------------------------- GK ------------------------------- #

# MMLU
# We have definition for 3 types of MMMLU suites
# From out experience native_mmlu >> meta_mmlu > mlmm_mmlu

MMLU_SUBSETS = [
    "abstract_algebra",
    "anatomy",
    "astronomy",
    "business_ethics",
    "clinical_knowledge",
    "college_biology",
    "college_chemistry",
    "college_computer_science",
    "college_mathematics",
    "college_medicine",
    "college_physics",
    "computer_security",
    "conceptual_physics",
    "econometrics",
    "electrical_engineering",
    "elementary_mathematics",
    "formal_logic",
    "global_facts",
    "high_school_biology",
    "high_school_chemistry",
    "high_school_computer_science",
    "high_school_european_history",
    "high_school_geography",
    "high_school_government_and_politics",
    "high_school_macroeconomics",
    "high_school_mathematics",
    "high_school_microeconomics",
    "high_school_physics",
    "high_school_psychology",
    "high_school_statistics",
    "high_school_us_history",
    "high_school_world_history",
    "human_aging",
    "human_sexuality",
    "international_law",
    "jurisprudence",
    "logical_fallacies",
    "machine_learning",
    "management",
    "marketing",
    "medical_genetics",
    "miscellaneous",
    "moral_disputes",
    "moral_scenarios",
    "nutrition",
    "philosophy",
    "prehistory",
    "professional_accounting",
    "professional_law",
    "professional_medicine",
    "professional_psychology",
    "public_relations",
    "security_studies",
    "sociology",
    "us_foreign_policy",
    "virology",
    "world_religions",
]

meta_mmlu_tasks = [
    LightevalTaskConfig(
        name=f"meta_mmlu_{language.name}_{formulation.name.lower()}:{subset}",
        prompt_function=get_mcq_prompt_function(
            language,
            lambda line: {
                "question": line["input_question"],
                "choices": [v for _, v in sorted(line["input_choice_list"].items(), key=lambda x: x[0])],
                "gold_idx": LETTER_INDICES.index(line["input_correct_responses"][0]),
            },
        ),
        suite=("custom",),
        hf_repo="meta-llama/Meta-Llama-3.1-8B-Instruct-evals",
        hf_subset=f"Meta-Llama-3.1-8B-Instruct-evals__multilingual_mmlu_{standardize_tag(language.value)}__details",
        hf_filter=partial(
            lambda language, subset, line: line["subtask_name"]
            == f"mmlu_{standardize_tag(language.value)}_chat.{subset}",
            language,
            subset,
        ),
        evaluation_splits=("latest",),
        metric=[
            loglikelihood_acc_metric(normalization=LogProbTokenNorm()),
        ],
    )
    for subset in MMLU_SUBSETS
    for language in [
        Language.GERMAN,
        Language.SPANISH,
        Language.FRENCH,
        Language.HINDI,
        Language.ITALIAN,
        Language.PORTUGUESE,
        Language.THAI,
    ]
    for formulation in [
        MCFFormulation(),
        CFFormulation(),
        HybridFormulation(),
    ]
]

mlmm_mmlu_tasks = [
    LightevalTaskConfig(
        name=f"mlmm_mmlu_{language.name}_{formulation.name.lower()}:{subset}",
        prompt_function=get_mcq_prompt_function(
            language,
            lambda line: {
                "question": line["question"],
                "choices": line["choices"],
                "gold_idx": LETTER_INDICES.index(line["answer"]),
            },
        ),
        suite=("custom",),
        hf_repo="jon-tow/okapi_mmlu",
        hf_subset=standardize_tag(language.value),
        hf_revision="refs/pr/1",
        hf_filter=partial(lambda subset, line: line["id"].split("/")[0] == subset, subset),
        trust_dataset=True,
        evaluation_splits=("test",),
        few_shots_split="dev",
        metric=[
            loglikelihood_acc_metric(normalization=LogProbTokenNorm()),
        ],
    )
    for subset in MMLU_SUBSETS
    for language in [
        Language.ENGLISH,
        Language.RUSSIAN,
        Language.GERMAN,
        Language.CHINESE,
        Language.FRENCH,
        Language.SPANISH,
        Language.ITALIAN,
        Language.DUTCH,
        Language.VIETNAMESE,
        Language.INDONESIAN,
        Language.ARABIC,
        Language.HUNGARIAN,
        Language.ROMANIAN,
        Language.DANISH,
        Language.SLOVAK,
        Language.UKRAINIAN,
        Language.CATALAN,
        Language.SERBIAN,
        Language.CROATIAN,
        Language.HINDI,
        Language.BENGALI,
        Language.TAMIL,
        Language.NEPALI,
        Language.MALAYALAM,
        Language.MARATHI,
        Language.TELUGU,
        Language.KANNADA,
    ]
    for formulation in [
        MCFFormulation(),
        CFFormulation(),
        HybridFormulation(),
    ]
]

rummlu = [
    LightevalTaskConfig(
        name=f"rummlu_{Language.RUSSIAN.value}_{formulation.name.lower()}:{subset}",
        prompt_function=get_mcq_prompt_function(
            Language.RUSSIAN,
            lambda line: {
                "question": line["inputs"]["text"],
                "choices": [line["inputs"][f"option_{i.lower()}"] for i in LETTER_INDICES[:4]],
                "gold_idx": LETTER_INDICES.index(line["outputs"]),
            },
        ),
        suite=("custom",),
        hf_repo="ai-forever/MERA",
        hf_subset="rummlu",
        hf_filter=lambda x: x["meta"]["domain"] == subset,
        evaluation_splits=("public_test",),
        metric=[
            loglikelihood_acc_metric(normalization=LogProbTokenNorm()),
        ],
    )
    for subset in MMLU_SUBSETS
    for formulation in [
        MCFFormulation(),
        CFFormulation(),
        HybridFormulation(),
    ]
]

mmlu_turkish = [
    LightevalTaskConfig(
        name=f"tr_leaderboard_mmlu_{Language.TURKISH.value}_{formulation.name.lower()}:{subset}",
        prompt_function=get_mcq_prompt_function(
            Language.TURKISH,
            lambda line: {"question": line["question"], "choices": line["choices"], "gold_idx": int(line["answer"])},
        ),
        suite=("custom",),
        hf_repo="malhajar/mmlu_tr-v0.2",
        hf_subset=subset,
        evaluation_splits=("test",),
        few_shots_split="dev",
        metric=(loglikelihood_acc_metric(normalization=LogProbTokenNorm()),),
    )
    for subset in MMLU_SUBSETS
    for formulation in [
        MCFFormulation(),
        CFFormulation(),
        HybridFormulation(),
    ]
]

# They are almost the same as MMLU subsets, but they are not exactly the same
CMMLU_SUBSETS = [
    "agronomy",
    "anatomy",
    "ancient_chinese",
    "arts",
    "astronomy",
    "business_ethics",
    "chinese_civil_service_exam",
    "chinese_driving_rule",
    "chinese_food_culture",
    "chinese_foreign_policy",
    "chinese_history",
    "chinese_literature",
    "chinese_teacher_qualification",
    "clinical_knowledge",
    "college_actuarial_science",
    "college_education",
    "college_engineering_hydrology",
    "college_law",
    "college_mathematics",
    "college_medical_statistics",
    "college_medicine",
    "computer_science",
    "computer_security",
    "conceptual_physics",
    "construction_project_management",
    "economics",
    "education",
    "electrical_engineering",
    "elementary_chinese",
    "elementary_commonsense",
    "elementary_information_and_technology",
    "elementary_mathematics",
    "ethnology",
    "food_science",
    "genetics",
    "global_facts",
    "high_school_biology",
    "high_school_chemistry",
    "high_school_geography",
    "high_school_mathematics",
    "high_school_physics",
    "high_school_politics",
    "human_sexuality",
    "international_law",
    "journalism",
    "jurisprudence",
    "legal_and_moral_basis",
    "logical",
    "machine_learning",
    "management",
    "marketing",
    "marxist_theory",
    "modern_chinese",
    "nutrition",
    "philosophy",
    "professional_accounting",
    "professional_law",
    "professional_medicine",
    "professional_psychology",
    "public_relations",
    "security_study",
    "sociology",
    "sports_science",
    "traditional_chinese_medicine",
    "virology",
    "world_history",
    "world_religions",
]

cmmlu_tasks = [
    LightevalTaskConfig(
        name=f"cmmlu_{Language.CHINESE.value}_{formulation.name.lower()}:{subset}",
        prompt_function=get_mcq_prompt_function(
            Language.CHINESE,
            lambda line: {
                "question": line["Question"],
                "choices": [line["A"], line["B"], line["C"], line["D"]],
                "gold_idx": LETTER_INDICES.index(line["Answer"]),
            },
        ),
        suite=("custom",),
        hf_repo="haonan-li/cmmlu",
        hf_subset=subset,
        evaluation_splits=("test",),
        few_shots_split="dev",
        metric=(loglikelihood_acc_metric(normalization=LogProbTokenNorm()),),
    )
    for subset in CMMLU_SUBSETS
    for formulation in [
        MCFFormulation(),
        CFFormulation(),
        HybridFormulation(),
    ]
]

ARABIC_MMLU_SUBSETS = [
    "Driving Test",
    "High Geography",
    "High History",
    "Islamic Studies",
    "Univ Accounting",
    "Primary General Knowledge",
    "Univ Political Science",
    "Primary Math",
    "Middle General Knowledge",
    "High Biology",
    "Primary Natural Science",
    "High Economics",
    "Middle Natural Science",
    "Middle Geography",
    "Primary Social Science",
    "Middle Computer Science",
    "Middle Islamic Studies",
    "Primary Computer Science",
    "High Physics",
    "Middle Social Science",
    "Middle Civics",
    "High Computer Science",
    "General Knowledge",
    "High Civics",
    "Prof Law",
    "High Islamic Studies",
    "Primary Arabic Language",
    "High Arabic Language",
    "Arabic Language (Grammar)",
    "Primary History",
    "Middle History",
    "Univ Economics",
    "Arabic Language (General)",
    "Univ Computer Science",
    "Primary Islamic Studies",
    "Primary Geography",
    "High Philosophy",
    "Middle Arabic Language",
    "Middle Economics",
    "Univ Management",
]

arabic_mmlu_tasks = [
    LightevalTaskConfig(
        name=f"arabic_mmlu_native_{Language.ARABIC.value}_{formulation.name.lower()}:{subset.lower().replace(' ', '_').replace('(', '').replace(')', '')}",
        prompt_function=get_mcq_prompt_function(
            Language.ARABIC,
            lambda line: {
                "context": line["Context"],
                "question": line["Question"],
                "choices": [o for o in [line[f"Option {i}"] for i in range(1, 6)] if o],
                "gold_idx": LETTER_INDICES.index(line["Answer Key"]),
            },
        ),
        suite=("custom",),
        hf_repo="yazeed7/ArabicMMLU",
        hf_subset=subset,
        evaluation_splits=("test",),
        metric=(loglikelihood_acc_metric(normalization=LogProbTokenNorm()),),
    )
    for subset in ARABIC_MMLU_SUBSETS
    for formulation in [
        MCFFormulation(),
        CFFormulation(),
        HybridFormulation(),
    ]
]

CEVAL_SUBSET = [
    "computer_network",
    "operating_system",
    "computer_architecture",
    "college_programming",
    "college_physics",
    "college_chemistry",
    "advanced_mathematics",
    "probability_and_statistics",
    "discrete_mathematics",
    "electrical_engineer",
    "metrology_engineer",
    "high_school_mathematics",
    "high_school_physics",
    "high_school_chemistry",
    "high_school_biology",
    "middle_school_mathematics",
    "middle_school_biology",
    "middle_school_physics",
    "middle_school_chemistry",
    "veterinary_medicine",
    "college_economics",
    "business_administration",
    "marxism",
    "mao_zedong_thought",
    "education_science",
    "teacher_qualification",
    "high_school_politics",
    "high_school_geography",
    "middle_school_politics",
    "middle_school_geography",
    "modern_chinese_history",
    "ideological_and_moral_cultivation",
    "logic",
    "law",
    "chinese_language_and_literature",
    "art_studies",
    "professional_tour_guide",
    "legal_professional",
    "high_school_chinese",
    "high_school_history",
    "middle_school_history",
    "civil_servant",
    "sports_science",
    "plant_protection",
    "basic_medicine",
    "clinical_medicine",
    "urban_and_rural_planner",
    "accountant",
    "fire_engineer",
    "environmental_impact_assessment_engineer",
    "tax_accountant",
    "physician",
]

ceval_tasks = [
    LightevalTaskConfig(
        name=f"ceval_{Language.CHINESE.value}_{formulation.name.lower()}",
        # for CF the new line has the best results, however it's not really compatible with options presentation
        prompt_function=get_mcq_prompt_function(
            Language.CHINESE,
            partial(
                ceval_adapter,
                Language.CHINESE,
                join_variant="NEW_LINE" if isinstance(formulation, CFFormulation) else "COMMA",
            ),
        ),
        suite=("custom",),
        hf_repo="ceval/ceval-exam",
        hf_subset=task,
        evaluation_splits=("val",),
        few_shots_split="dev",
        metric=(loglikelihood_acc_metric(normalization=LogProbTokenNorm()),),
    )
    for task in CEVAL_SUBSET
    for formulation in [
        MCFFormulation(),
        CFFormulation(),
        HybridFormulation(),
    ]
]

CHINESE_AGIEVAL_SUBSET = [
    "gaokao-biology",
    "gaokao-chinese",
    "gaokao-chemistry",
    "gaokao-geography",
    "gaokao-history",
    "gaokao-mathqa",
    "gaokao-physics",
    "logiqa-zh",
    "jec-qa-kd",
    "jec-qa-ca",
]

agieval_tasks_zh = [
    LightevalTaskConfig(
        name=f"agieval_{Language.CHINESE.value}_{formulation.name.lower()}:{subset}",
        prompt_function=get_mcq_prompt_function(
            Language.CHINESE,
            partial(
                agieval_prompt,
                Language.CHINESE,
                join_variant="NEW_LINE" if isinstance(formulation, CFFormulation) else "COMMA",
            ),
        ),
        suite=("custom",),
        hf_repo=f"hails/agieval-{subset}",
        hf_subset="default",
        evaluation_splits=("test",),
        few_shots_split=None,
        metric=(loglikelihood_acc_metric(normalization=LogProbPMINorm()),),
    )
    for subset in CHINESE_AGIEVAL_SUBSET
    for formulation in [
        MCFFormulation(),
        CFFormulation(),
        HybridFormulation(),
    ]
]

# Arc
mlmm_arc_challenge_tasks = [
    LightevalTaskConfig(
        name=f"mlmm_arc_{language.value}_{formulation.name.lower()}:challenge",
        prompt_function=get_mcq_prompt_function(
            language,
            lambda line: {
                "question": line["question"],
                "choices": line["choices"],
                "gold_idx": int(line["answerKey"]) - 1
                if line["answerKey"].isdigit()
                else LETTER_INDICES.index(line["answerKey"]),
            },
        ),
        suite=("custom",),
        hf_repo="jon-tow/okapi_arc_challenge",
        hf_subset=standardize_tag(language.value),
        hf_revision="823d5d7bfaf8974a3ab52a825b6cf4903b35dbc4",
        trust_dataset=True,
        evaluation_splits=("test",),
        few_shots_split="train",
        metric=(loglikelihood_acc_metric(normalization=LogProbPMINorm()),),
    )
    for language in [
        Language.ENGLISH,
        Language.RUSSIAN,
        Language.GERMAN,
        Language.CHINESE,
        Language.FRENCH,
        Language.SPANISH,
        Language.ITALIAN,
        Language.DUTCH,
        Language.VIETNAMESE,
        Language.INDONESIAN,
        Language.ARABIC,
        Language.HUNGARIAN,
        Language.ROMANIAN,
        Language.DANISH,
        Language.SLOVAK,
        Language.UKRAINIAN,
        Language.CATALAN,
        Language.SERBIAN,
        Language.CROATIAN,
        Language.HINDI,
        Language.BENGALI,
        Language.TAMIL,
        Language.NEPALI,
        Language.MALAYALAM,
        Language.MARATHI,
        Language.TELUGU,
        Language.KANNADA,
    ]
    for formulation in [
        MCFFormulation(),
        CFFormulation(),
        HybridFormulation(),
    ]
]

arabic_ledarboard_arc_easy = [
    LightevalTaskConfig(
        name=f"arc_{Language.ARABIC.value}_{formulation.name.lower()}:easy",
        prompt_function=get_mcq_prompt_function(Language.ARABIC, alghafa_adapter),
        suite=["custom"],
        hf_repo="OALL/AlGhafa-Arabic-LLM-Benchmark-Translated",
        hf_subset="arc_easy_ar",
        hf_revision="a31ebd34ca311d7e0cfc6ad7f458b3435af280f5",
        trust_dataset=True,
        evaluation_splits=["test"],
        few_shots_split="validation",
        metric=(loglikelihood_acc_metric(normalization=LogProbTokenNorm()),),
    )
    for formulation in [
        MCFFormulation(),
        CFFormulation(),
        HybridFormulation(),
    ]
]

turkish_arc = [
    LightevalTaskConfig(
        name=f"arc_{Language.TURKISH.value}_{formulation.name.lower()}:{subset}",
        prompt_function=get_mcq_prompt_function(
            Language.TURKISH,
            lambda line: {
                "question": line["question"],
                "choices": line["choices"]["text"],
                "gold_idx": int(line["answerKey"]) - 1
                if line["answerKey"].isdigit()
                else LETTER_INDICES.index(line["answerKey"]),
            },
        ),
        suite=("custom",),
        hf_repo="malhajar/arc-tr",
        hf_subset=f"ARC-{subset.capitalize()}",
        evaluation_splits=("test",),
        metric=(loglikelihood_acc_metric(normalization=LogProbTokenNorm()),),
    )
    for subset in ["easy", "challenge"]
    for formulation in [
        MCFFormulation(),
        CFFormulation(),
        HybridFormulation(),
    ]
]


# Thruthful-QA
mlmm_truthfulqa_tasks = [
    LightevalTaskConfig(
        name=f"mlmm_truthfulqa_{language.value}_{formulation.name.lower()}:{subset}",
        prompt_function=get_mcq_prompt_function(
            language,
            partial(
                lambda subset, line: {
                    "question": line["question"],
                    "choices": line[f"{subset}_targets"]["choices"],
                    "gold_idx": [ix for ix, label in enumerate(line[f"{subset}_targets"]["labels"]) if label == 1],  # type: ignore
                },
                subset,
            ),
        ),
        suite=("custom",),
        hf_repo="jon-tow/okapi_truthfulqa",
        hf_subset=language.value,
        hf_revision="cdd5db1a66fd04105622109d1c2a5cbc8cde7586",
        trust_dataset=True,
        evaluation_splits=("validation",),
        metric=(loglikelihood_acc_metric(normalization=LogProbTokenNorm()),),
    )
    for subset in ["mc1", "mc2"]
    for language in [
        Language.ARABIC,
        Language.BENGALI,
        Language.CATALAN,
        Language.DANISH,
        Language.GERMAN,
        Language.SPANISH,
        Language.BASQUE,
        Language.FRENCH,
        Language.GUJARATI,
        Language.HINDI,
        Language.CROATIAN,
        Language.HUNGARIAN,
        Language.ARMENIAN,
        Language.INDONESIAN,
        Language.ICELANDIC,
        Language.ITALIAN,
        Language.KANNADA,
        Language.MALAYALAM,
        Language.MARATHI,
        Language.NORWEGIAN,
        Language.NEPALI,
        Language.DUTCH,
        Language.PORTUGUESE,
        Language.ROMANIAN,
        Language.RUSSIAN,
        Language.SLOVAK,
        Language.SERBIAN,
        Language.SWEDISH,
        Language.TAMIL,
        Language.TELUGU,
        Language.UKRAINIAN,
        Language.VIETNAMESE,
        Language.CHINESE,
    ]
    for formulation in [
        MCFFormulation(),
        CFFormulation(),
        HybridFormulation(),
    ]
]

turkish_truthfulqa = [
    LightevalTaskConfig(
        name=f"truthfulqa_{Language.TURKISH.value}_{formulation.name.lower()}",
        prompt_function=get_mcq_prompt_function(
            Language.TURKISH,
            partial(
                lambda subset, line: {
                    "question": line["question"],
                    "choices": line[f"{subset}_targets"]["choices"],
                    "gold_idx": [ix for ix, label in enumerate(line[f"{subset}_targets"]["labels"]) if label == 1],  # type: ignore
                },
                subset,
            ),
        ),
        suite=("custom",),
        hf_repo="malhajar/truthful_qa-tr-v0.2",
        hf_subset="default",
        evaluation_splits=("validation",),
        metric=(loglikelihood_acc_metric(normalization=LogProbTokenNorm()),),
    )
    for subset in ["mc1", "mc2"]
    for formulation in [
        MCFFormulation(),
        CFFormulation(),
        HybridFormulation(),
    ]
]


exams_subjects_by_lang: dict[Language, set[str]] = {
    Language.ARABIC: {"Biology", "Islamic Studies", "Physics", "Science", "Social"},
    Language.BULGARIAN: {"Biology", "Chemistry", "Geography", "History", "Philosophy", "Physics"},
    Language.CROATIAN: {
        "Biology",
        "Chemistry",
        "Ethics",
        "Fine Arts",
        "Geography",
        "Geology",
        "History",
        "Informatics",
        "Philosophy",
        "Physics",
        "Politics",
        "Psychology",
        "Religion",
        "Sociology",
    },
    Language.HUNGARIAN: {
        "Agriculture",
        "Agriculture (Mechanical knowledge)",
        "Biology",
        "Chemistry",
        "Economics",
        "Economics & Marketing",
        "Economics Basics (Business)",
        "Economics Basics (Theoretical)",
        "Forestry",
        "Geography",
        "Landscaping",
        "Physics",
        "Politics",
        "Tourism",
    },
    Language.ITALIAN: {
        "Biology",
        "Chemistry",
        "Ethics",
        "Geography",
        "Geology",
        "History",
        "Informatics",
        "Philosophy",
        "Physics",
        "Politics",
        "Psychology",
        "Sociology",
    },
    Language.SERBIAN: {
        "Biology",
        "Chemistry",
        "Ethics",
        "Geography",
        "Geology",
        "History",
        "Informatics",
        "Philosophy",
        "Physics",
        "Politics",
        "Psychology",
        "Religion",
        "Sociology",
    },
    Language.FRENCH: {"Economics", "Economics & Marketing", "Economics Basics (Theoretical)", "Geography", "Physics"},
    Language.GERMAN: {
        "Chemistry",
        "Economics",
        "Economics & Marketing",
        "Economics Basics (Theoretical)",
        "Geography",
        "Physics",
        "Tourism",
    },
    Language.SPANISH: {"Geography", "Physics"},
    Language.LITHUANIAN: {"Geology", "History"},
    Language.ALBANIAN: {
        "Biology",
        "Business",
        "Chemistry",
        "Fine Arts",
        "History",
        "Philosophy",
        "Physics",
        "Sociology",
    },
    Language.MACEDONIAN: {
        "Biology",
        "Business",
        "Chemistry",
        "Fine Arts",
        "History",
        "Philosophy",
        "Physics",
        "Sociology",
    },
    Language.TURKISH: {
        "Biology",
        "Business",
        "Chemistry",
        "Geography",
        "History",
        "Philosophy",
        "Physics",
        "Sociology",
    },
    Language.POLISH: {"Professional"},
    Language.PORTUGUESE: {"Biology", "Economics", "Geology", "Philosophy"},
    Language.VIETNAMESE: {"Biology", "Chemistry", "Citizenship", "Geography", "History", "Physics"},
}

exams_tasks = [
    LightevalTaskConfig(
        name=f"exams_{language.value}_{formulation.name.lower()}",
        prompt_function=get_mcq_prompt_function(
            language,
            lambda line: {
                "question": line["question"]["stem"],
                "choices": line["question"]["choices"]["text"],
                "gold_idx": line["question"]["choices"]["label"].index(line["answerKey"]),
            },
        ),
        suite=("custom",),
        hf_repo="mhardalov/exams",
        hf_subset="multilingual",
        # Weird bug in dataset
        hf_filter=partial(
            lambda language, subject, line: line["answerKey"] != "@"
            and line["info"]["language"] == LangCodeLanguage(standardize_tag(language.value)).language_name().lower()
            and line["info"]["subject"] == subject,
            language,
            subject,
        ),
        evaluation_splits=("test",),
        few_shots_split="train",
        metric=(loglikelihood_acc_metric(normalization=LogProbTokenNorm()),),
    )
    for language in exams_subjects_by_lang.keys()
    for subject in exams_subjects_by_lang[language]
    for formulation in [
        MCFFormulation(),
        CFFormulation(),
        HybridFormulation(),
    ]
]

m3exam_tasks = [
    LightevalTaskConfig(
        name=f"m3exam_{language.name}_{formulation.name.lower()}",
        suite=("custom",),
        prompt_function=get_mcq_prompt_function(
            language,
            partial(get_m3exam_adapter, language),
        ),
        hf_repo="chiayewken/m3exam",
        hf_subset=LangCodeLanguage(standardize_tag(language.value)).language_name().lower(),
        evaluation_splits=("test",),
        few_shots_split="dev",
        generation_size=-1,
        metric=(loglikelihood_acc_metric(normalization=LogProbTokenNorm()),),
    )
    for language in [
        Language.AFRIKAANS,
        Language.CHINESE,
        Language.ENGLISH,
        Language.ITALIAN,
        Language.JAVANESE,
        Language.PORTUGUESE,
        Language.SWAHILI,
        Language.THAI,
        Language.VIETNAMESE,
    ]
    for formulation in [
        MCFFormulation(),
        CFFormulation(),
        HybridFormulation(),
    ]
]

c3_tasks = [
    LightevalTaskConfig(
        name=f"c3_{Language.CHINESE.name}_{formulation.name.lower()}",
        suite=("custom",),
        prompt_function=get_mcq_prompt_function(
            Language.CHINESE,
            lambda line: {
                "question": line["question"],
                "choices": line["choice"],
                "gold_idx": line["choice"].index(line["answer"]),
                "context": " ".join(line["context"]),
            },
        ),
        hf_repo="clue/clue",
        hf_subset="c3",
        evaluation_splits=("validation",),
        few_shots_split="train",
        metric=(loglikelihood_acc_metric(normalization=LogProbTokenNorm()),),
    )
    for formulation in [
        MCFFormulation(),
        CFFormulation(),
        HybridFormulation(),
    ]
]

# Thai Exams
THAI_EXAMS_SUBSETS = ["a_level", "ic", "onet", "tgat", "tpat1"]

# If too hard we can add help with para
thai_exams_tasks = [
    LightevalTaskConfig(
        name=f"thai_exams_{Language.THAI.value}_{formulation.name.lower()}:{subset}",
        prompt_function=get_mcq_prompt_function(Language.THAI, thai_exams_adapter),
        suite=("custom",),
        hf_repo="scb10x/thai_exam",
        hf_subset=subset,
        evaluation_splits=("test",),
        few_shots_split="train",
        metric=(loglikelihood_acc_metric(normalization=LogProbTokenNorm()),),
    )
    for subset in THAI_EXAMS_SUBSETS
    for formulation in [
        MCFFormulation(),
        CFFormulation(),
        HybridFormulation(),
    ]
]

xcsqa_tasks = [
    LightevalTaskConfig(
        name=f"xcsqa_{language.value}_{formulation.name.lower()}",
        prompt_function=get_mcq_prompt_function(
            language,
            lambda line: {
                "question": line["question"]["stem"],
                "choices": line["question"]["choices"]["text"],
                "gold_idx": line["question"]["choices"]["label"].index(line["answerKey"]),
            },
        ),
        suite=("custom",),
        hf_repo="INK-USC/xcsr",
        hf_subset=f"X-CSQA-{lang}",
        hf_filter=lambda x: all(
            len(x["question"]["choices"]["text"][i].strip()) > 0 for i in range(len(x["question"]["choices"]["text"]))
        ),
        evaluation_splits=("validation",),
        few_shots_split="train",
        metric=[
            loglikelihood_acc_metric(normalization=LogProbPMINorm()),
        ],
    )
    for language in [
        Language.ARABIC,
        Language.GERMAN,
        Language.ENGLISH,
        Language.SPANISH,
        Language.FRENCH,
        Language.HINDI,
        Language.ITALIAN,
        Language.JAPANESE,
        Language.DUTCH,
        Language.POLISH,
        Language.PORTUGUESE,
        Language.RUSSIAN,
        Language.SWAHILI,
        Language.URDU,
        Language.VIETNAMESE,
        Language.CHINESE,
    ]
    for formulation in [
        MCFFormulation(),
        CFFormulation(),
        HybridFormulation(),
    ]
    for lang in [language.value]
]


ALGHAFA_SUBSETS = [
    "mcq_exams_test_ar",
    "meta_ar_dialects",
    "meta_ar_msa",
    "multiple_choice_facts_truefalse_balanced_task",
    "multiple_choice_grounded_statement_soqal_task",
    "multiple_choice_grounded_statement_xglue_mlqa_task",
    "multiple_choice_rating_sentiment_no_neutral_task",
    "multiple_choice_rating_sentiment_task",
    "multiple_choice_sentiment_task",
]

alghafa_native_tasks = [
    LightevalTaskConfig(
        name=f"alghafa_{Language.ARABIC.value}_{formulation.name.lower()}:{subset}",
        hf_subset=subset,
        prompt_function=get_mcq_prompt_function(Language.ARABIC, alghafa_adapter),
        evaluation_splits=["test"],
        few_shots_split="validation",
        suite=["custom"],
        hf_repo="OALL/AlGhafa-Arabic-LLM-Benchmark-Native",
        metric=(loglikelihood_acc_metric(normalization=LogProbTokenNorm()),),
    )
    for subset in ALGHAFA_SUBSETS
    for formulation in [
        MCFFormulation(),
        CFFormulation(),
        HybridFormulation(),
    ]
]

race_ar_task = [
    LightevalTaskConfig(
        name=f"race_{Language.ARABIC.value}_{formulation.name.lower()}",
        prompt_function=get_mcq_prompt_function(Language.ARABIC, alghafa_adapter),
        suite=["custom"],
        hf_repo="OALL/AlGhafa-Arabic-LLM-Benchmark-Translated",
        hf_subset="race_ar",
        hf_revision="a31ebd34ca311d7e0cfc6ad7f458b3435af280f5",
        hf_avail_splits=["test", "validation"],
        evaluation_splits=["test"],
        few_shots_split="validation",
        trust_dataset=True,
        metric=(loglikelihood_acc_metric(normalization=LogProbTokenNorm()),),
    )
    for formulation in [
        MCFFormulation(),
        CFFormulation(),
        HybridFormulation(),
    ]
]

piqa_ar_tasks = [
    LightevalTaskConfig(
        name=f"piqa_{Language.ARABIC.value}_{formulation.name.lower()}",
        prompt_function=get_mcq_prompt_function(Language.ARABIC, alghafa_adapter),
        suite=["custom"],
        hf_repo="OALL/AlGhafa-Arabic-LLM-Benchmark-Translated",
        hf_revision="a31ebd34ca311d7e0cfc6ad7f458b3435af280f5",
        hf_subset="piqa_ar",
        hf_avail_splits=["test", "validation"],
        evaluation_splits=["test"],
        few_shots_split="validation",
        trust_dataset=True,
        metric=(loglikelihood_acc_metric(normalization=LogProbTokenNorm()),),
    )
    for formulation in [
        MCFFormulation(),
        CFFormulation(),
        HybridFormulation(),
    ]
]

openbook_ara_tasks = [
    LightevalTaskConfig(
        name=f"openbookqa_{Language.ARABIC.value}_{formulation.name.lower()}",
        prompt_function=get_mcq_prompt_function(Language.ARABIC, alghafa_adapter),
        suite=["custom"],
        hf_repo="OALL/AlGhafa-Arabic-LLM-Benchmark-Translated",
        hf_subset="openbook_qa_ext_ar",
        hf_revision="a31ebd34ca311d7e0cfc6ad7f458b3435af280f5",
        trust_dataset=True,
        evaluation_splits=["test"],
        few_shots_split="validation",
        metric=(loglikelihood_acc_metric(normalization=LogProbTokenNorm()),),
    )
    for formulation in [
        MCFFormulation(),
        CFFormulation(),
        HybridFormulation(),
    ]
]

openbook_rus_tasks = [
    LightevalTaskConfig(
        name=f"openbookqa_{Language.RUSSIAN.value}_{formulation.name.lower()}",
        prompt_function=get_mcq_prompt_function(
            Language.RUSSIAN,
            lambda line: {
                "question": line["inputs"]["question"],
                "choices": [line["inputs"][f"option_{i.lower()}"] for i in LETTER_INDICES[:4]],
                "gold_idx": LETTER_INDICES.index(line["outputs"]),
            },
        ),
        suite=["custom"],
        hf_repo="ai-forever/MERA",
        hf_subset="ruopenbookqa",
        evaluation_splits=("train",),
        metric=(loglikelihood_acc_metric(normalization=LogProbTokenNorm()),),
    )
    for formulation in [
        MCFFormulation(),
        CFFormulation(),
        HybridFormulation(),
    ]
]

sciq_ar_task = [
    LightevalTaskConfig(
        name=f"sciq_{Language.ARABIC.value}_{formulation.name.lower()}",
        prompt_function=get_mcq_prompt_function(
            Language.ARABIC,
            lambda line: {
                "question": line["question"],
                "choices": line["choices"],
                "gold_idx": line["choices"].index(line["answer"]),
            },
        ),
        suite=["custom"],
        hf_repo="OALL/AlGhafa-Arabic-LLM-Benchmark-Translated",
        hf_subset="sciq_ar",
        hf_revision="a31ebd34ca311d7e0cfc6ad7f458b3435af280f5",
        hf_avail_splits=["test", "validation"],
        evaluation_splits=["test"],
        few_shots_split="validation",
        few_shots_select="sequential",
        metric=(loglikelihood_acc_metric(normalization=LogProbTokenNorm()),),
        trust_dataset=True,
    )
    for formulation in [
        MCFFormulation(),
        CFFormulation(),
        HybridFormulation(),
    ]
]

worldtree_rus_tasks = [
    LightevalTaskConfig(
        name=f"worldtree_{Language.RUSSIAN.value}_{formulation.name.lower()}",
        prompt_function=get_mcq_prompt_function(
            Language.RUSSIAN,
            lambda line: {
                "question": line["inputs"]["question"],
                "choices": [line["inputs"][f"option_{i.lower()}"] for i in LETTER_INDICES[:4]],
                "gold_idx": LETTER_INDICES.index(line["outputs"]),
            },
        ),
        suite=("custom",),
        hf_repo="ai-forever/MERA",
        hf_subset="ruworldtree",
        evaluation_splits=("train",),
        metric=(loglikelihood_acc_metric(normalization=LogProbTokenNorm()),),
    )
    for formulation in [
        MCFFormulation(),
        CFFormulation(),
        HybridFormulation(),
    ]
]


# ------------------------------- Math Tasks ------------------------------- #

mathqa_rus_tasks = [
    LightevalTaskConfig(
        name=f"mathlogic_qa_{Language.RUSSIAN.value}_{formulation.name.lower()}",
        prompt_function=get_mcq_prompt_function(
            Language.RUSSIAN,
            lambda line: {
                "question": line["inputs"]["text"],
                "choices": [line["inputs"][f"option_{i.lower()}"] for i in LETTER_INDICES[:4]],
                "gold_idx": LETTER_INDICES.index(line["outputs"]),
            },
        ),
        suite=("custom",),
        hf_repo="ai-forever/MERA",
        hf_subset="mathlogicqa",
        evaluation_splits=("train",),
        metric=(loglikelihood_acc_metric(normalization=LogProbTokenNorm()),),
    )
    for formulation in [
        MCFFormulation(),
        CFFormulation(),
        HybridFormulation(),
    ]
]
