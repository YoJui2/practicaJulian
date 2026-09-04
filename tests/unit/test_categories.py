from app.categories import (
    CATEGORIES,
    find_category_by_name,
    get_category_descriptions,
    get_category_labels,
    get_category_names,
)


def test_category_helpers_return_catalog_values():
    assert get_category_names() == [category["name"] for category in CATEGORIES]
    assert get_category_labels() == [category["label"] for category in CATEGORIES]
    assert get_category_descriptions() == [category["description"] for category in CATEGORIES]


def test_find_category_by_name_returns_matching_category():
    expected = CATEGORIES[0]

    assert find_category_by_name(expected["name"]) is expected


def test_find_category_by_name_returns_none_for_unknown_name():
    assert find_category_by_name("unknown_category") is None
