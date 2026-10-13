MAX_QUESTION_LENGTH = 70

TRUE_FALSE_ANSWERS = frozenset(
    {
        "true",
        "false",
        "verdadero",
        "verdadera",
        "falso",
        "falsa",
    }
)


def is_true_false_question(answer: str, options: list[str] | tuple[str, ...]) -> bool:
    normalized_answer = " ".join(answer.split()).casefold().rstrip(".!?")
    if normalized_answer in TRUE_FALSE_ANSWERS:
        return True

    normalized_options = {
        " ".join(option.split()).casefold().rstrip(".!?") for option in options
    }
    return len(normalized_options) == 2 and normalized_options.issubset(
        TRUE_FALSE_ANSWERS
    )
