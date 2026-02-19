from core.light_split import simple_split_by_mark, simple_split_by_comma, simple_split_by_connectors, simple_split_long_sentences
from core.utils.models import _3_1_SPLIT_BY_NLP
from core.utils import check_file_exists


@check_file_exists(_3_1_SPLIT_BY_NLP)
def split_by_spacy():
    """Split sentences using lightweight rules (no spaCy)."""
    simple_split_by_mark()
    simple_split_by_comma()
    simple_split_by_connectors()
    simple_split_long_sentences()
    return


if __name__ == '__main__':
    split_by_spacy()
